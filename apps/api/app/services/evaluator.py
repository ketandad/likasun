"""Evaluation service for controls against assets."""

from __future__ import annotations

import logging
import os
import re
import time
from datetime import date, datetime
from typing import Any, Dict, List
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from packages.rules.engine import evaluate_logic as base_evaluate_logic

from app.models import assets as asset_m
from app.models import controls as control_m
from app.models import exceptions as exc_m
from app.models import results as result_m
from app.models import runs as run_m
from app.models.db import SessionLocal

logger = logging.getLogger(__name__)

from app.metrics import (
    evaluate_duration_seconds,
    evaluate_runs_total,
    results_total,
)


def _get_var(data: Dict[str, Any], path: str) -> Any:
    current: Any = data
    for part in path.split("."):
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            raise KeyError(path)
    return current


def _evaluate(rule: Any, data: Dict[str, Any]) -> Any:
    if not isinstance(rule, dict):
        return rule
    if not rule:
        return rule
    op, values = next(iter(rule.items()))

    if op == "var":
        return _get_var(data, values)
    if op == "exists":
        try:
            _get_var(data, values)
            return True
        except KeyError:
            return False
    if op == "regex":
        val = _evaluate(values[0], data)
        pattern = _evaluate(values[1], data)
        return bool(re.search(str(pattern), str(val)))
    if op == "contains":
        arr = _evaluate(values[0], data)
        val = _evaluate(values[1], data)
        return val in arr
    if op == "==":
        a, b = values
        return _evaluate(a, data) == _evaluate(b, data)
    if op == "!=":
        a, b = values
        return _evaluate(a, data) != _evaluate(b, data)
    if op == ">":
        a, b = values
        return _evaluate(a, data) > _evaluate(b, data)
    if op == ">=":
        a, b = values
        return _evaluate(a, data) >= _evaluate(b, data)
    if op == "<":
        a, b = values
        return _evaluate(a, data) < _evaluate(b, data)
    if op == "<=":
        a, b = values
        return _evaluate(a, data) <= _evaluate(b, data)
    if op == "in":
        a, b = values
        return _evaluate(a, data) in _evaluate(b, data)
    if op == "and":
        return all(_evaluate(v, data) for v in values)
    if op == "or":
        return any(_evaluate(v, data) for v in values)
    if op == "!":
        return not _evaluate(values, data)

    # Fallback to base evaluator for other ops
    return base_evaluate_logic(rule, data)


def _build_context(asset: asset_m.Asset) -> Dict[str, Any]:
    return {
        "asset_id": asset.asset_id,
        "type": asset.type,
        "cloud": asset.cloud,
        "region": asset.region,
        "tags": asset.tags or {},
        "config": asset.config or {},
    }


def evaluate_control(
    control: control_m.Control, assets: List[asset_m.Asset]
) -> List[result_m.Result]:
    results: List[result_m.Result] = []
    for asset in assets:
        ctx = _build_context(asset)
        try:
            outcome = _evaluate(control.logic, ctx)
            status = "PASS" if outcome else "FAIL"
        except KeyError:
            status = "NA"
        res = result_m.Result(
            control_id=control.control_id,
            control_title=control.title,
            asset_id=asset.asset_id,
            status=status,
            severity=control.severity,
            frameworks=control.frameworks,
            evidence={
                "asset_id": asset.asset_id,
                "control_id": control.control_id,
                "source": (asset.evidence or {}).get("source"),
                "pointer": (asset.evidence or {}).get("pointer"),
            },
            fix=control.fix,
        )
        results.append(res)
    return results


def _exception_matches(exc: exc_m.Exception, asset: asset_m.Asset) -> bool:
    sel = exc.selector or {}
    if sel.get("asset_id") and sel["asset_id"] != asset.asset_id:
        return False
    if sel.get("type") and sel["type"] != asset.type:
        return False
    env = sel.get("env")
    if env and (asset.tags or {}).get("env") != env:
        return False
    if sel.get("cloud") and sel["cloud"] != asset.cloud:
        return False
    return True


@evaluate_duration_seconds.time()
def run_evaluation(
    job_id: str | None = None,
    *,
    controls_scope: List[str] | None = None,
    assets_scope: List[str] | None = None,
    dry_run: bool = False,
) -> Dict[str, Any]:
    start = time.perf_counter()
    session: Session = SessionLocal()
    run_id = str(uuid4())
    run = run_m.EvaluationRun(run_id=run_id, status="running")
    session.add(run)
    session.commit()

    today = date.today()
    exceptions = session.scalars(
        select(exc_m.Exception).where(exc_m.Exception.expires_at >= today)
    ).all()

    controls_query = (
        session.query(control_m.Control).order_by(control_m.Control.control_id)
    )
    if controls_scope:
        controls_query = controls_query.filter(
            control_m.Control.control_id.in_(controls_scope)
        )
    controls_list = controls_query.all()

    results_count = 0
    assets_count = 0
    status_counts: Dict[str, int] = {}

    for control in controls_list:
        types = control.applies_to.get("types")
        if not types and control.applies_to.get("type"):
            types = [control.applies_to.get("type")]
        asset_query = session.query(asset_m.Asset).filter(
            asset_m.Asset.type.in_(types or [])
        )
        if assets_scope:
            asset_query = asset_query.filter(
                asset_m.Asset.asset_id.in_(assets_scope)
            )
        assets_list = asset_query.order_by(asset_m.Asset.asset_id).all()
        assets_count += len(assets_list)
        control_results = evaluate_control(control, assets_list)
        for res, asset in zip(control_results, assets_list):
            for exc in exceptions:
                if exc.control_id == control.control_id and _exception_matches(exc, asset):
                    res.meta = {"prev_status": res.status}
                    res.status = "WAIVED"
                    break
            if not dry_run:
                res.run_id = run_id
        results_count += len(control_results)
        if not dry_run and control_results:
            session.bulk_save_objects(control_results)
            session.commit()
            for r in control_results:
                status_counts[r.status] = status_counts.get(r.status, 0) + 1

    run.controls_count = len(controls_list)
    run.assets_count = assets_count
    run.results_count = results_count
    run.finished_at = datetime.utcnow()
    run.status = "completed"
    session.commit()

    evaluate_runs_total.inc()
    for status, count in status_counts.items():
        results_total.labels(status=status).inc(count)

    # Cleanup old runs
    keep = int(os.getenv("EVALUATION_KEEP", "3"))
    run_ids = session.scalars(
        select(run_m.EvaluationRun.run_id).order_by(run_m.EvaluationRun.started_at.desc())
    ).all()
    if len(run_ids) > keep:
        old_ids = run_ids[keep:]
        session.query(result_m.Result).filter(
            result_m.Result.run_id.in_(old_ids)
        ).delete(synchronize_session=False)
        session.query(run_m.EvaluationRun).filter(
            run_m.EvaluationRun.run_id.in_(old_ids)
        ).delete(synchronize_session=False)
        session.commit()

    session.close()
    duration = time.perf_counter() - start
    logger.info("Evaluation run %s completed in %.2fs", run_id, duration)
    return {
        "run_id": run_id,
        "controls_count": len(controls_list),
        "assets_count": assets_count,
        "results_count": results_count,
    }


__all__ = ["run_evaluation", "evaluate_control"]

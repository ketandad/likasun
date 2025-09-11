"""Endpoints for evaluation runs and results."""

from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.jobs.evaluation import enqueue
from app.core.license import license_required
from app.models import assets as asset_m
from app.models import controls as control_m
from app.models import results as result_m
from app.models import runs as run_m

router = APIRouter(prefix="/evaluate", tags=["evaluate"])


@router.post("/run", dependencies=[Depends(license_required("evaluate"))])
def run_evaluation(
    controls: Optional[List[str]] = None,
    assets: Optional[List[str]] = None,
    dry_run: bool = False,
):
    return enqueue(controls=controls, assets=assets, dry_run=dry_run)


@router.get("/results")
def list_results(
    status: str | None = Query(None),
    severity: str | None = Query(None),
    env: str | None = Query(None),
    cloud: str | None = Query(None),
    category: str | None = Query(None),
    framework: str | None = Query(None),
    control_id: str | None = Query(None),
    type: str | None = Query(None),
    run_id: str | None = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    query = db.query(result_m.Result)
    if status:
        query = query.filter(result_m.Result.status == status)
    if severity:
        query = query.filter(result_m.Result.severity == severity)
    if control_id:
        query = query.filter(result_m.Result.control_id == control_id)
    if framework:
        query = query.filter(result_m.Result.frameworks.contains([framework]))
    if run_id:
        query = query.filter(result_m.Result.run_id == run_id)
    if env or cloud or type or category:
        query = query.join(asset_m.Asset, result_m.Result.asset_id == asset_m.Asset.asset_id)
    if env:
        query = query.filter(asset_m.Asset.tags["env"].astext == env)
    if cloud:
        query = query.filter(asset_m.Asset.cloud == cloud)
    if type:
        query = query.filter(asset_m.Asset.type == type)
    if category:
        query = query.join(
            control_m.Control,
            result_m.Result.control_id == control_m.Control.control_id,
        ).filter(control_m.Control.category == category)
    rows = (
        query.order_by(result_m.Result.id).offset(offset).limit(limit).all()
    )
    return [
        {
            "control_id": r.control_id,
            "control_title": r.control_title,
            "asset_id": r.asset_id,
            "status": r.status,
            "severity": r.severity,
            "frameworks": r.frameworks,
            "evidence": r.evidence,
            "run_id": r.run_id,
        }
        for r in rows
    ]


@router.get("/runs")
def list_runs(db: Session = Depends(get_db)):
    runs = db.scalars(
        select(run_m.EvaluationRun).order_by(run_m.EvaluationRun.started_at.desc())
    ).all()
    return [
        {
            "run_id": r.run_id,
            "started_at": r.started_at,
            "finished_at": r.finished_at,
            "controls_count": r.controls_count,
            "assets_count": r.assets_count,
            "results_count": r.results_count,
            "status": r.status,
        }
        for r in runs
    ]


__all__ = ["router"]

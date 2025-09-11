"""Results endpoints."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, Iterable, List

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy import asc, desc
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.models import assets as asset_m
from app.models import controls as control_m
from app.models import results as result_m
from app.models import runs as run_m


class ResultStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    NA = "NA"
    WAIVED = "WAIVED"


class Severity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class CloudEnum(str, Enum):
    aws = "aws"
    azure = "azure"
    gcp = "gcp"
    iac = "iac"


class SortBy(str, Enum):
    evaluated_at = "evaluated_at"
    severity = "severity"
    status = "status"
    control_id = "control_id"
    asset_id = "asset_id"


class SortDir(str, Enum):
    asc = "asc"
    desc = "desc"


class ResultItem(BaseModel):
    control_id: str
    control_title: str
    category: str | None = None
    severity: str
    frameworks: List[str] = []
    asset_id: str
    type: str | None = None
    cloud: str | None = None
    region: str | None = None
    env: str | None = None
    status: str
    evidence: Dict[str, Any] | None = None
    fix: Dict[str, Any] | None = None
    evaluated_at: datetime
    run_id: str


class ResultsPage(BaseModel):
    items: List[ResultItem]
    page: int
    page_size: int
    total_items: int
    total_pages: int
    run_id: str


router = APIRouter(prefix="/results", tags=["results"])


def _latest_run_id(db: Session) -> str | None:
    return db.query(run_m.EvaluationRun.run_id).order_by(
        run_m.EvaluationRun.started_at.desc()
    ).limit(1).scalar()


def _apply_filters(
    query,  # type: ignore
    *,
    status: ResultStatus | None,
    severity: Severity | None,
    env: str | None,
    cloud: CloudEnum | None,
    category: str | None,
    framework: str | None,
    control_id: str | None,
    type_: str | None,
    asset_id: str | None,
    evaluated_from: datetime | None,
    evaluated_to: datetime | None,
):
    if status:
        query = query.filter(result_m.Result.status == status)
    if severity:
        query = query.filter(result_m.Result.severity == severity)
    if control_id:
        query = query.filter(result_m.Result.control_id == control_id)
    if asset_id:
        query = query.filter(result_m.Result.asset_id == asset_id)
    if category:
        query = query.filter(control_m.Control.category == category)
    if framework:
        query = query.filter(result_m.Result.frameworks.contains([framework]))
    if cloud:
        query = query.filter(asset_m.Asset.cloud == cloud)
    if type_:
        query = query.filter(asset_m.Asset.type == type_)
    if env:
        query = query.filter(asset_m.Asset.tags["env"].as_string() == env)
    if evaluated_from:
        query = query.filter(result_m.Result.evaluated_at >= evaluated_from)
    if evaluated_to:
        query = query.filter(result_m.Result.evaluated_at <= evaluated_to)
    return query


def _build_query(
    db: Session,
    *,
    run_id: str | None,
    status: ResultStatus | None,
    severity: Severity | None,
    env: str | None,
    cloud: CloudEnum | None,
    category: str | None,
    framework: str | None,
    control_id: str | None,
    type_: str | None,
    asset_id: str | None,
    evaluated_from: datetime | None,
    evaluated_to: datetime | None,
):
    if run_id is None:
        run_id = _latest_run_id(db)
    if run_id is None:
        return db.query(result_m.Result).filter(False), None
    query = (
        db.query(result_m.Result, asset_m.Asset, control_m.Control)
        .join(asset_m.Asset, asset_m.Asset.asset_id == result_m.Result.asset_id)
        .join(
            control_m.Control,
            control_m.Control.control_id == result_m.Result.control_id,
        )
        .filter(result_m.Result.run_id == run_id)
    )
    query = _apply_filters(
        query,
        status=status,
        severity=severity,
        env=env,
        cloud=cloud,
        category=category,
        framework=framework,
        control_id=control_id,
        type_=type_,
        asset_id=asset_id,
        evaluated_from=evaluated_from,
        evaluated_to=evaluated_to,
    )
    return query, run_id


def _serialize(res: result_m.Result, asset: asset_m.Asset, control: control_m.Control) -> ResultItem:
    return ResultItem(
        control_id=res.control_id,
        control_title=res.control_title,
        category=control.category,
        severity=res.severity,
        frameworks=list(res.frameworks or []),
        asset_id=res.asset_id,
        type=asset.type,
        cloud=asset.cloud,
        region=asset.region,
        env=(asset.tags or {}).get("env"),
        status=res.status,
        evidence=res.evidence,
        fix=res.fix,
        evaluated_at=res.evaluated_at,
        run_id=res.run_id,
    )


@router.get("/")
def list_results(
    *,
    status: ResultStatus | None = Query(None),
    severity: Severity | None = Query(None),
    env: str | None = Query(None),
    cloud: CloudEnum | None = Query(None),
    category: str | None = Query(None),
    framework: str | None = Query(None),
    control_id: str | None = Query(None),
    type: str | None = Query(None, alias="type"),
    asset_id: str | None = Query(None),
    run_id: str | None = Query(None),
    evaluated_from: datetime | None = Query(None),
    evaluated_to: datetime | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=1000),
    sort_by: SortBy = Query(SortBy.evaluated_at),
    sort_dir: SortDir = Query(SortDir.desc),
    db: Session = Depends(get_db),
) -> ResultsPage:
    query, actual_run_id = _build_query(
        db,
        run_id=run_id,
        status=status,
        severity=severity,
        env=env,
        cloud=cloud,
        category=category,
        framework=framework,
        control_id=control_id,
        type_=type,
        asset_id=asset_id,
        evaluated_from=evaluated_from,
        evaluated_to=evaluated_to,
    )
    if actual_run_id is None:
        return ResultsPage(
            items=[],
            page=page,
            page_size=page_size,
            total_items=0,
            total_pages=0,
            run_id="",
        )
    sort_column_map = {
        SortBy.evaluated_at: result_m.Result.evaluated_at,
        SortBy.severity: result_m.Result.severity,
        SortBy.status: result_m.Result.status,
        SortBy.control_id: result_m.Result.control_id,
        SortBy.asset_id: result_m.Result.asset_id,
    }
    sort_col = sort_column_map.get(sort_by, result_m.Result.evaluated_at)
    order = desc(sort_col) if sort_dir == SortDir.desc else asc(sort_col)
    query = query.order_by(order)
    total_items = query.count()
    query = query.offset((page - 1) * page_size).limit(page_size)
    items = [_serialize(r, a, c) for r, a, c in query.all()]
    total_pages = (total_items + page_size - 1) // page_size
    return ResultsPage(
        items=items,
        page=page,
        page_size=page_size,
        total_items=total_items,
        total_pages=total_pages,
        run_id=actual_run_id,
    )


@router.get("/export.csv")
def export_results(
    *,
    status: ResultStatus | None = Query(None),
    severity: Severity | None = Query(None),
    env: str | None = Query(None),
    cloud: CloudEnum | None = Query(None),
    category: str | None = Query(None),
    framework: str | None = Query(None),
    control_id: str | None = Query(None),
    type: str | None = Query(None, alias="type"),
    asset_id: str | None = Query(None),
    run_id: str | None = Query(None),
    evaluated_from: datetime | None = Query(None),
    evaluated_to: datetime | None = Query(None),
    sort_by: SortBy = Query(SortBy.evaluated_at),
    sort_dir: SortDir = Query(SortDir.desc),
    db: Session = Depends(get_db),
) -> StreamingResponse:
    query, actual_run_id = _build_query(
        db,
        run_id=run_id,
        status=status,
        severity=severity,
        env=env,
        cloud=cloud,
        category=category,
        framework=framework,
        control_id=control_id,
        type_=type,
        asset_id=asset_id,
        evaluated_from=evaluated_from,
        evaluated_to=evaluated_to,
    )
    if actual_run_id is None:
        actual_run_id = ""
    sort_column_map = {
        SortBy.evaluated_at: result_m.Result.evaluated_at,
        SortBy.severity: result_m.Result.severity,
        SortBy.status: result_m.Result.status,
        SortBy.control_id: result_m.Result.control_id,
        SortBy.asset_id: result_m.Result.asset_id,
    }
    sort_col = sort_column_map.get(sort_by, result_m.Result.evaluated_at)
    order = desc(sort_col) if sort_dir == SortDir.desc else asc(sort_col)
    query = query.order_by(order)

    headers = [
        "run_id",
        "evaluated_at",
        "status",
        "severity",
        "category",
        "framework_ids",
        "control_id",
        "control_title",
        "asset_id",
        "asset_type",
        "cloud",
        "region",
        "env",
        "evidence_source",
        "evidence_pointer",
        "fix",
    ]

    def row_iter() -> Iterable[str]:
        import csv
        import io

        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow(headers)
        yield buf.getvalue()
        buf.seek(0)
        buf.truncate(0)
        for r, a, c in query.yield_per(100):
            row = [
                r.run_id,
                r.evaluated_at.isoformat(),
                r.status,
                r.severity,
                c.category,
                "|".join(r.frameworks or []),
                r.control_id,
                r.control_title,
                r.asset_id,
                a.type,
                a.cloud,
                a.region,
                (a.tags or {}).get("env"),
                (r.evidence or {}).get("source"),
                (r.evidence or {}).get("pointer"),
                (r.fix or {}).get("short"),
            ]
            writer.writerow(row)
            yield buf.getvalue()
            buf.seek(0)
            buf.truncate(0)

    filename = f"raybeam_results_{actual_run_id or 'latest'}.csv"
    return StreamingResponse(
        row_iter(),
        media_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": f"attachment; filename=\"{filename}\"",
        },
    )


@router.get("/summary")
def summary_results(
    *,
    status: ResultStatus | None = Query(None),
    severity: Severity | None = Query(None),
    env: str | None = Query(None),
    cloud: CloudEnum | None = Query(None),
    category: str | None = Query(None),
    framework: str | None = Query(None),
    control_id: str | None = Query(None),
    type: str | None = Query(None, alias="type"),
    asset_id: str | None = Query(None),
    run_id: str | None = Query(None),
    evaluated_from: datetime | None = Query(None),
    evaluated_to: datetime | None = Query(None),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    query, actual_run_id = _build_query(
        db,
        run_id=run_id,
        status=status,
        severity=severity,
        env=env,
        cloud=cloud,
        category=category,
        framework=framework,
        control_id=control_id,
        type_=type,
        asset_id=asset_id,
        evaluated_from=evaluated_from,
        evaluated_to=evaluated_to,
    )
    by_status: Dict[str, int] = {s.value: 0 for s in ResultStatus}
    by_severity: Dict[str, int] = {s.value: 0 for s in Severity}
    by_framework: Dict[str, int] = {}
    for r, a, c in query.all():
        by_status[r.status] = by_status.get(r.status, 0) + 1
        by_severity[r.severity] = by_severity.get(r.severity, 0) + 1
        for fw in r.frameworks or []:
            by_framework[fw] = by_framework.get(fw, 0) + 1
    return {
        "by_status": by_status,
        "by_severity": by_severity,
        "by_framework": by_framework,
        "run_id": actual_run_id or "",
    }

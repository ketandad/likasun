"""Assets endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.models import assets as asset_m
from app.models import controls as control_m
from app.models import results as result_m
from app.models import runs as run_m

router = APIRouter(prefix="/assets", tags=["assets"])


@router.get("/")
def list_assets(db: Session = Depends(get_db)) -> list[dict]:
    assets = db.query(asset_m.Asset).all()
    return [
        {
            "id": a.id,
            "asset_id": a.asset_id,
            "cloud": a.cloud,
            "type": a.type,
            "region": a.region,
            "tags": a.tags,
            "config": a.config,
            "evidence": a.evidence,
            "ingest_source": a.ingest_source,
            "ingested_at": a.ingested_at,
        }
        for a in assets
    ]


@router.get("/{asset_id}")
def get_asset(
    asset_id: str,
    run_id: str | None = Query(None),
    db: Session = Depends(get_db),
) -> dict:
    asset = (
        db.query(asset_m.Asset).filter(asset_m.Asset.asset_id == asset_id).first()
    )
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    if run_id is None:
        run_id = (
            db.query(run_m.EvaluationRun.run_id)
            .order_by(run_m.EvaluationRun.started_at.desc())
            .limit(1)
            .scalar()
        )
    if run_id is None:
        results: list[dict] = []
    else:
        query = (
            db.query(result_m.Result, control_m.Control)
            .join(
                control_m.Control,
                control_m.Control.control_id == result_m.Result.control_id,
            )
            .filter(
                result_m.Result.asset_id == asset_id,
                result_m.Result.run_id == run_id,
            )
        )
        results = [
            {
                "control_id": r.control_id,
                "control_title": r.control_title,
                "category": c.category,
                "severity": r.severity,
                "frameworks": list(r.frameworks or []),
                "asset_id": r.asset_id,
                "type": asset.type,
                "cloud": asset.cloud,
                "region": asset.region,
                "env": (asset.tags or {}).get("env"),
                "status": r.status,
                "evidence": r.evidence,
                "fix": r.fix,
                "evaluated_at": r.evaluated_at,
                "run_id": r.run_id,
            }
            for r, c in query.all()
        ]
    asset_data = {
        "asset_id": asset.asset_id,
        "type": asset.type,
        "cloud": asset.cloud,
        "region": asset.region,
        "tags": asset.tags,
        "config": asset.config,
    }
    return {"asset": asset_data, "results": results, "run_id": run_id or ""}


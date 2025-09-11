"""Assets endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.models.assets import Asset

router = APIRouter(prefix="/assets", tags=["assets"])


@router.get("/")
def list_assets(db: Session = Depends(get_db)) -> list[dict]:
    assets = db.query(Asset).all()
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


from __future__ import annotations

import uuid
from pathlib import Path
from typing import List

from fastapi import APIRouter, Depends, File, Query, UploadFile, HTTPException
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.ingest.parsers import get_parser
from app.ingest.connectors import get_connector
from app.models.assets import Asset

router = APIRouter(prefix="/ingest", tags=["ingest"])

UPLOAD_ROOT = Path("/data/uploads")


@router.post("/files")
async def upload_files(files: List[UploadFile] = File(...)) -> dict:
    session_id = uuid.uuid4().hex
    session_dir = UPLOAD_ROOT / session_id
    session_dir.mkdir(parents=True, exist_ok=True)
    uploads: dict[str, str] = {}
    for file in files:
        dest = session_dir / file.filename
        dest.write_bytes(await file.read())
        uploads[file.filename] = f"{session_id}/{file.filename}"
    return {"upload_ids": uploads}


@router.post("/parse")
def parse_uploads(
    cloud: str,
    upload_id: List[str] = Query(...),
    db: Session = Depends(get_db),
) -> dict:
    parser = get_parser(cloud)
    paths = [UPLOAD_ROOT / uid for uid in upload_id]
    assets_data = parser(paths)

    for data in assets_data:
        existing = (
            db.query(Asset)
            .filter(Asset.asset_id == data["asset_id"], Asset.cloud == data["cloud"])
            .one_or_none()
        )
        if existing:
            for key, value in data.items():
                setattr(existing, key, value)
        else:
            db.add(Asset(**data))
    db.commit()
    return {"assets": len(assets_data)}


@router.post("/live")
def ingest_live(cloud: str, db: Session = Depends(get_db)) -> dict:
    connector = get_connector(cloud)
    try:
        assets = connector.list_assets()
    except Exception as exc:  # pragma: no cover - surfaced in response
        return {"ingested": 0, "errors": [str(exc)]}

    for asset in assets:
        existing = (
            db.query(Asset)
            .filter(Asset.asset_id == asset.asset_id, Asset.cloud == asset.cloud)
            .one_or_none()
        )
        if existing:
            for field in ["type", "region", "tags", "config", "evidence", "ingest_source"]:
                setattr(existing, field, getattr(asset, field))
        else:
            db.add(asset)
    db.commit()
    return {"ingested": len(assets), "errors": []}


@router.get("/live/permissions")
def live_permissions(cloud: str) -> dict:
    connector = get_connector(cloud)
    return connector.validate_permissions()

"""Policy vs Practice module endpoints."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.models import assets as asset_m

router = APIRouter(prefix="/modules/policy", tags=["modules"])

UPLOAD_DIR = Path("./data/uploads/modules/policy")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/upload")
async def upload_policy(file: UploadFile = File(...)) -> dict:
    path = UPLOAD_DIR / file.filename
    path.write_bytes(await file.read())
    return {"policy_path": str(path)}


class IngestRequest(BaseModel):
    policy_path: str
    actual: Dict[str, Any]


@router.post("/ingest")
def ingest_policy(req: IngestRequest, db: Session = Depends(get_db)) -> dict:
    path = Path(req.policy_path)
    if not path.exists():
        raise HTTPException(status_code=404, detail="policy not found")
    data = json.loads(path.read_text())
    cfg = {
        "policy_retention_days": data.get("retention_days"),
        "policy_requires_mfa": data.get("requires_mfa"),
        "policy_encryption_at_rest": data.get("encryption_at_rest"),
        "policy_min_tls": data.get("min_tls"),
        "actual_retention_days": req.actual.get("retention_days"),
        "actual_mfa": req.actual.get("requires_mfa"),
        "actual_encryption_at_rest": req.actual.get("encryption_at_rest"),
        "actual_min_tls": req.actual.get("min_tls"),
    }
    asset = asset_m.Asset(
        asset_id=f"policy:{path.stem}",
        cloud="saas",
        type="policy",
        region="",
        tags={},
        config=cfg,
        evidence={"source": str(path), "pointer": "policy"},
        ingest_source="policy",
    )
    db.merge(asset)
    db.commit()
    return {"ingested": asset.asset_id}

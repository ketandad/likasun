"""Residency module endpoints."""

from __future__ import annotations

from pathlib import Path
import yaml

from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.models import assets as asset_m
from app.models import results as result_m

router = APIRouter(prefix="/modules/residency", tags=["modules"])

POLICY_PATH = Path("/data/policies/residency.yaml")
POLICY_PATH.parent.mkdir(parents=True, exist_ok=True)


@router.post("/policy")
async def upload_policy(file: UploadFile = File(...)) -> dict:
    POLICY_PATH.write_bytes(await file.read())
    return {"policy_path": str(POLICY_PATH)}


@router.get("/check")
def check_residency(db: Session = Depends(get_db)) -> dict:
    if not POLICY_PATH.exists():
        return {"results": 0}
    policy = yaml.safe_load(POLICY_PATH.read_text()) or {}
    assets = db.query(asset_m.Asset).all()
    results = []
    for a in assets:
        data_class = (a.config or {}).get("data_class")
        if not data_class:
            continue
        allowed = policy.get(data_class, [])
        status = "PASS" if a.region in allowed else "FAIL"
        res = result_m.Result(
            control_id="RESIDENCY_VIOLATION",
            control_title="Asset within allowed region",
            asset_id=a.asset_id,
            status=status,
            severity="high",
            frameworks=["FEDRAMP_LOW", "SOC2", "CIS", "CCPA"],
            evidence={"asset_region": a.region, "allowed": allowed},
            fix={},
            run_id="residency",
        )
        results.append(res)
    db.bulk_save_objects(results)
    db.commit()
    return {"results": len(results)}

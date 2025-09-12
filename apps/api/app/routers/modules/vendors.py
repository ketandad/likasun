"""Vendors module endpoints."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import List

from fastapi import APIRouter, UploadFile, File, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.models import vendors as vendor_m
from app.models import assets as asset_m

router = APIRouter(prefix="/modules/vendors", tags=["modules"])

UPLOAD_DIR = Path("./data/uploads/modules/vendors")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


class VendorModel(BaseModel):
    vendor_id: str
    product: str
    scopes: List[str] = []
    data_classes: List[str] = []
    dpa_present: bool = False
    soc2: bool = False
    iso27001: bool = False
    last_review_days: int = 0


@router.post("/upsert")
def upsert_vendor(v: VendorModel, db: Session = Depends(get_db)) -> dict:
    vendor = vendor_m.Vendor(
        vendor_id=v.vendor_id,
        product=v.product,
        scopes={"items": v.scopes},
        data_classes={"items": v.data_classes},
        dpia_status="",
        risk="",
        meta={
            "dpa_present": v.dpa_present,
            "soc2": v.soc2,
            "iso27001": v.iso27001,
            "last_review_days": v.last_review_days,
        },
    )
    db.merge(vendor)
    asset = asset_m.Asset(
        asset_id=f"vendor:{v.vendor_id}",
        cloud="saas",
        type="vendor",
        region="",
        tags={"vendor": v.vendor_id},
        config={
            "scopes": v.scopes,
            "data_classes": v.data_classes,
            "meta": vendor.meta,
            "has_critical_scope": any(s in {"payments", "health"} for s in v.scopes),
        },
        evidence={"source": f"vendor:{v.vendor_id}", "pointer": "record"},
        ingest_source="vendors",
    )
    db.merge(asset)
    db.commit()
    return {"upserted": v.vendor_id}


@router.post("/bulk")
async def bulk_vendors(file: UploadFile = File(...), db: Session = Depends(get_db)) -> dict:
    path = UPLOAD_DIR / file.filename
    path.write_bytes(await file.read())
    count = 0
    if file.filename.endswith(".json"):
        data = json.loads(path.read_text())
        for item in data:
            upsert_vendor(VendorModel(**item), db)
            count += 1
    else:
        with path.open() as f:
            reader = csv.DictReader(f)
            for row in reader:
                item = VendorModel(
                    vendor_id=row["vendor_id"],
                    product=row["product"],
                    scopes=[s.strip() for s in row.get("scopes", "").split(";") if s],
                    data_classes=[s.strip() for s in row.get("data_classes", "").split(";") if s],
                    dpa_present=row.get("dpa_present", "false").lower() == "true",
                    soc2=row.get("soc2", "false").lower() == "true",
                    iso27001=row.get("iso27001", "false").lower() == "true",
                    last_review_days=int(row.get("last_review_days", "0")),
                )
                upsert_vendor(item, db)
                count += 1
    return {"ingested": count}

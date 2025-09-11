"""Contracts module endpoints."""

from __future__ import annotations

import re
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.models import documents as doc_m
from app.models import assets as asset_m

router = APIRouter(prefix="/modules/contracts", tags=["modules"])

UPLOAD_DIR = Path("/data/uploads/modules/contracts")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


class IngestRequest(BaseModel):
    doc_path: str
    vendor: str
    product: str
    region: str | None = None


@router.post("/upload")
async def upload_contract(file: UploadFile = File(...)) -> dict:
    path = UPLOAD_DIR / file.filename
    data = await file.read()
    path.write_bytes(data)
    return {"doc_path": str(path)}


def _extract_fields(text: str) -> dict:
    def _search(pattern: str, cast=str):
        m = re.search(pattern, text, re.IGNORECASE)
        if not m:
            return None
        return cast(m.group(1))

    renewal = _search(r"renewal date[:\-\s]+(\d{4}-\d{2}-\d{2})")
    termination = _search(r"termination notice[:\-\s]+(\d+)", int)
    breach = _search(r"breach (?:window|notification)[:\-\s]+(\d+)", int)
    location = _search(r"data location[:\-\s]+([\w-]+)")
    dpa = bool(re.search(r"dpa[:\-\s]+(yes|present|true)", text, re.IGNORECASE))
    return {
        "renewal_date": renewal,
        "termination_notice_days": termination,
        "breach_window_hours": breach,
        "data_location": location,
        "dpa_present": dpa,
    }


@router.post("/ingest")
def ingest_contract(req: IngestRequest, db: Session = Depends(get_db)) -> dict:
    path = Path(req.doc_path)
    if not path.exists():
        raise HTTPException(status_code=404, detail="doc_path not found")
    text = path.read_text(errors="ignore")
    fields = _extract_fields(text)
    doc_id = path.stem
    document = doc_m.Document(
        doc_id=doc_id,
        kind="contract",
        clauses=fields,
        meta={"vendor": req.vendor, "product": req.product},
        ingest_source=str(path),
    )
    db.merge(document)
    asset = asset_m.Asset(
        asset_id=f"contract:{doc_id}",
        cloud="saas",
        type="contract",
        region=req.region or "",
        tags={"vendor": req.vendor, "product": req.product},
        config=fields,
        evidence={
            "source": f"doc:contracts:{path.name}",
            "pointer": "page:1",
        },
        ingest_source="contracts",
    )
    db.merge(asset)
    db.commit()
    return {"ingested": doc_id}

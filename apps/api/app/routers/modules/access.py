"""Access module endpoints."""

from __future__ import annotations

import csv
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.models import assets as asset_m
from app.models import actors as actor_m

router = APIRouter(prefix="/modules/access", tags=["modules"])

UPLOAD_DIR = Path("./data/uploads/modules/access")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


class UploadResponse(BaseModel):
    hr_path: str
    iam_path: str


@router.post("/upload", response_model=UploadResponse)
async def upload_access(hr: UploadFile = File(...), iam: UploadFile = File(...)) -> UploadResponse:
    hr_path = UPLOAD_DIR / hr.filename
    hr_path.write_bytes(await hr.read())
    iam_path = UPLOAD_DIR / iam.filename
    iam_path.write_bytes(await iam.read())
    return UploadResponse(hr_path=str(hr_path), iam_path=str(iam_path))


class IngestRequest(BaseModel):
    hr_path: str
    iam_path: str


@router.post("/ingest")
def ingest_access(req: IngestRequest, db: Session = Depends(get_db)) -> dict:
    hr_file = Path(req.hr_path)
    iam_file = Path(req.iam_path)
    if not hr_file.exists() or not iam_file.exists():
        raise HTTPException(status_code=404, detail="file not found")

    hr_data: dict[str, dict] = {}
    with hr_file.open() as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, start=2):
            hr_data[row["email"]] = {"status": row.get("status"), "row": i}

    iam_data: dict[str, dict] = {}
    with iam_file.open() as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, start=2):
            iam_data[row["email"]] = {
                "mfa": row.get("mfa", "false").lower() == "true",
                "roles": [r.strip() for r in row.get("roles", "").split(";") if r],
                "last_seen": row.get("last_seen"),
                "row": i,
            }

    emails = set(hr_data) | set(iam_data)
    now = datetime.now(timezone.utc)
    for email in emails:
        hr = hr_data.get(email)
        iam = iam_data.get(email)
        hr_status = hr.get("status") if hr else "unknown"
        iam_status = "active" if iam else "inactive"
        mfa = iam.get("mfa", False) if iam else False
        roles = iam.get("roles", []) if iam else []
        last_seen_str = iam.get("last_seen") if iam else None
        last_seen_days = 9999
        last_seen_dt = None
        if last_seen_str:
            try:
                last_seen_dt = datetime.fromisoformat(last_seen_str).astimezone(timezone.utc)
                last_seen_days = (now - last_seen_dt).days
            except Exception:
                pass
        actor = actor_m.Actor(
            actor_id=email,
            source="access",
            status=iam_status,
            mfa=mfa,
            roles={"roles": roles},
            last_seen=last_seen_dt,
            meta={"hr_status": hr_status},
        )
        db.merge(actor)
        evidence = {
            "source": {"hr": str(hr_file), "iam": str(iam_file)},
            "pointer": {
                "hr": hr.get("row") if hr else None,
                "iam": iam.get("row") if iam else None,
            },
        }
        asset = asset_m.Asset(
            asset_id=f"user:{email}",
            cloud="saas",
            type="useraccount",
            region="",
            tags={"email": email},
            config={
                "hr_status": hr_status,
                "iam_status": iam_status,
                "mfa": mfa,
                "roles": roles,
                "last_seen_days": last_seen_days,
            },
            evidence=evidence,
            ingest_source="access",
        )
        db.merge(asset)
    db.commit()
    return {"ingested": len(emails)}

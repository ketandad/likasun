"""Compliance endpoints."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Tuple

import io
import yaml
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.models import results as result_m, runs as run_m
from app.core.license import license_required


class Framework(str, Enum):
    PCI_DSS = "PCI-DSS"
    GDPR = "GDPR"
    DPDP = "DPDP"
    ISO27001 = "ISO27001"
    NIST_800_53 = "NIST-800-53"
    HIPAA = "HIPAA"
    FEDRAMP_LOW = "FedRAMP-Low"
    FEDRAMP_MODERATE = "FedRAMP-Moderate"
    FEDRAMP_HIGH = "FedRAMP-High"
    SOC2 = "SOC2"
    CIS = "CIS"
    CCPA = "CCPA"


FRAMEWORK_FILES = {
    Framework.PCI_DSS: "pci.yaml",
    Framework.GDPR: "gdpr.yaml",
    Framework.DPDP: "dpdp.yaml",
    Framework.ISO27001: "iso27001.yaml",
    Framework.NIST_800_53: "nist80053.yaml",
    Framework.HIPAA: "hipaa.yaml",
    Framework.FEDRAMP_LOW: "fedramp_low.yaml",
    Framework.FEDRAMP_MODERATE: "fedramp_moderate.yaml",
    Framework.FEDRAMP_HIGH: "fedramp_high.yaml",
    Framework.SOC2: "soc2.yaml",
    Framework.CIS: "cis.yaml",
    Framework.CCPA: "ccpa.yaml",
}


router = APIRouter(
    prefix="/compliance",
    tags=["compliance"],
    dependencies=[Depends(license_required("compliance"))],
)


REPO_ROOT = Path(__file__).resolve().parents[4]
MAPPINGS_DIR = REPO_ROOT / "packages" / "rules" / "mappings"

_mappings_cache: Dict[Framework, List[Dict]] = {}
for fw, fname in FRAMEWORK_FILES.items():
    path = MAPPINGS_DIR / fname
    if path.exists():
        with path.open("r", encoding="utf-8") as f:
            _mappings_cache[fw] = yaml.safe_load(f) or []
    else:
        _mappings_cache[fw] = []

_summary_cache: Dict[Tuple[Framework, str], Dict] = {}


def get_latest_run_id(db: Session) -> str | None:
    return (
        db.query(run_m.EvaluationRun.run_id)
        .order_by(run_m.EvaluationRun.started_at.desc())
        .limit(1)
        .scalar()
    )


def _compute_requirement_status(statuses: List[str]) -> str:
    if not statuses:
        return "NA"
    if "FAIL" in statuses:
        return "FAIL"
    if all(s == "PASS" for s in statuses):
        return "PASS"
    if set(statuses).issubset({"PASS", "WAIVED"}) and "WAIVED" in statuses:
        return "WAIVED"
    if all(s == "NA" for s in statuses):
        return "NA"
    return "FAIL"


def _build_summary(framework: Framework, db: Session) -> Dict:
    run_id = get_latest_run_id(db)
    if run_id is None:
        raise HTTPException(status_code=404, detail="No evaluation runs found")
    cache_key = (framework, run_id)
    if cache_key in _summary_cache:
        return _summary_cache[cache_key]

    mapping = _mappings_cache.get(framework, [])
    requirements = []
    counts = {"pass": 0, "fail": 0, "waived": 0, "na": 0}

    for item in mapping:
        control_ids = item.get("mapped_controls", [])
        res = (
            db.query(result_m.Result)
            .filter(
                result_m.Result.run_id == run_id,
                result_m.Result.control_id.in_(control_ids),
            )
            .all()
        )
        statuses = [r.status for r in res]
        req_status = _compute_requirement_status(statuses)
        counts[req_status.lower()] += 1
        evidence = [
            {
                "control_id": r.control_id,
                "asset_id": r.asset_id,
                "status": r.status,
            }
            for r in res
        ]
        requirements.append(
            {
                "id": item.get("requirement_id"),
                "title": item.get("title"),
                "mapped_controls": control_ids,
                "status": req_status,
                "evidence": evidence,
            }
        )

    total = len(mapping)
    score = int((counts["pass"] / total) * 100) if total else 0
    summary = {
        "framework": framework.value,
        "requirements": requirements,
        "summary": {
            "total_requirements": total,
            "pass": counts["pass"],
            "fail": counts["fail"],
            "na": counts["na"],
            "waived": counts["waived"],
            "score_percent": score,
        },
        "run_id": run_id,
    }
    _summary_cache[cache_key] = summary
    return summary


def load_framework_mapping(framework: str) -> List[Dict]:
    try:
        fw = Framework(framework)
    except ValueError:
        return []
    return _mappings_cache.get(fw, [])


def compute_framework_summary(framework: str, run_id: str, db: Session) -> Dict[str, int]:
    counts = {"pass": 0, "fail": 0, "na": 0, "waived": 0}
    mapping = load_framework_mapping(framework)
    if not run_id or not mapping:
        return counts
    for item in mapping:
        control_ids = item.get("mapped_controls", [])
        statuses = [
            r[0]
            for r in db.query(result_m.Result.status)
            .filter(
                result_m.Result.run_id == run_id,
                result_m.Result.control_id.in_(control_ids),
            )
            .all()
        ]
        req_status = _compute_requirement_status(statuses)
        counts[req_status.lower()] += 1
    return counts


def list_failed_requirements(
    framework: str, run_id: str, db: Session, limit: int = 50
) -> List[Tuple[str, str, List[str]]]:
    failed: List[Tuple[str, str, List[str]]] = []
    mapping = load_framework_mapping(framework)
    if not run_id or not mapping:
        return failed
    for item in mapping:
        control_ids = item.get("mapped_controls", [])
        has_fail = (
            db.query(result_m.Result)
            .filter(
                result_m.Result.run_id == run_id,
                result_m.Result.control_id.in_(control_ids),
                result_m.Result.status == "FAIL",
            )
            .first()
        )
        if has_fail:
            failed.append((item.get("requirement_id"), item.get("title"), control_ids))
            if len(failed) >= limit:
                break
    return failed


@router.get("/summary")
def compliance_summary(
    *, framework: Framework = Query(...), db: Session = Depends(get_db)
):
    return _build_summary(framework, db)


@router.get("/evidence-pack")
def evidence_pack(
    framework: str = Query(..., alias="framework"),
    run_id: str | None = None,
    db: Session = Depends(get_db),
):
    mapping = load_framework_mapping(framework)
    if not mapping:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown or empty framework mapping: {framework}",
        )

    rid = run_id or get_latest_run_id(db)
    if not rid:
        rid = "none"

    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    w, h = A4
    y = h - 36

    c.setFont("Helvetica-Bold", 14)
    c.drawString(36, y, f"RayBeam Evidence Pack — {framework}")
    y -= 18
    c.setFont("Helvetica", 10)
    c.drawString(36, y, f"Run: {rid}   Generated: {datetime.utcnow().isoformat()}Z")
    y -= 24

    summary = compute_framework_summary(framework, rid, db)
    c.drawString(
        36,
        y,
        f"Summary: PASS={summary.get('pass',0)}  FAIL={summary.get('fail',0)}  NA={summary.get('na',0)}  WAIVED={summary.get('waived',0)}",
    )
    y -= 24

    failed = list_failed_requirements(framework, rid, db, limit=50)
    if not failed:
        c.drawString(36, y, "No failed requirements for this run.")
        y -= 18
    else:
        c.setFont("Helvetica-Bold", 12)
        c.drawString(36, y, "Failed Requirements:")
        y -= 18
        c.setFont("Helvetica", 10)
        for req_id, title, controls in failed:
            line = f"• {req_id} — {title} (controls: {', '.join(controls)[:120]})"
            if y < 60:
                c.showPage()
                y = h - 36
                c.setFont("Helvetica", 10)
            c.drawString(36, y, line)
            y -= 14

    c.showPage()
    c.save()
    buf.seek(0)

    headers = {
        "Content-Disposition": f'attachment; filename="raybeam_evidence_{framework}_{rid}.pdf"'
    }
    return StreamingResponse(buf, media_type="application/pdf", headers=headers)


@router.get("/export.csv")
def compliance_export_csv(
    *, framework: Framework = Query(...), db: Session = Depends(get_db)
):
    data = _build_summary(framework, db)
    run_id = data["run_id"]

    def generate():
        yield "requirement_id,requirement_title,mapped_controls,status,run_id\n"
        for r in data["requirements"]:
            mapped_controls = ";".join(r["mapped_controls"])
            row = f"{r['id']},{r['title']},{mapped_controls},{r['status']},{run_id}\n"
            yield row

    headers = {
        "Content-Disposition": f"attachment; filename=raybeam_compliance_{framework.value}_{run_id}.csv",
    }
    return StreamingResponse(generate(), media_type="text/csv", headers=headers)

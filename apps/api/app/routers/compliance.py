"""Compliance endpoints."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from io import BytesIO
from pathlib import Path
from typing import Dict, List, Tuple

import yaml
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.models import results as result_m, runs as run_m
from app.core.license import license_required

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import (
        SimpleDocTemplate,
        Paragraph,
        Spacer,
        Table,
        PageBreak,
    )
except Exception:  # pragma: no cover - reportlab may be missing in some environments
    SimpleDocTemplate = None  # type: ignore


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


def _latest_run_id(db: Session) -> str | None:
    return db.query(run_m.EvaluationRun.run_id).order_by(
        run_m.EvaluationRun.started_at.desc()
    ).limit(1).scalar()


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
    run_id = _latest_run_id(db)
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


@router.get("/summary")
def compliance_summary(
    *, framework: Framework = Query(...), db: Session = Depends(get_db)
):
    return _build_summary(framework, db)


@router.get("/evidence-pack")
def compliance_evidence_pack(
    *, framework: Framework = Query(...), db: Session = Depends(get_db)
):
    data = _build_summary(framework, db)
    if SimpleDocTemplate is None:
        raise HTTPException(status_code=500, detail="PDF generator not available")
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story: List = []

    # Cover page
    story.append(Paragraph(f"{framework.value} Evidence Pack", styles["Title"]))
    story.append(Spacer(1, 12))
    story.append(Paragraph(datetime.utcnow().strftime("%Y-%m-%d"), styles["Normal"]))
    story.append(Paragraph(f"Run ID: {data['run_id']}", styles["Normal"]))
    story.append(PageBreak())

    # Executive summary
    summary = data["summary"]
    story.append(Paragraph("Executive Summary", styles["Heading1"]))
    story.append(Paragraph(f"Score: {summary['score_percent']}%", styles["Normal"]))
    story.append(
        Paragraph(
            f"Totals - PASS: {summary['pass']}, FAIL: {summary['fail']}, NA: {summary['na']}, WAIVED: {summary['waived']}",
            styles["Normal"],
        )
    )
    story.append(PageBreak())

    # Coverage matrix
    story.append(Paragraph("Coverage Matrix", styles["Heading1"]))
    table_data = [["Requirement", "Status"]]
    for r in data["requirements"]:
        table_data.append([f"{r['id']}: {r['title']}", r["status"]])
    story.append(Table(table_data))
    story.append(PageBreak())

    # Failed requirements
    story.append(Paragraph("Failed Requirements", styles["Heading1"]))
    for r in data["requirements"]:
        if r["status"] == "FAIL":
            story.append(Paragraph(f"{r['id']} - {r['title']}", styles["Heading2"]))
            for ev in r["evidence"]:
                story.append(
                    Paragraph(
                        f"{ev['control_id']} / {ev['asset_id']}: {ev['status']}",
                        styles["Normal"],
                    )
                )
    story.append(PageBreak())

    # Exceptions
    story.append(Paragraph("Exceptions", styles["Heading1"]))
    for r in data["requirements"]:
        if r["status"] == "WAIVED":
            story.append(Paragraph(f"{r['id']} - {r['title']}", styles["Normal"]))

    doc.build(story)
    buffer.seek(0)
    headers = {
        "Content-Type": "application/pdf",
        "Content-Disposition": f"attachment; filename=raybeam_evidence_{framework.value}_{data['run_id']}.pdf",
    }
    return StreamingResponse(buffer, media_type="application/pdf", headers=headers)


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

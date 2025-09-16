
from __future__ import annotations
"""Rules endpoints for rule-pack management."""

import io
import tarfile
import tempfile
from pathlib import Path
from typing import List

import yaml
from fastapi import APIRouter, File, HTTPException, UploadFile, Depends, Query
from sqlalchemy.orm import Session

from ..dependencies import get_db
from ..models import controls as control_m, meta as meta_m
from packages.rules.engine import ControlTemplate, RuleEngine
from packages.rules.frameworks import Framework
from packages.shared.crypto import verify_signature
from app.services.audit import record

router = APIRouter(prefix="/rules", tags=["rules"])

RULEPACK_DIR = Path("/data/rulepacks")
REQUIRED_MAPPINGS = {
    "pci",
    "gdpr",
    "dpdp",
    "iso27001",
    "nist",
    "hipaa",
    "fedramp_low",
    "fedramp_moderate",
    "fedramp_high",
    "soc2",
    "cis",
    "ccpa",
}


def _parse_pack(data: bytes) -> tuple[dict, List[dict], List[str]]:
    """Validate *data* tarball and return (meta, controls, frameworks)."""
    with tarfile.open(fileobj=io.BytesIO(data)) as tar:
        try:
            meta_bytes = tar.extractfile("rules/meta.yaml").read()
            sig = tar.extractfile("rules/signatures/meta.sig").read().decode().strip()
        except Exception as exc:  # pragma: no cover - defensive
            raise ValueError("Missing meta or signature") from exc
        verify_signature(meta_bytes, sig)
        meta = yaml.safe_load(meta_bytes)
        tmpdir = tempfile.mkdtemp()
        tar.extractall(tmpdir)
    rule_dir = Path(tmpdir) / "rules"
    templates_dir = rule_dir / "templates"
    mappings_dir = rule_dir / "mappings"
    expansions = yaml.safe_load((rule_dir / "expansions.yaml").read_text())
    envs = expansions.get("envs", [])
    types = expansions.get("types", [])
    params = expansions.get("params", [{}])
    templates: List[ControlTemplate] = []
    for p in templates_dir.glob("*.y*ml"):
        t = yaml.safe_load(p.read_text())
        templates.append(
            ControlTemplate(
                template_id=t["template_id"],
                title=t["title"],
                logic=t.get("logic", {}),
                frameworks=[Framework(f) for f in t.get("frameworks", [])],
            )
        )
    engine = RuleEngine(templates)
    controls = engine.expand(envs, types, params)
    control_ids = {c["control_id"] for c in controls}
    frameworks: List[str] = []
    for name in REQUIRED_MAPPINGS:
        mp = mappings_dir / f"{name}.yaml"
        if not mp.exists():
            raise ValueError(f"Missing mapping: {name}.yaml")
        data = yaml.safe_load(mp.read_text())
        for cid in data.get("mapped_controls", []):
            if cid not in control_ids:
                raise ValueError(f"Mapping {name} references unknown control {cid}")
        frameworks.append(name.upper())
    return meta, controls, frameworks


def _apply_pack(meta: dict, controls: List[dict], session: Session) -> None:
    session.query(control_m.Control).delete()
    for c in controls:
        obj = control_m.Control(
            control_id=c["control_id"],
            title=c["title"],
            category="",
            severity="",
            applies_to=c.get("applies_to", {}),
            logic=c.get("logic", {}),
            frameworks=c.get("frameworks", []),
            fix={},
        )
        session.add(obj)
    existing = session.get(meta_m.Meta, "active_rulepack_version")
    if existing:
        existing.value = meta["version"]
    else:
        session.add(meta_m.Meta(key="active_rulepack_version", value=meta["version"]))
    session.commit()


@router.post("/upload")
async def upload_rulepack(
    file: UploadFile = File(...),
    apply: bool = Query(False),
    db: Session = Depends(get_db),
) -> dict:
    data = await file.read()
    try:
        meta, controls, frameworks = _parse_pack(data)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    version = meta["version"]
    RULEPACK_DIR.mkdir(parents=True, exist_ok=True)
    (RULEPACK_DIR / f"{version}.tar.gz").write_bytes(data)
    if apply:
        _apply_pack(meta, controls, db)
        packs = sorted(RULEPACK_DIR.glob("*.tar.gz"), key=lambda p: p.stat().st_mtime, reverse=True)
        for p in packs[3:]:
            p.unlink()
    result = {"version": version, "control_count": len(controls), "frameworks": frameworks}
    record("RULEPACK_UPLOAD", resource=version, details=result)
    return result


@router.post("/rollback")
async def rollback_rulepack(version: str, db: Session = Depends(get_db)) -> dict:
    path = RULEPACK_DIR / f"{version}.tar.gz"
    if not path.exists():
        raise HTTPException(status_code=404, detail="Version not found")
    data = path.read_bytes()
    try:
        meta, controls, frameworks = _parse_pack(data)
    except ValueError as exc:  # pragma: no cover - should not happen if pack saved
        raise HTTPException(status_code=400, detail=str(exc))
    _apply_pack(meta, controls, db)
    result = {"version": version, "control_count": len(controls), "frameworks": frameworks}
    record("RULEPACK_ROLLBACK", resource=version, details=result)
    return result


@router.get("/status")
async def rulepack_status(db: Session = Depends(get_db)) -> dict:
    obj = db.get(meta_m.Meta, "active_rulepack_version")
    current = obj.value if obj else None
    available = sorted([p.stem for p in RULEPACK_DIR.glob("*.tar.gz")])
    return {"current": current, "available": available}

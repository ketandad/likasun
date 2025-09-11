from datetime import date, timedelta
import base64
import os
import sys
import tarfile
from pathlib import Path

import yaml
from nacl import signing

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

sys.path.append(str(Path(__file__).resolve().parents[4]))

from main import app
from app.dependencies import get_db
from app.core.config import settings
from app.core import license as lic
from app.core.security import get_current_user
from app.models.db import Base
from app.models import db as models_db
from app.services import evaluator
from app.routers import rules as rules_router

ROOT = Path(__file__).resolve().parents[4]
FIXTURES = ROOT / "tests" / "fixtures"

PRIVATE_KEY_B64 = "gpXAdxXlavULojMEhEjRN8gmpXBOcIrtn3rwlKQCCis="


def make_pack(tmp_path: Path, version: str, tamper: bool = False) -> Path:
    pack_dir = tmp_path / "build" / "rules"
    (pack_dir / "templates").mkdir(parents=True, exist_ok=True)
    (pack_dir / "mappings").mkdir(exist_ok=True)
    (pack_dir / "signatures").mkdir(exist_ok=True)
    meta = {
        "version": version,
        "date": "2024-01-01",
        "min_engine_version": "0",
        "description": "test",
    }
    meta_yaml = yaml.safe_dump(meta)
    sk = signing.SigningKey(base64.b64decode(PRIVATE_KEY_B64))
    sig = sk.sign(meta_yaml.encode()).signature
    (pack_dir / "meta.yaml").write_text(meta_yaml if not tamper else meta_yaml + "#tamper")
    (pack_dir / "signatures" / "meta.sig").write_text(base64.b64encode(sig).decode())
    (pack_dir / "expansions.yaml").write_text(
        yaml.safe_dump({"envs": ["demo"], "types": ["StorageBucket"], "params": [{"enabled": True}]})
    )
    template = {
        "template_id": f"tmpl{version}",
        "title": "Sample {env} {type}",
        "logic": {"var": "enabled"},
        "frameworks": ["PCI"],
        "severity": "low",
        "category": "general",
    }
    (pack_dir / "templates" / "tmpl.yaml").write_text(yaml.safe_dump(template))
    mapping = {
        "requirement_id": "r1",
        "title": "req",
        "mapped_controls": [f"tmpl{version}-demo-StorageBucket"],
    }
    for name in [
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
    ]:
        (pack_dir / "mappings" / f"{name}.yaml").write_text(yaml.safe_dump(mapping))
    tar_path = tmp_path / f"{version}.tar.gz"
    with tarfile.open(tar_path, "w:gz") as tar:
        tar.add(pack_dir, arcname="rules")
    return tar_path


def setup_client(tmp_path: Path):
    os.chdir(ROOT)
    engine = create_engine(
        "sqlite:///:memory:",
        future=True,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    models_db.SessionLocal = TestingSessionLocal
    models_db.engine = engine
    evaluator.SessionLocal = TestingSessionLocal
    app.dependency_overrides[get_current_user] = lambda: {"username": "admin", "role": "admin"}
    settings.LICENSE_FILE = str(FIXTURES / "licenses" / "dev.json")
    lic._current_license = None  # type: ignore
    lic.load_license()
    rules_router.RULEPACK_DIR = tmp_path
    return TestClient(app), TestingSessionLocal


def test_ingest_evaluate_compliance_and_exception(tmp_path: Path):
    client, SessionLocal = setup_client(tmp_path)
    version = "2024.01.0"
    ctrl_id = f"tmpl{version}-demo-StorageBucket"
    pack = make_pack(tmp_path, version)
    with pack.open("rb") as f:
        r = client.post(
            "/rules/upload?apply=true",
            files={"file": ("p.tar.gz", f.read(), "application/gzip")},
        )
    assert r.status_code == 200

    r = client.post("/assets/load-demo")
    assert r.status_code == 200
    assert r.json()["ingested"] > 0

    r = client.post("/evaluate/run")
    assert r.status_code == 200
    run_id = r.json()["run_id"]

    r = client.get("/evaluate/results", params={"run_id": run_id})
    assert r.status_code == 200
    assert r.json()

    r = client.get(
        "/evaluate/results", params={"framework": "FedRAMP Moderate"}
    )
    assert r.status_code == 200

    r = client.get(
        "/compliance/evidence-pack", params={"framework": "PCI-DSS"}
    )
    assert r.status_code == 200
    assert r.headers["content-type"] == "application/pdf"

    exc = {
        "control_id": ctrl_id,
        "selector": {"type": "StorageBucket", "env": "demo"},
        "reason": "waiver",
        "expires_at": (date.today() + timedelta(days=1)).isoformat(),
    }
    r = client.post("/exceptions", json=exc)
    assert r.status_code == 200

    r = client.post("/evaluate/run")
    run_id = r.json()["run_id"]
    r = client.get(
        "/evaluate/results",
        params={"run_id": run_id, "control_id": ctrl_id},
    )
    assert r.status_code == 200
    assert r.json()[0]["status"] == "WAIVED"


def test_invalid_rulepack_rejected(tmp_path: Path):
    client, _ = setup_client(tmp_path)
    pack = make_pack(tmp_path, "2024.01.1", tamper=True)
    with pack.open("rb") as f:
        r = client.post(
            "/rules/upload?apply=true",
            files={"file": ("p.tar.gz", f.read(), "application/gzip")},
        )
    assert r.status_code == 400

import base64
import json
import tarfile
from io import BytesIO
from pathlib import Path

import yaml
from fastapi.testclient import TestClient
from nacl import signing
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

ROOT = Path(__file__).resolve().parents[1]
import sys
sys.path.append(str(ROOT / "apps/api"))

from main import app  # type: ignore
from app.dependencies import get_db
from app.models.db import Base
from app.routers import rules as rules_router
from app.models import controls as control_m, meta as meta_m

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
        yaml.safe_dump({"envs": ["dev"], "types": ["ec2"], "params": [{"enabled": True}]})
    )
    template = {
        "template_id": f"tmpl{version}",
        "title": "Sample {env} {type}",
        "logic": {"var": "enabled"},
        "frameworks": ["PCI"],
    }
    (pack_dir / "templates" / "tmpl.yaml").write_text(yaml.safe_dump(template))
    mapping = {
        "requirement_id": "r1",
        "title": "req",
        "mapped_controls": [f"tmpl{version}-dev-ec2"],
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
    rules_router.RULEPACK_DIR = tmp_path
    return TestClient(app), TestingSessionLocal


def test_valid_pack_applies(tmp_path):
    pack = make_pack(tmp_path, "2024.01.0")
    client, SessionLocal = setup_client(tmp_path)
    with pack.open("rb") as f:
        r = client.post("/rules/upload?apply=true", files={"file": ("p.tar.gz", f.read(), "application/gzip")})
    assert r.status_code == 200
    session = SessionLocal()
    assert session.query(control_m.Control).count() == 1
    meta = session.get(meta_m.Meta, "active_rulepack_version")
    assert meta and meta.value == "2024.01.0"


def test_invalid_signature_rejected(tmp_path):
    pack = make_pack(tmp_path, "2024.01.1", tamper=True)
    client, SessionLocal = setup_client(tmp_path)
    with pack.open("rb") as f:
        r = client.post("/rules/upload?apply=true", files={"file": ("p.tar.gz", f.read(), "application/gzip")})
    assert r.status_code == 400
    session = SessionLocal()
    assert session.query(control_m.Control).count() == 0


def test_rollback_restores(tmp_path):
    pack1 = make_pack(tmp_path, "2024.01.0")
    pack2 = make_pack(tmp_path, "2024.02.0")
    client, SessionLocal = setup_client(tmp_path)
    with pack1.open("rb") as f:
        client.post("/rules/upload?apply=true", files={"file": ("a.tar.gz", f.read(), "application/gzip")})
    with pack2.open("rb") as f:
        client.post("/rules/upload?apply=true", files={"file": ("b.tar.gz", f.read(), "application/gzip")})
    session = SessionLocal()
    ctrl = session.query(control_m.Control).one()
    assert ctrl.control_id == "tmpl2024.02.0-dev-ec2"
    r = client.post("/rules/rollback?version=2024.01.0")
    assert r.status_code == 200
    session.close()
    session = SessionLocal()
    ctrl = session.query(control_m.Control).one()
    assert ctrl.control_id == "tmpl2024.01.0-dev-ec2"

import sys
from datetime import date, datetime, timedelta
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import json
import base64
import uuid
from nacl import signing

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT / "apps/api"))

from main import app  # type: ignore
from app.dependencies import get_db
from app.models.db import Base
from app.models import results as result_m, assets as asset_m, controls as control_m, runs as run_m
from app.core.config import settings
from app.core import license as lic

PRIVATE_KEY_B64 = "gpXAdxXlavULojMEhEjRN8gmpXBOcIrtn3rwlKQCCis="


def setup_client():
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

    license_data = {
        "org": "Acme",
        "edition": "enterprise",
        "features": ["evaluate", "compliance"],
        "seats": 5,
        "expiry": (date.today() + timedelta(days=30)).isoformat(),
        "jti": str(uuid.uuid4()),
        "iat": int(datetime.utcnow().timestamp()),
    }
    payload = json.dumps(license_data, sort_keys=True, separators=(",", ":")).encode()
    sk = signing.SigningKey(base64.b64decode(PRIVATE_KEY_B64))
    sig = sk.sign(payload).signature
    license_data["sig"] = base64.b64encode(sig).decode()
    path = ROOT / "test_license.rbl"
    path.write_text(json.dumps(license_data))
    settings.LICENSE_FILE = str(path)
    lic._current_license = None  # type: ignore
    lic.load_license()

    return TestClient(app), TestingSessionLocal


def seed_data(SessionLocal):
    session = SessionLocal()
    run = run_m.EvaluationRun(run_id="run1", status="finished")
    asset = asset_m.Asset(
        asset_id="A1",
        cloud="aws",
        type="Bucket",
        region="us-east-1",
        tags={},
        config={},
        evidence={},
        ingest_source="test",
    )
    controls = [
        control_m.Control(
            control_id=f"C{i}",
            title=f"Control {i}",
            category="Cat",
            severity="LOW",
            applies_to={},
            logic={},
            frameworks=[],
            fix={},
        )
        for i in range(1, 6)
    ]
    results = [
        result_m.Result(
            control_id="C1",
            control_title="Control 1",
            asset_id="A1",
            status="PASS",
            severity="LOW",
            frameworks=[],
            evidence={},
            fix={},
            evaluated_at=datetime(2024, 1, 1),
            run_id="run1",
        ),
        result_m.Result(
            control_id="C2",
            control_title="Control 2",
            asset_id="A1",
            status="FAIL",
            severity="LOW",
            frameworks=[],
            evidence={},
            fix={},
            evaluated_at=datetime(2024, 1, 1),
            run_id="run1",
        ),
        result_m.Result(
            control_id="C3",
            control_title="Control 3",
            asset_id="A1",
            status="WAIVED",
            severity="LOW",
            frameworks=[],
            evidence={},
            fix={},
            evaluated_at=datetime(2024, 1, 1),
            run_id="run1",
        ),
    ]
    session.add_all([run, asset] + controls + results)
    session.commit()
    session.close()


def test_summary_counts():
    client, SessionLocal = setup_client()
    seed_data(SessionLocal)
    resp = client.get("/compliance/summary", params={"framework": "FedRAMP-Moderate"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["framework"] == "FedRAMP-Moderate"
    assert data["summary"] == {
        "total_requirements": 5,
        "pass": 1,
        "fail": 1,
        "na": 2,
        "waived": 1,
        "score_percent": 20,
    }
    assert data["run_id"] == "run1"


def test_evidence_pack_pdf():
    client, SessionLocal = setup_client()
    seed_data(SessionLocal)
    resp = client.get("/compliance/evidence-pack", params={"framework": "PCI-DSS"})
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "application/pdf"
    assert resp.content.startswith(b"%PDF")


def test_export_csv():
    client, SessionLocal = setup_client()
    seed_data(SessionLocal)
    resp = client.get("/compliance/export.csv", params={"framework": "SOC2"})
    assert resp.status_code == 200
    lines = resp.text.strip().split("\n")
    assert lines[0] == "requirement_id,requirement_title,mapped_controls,status,run_id"
    assert len(lines) == 6


def test_framework_filters():
    client, SessionLocal = setup_client()
    seed_data(SessionLocal)
    frameworks = [
        "FedRAMP-Low",
        "FedRAMP-Moderate",
        "FedRAMP-High",
        "SOC2",
        "CIS",
        "CCPA",
    ]
    for fw in frameworks:
        resp = client.get("/compliance/summary", params={"framework": fw})
        assert resp.status_code == 200
        assert resp.json()["framework"] == fw

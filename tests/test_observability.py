import re
import sys
from pathlib import Path
from datetime import date
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT / "apps/api"))

from main import app  # type: ignore
from app.dependencies import get_db
from app.core.config import settings
from app.core.security import users_db
from app.models.db import Base
from app.models import controls as control_m, assets as asset_m, audit as audit_m
from app.services import evaluator
from app.core import license as license_mod
from packages.schemas.license import License


def setup_client():
    engine = create_engine(
        "sqlite:///:memory:",
        future=True,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    # ensure audit model loaded
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    import app.models.db as models_db

    models_db.SessionLocal = TestingSessionLocal
    evaluator.SessionLocal = TestingSessionLocal
    license_mod._current_license = License(
        org="t",
        edition="enterprise",
        features=["evaluate", "compliance"],
        seats=10,
        expiry=date(2099, 1, 1),
        jti=uuid4(),
        iat=0,
        scope={},
        sig="x",
    )
    return TestClient(app), TestingSessionLocal


def test_metrics_route_enabled():
    client, _ = setup_client()
    settings.METRICS_ENABLED = True
    resp = client.get("/metrics")
    assert resp.status_code == 200
    assert "raybeam_http_requests_total" in resp.text


def test_evaluation_increments_metrics():
    client, SessionLocal = setup_client()
    settings.METRICS_ENABLED = True
    session = SessionLocal()
    control = control_m.Control(
        control_id="C1",
        title="Check",
        category="cat",
        severity="low",
        applies_to={"types": ["Server"]},
        logic={"==": [{"var": "config.ok"}, True]},
        frameworks=[],
        fix={},
    )
    asset = asset_m.Asset(
        asset_id="A1",
        cloud="aws",
        type="Server",
        region="us",
        tags={},
        config={"ok": True},
        evidence={"source": "x", "pointer": "y"},
        ingest_source="test",
    )
    session.add_all([control, asset])
    session.commit()
    session.close()

    metrics_before = client.get("/metrics").text
    m = re.search(r"raybeam_evaluate_runs_total\s+(\d+)", metrics_before)
    runs_before = int(m.group(1)) if m else 0

    res = client.post("/evaluate/run")
    assert res.status_code == 200

    metrics_after = client.get("/metrics").text
    m2 = re.search(r"raybeam_evaluate_runs_total\s+(\d+)", metrics_after)
    runs_after = int(m2.group(1)) if m2 else 0
    assert runs_after == runs_before + 1
    before_pass = re.search(
        r'raybeam_results_total\{status="PASS"\}\s+(\d+)', metrics_before
    )
    after_pass = re.search(
        r'raybeam_results_total\{status="PASS"\}\s+(\d+)', metrics_after
    )
    bp = int(before_pass.group(1)) if before_pass else 0
    ap = int(after_pass.group(1)) if after_pass else 0
    assert ap == bp + 1


def test_exception_audit_logged():
    client, SessionLocal = setup_client()
    users_db.clear()
    users_db["admin"] = {"username": "admin", "password": "pw", "role": "admin"}

    session = SessionLocal()
    control = control_m.Control(
        control_id="C2",
        title="Check",
        category="c",
        severity="low",
        applies_to={"types": ["Server"]},
        logic={},
        frameworks=[],
        fix={},
    )
    session.add(control)
    session.commit()
    session.close()

    token = client.post("/auth/login", data={"username": "admin", "password": "pw"}).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "control_id": "C2",
        "selector": {"type": "Server"},
        "reason": "test",
        "expires_at": date(2099, 1, 1).isoformat(),
    }
    resp = client.post("/exceptions", json=payload, headers=headers)
    assert resp.status_code == 200

    session = SessionLocal()
    log = (
        session.query(audit_m.AuditLog)
        .filter(audit_m.AuditLog.action == "EXCEPTION_CREATE")
        .one()
    )
    assert log.actor == "admin"
    session.close()

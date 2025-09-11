import sys
from datetime import date
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Ensure app module importable
ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT / "apps/api"))

from main import app  # type: ignore
from app.dependencies import get_db
from app.models.db import Base
from app.models import controls as control_m, assets as asset_m, exceptions as exc_m, results as result_m, db as models_db


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
    models_db.SessionLocal = TestingSessionLocal
    return TestClient(app), TestingSessionLocal


def test_exception_waives_result():
    client, SessionLocal = setup_client()
    session = SessionLocal()
    control = control_m.Control(
        control_id="IAM_USERS_MFA",
        title="Users must have MFA",
        category="iam",
        severity="high",
        applies_to={"types": ["User"]},
        logic={"==": [{"var": "config.mfa"}, True]},
        frameworks=["FedRAMP-Moderate"],
        fix={},
    )
    asset = asset_m.Asset(
        asset_id="user1",
        cloud="aws",
        type="User",
        region="us-east-1",
        tags={"env": "prod"},
        config={"mfa": False},
        evidence={"source": "x", "pointer": "y"},
        ingest_source="test",
    )
    exc = exc_m.Exception(
        control_id="IAM_USERS_MFA",
        selector={"type": "User", "env": "prod"},
        reason="waived",
        expires_at=date(2099, 1, 1),
        created_by="me",
    )
    session.add_all([control, asset, exc])
    session.commit()
    session.close()

    from app.services import evaluator

    evaluator.SessionLocal = SessionLocal
    evaluator.run_evaluation()

    session = SessionLocal()
    res = session.query(result_m.Result).one()
    assert res.status == "WAIVED"
    assert res.meta["prev_status"] == "FAIL"


def test_expired_exception_ignored():
    client, SessionLocal = setup_client()
    session = SessionLocal()
    control = control_m.Control(
        control_id="IAM_USERS_MFA",
        title="Users must have MFA",
        category="iam",
        severity="high",
        applies_to={"types": ["User"]},
        logic={"==": [{"var": "config.mfa"}, True]},
        frameworks=["FedRAMP-Moderate"],
        fix={},
    )
    asset = asset_m.Asset(
        asset_id="user1",
        cloud="aws",
        type="User",
        region="us-east-1",
        tags={"env": "prod"},
        config={"mfa": False},
        evidence={"source": "x", "pointer": "y"},
        ingest_source="test",
    )
    exc = exc_m.Exception(
        control_id="IAM_USERS_MFA",
        selector={"type": "User", "env": "prod"},
        reason="waived",
        expires_at=date(2020, 1, 1),
        created_by="me",
    )
    session.add_all([control, asset, exc])
    session.commit()
    session.close()

    from app.services import evaluator

    evaluator.SessionLocal = SessionLocal
    evaluator.run_evaluation()

    session = SessionLocal()
    res = session.query(result_m.Result).one()
    assert res.status == "FAIL"


def test_framework_filtering():
    client, SessionLocal = setup_client()
    session = SessionLocal()
    control = control_m.Control(
        control_id="C2",
        title="Check encryption",
        category="storage",
        severity="low",
        applies_to={"types": ["Bucket"]},
        logic={"==": [{"var": "config.encrypted"}, True]},
        frameworks=["FedRAMP-Moderate"],
        fix={},
    )
    asset = asset_m.Asset(
        asset_id="A2",
        cloud="aws",
        type="Bucket",
        region="us",
        tags={"env": "prod"},
        config={"encrypted": False},
        evidence={"source": "x", "pointer": "y"},
        ingest_source="test",
    )
    session.add_all([control, asset])
    session.commit()
    session.close()

    from app.services import evaluator

    evaluator.SessionLocal = SessionLocal
    evaluator.run_evaluation()

    resp = client.get(
        "/evaluate/results",
        params={"framework": "FedRAMP-Moderate", "status": "FAIL"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["control_id"] == "C2"
    assert data[0]["status"] == "FAIL"

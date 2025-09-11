import sys
from datetime import datetime
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT / "apps/api"))

from main import app  # type: ignore
from app.dependencies import get_db
from app.models.db import Base
from app.models import results as result_m, assets as asset_m, controls as control_m, runs as run_m


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
    return TestClient(app), TestingSessionLocal


def seed_data(SessionLocal):
    session = SessionLocal()
    run = run_m.EvaluationRun(run_id="run1", status="finished")
    asset1 = asset_m.Asset(
        asset_id="A1",
        cloud="aws",
        type="Bucket",
        region="us-east-1",
        tags={"env": "prod"},
        config={},
        evidence={},
        ingest_source="test",
    )
    asset2 = asset_m.Asset(
        asset_id="A2",
        cloud="aws",
        type="Bucket",
        region="us-west-1",
        tags={"env": "dev"},
        config={},
        evidence={},
        ingest_source="test",
    )
    control1 = control_m.Control(
        control_id="C1",
        title="Encrypt bucket",
        category="Storage",
        severity="LOW",
        applies_to={},
        logic={},
        frameworks=["SOC2"],
        fix={},
    )
    control2 = control_m.Control(
        control_id="C2",
        title="MFA required",
        category="Identity",
        severity="HIGH",
        applies_to={},
        logic={},
        frameworks=["FedRAMP-Moderate"],
        fix={},
    )
    res1 = result_m.Result(
        control_id="C1",
        control_title="Encrypt bucket",
        asset_id="A1",
        status="PASS",
        severity="LOW",
        frameworks=["SOC2"],
        evidence={},
        fix={},
        evaluated_at=datetime(2024, 1, 1),
        run_id="run1",
    )
    res2 = result_m.Result(
        control_id="C2",
        control_title="MFA required",
        asset_id="A2",
        status="FAIL",
        severity="HIGH",
        frameworks=["FedRAMP-Moderate"],
        evidence={},
        fix={},
        evaluated_at=datetime(2024, 1, 2),
        run_id="run1",
    )
    res3 = result_m.Result(
        control_id="C1",
        control_title="Encrypt bucket",
        asset_id="A2",
        status="FAIL",
        severity="LOW",
        frameworks=["SOC2"],
        evidence={},
        fix={},
        evaluated_at=datetime(2024, 1, 3),
        run_id="run1",
    )
    session.add_all([run, asset1, asset2, control1, control2, res1, res2, res3])
    session.commit()
    session.close()


def test_filter_combination():
    client, SessionLocal = setup_client()
    seed_data(SessionLocal)
    resp = client.get(
        "/results",
        params={"status": "FAIL", "severity": "HIGH"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_items"] == 1
    assert data["items"][0]["control_id"] == "C2"


def test_pagination():
    client, SessionLocal = setup_client()
    seed_data(SessionLocal)
    resp = client.get("/results", params={"page": 2, "page_size": 2})
    assert resp.status_code == 200
    data = resp.json()
    assert data["page"] == 2
    assert data["page_size"] == 2
    assert data["total_items"] == 3
    assert data["total_pages"] == 2
    assert len(data["items"]) == 1


def test_csv_export():
    client, SessionLocal = setup_client()
    seed_data(SessionLocal)
    resp = client.get(
        "/results/export.csv", params={"status": "FAIL"}
    )
    assert resp.status_code == 200
    lines = resp.text.strip().split("\n")
    assert lines[0].startswith("run_id,evaluated_at,status")
    assert len(lines) - 1 == 2


def test_framework_filter():
    client, SessionLocal = setup_client()
    seed_data(SessionLocal)
    resp = client.get(
        "/results",
        params={"framework": "FedRAMP-Moderate", "status": "FAIL"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_items"] == 1
    assert data["items"][0]["frameworks"] == ["FedRAMP-Moderate"]

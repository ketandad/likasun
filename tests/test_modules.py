import sys
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
from app.models import controls as control_m, results as result_m, assets as asset_m
from app.services import evaluator


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
    evaluator.SessionLocal = TestingSessionLocal
    return TestClient(app), TestingSessionLocal


def test_contracts_module():
    client, SessionLocal = setup_client()
    session = SessionLocal()
    # controls
    c1 = control_m.Control(
        control_id="GDPR_BREACH_72H",
        title="Contract breach window within 72h",
        category="contract",
        severity="low",
        applies_to={"types": ["contract"]},
        logic={"<=": [{"var": "config.breach_window_hours"}, 72]},
        frameworks=["SOC2"],
        fix={},
    )
    c2 = control_m.Control(
        control_id="DATA_LOCATION_SPECIFIED",
        title="Contract specifies data location",
        category="contract",
        severity="low",
        applies_to={"types": ["contract"]},
        logic={"exists": "config.data_location"},
        frameworks=["SOC2"],
        fix={},
    )
    session.add_all([c1, c2])
    session.commit()
    session.close()

    fixture = Path("tests/fixtures/modules/contracts/sample_contract.txt")
    upload = client.post("/modules/contracts/upload", files={"file": (fixture.name, open(fixture, "rb"), "text/plain")})
    doc_path = upload.json()["doc_path"]
    client.post(
        "/modules/contracts/ingest",
        json={"doc_path": doc_path, "vendor": "V", "product": "P", "region": "us"},
    )
    evaluator.run_evaluation()
    session = SessionLocal()
    results = session.query(result_m.Result).order_by(result_m.Result.control_id).all()
    statuses = {r.control_id: r.status for r in results}
    assert statuses["GDPR_BREACH_72H"] == "FAIL"
    assert statuses["DATA_LOCATION_SPECIFIED"] == "PASS"


def test_access_module():
    client, SessionLocal = setup_client()
    session = SessionLocal()
    controls = [
        control_m.Control(
            control_id="GHOST_ACCOUNT",
            title="No ghost accounts",
            category="access",
            severity="low",
            applies_to={"types": ["useraccount"]},
            logic={
                "!": {
                    "and": [
                        {"==": [{"var": "config.hr_status"}, "left"]},
                        {"==": [{"var": "config.iam_status"}, "active"]},
                    ]
                }
            },
            frameworks=["SOC2"],
            fix={},
        ),
        control_m.Control(
            control_id="ADMIN_NO_MFA",
            title="Admins have MFA",
            category="access",
            severity="low",
            applies_to={"types": ["useraccount"]},
            logic={
                "or": [
                    {"!": {"contains": [{"var": "config.roles"}, "admin"]}},
                    {"==": [{"var": "config.mfa"}, True]},
                ]
            },
            frameworks=["SOC2"],
            fix={},
        ),
        control_m.Control(
            control_id="STALE_ACCOUNT_90D",
            title="Accounts used within 90 days",
            category="access",
            severity="low",
            applies_to={"types": ["useraccount"]},
            logic={"<=": [{"var": "config.last_seen_days"}, 90]},
            frameworks=["SOC2"],
            fix={},
        ),
    ]
    session.add_all(controls)
    session.commit()
    session.close()

    fixdir = Path("tests/fixtures/modules/access")
    files = {
        "hr": ("hr.csv", open(fixdir / "hr.csv", "rb"), "text/csv"),
        "iam": ("iam.csv", open(fixdir / "iam.csv", "rb"), "text/csv"),
    }
    upload = client.post("/modules/access/upload", files=files)
    paths = upload.json()
    client.post("/modules/access/ingest", json=paths)
    evaluator.run_evaluation()
    session = SessionLocal()
    fails = session.query(result_m.Result).filter(result_m.Result.status == "FAIL").count()
    assert fails >= 3


def test_vendors_module():
    client, SessionLocal = setup_client()
    session = SessionLocal()
    controls = [
        control_m.Control(
            control_id="PII_NO_DPA",
            title="PII vendors must have DPA",
            category="vendor",
            severity="low",
            applies_to={"types": ["vendor"]},
            logic={
                "or": [
                    {"!": {"contains": [{"var": "config.data_classes"}, "PII"]}},
                    {"==": [{"var": "config.meta.dpa_present"}, True]},
                ]
            },
            frameworks=["SOC2"],
            fix={},
        ),
        control_m.Control(
            control_id="MISSING_SOC2_OR_ISO",
            title="Vendor must have SOC2 or ISO",
            category="vendor",
            severity="low",
            applies_to={"types": ["vendor"]},
            logic={
                "or": [
                    {"==": [{"var": "config.meta.soc2"}, True]},
                    {"==": [{"var": "config.meta.iso27001"}, True]},
                ]
            },
            frameworks=["SOC2"],
            fix={},
        ),
        control_m.Control(
            control_id="CRITICAL_SCOPE_UNREVIEWED",
            title="Critical vendors reviewed",
            category="vendor",
            severity="low",
            applies_to={"types": ["vendor"]},
            logic={
                "or": [
                    {"==": [{"var": "config.has_critical_scope"}, False]},
                    {"<=": [{"var": "config.meta.last_review_days"}, 365]},
                ]
            },
            frameworks=["SOC2"],
            fix={},
        ),
    ]
    session.add_all(controls)
    session.commit()
    session.close()

    fixture = Path("tests/fixtures/modules/vendors/vendors.csv")
    client.post(
        "/modules/vendors/bulk",
        files={"file": ("vendors.csv", open(fixture, "rb"), "text/csv")},
    )
    evaluator.run_evaluation()
    session = SessionLocal()
    fails = session.query(result_m.Result).filter(result_m.Result.status == "FAIL").count()
    assert fails >= 2


def test_residency_module():
    client, SessionLocal = setup_client()
    session = SessionLocal()
    asset = asset_m.Asset(
        asset_id="data1",
        cloud="saas",
        type="dataflow",
        region="us",
        tags={},
        config={"data_class": "pii"},
        evidence={},
        ingest_source="test",
    )
    session.add(asset)
    session.commit()
    session.close()

    policy_file = Path("tests/fixtures/modules/residency/policy.yaml")
    client.post(
        "/modules/residency/policy",
        files={"file": ("policy.yaml", open(policy_file, "rb"), "text/yaml")},
    )
    client.get("/modules/residency/check")
    session = SessionLocal()
    res = session.query(result_m.Result).one()
    assert res.status == "FAIL"


def test_policy_module():
    client, SessionLocal = setup_client()
    session = SessionLocal()
    controls = [
        control_m.Control(
            control_id="POLICY_MISMATCH_MFA",
            title="Policy requires MFA",
            category="policy",
            severity="low",
            applies_to={"types": ["policy"]},
            logic={
                "or": [
                    {"==": [{"var": "config.policy_requires_mfa"}, False]},
                    {"==": [{"var": "config.actual_mfa"}, True]},
                ]
            },
            frameworks=["SOC2"],
            fix={},
        ),
        control_m.Control(
            control_id="POLICY_MISMATCH_ENCRYPTION",
            title="Encryption matches policy",
            category="policy",
            severity="low",
            applies_to={"types": ["policy"]},
            logic={
                "or": [
                    {"==": [{"var": "config.policy_encryption_at_rest"}, False]},
                    {"==": [{"var": "config.actual_encryption_at_rest"}, True]},
                ]
            },
            frameworks=["SOC2"],
            fix={},
        ),
    ]
    session.add_all(controls)
    session.commit()
    session.close()

    fixture = Path("tests/fixtures/modules/policy/policy.json")
    upload = client.post(
        "/modules/policy/upload",
        files={"file": ("policy.json", open(fixture, "rb"), "application/json")},
    )
    policy_path = upload.json()["policy_path"]
    client.post(
        "/modules/policy/ingest",
        json={
            "policy_path": policy_path,
            "actual": {
                "retention_days": 15,
                "requires_mfa": False,
                "encryption_at_rest": False,
                "min_tls": "1.0",
            },
        },
    )
    evaluator.run_evaluation()
    session = SessionLocal()
    fails = session.query(result_m.Result).filter(result_m.Result.status == "FAIL").count()
    assert fails >= 2

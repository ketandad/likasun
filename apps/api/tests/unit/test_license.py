import base64
import json
import uuid
from datetime import date, datetime, timedelta
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from nacl import signing
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

BASE = Path(__file__).resolve().parents[2]
ROOT = Path(__file__).resolve().parents[4]
sys.path.extend([str(BASE), str(ROOT)])

from main import app  # noqa: E402
from app.core import license as lic  # noqa: E402
from app.core.config import settings  # noqa: E402
from app.core.security import users_db  # noqa: E402
from app.dependencies import get_db  # noqa: E402
from app.models.db import Base  # noqa: E402
from app.models import db as models_db  # noqa: E402
from app.services import evaluator  # noqa: E402

PRIVATE_KEY_B64 = "gpXAdxXlavULojMEhEjRN8gmpXBOcIrtn3rwlKQCCis="
FIXTURES = ROOT / "tests" / "fixtures" / "licenses"


def load_license_file(path: Path) -> None:
    settings.LICENSE_FILE = str(path)
    lic._current_license = None  # type: ignore
    lic.load_license()


def setup_client(path: Path) -> TestClient:
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
    load_license_file(path)
    users_db.clear()
    return TestClient(app)


def test_invalid_signature(tmp_path: Path):
    data = json.loads((FIXTURES / "dev.json").read_text())
    data["org"] = "Tampered"
    tampered = tmp_path / "lic.json"
    tampered.write_text(json.dumps(data))
    with pytest.raises(lic.LicenseError):
        load_license_file(tampered)


def test_expired_license_blocks():
    client = setup_client(FIXTURES / "expired.json")
    r = client.post("/evaluate/run")
    assert r.status_code == 403


def test_feature_flag_enforced():
    client = setup_client(FIXTURES / "missing_feature.json")
    r = client.post("/evaluate/run")
    assert r.status_code == 402


def make_license(**overrides):
    data = {
        "org": "Acme",
        "edition": "enterprise",
        "features": ["evaluate", "compliance"],
        "seats": 5,
        "expiry": (date.today() + timedelta(days=30)).isoformat(),
        "jti": str(uuid.uuid4()),
        "iat": int(datetime.utcnow().timestamp()),
    }
    data.update(overrides)
    payload = data.copy()
    payload_bytes = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    sk = signing.SigningKey(base64.b64decode(PRIVATE_KEY_B64))
    sig = sk.sign(payload_bytes).signature
    data["sig"] = base64.b64encode(sig).decode()
    return data


def test_seat_limit(tmp_path: Path):
    data = make_license(seats=1)
    path = tmp_path / "license.json"
    path.write_text(json.dumps(data))
    client = setup_client(path)
    r1 = client.post("/auth/register", json={"username": "a", "password": "x"})
    assert r1.status_code == 200
    r2 = client.post("/auth/register", json={"username": "b", "password": "x"})
    assert r2.status_code == 403

import base64
import json
import uuid
from datetime import date, datetime, timedelta
from pathlib import Path
import sys

import pytest
from fastapi.testclient import TestClient
from nacl import signing

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT / "apps/api"))

from main import app  # type: ignore
from app.core import license as lic
from app.core.config import settings
from app.core.security import users_db

PRIVATE_KEY_B64 = "gpXAdxXlavULojMEhEjRN8gmpXBOcIrtn3rwlKQCCis="


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


def setup_client(tmp_path, license_data):
    path = tmp_path / "license.rbl"
    Path(path).write_text(json.dumps(license_data))
    settings.LICENSE_FILE = str(path)
    lic._current_license = None  # type: ignore
    lic.load_license()
    users_db.clear()
    return TestClient(app)


def test_invalid_signature(tmp_path):
    data = make_license()
    data["org"] = "Tampered"
    path = tmp_path / "license.rbl"
    path.write_text(json.dumps(data))
    settings.LICENSE_FILE = str(path)
    lic._current_license = None  # type: ignore
    with pytest.raises(lic.LicenseError):
        lic.load_license()


def test_expired_license_blocks(tmp_path):
    data = make_license(expiry=(date.today() - timedelta(days=15)).isoformat())
    client = setup_client(tmp_path, data)
    r = client.post("/evaluate/run")
    assert r.status_code == 403


def test_feature_flag_enforced(tmp_path):
    data = make_license(features=[])
    client = setup_client(tmp_path, data)
    r = client.post("/evaluate/run")
    assert r.status_code == 402


def test_seat_limit(tmp_path):
    data = make_license(features=[], seats=1)
    client = setup_client(tmp_path, data)
    r1 = client.post("/auth/register", json={"username": "a", "password": "x"})
    assert r1.status_code == 200
    r2 = client.post("/auth/register", json={"username": "b", "password": "x"})
    assert r2.status_code == 403

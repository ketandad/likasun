import sys
from pathlib import Path

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT / "apps/api"))

from main import app  # type: ignore
from app.__version__ import __version__


def test_health_returns_version():
    client = TestClient(app)
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"ok": True, "version": __version__}

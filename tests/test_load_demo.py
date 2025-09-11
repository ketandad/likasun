from fastapi.testclient import TestClient
from api.main import app


def test_load_demo():
    client = TestClient(app)
    response = client.post("/assets/load-demo")
    assert response.status_code == 200
    assert "ingested" in response.json()
    resp = client.get('/assets')
    assets = resp.json()
    assert len(assets) >= 10
    assert all((a.get('tags') or {}).get('env') == 'demo' for a in assets)

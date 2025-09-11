from __future__ import annotations

from fastapi.testclient import TestClient

from .test_ingest import create_test_client
from .mocks.aws import MockAWSConnector


def test_live_ingest_aws(monkeypatch):
    client: TestClient = create_test_client()

    def _get_connector(cloud: str):
        assert cloud == "aws"
        return MockAWSConnector()

    monkeypatch.setattr("app.routers.ingest.get_connector", _get_connector)

    resp = client.post("/ingest/live", params={"cloud": "aws"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["ingested"] >= 10
    assert data["errors"] == []

    resp = client.get("/assets")
    assets = resp.json()
    assert len(assets) >= 10
    sample = next(a for a in assets if a["asset_id"] == "bucket1")
    assert sample["evidence"]["source"] == "live:aws:s3"

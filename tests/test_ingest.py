from __future__ import annotations

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


def create_test_client() -> TestClient:
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
    return TestClient(app)


def test_ingest_end_to_end():
    client = create_test_client()
    fixture_dir = Path("tests/fixtures/ingest")
    files = []
    names = [
        "aws_s3_inventory.csv",
        "aws_iam_credential_report.csv",
        "azure_resource_graph.json",
        "gcp_asset_inventory.json",
        "terraform_plan.json",
    ]
    for name in names:
        files.append(("files", (name, open(fixture_dir / name, "rb"), "application/octet-stream")))
    resp = client.post("/ingest/files", files=files)
    assert resp.status_code == 200
    uploads = resp.json()["upload_ids"]

    client.post(
        "/ingest/parse",
        params={
            "cloud": "aws",
            "upload_id": [uploads["aws_s3_inventory.csv"], uploads["aws_iam_credential_report.csv"]],
        },
    )
    client.post(
        "/ingest/parse",
        params={"cloud": "azure", "upload_id": [uploads["azure_resource_graph.json"]]},
    )
    client.post(
        "/ingest/parse",
        params={"cloud": "gcp", "upload_id": [uploads["gcp_asset_inventory.json"]]},
    )
    client.post(
        "/ingest/parse",
        params={"cloud": "iac", "upload_id": [uploads["terraform_plan.json"]]},
    )

    resp = client.get("/assets")
    assert resp.status_code == 200
    assets = resp.json()
    assert len(assets) >= 10
    sample = next(a for a in assets if a["asset_id"] == "bucket-a")
    assert sample["evidence"]["file"].endswith("aws_s3_inventory.csv")

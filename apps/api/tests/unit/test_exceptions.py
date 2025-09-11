from datetime import date

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[4]))

from app.services.evaluator import _exception_matches
from app.models import exceptions as exc_m, assets as asset_m


def test_exception_selector_matches_type_env_cloud():
    exc = exc_m.Exception(
        control_id="C1",
        selector={"type": "User", "env": "dev", "cloud": "aws"},
        reason="r",
        expires_at=date(2099, 1, 1),
        created_by="u",
    )
    asset = asset_m.Asset(
        asset_id="A1",
        cloud="aws",
        type="User",
        region="us",
        tags={"env": "dev"},
        config={},
        evidence={},
        ingest_source="t",
    )
    assert _exception_matches(exc, asset)
    asset2 = asset_m.Asset(
        asset_id="A2",
        cloud="aws",
        type="User",
        region="us",
        tags={"env": "prod"},
        config={},
        evidence={},
        ingest_source="t",
    )
    assert not _exception_matches(exc, asset2)

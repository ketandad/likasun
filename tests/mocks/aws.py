from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict

from app.ingest.connectors.base import Connector
from app.models.assets import Asset


class MockAWSConnector(Connector):
    cloud = "aws"

    def __init__(self) -> None:
        data_path = Path(__file__).with_name("mock_aws.json")
        self.data = json.loads(data_path.read_text())

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def list_assets(self) -> List[Asset]:
        now = self._now()
        assets: List[Asset] = []
        for inst in self.data["ec2"]:
            assets.append(
                Asset(
                    asset_id=inst["InstanceId"],
                    cloud="aws",
                    type="ec2",
                    region=inst["Placement"]["AvailabilityZone"][:-1],
                    tags={},
                    config=inst,
                    evidence={"source": "live:aws:ec2", "timestamp": now},
                    ingest_source="live",
                )
            )
        for bucket in self.data["s3"]:
            assets.append(
                Asset(
                    asset_id=bucket["Name"],
                    cloud="aws",
                    type="s3",
                    region=bucket["Region"],
                    tags={},
                    config=bucket,
                    evidence={"source": "live:aws:s3", "timestamp": now},
                    ingest_source="live",
                )
            )
        for user in self.data["iam_users"]:
            assets.append(
                Asset(
                    asset_id=user["UserName"],
                    cloud="aws",
                    type="iam_user",
                    region="global",
                    tags={},
                    config=user,
                    evidence={"source": "live:aws:iam", "timestamp": now},
                    ingest_source="live",
                )
            )
        for db in self.data["rds"]:
            assets.append(
                Asset(
                    asset_id=db["DBInstanceIdentifier"],
                    cloud="aws",
                    type="rds",
                    region=db["AvailabilityZone"][:-1],
                    tags={},
                    config=db,
                    evidence={"source": "live:aws:rds", "timestamp": now},
                    ingest_source="live",
                )
            )
        for key in self.data["keys"]:
            assets.append(
                Asset(
                    asset_id=key["AccessKeyId"],
                    cloud="aws",
                    type="iam_access_key",
                    region="global",
                    tags={},
                    config=key,
                    evidence={"source": "live:aws:iam", "timestamp": now},
                    ingest_source="live",
                )
            )
        return assets

    def validate_permissions(self) -> Dict[str, bool]:
        return {"mock": True}

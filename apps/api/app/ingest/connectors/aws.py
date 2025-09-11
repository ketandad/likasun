from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import List, Dict

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from .base import Connector
from app.models.assets import Asset


class AWSConnector(Connector):
    """Connector for AWS using boto3."""

    cloud = "aws"

    def __init__(self) -> None:
        self.session = boto3.Session(
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        )

    # Helper for timestamp
    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def list_assets(self) -> List[Asset]:
        assets: List[Asset] = []
        now = self._now()

        try:
            ec2 = self.session.client("ec2")
            resp = ec2.describe_instances()
            for reservation in resp.get("Reservations", []):
                for inst in reservation.get("Instances", []):
                    tags = {t["Key"]: t["Value"] for t in inst.get("Tags", [])}
                    region = inst.get("Placement", {}).get("AvailabilityZone", "")[:-1]
                    assets.append(
                        Asset(
                            asset_id=inst["InstanceId"],
                            cloud="aws",
                            type="ec2",
                            region=region,
                            tags=tags,
                            config=inst,
                            evidence={"source": "live:aws:ec2", "timestamp": now},
                            ingest_source="live",
                        )
                    )
        except Exception:
            pass

        try:
            s3 = self.session.client("s3")
            resp = s3.list_buckets()
            for bucket in resp.get("Buckets", []):
                try:
                    loc = s3.get_bucket_location(Bucket=bucket["Name"]).get("LocationConstraint")
                    region = loc or "us-east-1"
                except Exception:
                    region = ""
                assets.append(
                    Asset(
                        asset_id=bucket["Name"],
                        cloud="aws",
                        type="s3",
                        region=region,
                        tags={},
                        config=bucket,
                        evidence={"source": "live:aws:s3", "timestamp": now},
                        ingest_source="live",
                    )
                )
        except Exception:
            pass

        try:
            iam = self.session.client("iam")
            users = iam.list_users().get("Users", [])
            for user in users:
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
                keys = iam.list_access_keys(UserName=user["UserName"]).get("AccessKeyMetadata", [])
                for key in keys:
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
        except Exception:
            pass

        try:
            rds = self.session.client("rds")
            resp = rds.describe_db_instances()
            for db in resp.get("DBInstances", []):
                region = db.get("AvailabilityZone", "")[:-1]
                assets.append(
                    Asset(
                        asset_id=db["DBInstanceIdentifier"],
                        cloud="aws",
                        type="rds",
                        region=region,
                        tags={},
                        config=db,
                        evidence={"source": "live:aws:rds", "timestamp": now},
                        ingest_source="live",
                    )
                )
        except Exception:
            pass

        return assets

    def validate_permissions(self) -> Dict[str, bool]:
        checks = {
            "ec2:DescribeInstances": False,
            "s3:ListAllMyBuckets": False,
            "iam:ListUsers": False,
            "rds:DescribeDBInstances": False,
        }
        try:
            self.session.client("ec2").describe_instances(MaxResults=1)
            checks["ec2:DescribeInstances"] = True
        except Exception:
            pass
        try:
            self.session.client("s3").list_buckets()
            checks["s3:ListAllMyBuckets"] = True
        except Exception:
            pass
        try:
            self.session.client("iam").list_users()
            checks["iam:ListUsers"] = True
        except Exception:
            pass
        try:
            self.session.client("rds").describe_db_instances()
            checks["rds:DescribeDBInstances"] = True
        except Exception:
            pass
        return checks

from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import List, Dict

from .base import Connector
from app.models.assets import Asset


class GCPConnector(Connector):
    """Connector for GCP using google-cloud libraries."""

    cloud = "gcp"

    def __init__(self) -> None:
        self.project = os.getenv("GCP_PROJECT")

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def list_assets(self) -> List[Asset]:
        assets: List[Asset] = []
        now = self._now()
        try:
            from google.cloud import asset_v1

            client = asset_v1.AssetServiceClient()
            parent = f"projects/{self.project}"
            for asset in client.list_assets(request={"parent": parent}):
                config = asset.to_dict()
                assets.append(
                    Asset(
                        asset_id=asset.name,
                        cloud="gcp",
                        type=asset.asset_type,
                        region=config.get("resource", {}).get("location", ""),
                        tags={},
                        config=config,
                        evidence={"source": "live:gcp:asset", "timestamp": now},
                        ingest_source="live",
                    )
                )
        except Exception:
            pass

        try:
            from google.cloud import compute_v1

            compute = compute_v1.InstancesClient()
            request = compute_v1.AggregatedListInstancesRequest(project=self.project)
            agg = compute.aggregated_list(request=request)
            for zone, resp in agg:
                for inst in resp.instances or []:
                    config = inst.to_dict()
                    region = zone.split("/")[-1]
                    tags = {t: True for t in inst.tags.items} if inst.tags else {}
                    assets.append(
                        Asset(
                            asset_id=str(inst.id or inst.name),
                            cloud="gcp",
                            type="compute_instance",
                            region=region,
                            tags=tags,
                            config=config,
                            evidence={"source": "live:gcp:compute", "timestamp": now},
                            ingest_source="live",
                        )
                    )
        except Exception:
            pass

        try:
            from google.cloud import sql_v1beta4

            sql = sql_v1beta4.SqlInstancesServiceClient()
            resp = sql.list(request={"project": self.project})
            for db in resp.items:
                config = db.to_dict()
                assets.append(
                    Asset(
                        asset_id=db.name,
                        cloud="gcp",
                        type="sql_instance",
                        region=db.region,
                        tags={},
                        config=config,
                        evidence={"source": "live:gcp:sql", "timestamp": now},
                        ingest_source="live",
                    )
                )
        except Exception:
            pass

        return assets

    def validate_permissions(self) -> Dict[str, bool]:
        checks = {
            "asset:listAssets": False,
            "compute:instances:aggregatedList": False,
            "sql:instances:list": False,
        }
        try:
            from google.cloud import asset_v1

            asset_v1.AssetServiceClient().list_assets(
                request={"parent": f"projects/{self.project}", "page_size": 1}
            )
            checks["asset:listAssets"] = True
        except Exception:
            pass
        try:
            from google.cloud import compute_v1

            compute_v1.InstancesClient().aggregated_list(
                request=compute_v1.AggregatedListInstancesRequest(project=self.project)
            )
            checks["compute:instances:aggregatedList"] = True
        except Exception:
            pass
        try:
            from google.cloud import sql_v1beta4

            sql_v1beta4.SqlInstancesServiceClient().list(request={"project": self.project})
            checks["sql:instances:list"] = True
        except Exception:
            pass
        return checks

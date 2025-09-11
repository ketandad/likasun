from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import List, Dict

from .base import Connector
from app.models.assets import Asset


class AzureConnector(Connector):
    """Connector for Azure using Azure SDK."""

    cloud = "azure"

    def __init__(self) -> None:
        from azure.identity import ClientSecretCredential

        self.tenant_id = os.getenv("AZURE_TENANT_ID")
        self.subscription_id = os.getenv("AZURE_SUBSCRIPTION_ID")
        self.credential = ClientSecretCredential(
            tenant_id=self.tenant_id,
            client_id=os.getenv("AZURE_CLIENT_ID"),
            client_secret=os.getenv("AZURE_CLIENT_SECRET"),
        )

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def list_assets(self) -> List[Asset]:
        now = self._now()
        assets: List[Asset] = []
        try:
            from azure.mgmt.resourcegraph import ResourceGraphClient

            client = ResourceGraphClient(self.credential)
            query = "resources | project id, type, location, tags"
            request = {"subscriptions": [self.subscription_id], "query": query}
            result = client.resources(request)
            for item in result.data or []:
                assets.append(
                    Asset(
                        asset_id=item["id"],
                        cloud="azure",
                        type=item["type"],
                        region=item.get("location", ""),
                        tags=item.get("tags", {}),
                        config=item,
                        evidence={"source": "live:azure:resourcegraph", "timestamp": now},
                        ingest_source="live",
                    )
                )
        except Exception:
            pass

        try:
            from azure.mgmt.storage import StorageManagementClient

            storage = StorageManagementClient(self.credential, self.subscription_id)
            for account in storage.storage_accounts.list():
                assets.append(
                    Asset(
                        asset_id=account.id,
                        cloud="azure",
                        type="storage_account",
                        region=account.location,
                        tags=account.tags or {},
                        config=account.as_dict(),
                        evidence={"source": "live:azure:storage", "timestamp": now},
                        ingest_source="live",
                    )
                )
        except Exception:
            pass

        try:
            from azure.graphrbac import GraphRbacManagementClient

            graph = GraphRbacManagementClient(self.credential, self.tenant_id)
            for user in graph.users.list():
                assets.append(
                    Asset(
                        asset_id=user.object_id,
                        cloud="azure",
                        type="aad_user",
                        region="global",
                        tags={},
                        config=user.as_dict(),
                        evidence={"source": "live:azure:ad", "timestamp": now},
                        ingest_source="live",
                    )
                )
        except Exception:
            pass

        return assets

    def validate_permissions(self) -> Dict[str, bool]:
        checks = {
            "resourcegraph:resources": False,
            "storage:storageAccounts:list": False,
            "aad:users:list": False,
        }
        try:
            from azure.mgmt.resourcegraph import ResourceGraphClient

            client = ResourceGraphClient(self.credential)
            client.resources({"subscriptions": [self.subscription_id], "query": "resources | take 1"})
            checks["resourcegraph:resources"] = True
        except Exception:
            pass
        try:
            from azure.mgmt.storage import StorageManagementClient

            storage = StorageManagementClient(self.credential, self.subscription_id)
            list(storage.storage_accounts.list())
            checks["storage:storageAccounts:list"] = True
        except Exception:
            pass
        try:
            from azure.graphrbac import GraphRbacManagementClient

            graph = GraphRbacManagementClient(self.credential, self.tenant_id)
            list(graph.users.list())
            checks["aad:users:list"] = True
        except Exception:
            pass
        return checks

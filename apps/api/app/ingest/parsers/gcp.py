from __future__ import annotations

import json
from pathlib import Path
from typing import Any

_TYPE_MAP = {
    "compute.googleapis.com/Instance": "VM",
    "storage.googleapis.com/Bucket": "StorageBucket",
}


def parse_files(paths: list[Path]) -> list[dict[str, Any]]:
    assets: list[dict[str, Any]] = []
    for path in paths:
        data = json.loads(path.read_text())
        records = data.get("assets", [])
        for idx, item in enumerate(records, start=1):
            resource = item.get("resource", {})
            location = resource.get("location", "")
            tags = resource.get("data", {}).get("labels", {})
            assets.append(
                {
                    "asset_id": item.get("name", ""),
                    "cloud": "gcp",
                    "type": _TYPE_MAP.get(item.get("assetType", ""), item.get("assetType", "")),
                    "region": location,
                    "tags": tags,
                    "config": item,
                    "evidence": {"file": str(path), "record": idx},
                    "ingest_source": "gcp_asset_inventory",
                }
            )
    return assets

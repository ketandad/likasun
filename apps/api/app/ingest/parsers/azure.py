from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

_TYPE_MAP = {
    "Microsoft.Compute/virtualMachines": "VM",
    "Microsoft.Storage/storageAccounts": "StorageBucket",
}


def parse_files(paths: list[Path]) -> list[dict[str, Any]]:
    assets: list[dict[str, Any]] = []
    for path in paths:
        if path.suffix == ".json":
            data = json.loads(path.read_text())
            records = data.get("data")
            if records is None and isinstance(data, list):
                records = data
            for idx, item in enumerate(records or [], start=1):
                assets.append(
                    {
                        "asset_id": item.get("id", ""),
                        "cloud": "azure",
                        "type": _TYPE_MAP.get(item.get("type", ""), item.get("type", "")),
                        "region": item.get("location", ""),
                        "tags": item.get("tags", {}),
                        "config": item,
                        "evidence": {"file": str(path), "record": idx},
                        "ingest_source": "azure_graph",
                    }
                )
        elif path.suffix == ".csv":
            with path.open(newline="") as f:
                reader = csv.DictReader(f)
                for idx, row in enumerate(reader, start=2):
                    assets.append(
                        {
                            "asset_id": row.get("id", ""),
                            "cloud": "azure",
                            "type": _TYPE_MAP.get(row.get("type", ""), row.get("type", "")),
                            "region": row.get("location", ""),
                            "tags": json.loads(row.get("tags", "{}")),
                            "config": row,
                            "evidence": {"file": str(path), "record": idx},
                            "ingest_source": "azure_graph",
                        }
                    )
    return assets

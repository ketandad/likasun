from __future__ import annotations

import json
from pathlib import Path
from typing import Any

_TYPE_MAP = {
    "aws_s3_bucket": "StorageBucket",
    "google_compute_instance": "VM",
}


def parse_files(paths: list[Path]) -> list[dict[str, Any]]:
    assets: list[dict[str, Any]] = []
    for path in paths:
        data = json.loads(path.read_text())
        root = data.get("planned_values", {}).get("root_module", {})
        resources = root.get("resources", [])
        for idx, res in enumerate(resources, start=1):
            values = res.get("values", {})
            asset_id = (
                values.get("id")
                or values.get("name")
                or values.get("bucket")
                or res.get("address")
            )
            region = values.get("region") or values.get("zone") or ""
            assets.append(
                {
                    "asset_id": asset_id,
                    "cloud": "iac",
                    "type": _TYPE_MAP.get(res.get("type", ""), res.get("type", "")),
                    "region": region,
                    "tags": values.get("tags", {}),
                    "config": res,
                    "evidence": {"file": str(path), "record": idx},
                    "ingest_source": "terraform_plan",
                }
            )
    return assets

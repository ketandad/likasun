from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


def _parse_s3_inventory(path: Path) -> list[dict[str, Any]]:
    assets: list[dict[str, Any]] = []
    with path.open(newline="") as f:
        reader = csv.DictReader(f)
        for idx, row in enumerate(reader, start=2):  # header is line 1
            tags = {k[4:]: v for k, v in row.items() if k.startswith("Tag_") and v}
            assets.append(
                {
                    "asset_id": row.get("Bucket", ""),
                    "cloud": "aws",
                    "type": "StorageBucket",
                    "region": row.get("Region", ""),
                    "tags": tags,
                    "config": row,
                    "evidence": {"file": str(path), "record": idx},
                    "ingest_source": "aws_export",
                }
            )
    return assets


def _parse_iam_credential_report(path: Path) -> list[dict[str, Any]]:
    assets: list[dict[str, Any]] = []
    with path.open(newline="") as f:
        reader = csv.DictReader(f)
        for idx, row in enumerate(reader, start=2):
            assets.append(
                {
                    "asset_id": row.get("arn", ""),
                    "cloud": "aws",
                    "type": "User",
                    "region": "",
                    "tags": {},
                    "config": row,
                    "evidence": {"file": str(path), "record": idx},
                    "ingest_source": "aws_export",
                }
            )
    return assets


_PARSERS = {
    "aws_s3_inventory.csv": _parse_s3_inventory,
    "aws_iam_credential_report.csv": _parse_iam_credential_report,
}


def parse_files(paths: list[Path]) -> list[dict[str, Any]]:
    assets: list[dict[str, Any]] = []
    for path in paths:
        parser = _PARSERS.get(path.name)
        if parser:
            assets.extend(parser(path))
        elif path.suffix == ".json":
            try:
                data = json.loads(path.read_text())
            except json.JSONDecodeError:
                continue
            assets.append(
                {
                    "asset_id": path.stem,
                    "cloud": "aws",
                    "type": "Config",
                    "region": "",
                    "tags": {},
                    "config": data,
                    "evidence": {"file": str(path), "record": 1},
                    "ingest_source": "aws_export",
                }
            )
    return assets

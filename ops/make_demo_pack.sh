#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SRC="$ROOT/tests/fixtures/ingest"
OUT="$ROOT/tmp"
mkdir -p "$OUT"

PKG="$OUT/demo_ingest_pack.tar.gz"
rm -f "$PKG"

# pack only small fixture files
tar -czf "$PKG" -C "$SRC" \
  aws_s3_inventory.csv \
  aws_iam_credential_report.csv \
  azure_resource_graph.json \
  gcp_asset_inventory.json \
  terraform_plan.json

echo "Built $PKG"

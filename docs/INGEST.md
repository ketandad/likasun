# Ingestion

RayBeam supports offline exports and live connectors.

## Cloud Exports

1. Generate inventory exports from your cloud provider.
   - **AWS**: Use `aws configservice select-resource-config` and `aws iam get-account-authorization-details`.
   - **Azure**: Export resources with `az graph query` and policy assignments with `az policy state trigger-scan`.
   - **GCP**: Use `gcloud asset search-all-resources` and `gcloud asset search-all-iam-policies`.
2. Upload the resulting JSON files on the `/ingest` page or via `POST /ingest/files`.

## Okta and HR CSV

Upload CSV exports for identity and HR systems. The parser maps columns like `email`, `department`, and `status`.

## Terraform

Provide a Terraform state file (`terraform.tfstate`). The parser extracts providers, resources, and outputs.

## Live Connectors

For continuous sync, call `GET /ingest/live/permissions` to view required IAM permissions, then `POST /ingest/live` with credentials. The API fetches resources directly.

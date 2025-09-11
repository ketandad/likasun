# Compliance API

The compliance router provides reporting for multiple security frameworks.

## Endpoints

### `GET /compliance/summary`
Return aggregated requirement status for a given framework.

**Query Parameters**
- `framework` (required): one of `PCI-DSS`, `GDPR`, `DPDP`, `ISO27001`, `NIST-800-53`, `HIPAA`, `FedRAMP-Low`, `FedRAMP-Moderate`, `FedRAMP-High`, `SOC2`, `CIS`, `CCPA`.

### `GET /compliance/evidence-pack`
Download a PDF evidence pack for the framework. Includes cover page, executive summary, coverage matrix, failed requirements, and exceptions.

### `GET /compliance/export.csv`
Stream a CSV export of requirement statuses for the framework.

Both export endpoints require the same `framework` query parameter.

## Notes
- Results are computed from the latest evaluation run.
- Summaries are cached per framework and run for repeat queries.

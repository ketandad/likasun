# RayBeam — On-Prem Compliance & Risk Platform

RayBeam helps organizations evaluate cloud infrastructure, generate compliance evidence, and manage risk entirely on-premise.

## Features

- Offline and live ingestion for AWS, Azure, GCP, and Terraform
- Template-driven evaluation engine with JsonLogic
- Compliance reporting and evidence pack export
- Exception and licensing enforcement
- Audit logs, metrics, and manual test playbooks

## Supported Frameworks

RayBeam ships with mappings for:

- PCI
- GDPR
- DPDP
- ISO 27001
- NIST
- HIPAA
- FedRAMP Low/Moderate/High
- SOC2
- CIS
- CCPA

## Quick Start

```bash
docker compose -f ops/docker-compose.yml up
```

### Credentials

The first admin user is seeded from the `RB_ADMIN_EMAIL` and `RB_ADMIN_PASSWORD` environment variables when the API starts.

### Demo Data

Generate sample assets and results for exploration:

```bash
make demo-pack
```

## Next Steps

- [Admin Guide](ADMIN.md)
- [Ingestion](INGEST.md)
- [Security Model](SECURITY.md)
- [Rule Templates](RULES.md)
- [Compliance Reporting](COMPLIANCE.md)
- [Observability](OBSERVABILITY.md)
- [Audit Logs](AUDIT.md)
- [Manual Test Playbook](MANUAL_TEST.md)
- [Roadmap](ROADMAP.md)

# Admin Guide

## Installation and Upgrades

### Docker Compose

```bash
docker compose -f ops/docker-compose.yml up -d
docker compose -f ops/docker-compose.yml pull  # upgrade
```

### Kubernetes

Use the Helm chart under `ops/helm/`:

```bash
helm upgrade --install raybeam ops/helm
```

## Database Migrations

Apply migrations after upgrading the API:

```bash
cd apps/api
alembic upgrade head
```

## Licensing

Upload license files at `/settings/license`. The API validates the Ed25519 signature and enforces seat and feature limits.

## Rule-Pack Updates

Rule packs are signed tarballs. Upload via `/settings/rulepacks` and rollback from the same screen if needed.

## Backups

Back up both the Postgres database and the `/data` volume used by the API and web containers.

## Egress Control

Outbound requests are restricted to the allowlist defined in configuration. Denied requests return HTTP 403.

## Security Patches

Dependabot tracks vulnerable dependencies. Regularly review SBOM scan results and apply updates.

# Security

## Threat Model

RayBeam runs entirely on-premise. Users authenticate via the web UI or API; actions are logged to the audit table. Evaluation results and evidence never leave the environment unless exported by an admin.

## Container Hardening

Images are built from minimal base layers. Containers run as non-root and drop Linux capabilities. Only the `api` container requires outbound network access for live ingestion.

## Network Policy

Deploy behind a firewall. Expose only the web and API services. Configure outbound allowlists to restrict external egress.

## Dependency Scanning

SBOMs are produced for each release and scanned for known vulnerabilities. Dependabot updates packages automatically and alerts on security advisories.

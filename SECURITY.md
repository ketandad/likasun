# Security Hardening

This project is configured to run with a defense-in-depth posture suitable for on-prem deployments.

## Containers

- Non-root users (api:10001, web:10002)
- Read-only root filesystems; only `/data` for the API and `/tmp` tmpfs are writable
- `cap_drop: [ALL]` and `no-new-privileges`
- `ulimit nofile` set to 8192 or higher

## Egress Control

Outbound HTTP connections are blocked by default. To allow specific hosts, set the `EGRESS_ALLOWLIST` environment variable to a comma-separated list of domains. Any attempted request to hosts not on this list will raise an `Egress blocked` error.

## Web Security Headers

The web frontend sends strict security headers, including CSP, X-Frame-Options, Referrer-Policy, Permissions-Policy, and X-Content-Type-Options.

## Supply Chain

CI builds deterministic images, generates an SBOM with Syft, and scans for vulnerabilities with Grype. The SBOM is uploaded as a workflow artifact.

## Kubernetes

Example manifests under `ops/k8s` run the API with `runAsNonRoot`, `readOnlyRootFilesystem`, dropped capabilities, and a deny-all egress `NetworkPolicy`.

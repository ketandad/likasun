# AGENTS

## Prompt 10 — Exceptions Workflow

- Implement `exceptions` table with: id, control_id, selector JSON, reason, expires_at, created_by, created_at
- Load all active exceptions at start of evaluation run
- Matching rules:
  - selector may match by asset_id, type, env (from tags.env), or cloud
  - if match → set status="WAIVED", keep original in result.meta.prev_status
- Endpoints:
  - POST /exceptions (admin only)
  - GET /exceptions (list, filter active)
  - DELETE /exceptions/{id}
- Enforce validation: expires_at ≥ today, control_id exists, selector non-empty, reject duplicates
- UI: add /exceptions page with list + add/delete form
- Tests:
  - exception applies correctly to FAIL → WAIVED
  - expired exceptions ignored
  - meta.prev_status preserved

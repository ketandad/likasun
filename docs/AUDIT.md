# Audit Logs

The API writes to the `audit_logs` table for key actions:

- `LOGIN`
- `INGEST_UPLOAD`
- `INGEST_PARSE`
- `INGEST_LIVE`
- `EVALUATE_RUN`
- `EXCEPTION_CREATE`
- `EXCEPTION_DELETE`
- `RULEPACK_UPLOAD`
- `RULEPACK_ROLLBACK`
- `LICENSE_UPLOAD`
- `COMPLIANCE_EXPORT`

Each row records:

| column   | description |
|----------|-------------|
| `id`     | UUID primary key |
| `ts`     | timestamp of action |
| `actor`  | user email/id or null for system |
| `action` | action string |
| `resource` | related resource id |
| `details` | JSON details |

Indexes on `ts` and `action` allow efficient time and action queries.

### Example export

```sql
COPY (
  SELECT * FROM audit_logs WHERE ts > NOW() - INTERVAL '30 days'
) TO STDOUT WITH CSV
```

Rotate or purge audit rows according to compliance requirements.

# Audit Logs

The API writes to the `audit_logs` table for key actions such as logins, ingestion, evaluations, exceptions, rule-pack updates, licenses, and compliance exports.

## Schema

| column   | description                         |
|----------|-------------------------------------|
| `id`     | UUID primary key                     |
| `ts`     | timestamp of action                  |
| `actor`  | user email/id or null for system     |
| `action` | action string                        |
| `resource` | related resource id               |
| `details` | JSON details                       |

Indexes on `ts` and `action` allow efficient time and action queries.

## Retention

Rotate or purge audit rows according to your compliance requirements. The API does not delete logs automatically.

## Export

```sql
COPY (
  SELECT * FROM audit_logs WHERE ts > NOW() - INTERVAL '30 days'
) TO STDOUT WITH CSV
```

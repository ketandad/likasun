# Rule Templates

Controls are defined in YAML files and evaluated with a JsonLogic subset.

## Template Schema

```yaml
id: aws_s3_public
applies_to:
  types: [aws.s3]
  selector: account_id
severity: HIGH
logic:
  and:
    - ==: [{ var: public }, true]
    - exists: owner
mappings:
  - framework: PCI
    control: '1.2.3'
```

Fields:

- `id` – unique control identifier
- `applies_to` – asset types and optional selector
- `severity` – LOW, MEDIUM, or HIGH
- `logic` – JsonLogic expression
- `mappings` – list of framework/control pairs

## JsonLogic Operators

Supported operators:

`==`, `!=`, `>`, `>=`, `<`, `<=`, `in`, `and`, `or`, `!`, `exists(var)`, `regex(var, pattern)`, `contains(array, value)`

## Example Expansion

During evaluation the template above expands per asset. For an S3 bucket:

```json
{
  "public": true,
  "owner": "123456789"
}
```

The `logic` expression resolves to `true` and the result is `FAIL` unless an exception matches.

## Framework Mapping

Rule packs include matrices relating controls to frameworks such as PCI, GDPR, ISO 27001, NIST, HIPAA, FedRAMP, SOC2, CIS, CCPA, and DPDP.

## Adding Controls

1. Create a YAML file under `packages/rules/`.
2. Define the schema fields and mappings.
3. Run `make lint` to validate syntax.
4. Update the rule pack version and distribute the signed tarball.

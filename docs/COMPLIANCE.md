# Compliance Reporting

Each control is mapped to one or more compliance frameworks. Evaluation results are grouped by framework and control for dashboards and exports.

## Framework Mapping

Mappings reside in the rule templates. During evaluation, results inherit the `framework` and `control` fields which power `/compliance/summary` queries.

## Evidence Packs

Generate a PDF or CSV evidence pack per framework:

```bash
curl -o evidence.pdf http://localhost:8000/compliance/evidence-pack?framework=PCI
curl -o export.csv http://localhost:8000/compliance/export.csv?framework=PCI
```

Evidence packs list failing controls, associated assets, and references to supporting evidence.

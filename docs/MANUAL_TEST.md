# Manual Testing

1. Ingest demo data using the existing ingest endpoints (see fixtures in
   `tests/fixtures/ingest`).
2. POST `/evaluate/run` to execute an evaluation.
3. Confirm `/evaluate/runs` lists the new run with result counts.
4. GET `/evaluate/results?framework=FedRAMP-Moderate&status=FAIL` and verify
   that failing results for the framework are returned.

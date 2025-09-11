# Testing

## Unit and Integration Tests

```bash
cd apps/api
pytest
```

## End-to-End Tests

Playwright tests live in `apps/web/tests`.

```bash
cd apps/web
npm run test
```

Locally, browsers may be missing. Install them with:

```bash
npx playwright install --with-deps
```

## Makefile Targets

`make test` runs API and, if possible, web tests.
`make test:ci` runs the quieter variants for CI.
`make format` fixes formatting for Python and TypeScript files.

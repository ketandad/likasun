# Raybeam Monorepo

Monorepo template containing the API, web app, shared packages, and operational tooling for the Raybeam project.

## Repository structure

```text
raybeam/
├── apps/
│   ├── api/
│   │   └── main.py
│   └── web/
├── packages/
│   ├── rules/
│   ├── schemas/
│   └── shared/
├── ops/
│   ├── api.Dockerfile
│   ├── web.Dockerfile
│   ├── docker-compose.yml
│   ├── ci.yml
│   └── helm/
│       └── Chart.yaml
├── tests/
├── .editorconfig
├── eslint.config.js
├── .gitignore
├── .prettierignore
├── .prettierrc
├── LICENSE
├── Makefile
├── package.json
├── pyproject.toml
└── README.md
```

## Development

1. Ensure Docker is installed:
   ```sh
   docker --version
   ```
2. Format and lint code:
   ```sh
   make fmt
   make lint
   ```
3. Additional commands:
   ```sh
   make test
   make build
   make compose-up
   make compose-down
   ```

This project uses **Conventional Commits** for commit messages.

## License

Distributed under the Apache 2.0 License. See `LICENSE` for more information.

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

## Database

The API uses PostgreSQL by default. Create an `.env` in `apps/api/` (already
included) to configure the connection string:

```env
DATABASE_URL=postgresql+psycopg2://raybeam:raybeam@localhost:5432/raybeam
```

Start a local Postgres instance and run migrations:

```sh
docker compose -f ops/docker-compose.yml up -d db
cd apps/api
alembic upgrade head
```

For a lightweight SQLite database during development, override the URL:

```sh
export DATABASE_URL=sqlite:///./local.db
cd apps/api
alembic upgrade head
```

## License

Distributed under the Apache 2.0 License. See `LICENSE` for more information.

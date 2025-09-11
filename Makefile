.PHONY: test test:ci format build compose-up compose-down migrate migrate-rev downgrade codespace-demo

test:
	cd apps/api && pytest
	cd apps/web && npm run -s test || echo "Web tests skipped locally"

test:ci:
	cd apps/api && pytest -q
	cd apps/web && npm run -s test:ci

format:
	ruff check . --fix
	npm run format

build:
	@echo "no build step defined"

compose-up: ; docker compose -f ops/docker-compose.yml up -d

compose-down: ; docker compose -f ops/docker-compose.yml down

API_DIR=apps/api

migrate: ; cd $(API_DIR) && alembic upgrade head

migrate-rev: ; cd $(API_DIR) && alembic revision --autogenerate -m "$(m)"

downgrade: ; cd $(API_DIR) && alembic downgrade -1

demo-pack:
        ./ops/make_demo_pack.sh
        @echo "Use the pack at tmp/demo_ingest_pack.tar.gz"

codespace-demo:
	bash scripts/start_demo.sh

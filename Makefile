.PHONY: fmt lint test build compose-up compose-down migrate migrate-rev downgrade

fmt:
	black .
	prettier . --write --ignore-unknown

lint:
	ruff check .
	eslint . --ext .js,.jsx,.ts,.tsx || true
	prettier . --check --ignore-unknown

test:
	@echo "no tests yet"

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

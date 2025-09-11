.PHONY: fmt lint test build compose-up compose-down

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

compose-up:
	docker compose -f ops/docker-compose.yml up -d

compose-down:
	docker compose -f ops/docker-compose.yml down

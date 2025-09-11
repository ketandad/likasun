#!/bin/bash
set -e

# Install poetry if not present
if ! command -v poetry &> /dev/null; then
    curl -sSL https://install.python-poetry.org | python3 -
fi

# Install API dependencies
cd apps/api
poetry env use python3.11
poetry install

# Run tests
poetry run pytest -v

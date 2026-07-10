# MTGSim development commands

default:
    @just --list

# Start the API server (serves backend + frontend)
serve:
    uv run mtgsim-api

# Start with debug logging
serve-debug:
    uv run mtgsim-api --debug --reload

# Run tests
test *args:
    uv run pytest {{args}}

# Run tests with coverage
test-cov:
    uv run pytest --cov=src tests/

# Lint source and tests
lint:
    uv run ruff check src tests

# Format source and tests
fmt:
    uv run ruff format src tests

# Auto-fix lint issues
fix:
    uv run ruff check --fix src tests

# Lint + format
check: lint fmt

# Sync dependencies
sync:
    uv sync

# Sync MTGJSON reference database
db-sync:
    uv run mtgsim db sync

# Force re-download and sync MTGJSON data
db-sync-force:
    uv run mtgsim db sync --force

# Start the full stack (API server + deck viewer frontend)
dev:
    #!/usr/bin/env bash
    trap 'kill 0' EXIT
    uv run mtgsim-api &
    cd frontend && npm run dev &
    wait

# Start the deck viewer frontend (dev server)
dev-viewer:
    cd frontend && npm run dev

# Start the flashcards frontend (dev server)
dev-flashcards:
    cd frontend && npm run dev:flashcards

# Start Storybook for the UI component library
storybook:
    cd frontend && npm run storybook

# Build the deck viewer frontend
build-viewer:
    cd frontend && npm run build

# Build the flashcards frontend
build-flashcards:
    cd frontend && npm run build:flashcards

# Build Storybook static site
build-storybook:
    cd frontend && npm run build-storybook

# Typecheck all frontend packages
typecheck:
    cd frontend && npm run typecheck

# Lint frontend code
lint-frontend:
    cd frontend && npm run lint

# Install frontend dependencies
install-frontend:
    cd frontend && npm install

# Show CLI help
help:
    uv run mtgsim --help

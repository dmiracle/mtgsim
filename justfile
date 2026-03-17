# MTGSim development commands

# Start the API server (serves backend + frontend)
serve:
    uv run mtgsim-api

# Start with debug logging
serve-debug:
    uv run mtgsim-api --debug

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

# Show CLI help
help:
    uv run mtgsim --help

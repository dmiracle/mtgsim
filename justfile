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

# --- launchd services (API on :8001, mobile PWA build on :5175) ---

launch_agents := env_var('HOME') / "Library/LaunchAgents"
services := "com.mtgsim.api com.mtgsim.mobile"

# Build the mobile app and install + start both launchd services
services-install: mobile-build
    mkdir -p {{launch_agents}} ~/Library/Logs/mtgsim
    for s in {{services}}; do \
        launchctl bootout gui/$(id -u)/$s 2>/dev/null || true; \
        cp deploy/launchd/$s.plist {{launch_agents}}/; \
        launchctl bootstrap gui/$(id -u) {{launch_agents}}/$s.plist; \
    done

# Stop and remove both launchd services
services-uninstall:
    for s in {{services}}; do \
        launchctl bootout gui/$(id -u)/$s 2>/dev/null || true; \
        rm -f {{launch_agents}}/$s.plist; \
    done

# Restart both services (e.g. after backend changes)
services-restart:
    for s in {{services}}; do launchctl kickstart -k gui/$(id -u)/$s; done

# Show whether each service is running
services-status:
    for s in {{services}}; do launchctl print gui/$(id -u)/$s | grep -E "^\S|state =|pid =" | head -3; done

# Follow both service logs
services-logs:
    tail -f ~/Library/Logs/mtgsim/api.log ~/Library/Logs/mtgsim/mobile.log

# Build the mobile PWA for production
mobile-build:
    cd mobile && npm install && npm run build

# Rebuild the mobile app and restart its service (after frontend changes)
mobile-deploy: mobile-build
    launchctl kickstart -k gui/$(id -u)/com.mtgsim.mobile

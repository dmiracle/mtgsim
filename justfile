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

# --- launchd service: the API on 127.0.0.1:18001 (also serves the mobile PWA build), ---
# --- published over HTTPS on the tailnet only via tailscale serve                     ---

launch_agents := env_var('HOME') / "Library/LaunchAgents"
service := "com.mtgsim.api"
service_port := "18001"
tailscale := "/Applications/Tailscale.app/Contents/MacOS/Tailscale"

# Build the mobile app and install + start the launchd service
services-install: mobile-build
    mkdir -p {{launch_agents}} ~/Library/Logs/mtgsim
    launchctl bootout gui/$(id -u)/{{service}} 2>/dev/null || true
    while launchctl print gui/$(id -u)/{{service}} >/dev/null 2>&1; do sleep 0.2; done
    cp deploy/launchd/{{service}}.plist {{launch_agents}}/
    launchctl bootstrap gui/$(id -u) {{launch_agents}}/{{service}}.plist
    {{tailscale}} serve --bg --https=443 http://127.0.0.1:{{service_port}}

# Stop and remove the launchd service and its tailscale serve route
services-uninstall:
    {{tailscale}} serve --https=443 off || true
    launchctl bootout gui/$(id -u)/{{service}} 2>/dev/null || true
    rm -f {{launch_agents}}/{{service}}.plist

# Restart the API (after backend changes)
services-restart:
    launchctl kickstart -k gui/$(id -u)/{{service}}

# Show whether the service is running
services-status:
    launchctl print gui/$(id -u)/{{service}} | grep -E "^\S|state =|pid =" | head -3

# Follow the service log
services-logs:
    tail -f ~/Library/Logs/mtgsim/api.log

# Build the mobile PWA; the API serves mobile/dist, so a build is live immediately
mobile-build:
    cd mobile && npm ci && npm run build

# Rebuild the mobile app (alias kept for muscle memory)
mobile-deploy: mobile-build

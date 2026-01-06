# Repository Guidelines

## Project Structure & Module Organization
- `src/mtgsim/` holds the Python package: Typer CLI in `cli/`, domain + SQLModel models in `db/`, MTGJSON sync in `sync/mtgjson.py`, ASCII rendering in `render/`, extraction pipelines in `extract/`, and the FastAPI backend in `api/` (routers/services/data/models mirror `docs/architecture.md`).
- `resources/` contains MTGJSON SQLite/JSON snapshots; runtime copies live at `~/.mtgsim/reference/mtgjson/`.
- `web/` is the static viewer served at `/web`; `webapp/` hosts the deck viewer assets and index generators.
- `tests/` covers CLI and API behavior (API cases in `tests/api/`); keep new tests close to their code.
- `docs/architecture.md` documents backend layers—refresh it when endpoints or data flows change.

## Build, Test, and Development Commands
- `uv sync` — install dependencies (Python 3.14+) into the local environment.
- `uv run mtgsim --help` — list CLI commands; `uv run mtgsim db sync` refreshes MTGJSON reference DBs in `~/.mtgsim/reference/mtgjson/`.
- `uv run mtgsim-api` — start the FastAPI server with reload; serves `/api/*` plus static `web/` and `webapp/` assets.
- `uv run pytest` — run the suite; `uv run pytest tests/api -q` for API-only checks.
- `uv run ruff check src tests` and `uv run ruff format src tests` — lint and format before sending changes.

## Coding Style & Naming Conventions
- Python throughout; 4-space indents, max line length 120, double quotes preferred (ruff config).
- Type hints everywhere; favor SQLModel models in `db/` and Pydantic models in `api/models/` for request/response shapes.
- Snake_case for functions/variables, PascalCase for classes; Typer commands stay short and imperative.
- Avoid module-level side effects beyond constants; keep I/O behind CLI commands, services, or FastAPI routers.

## Testing Guidelines
- Tests use pytest; name files `test_*.py` and share fixtures in `tests/api/conftest.py` when useful.
- API tests expect reference SQLite DBs—run `mtgsim db sync` first or point to a populated `~/.mtgsim/reference/mtgjson/`.
- Add focused tests for new routers, services, or CLI flows; prefer deterministic data slices over long-running syncs.

## Commit & Pull Request Guidelines
- Write imperative commit subjects (`Add deck price filter`); conventional prefixes (`feat:`, `fix:`) are welcome but optional.
- Keep commits scoped to one concern and include related tests/formatting updates.
- PRs should summarize scope, link issues, list commands run, and call out API/CLI or schema changes; attach screenshots or sample outputs for UI or rendering tweaks.
- Avoid committing generated caches (`__pycache__`, local database dumps, large resource zips) unless explicitly needed.

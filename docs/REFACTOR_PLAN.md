# MTGSim Refactor Notes

## Current Functionality & Data Flow
- CLI (`src/mtgsim/cli`): Typer commands for card rendering/extraction, reference-data sync (`sync/mtgjson.py`), and a personal collection database (`db/models.py`, `CardRepository`). Extraction pipelines include mock and OpenAI vision (`extract/pipelines.py`).
- Reference data: `mtgsim db sync` downloads MTGJSON SQLite/JSON into `~/.mtgsim/reference/mtgjson/` and reshapes DeckList/AllDeckFiles into `AllDecks.sqlite` plus AllSetFiles into `AllSets.sqlite`.
- API (`src/mtgsim/api`): FastAPI routers → services → data layer. `api/data/*.py` uses raw `sqlite3` against reference DBs; services map dicts to Pydantic models (`api/models/*`). Static assets under `web/` and `webapp/` are intended to be mounted.
- Tests (`tests/api`): cover FastAPI routes and boot-time behavior; fixtures pre-init the reference DB connections.

## Pain Points / Duplication
- Repeated SQL fragments and price lookups across `api/data/cards.py`, `api/data/sets.py`, `api/data/decks.py` (tcgplayer-only filters, pagination math, color parsing).
- Manual dict→Pydantic mapping duplicated in services (`card_service`, `deck_service`, `set_service`) with near-identical structures.
- Path resolution to resources/reference data duplicated (`sync/mtgjson.py`, `api/data/keywords.py`, `api/data/database.py`), and `api/main.py` mounts use string paths that will raise on import (`"web".exists()`).
- Mixed DB access patterns: SQLModel for the personal collection vs raw sqlite for reference data; no shared repository abstractions or DI for FastAPI.
- Stats and formats endpoints are stubbed; UI cannot reflect real reference DB contents.
- Typer commands in `card_commands.py` use `@typer.Typer().command()` instead of the declared `card_app`, making registration brittle.

## Refactor Plan
1) **Centralize configuration/paths**: add `mtgsim/config.py` (or `settings.py`) for project root, resources dir, reference dir, user DB path. Replace ad-hoc `Path.home() / ".mtgsim"` usage across sync/data/CLI.
2) **Unify reference DB access**: introduce a `mtgsim/reference` module with a `ReferenceDb` wrapper that opens read-only connections to AllPrintings/AllPrices/AllDecks/AllSets and provides helpers for JSON decoding, pagination, and price joins. Replace copy/paste SQL builders in `api/data/*.py` with shared utilities.
3) **Normalize DTOs/mappers**: centralize row→model mappers for card/set/deck summaries in one module (e.g., `api/models/shared.py`) to remove manual dict construction in services.
4) **Price utilities**: add `api/data/pricing.py` for tcgplayer and multi-provider averages, deck total calculators, and reuse in cards/sets/decks instead of inline queries.
5) **Fix static mounting & CLI wiring**: switch to `Path("web")`/`Path("webapp")` existence checks in `api/main.py`; register Typer commands via a single `app = Typer()` and `@app.command` (or re-use `card_app`) for consistent help/dispatch.
6) **Implement real stats/format data**: compute totals, histograms, and recent sets from the reference DBs in `stats_service`; drive formats/keywords endpoints from actual data rather than placeholders.
7) **Sync pipeline cleanup**: extract download/decompress helpers with checksum/mtime guards; stream deck/set imports to avoid full-table deletes when unnecessary; switch `print` to a shared logger.

## Suggested Sequence
- Land config + reference repository layer (steps 1–4), then patch static mounts and Typer wiring (step 5). Follow with real stats/format implementations (step 6) and adjust sync ergonomics (step 7). Add unit tests around new repositories/pricing plus a quick pass over `tests/api` to verify behavior. 

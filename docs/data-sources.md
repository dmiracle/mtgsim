# Data Sources & Sync Pipelines

This document describes every data source, how it's fetched, and how it's ingested into the database.

## Database

All data lives in a single SQLite file: `~/.mtgsim/mtgsim.sqlite` (override with `MTGSIM_HOME` env var).

Flashcard/SRS state lives in a separate file: `~/.srs/srs.db` (override with `SRS_DB_PATH` env var).

## Quick Reference

| Source | CLI Command | Frequency | Tables |
|--------|-------------|-----------|--------|
| MTGJSON Cards/Sets | `mtgsim db sync --cards` | Per set release | mj_set, mj_card, mj_card_identifier, mj_card_legality |
| MTGJSON Prices | `mtgsim db sync --prices` | Daily | mj_card_price |
| MTGJSON Decks | `mtgsim db sync --decks` | Per set release | mj_deck, mj_deck_card |
| MTGJSON Keywords | `mtgsim db sync --keywords` | Per set release | mj_keyword, mj_keyword_definition |
| Scryfall Tags | `mtgsim db sync --tags` | Monthly | mj_card_tag |
| 17Lands Metadata | `mtgsim db sync --17lands --17l-metadata-only` | Weekly | sl_dataset |
| 17Lands CSVs | `mtgsim db sync --17lands` | Per set release | (downloads only) |
| 17Lands Ingest | `mtgsim db sync --17lands --17l-ingest` | After download | sl_draft_pick, sl_draft_card, sl_game, sl_game_card, sl_replay, sl_replay_turn |
| 17Lands Card Stats | `mtgsim db sync --17lands --17l-stats --17l-expansion <CODE>` | After ingest | sl_card_stat |
| 17Lands Card Ratings | `mtgsim db sync --17lands --17l-ratings --17l-expansion <CODE>` | Weekly for in-season sets | sl_card_stat |
| Full sync (all MTGJSON) | `mtgsim db sync` | Per set release | All mj_* tables except 17lands |

Add `--force` to any command to re-download files that already exist.

---

## 1. MTGJSON

**Base URL:** `https://mtgjson.com/api/v5`

### Cards & Sets (`--cards`)

**Source file:** `AllPrintings.sqlite.xz`
**Download URL:** `https://mtgjson.com/api/v5/AllPrintings.sqlite.xz`
**Local path:** `~/.mtgsim/reference/mtgjson/AllPrintings.sqlite`

**Pipeline:**
1. Download `.xz` compressed SQLite file
2. Decompress with `lzma`
3. Open source SQLite, read `sets` and `cards` tables
4. Transform rows into SQLModel objects
5. Batch insert into destination tables (10,000 rows per commit)

**Tables populated:**

| Table | Source Table | Key Fields |
|-------|-------------|------------|
| `mj_set` | sets | code, name, type, releaseDate, baseSetSize, totalSetSize |
| `mj_card` | cards | uuid, name, setCode, manaCost, manaValue, type, text, power, toughness, rarity, colors, keywords (JSON) |
| `mj_card_identifier` | cardIdentifiers | scryfallId, tcgplayerProductId, mtgoId, multiverseId |
| `mj_card_legality` | cardLegalities | format, status (Legal, Banned, Restricted, etc.) |

**When to update:** After a new MTG set releases (roughly every 3 months).

### Prices (`--prices`)

**Source file:** `AllPricesToday.sqlite.xz`
**Download URL:** `https://mtgjson.com/api/v5/AllPricesToday.sqlite.xz`
**Local path:** `~/.mtgsim/reference/mtgjson/AllPricesToday.sqlite`

**Table populated:** `mj_card_price`
- card_uuid (FK to mj_card), provider (tcgplayer, cardmarket, cardsphere, cardkingdom), listing_type (retail, buylist), finish (normal, foil, etched), currency, price, updated_at
- Batch size: 50,000 rows

**When to update:** Daily for current prices. The file contains only today's snapshot.

### Decks (`--decks`)

**Source file:** `AllDeckFiles.tar.xz`
**Download URL:** `https://mtgjson.com/api/v5/AllDeckFiles.tar.xz`
**Local path:** `~/.mtgsim/reference/mtgjson/AllDeckFiles/`

**Tables populated:**
- `mj_deck` — name, code, type, releaseDate
- `mj_deck_card` — deck_id, card_uuid, board (main/side/commander), count

**When to update:** After a new set release (new precon decks).

### Keywords (`--keywords`)

**Source file:** `Keywords.json.xz`
**Download URL:** `https://mtgjson.com/api/v5/Keywords.json.xz`
**Local path:** `~/.mtgsim/reference/mtgjson/Keywords.json`

**Tables populated:**
- `mj_keyword` — name, type (abilityWords, keywordAbilities, keywordActions)
- `mj_keyword_definition` — keyword, definition, source (synced from `src/mtgsim/data/keyword-definitions.json`)

**When to update:** After a new set introduces new keywords (check release notes).

**Note:** MTGJSON provides keyword names only. Definitions come from our curated JSON file, which was verified against the MTG Comprehensive Rules (April 2025 edition).

---

## 2. Scryfall Oracle Tags (`--tags`)

**API:** `https://api.scryfall.com/cards/search?q=oracletag:<tag>&unique=cards`
**Rate limit:** 100ms between pages (Scryfall TOS)
**Cache file:** `~/.mtgsim/reference/scryfall/oracle_tags.json`

**Tags fetched:** mana-dork, mana-rock, ramp, removal, boardwipe, tutor, counterspell, draw, lifegain

**Pipeline:**
1. For each tag, paginate through Scryfall search API
2. Collect card names per tag
3. Save to local JSON cache
4. Sync cache into `mj_card_tag` table (card_uuid, tag)

**Table populated:** `mj_card_tag`

**When to update:** Monthly, or after a new set releases. Tags are community-curated on Scryfall.

---

## 3. 17Lands Public Datasets (`--17lands`)

**Metadata API:** `https://17lands.cdn.prismic.io/api/v2` (Prismic CMS)
**Data files:** `https://17lands-public.s3.amazonaws.com/analysis_data/`
**License:** Creative Commons Attribution 4.0 (CC BY 4.0). Attribution is required: cite as **"17Lands"** (capital L) with a link, visible at the top level of anything built on the data — the API includes an `attribution` field on stats responses for this reason.

### 17Lands data source catalog

17Lands exposes data three ways; we only consume the first:

1. **Public datasets** (this section) — anonymized per-draft/per-game CSVs on S3, indexed via Prismic. CC BY 4.0, explicitly encouraged for third-party analysis. Publication schedule per set: draft data ~2 weeks after Arena release, game data ~3 weeks, replay data ~6 weeks; files are refreshed for a few months, then frozen.
2. **Curated data (unofficial site API)** — the JSON endpoints behind pages like Card Data (`GET /card_ratings/data?expansion=X&format=Y&start_date&end_date`) and Deck Color Data (`GET /color_ratings/data`). Used **sparingly**: `--17l-ratings` makes exactly one request per set/format (with an identifying User-Agent) to fetch the site-calculated Card Data table into `sl_card_stat` (`source='17lands'`) — the only source of win-rate stats for in-season sets whose public game file isn't out yet. Per the [usage guidelines](https://www.17lands.com/usage_guidelines), bulk scraping is discouraged, endpoints are rate-limited and unversioned, and third-party tools showing curated data face a **12-day embargo** on new expansions (7 days for specialty formats). Note the endpoint only serves a live recent window: for past sets it returns near-empty stats regardless of date range (verified July 2026 — SOS returned data for 42/341 cards vs 321/334 for in-season MSH), so for any set whose limited season is over, the public datasets are the **only** complete source (`--17l-stats`, `source='public_dataset'`).
3. **Personal data (authenticated)** — a user's own event history via `mtgdb.sync.seventeenlands_client` (`db sync-17l-personal`), throttled to one request per 5s.

**Good-citizen behavior baked into the sync:** downloads skip existing files, sleep 3s between S3 fetches, and record the dataset version at download time (`*_downloaded_version`) so stale files are reported rather than silently kept or hammered for re-download.

### Metadata Sync (`--17l-metadata-only`)

**Pipeline:**
1. Fetch Prismic master ref
2. Query `public-data` document type
3. Parse 120+ dataset entries (expansion, format, URLs)
4. Upsert into `sl_dataset`

### File Download (default with `--17lands`)

**URL patterns:**
- `analysis_data/draft_data/draft_data_public.<EXP>.<FMT>.csv.gz`
- `analysis_data/game_data/game_data_public.<EXP>.<FMT>.csv.gz`
- `analysis_data/replay_data/replay_data_public.<EXP>.<FMT>.csv.gz`

**Local paths:** `~/.mtgsim/reference/17lands/<type>/`

Files are tar-wrapped gzip CSVs. Filter downloads with `--17l-expansion <CODE>`.

### CSV Ingestion (`--17l-ingest`)

**Pipeline:** Parse wide-format CSVs into normalized rows with 1,000-row batch inserts.

| Data Type | Tables | Row Description |
|-----------|--------|-----------------|
| draft | `sl_draft_pick`, `sl_draft_card` | One pick row + one card row per card in pack/pool |
| game | `sl_game`, `sl_game_card` | One game row + one card row per card in deck/hand/drawn/sideboard |
| replay | `sl_replay`, `sl_replay_turn` | One replay row + one turn row per turn per player (up to 30 turns) |

**Filter options:**
- `--17l-expansion <CODE>` — restrict to one expansion
- `--17l-format <FMT>` — restrict to one format (e.g. `PremierDraft`)
- `--17l-data-type <draft|game|replay|all>` — restrict downloads/ingest to one data type

Re-ingesting a dataset first clears its previously ingested rows, so ingestion is idempotent.

**When to update:** draft data appears ~2 weeks after a set's Arena release, game data ~3 weeks, replay data ~6 weeks; 17Lands refreshes the files for a few months afterward.

### Card Stats (`--17l-stats`)

Computes 17Lands-style per-card metrics **locally** from the ingested tables into `sl_card_stat` — no requests to 17lands.com:

```bash
mtgsim db sync --17lands --17l-stats --17l-expansion SOS --17l-format PremierDraft
```

Metrics follow [17Lands' definitions](https://www.17lands.com/metrics_definitions): ALSA (`avg_seen`), ATA (`avg_pick`), GP WR (`win_rate`), OH WR, GD WR, GIH WR (`ever_drawn_win_rate`), GNS WR, IWD (`drawn_improvement_win_rate`), play rate. Rows are enriched with color/rarity from `mj_card` and provenance (`source`, `dataset_last_updated`, `computed_at`). Served by `GET /api/17lands/card_stats?expansion=<CODE>&format=<FMT>`.

Numbers will differ slightly from 17lands.com: the site aggregates a live window with its own filters, while our stats reflect the downloaded file snapshot.

---

## 4. Keyword Definitions (manual)

**Source file:** `src/mtgsim/data/keyword-definitions.json`
**Table:** `mj_keyword_definition`

This is a curated JSON file containing ~352 keyword definitions verified against the MTG Comprehensive Rules. It is synced to the database as part of the `--keywords` CLI flag.

**When to update:** When new keywords are introduced in a set. Add the keyword and definition to the JSON file, then run `mtgsim db sync --keywords`.

---

## 5. SRS / Flashcard Data

**Database:** `~/.srs/srs.db` (separate from mtgsim.sqlite)
**Managed by:** `srs` package (editable dependency at `../srs`)

**Tables (in srs.db):**
- `applications` — app-level grouping (one "mtgsim" app)
- `collections` — flashcard collections (per keyword type, per set)
- `flashcards` — question/answer pairs (JSON)
- `flashcard_collections` — many-to-many junction
- `srs_state` — SM-2 scheduling state per user/card
- `review_events` — audit trail of reviews

**Populated by:** `POST /api/flashcards/generate` endpoint, which reads from mtgsim.sqlite (`mj_keyword`, `mj_keyword_definition`, `mj_card`) and creates flashcards in srs.db.

**Not part of CLI sync** — flashcards are generated on-demand via the API.

---

## Directory Structure

```
~/.mtgsim/                              (MTGSIM_HOME)
├── mtgsim.sqlite                       (main database, ~500MB+)
├── corpus_wordfreq.json                (computed word frequencies)
└── reference/
    ├── mtgjson/
    │   ├── AllPrintings.sqlite         (source: mtgjson.com)
    │   ├── AllPricesToday.sqlite       (source: mtgjson.com)
    │   ├── Keywords.json               (source: mtgjson.com)
    │   └── AllDeckFiles/               (source: mtgjson.com)
    ├── scryfall/
    │   └── oracle_tags.json            (cache: scryfall API)
    └── 17lands/
        ├── draft_data/*.csv.gz         (source: 17lands S3)
        ├── game_data/*.csv.gz
        └── replay_data/*.csv.gz

~/.srs/
└── srs.db                              (flashcard SRS state)
```

## Full Sync Example

```bash
# Initial setup (downloads ~2GB, takes 10-15 minutes)
mtgsim db sync

# Update prices (daily)
mtgsim db sync --prices

# After a new set release
mtgsim db sync --cards --keywords --tags

# Add 17Lands data for a new set
mtgsim db sync --17lands --17l-expansion FDN
mtgsim db sync --17lands --17l-ingest --17l-expansion FDN --17l-data-type game
```

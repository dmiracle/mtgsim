"""Database CLI commands."""

import typer
from mtgdb.config import DB_PATH

db_app = typer.Typer(help="Database operations")


@db_app.command("init")
def db_init():
    """Initialize the unified database schema.

    Creates the database at ~/.mtgsim/mtgsim.sqlite with all tables.
    Run 'mtgsim db sync' after to populate with MTGJSON data.
    """
    import sqlite3

    from mtgdb.session import init_db

    init_db()
    typer.echo(f"Database initialized at {DB_PATH}")

    # Show table list
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [row[0] for row in cursor.fetchall()]
    conn.close()

    typer.echo(f"Tables created: {', '.join(tables)}")


@db_app.command("sync")
def db_sync(
    force: bool = typer.Option(False, "--force", "-f", help="Force re-download even if files exist"),
    cards_only: bool = typer.Option(False, "--cards", help="Sync only cards"),
    sets_only: bool = typer.Option(False, "--sets", help="Sync only sets"),
    prices_only: bool = typer.Option(False, "--prices", help="Sync only prices"),
    decks_only: bool = typer.Option(False, "--decks", help="Sync only decks"),
    keywords_only: bool = typer.Option(False, "--keywords", help="Sync only keywords"),
    keyword_definitions_only: bool = typer.Option(
        False, "--keyword-definitions", help="Sync keyword definitions from Comprehensive Rules"
    ),
    tags_only: bool = typer.Option(False, "--tags", help="Sync only Scryfall oracle tags"),
    seventeenlands: bool = typer.Option(False, "--17lands", help="Sync 17Lands public datasets"),
    seventeenlands_expansion: str | None = typer.Option(
        None, "--17l-expansion", help="Filter 17Lands sync to expansion"
    ),
    seventeenlands_metadata_only: bool = typer.Option(
        False, "--17l-metadata-only", help="Only sync 17Lands metadata, skip downloads"
    ),
    seventeenlands_ingest: bool = typer.Option(
        False, "--17l-ingest", help="Ingest downloaded 17Lands CSVs into DB tables"
    ),
    seventeenlands_data_type: str | None = typer.Option(
        None, "--17l-data-type", help="Data type to ingest: draft, game, replay, or all"
    ),
):
    """Sync MTGJSON data to unified database.

    Downloads latest MTGJSON data and populates all tables in the unified
    database at ~/.mtgsim/mtgsim.sqlite.

    This includes:
    - Sets (mj_set)
    - Cards (mj_card, mj_card_identifier, mj_card_legality)
    - Prices (mj_card_price)
    - Decks (mj_deck, mj_deck_card)
    - Keywords (mj_keyword)
    - Tags (mj_card_tag) — Scryfall oracle tags

    By default syncs all data. Use flags to sync specific data types.
    """
    from mtgdb.config import (
        ALL_DECK_FILES_DIR,
        ALL_DECK_FILES_URL,
        ALL_PRICES_URL,
        ALL_PRINTINGS_URL,
        KEYWORDS_URL,
        MTGJSON_DIR,
        ensure_dirs,
    )
    from mtgdb.session import init_db
    from mtgdb.sync import sync_all, sync_cards, sync_decks, sync_keywords, sync_prices, sync_sets
    from mtgdb.sync.download import download_and_extract_tar_xz, download_and_extract_xz
    from mtgdb.sync.scryfall import fetch_all_tags, sync_tags

    try:
        if seventeenlands:
            from mtgdb.config import ensure_dirs
            from mtgdb.session import init_db
            from mtgdb.sync.seventeenlands import (
                download_dataset_files,
                ingest_datasets,
                sync_dataset_metadata,
            )

            ensure_dirs()
            init_db()
            count = sync_dataset_metadata()
            typer.echo(f"17Lands metadata synced: {count} datasets.")

            if not seventeenlands_metadata_only and not seventeenlands_ingest:
                downloaded = download_dataset_files(expansion=seventeenlands_expansion, force=force)
                typer.echo(f"17Lands files downloaded: {downloaded}.")

            if seventeenlands_ingest:
                dt = seventeenlands_data_type or "all"
                data_types = ["draft", "game", "replay"] if dt == "all" else [dt]
                results = ingest_datasets(
                    expansion=seventeenlands_expansion,
                    data_types=data_types,
                )
                for key, rows in results.items():
                    typer.echo(f"  {key}: {rows:,} rows")
                typer.echo(f"17Lands ingestion complete: {len(results)} datasets.")
            return

        any_specific = (
            cards_only
            or sets_only
            or prices_only
            or decks_only
            or keywords_only
            or keyword_definitions_only
            or tags_only
        )
        if any_specific:
            ensure_dirs()
            init_db()

            printings_db = MTGJSON_DIR / "AllPrintings.sqlite"
            prices_db = MTGJSON_DIR / "AllPricesToday.sqlite"
            keywords_file = MTGJSON_DIR / "Keywords.json"

            if sets_only:
                download_and_extract_xz(ALL_PRINTINGS_URL, printings_db, force)
                result = sync_sets(printings_db)
                typer.echo(result.summary())

            if cards_only:
                download_and_extract_xz(ALL_PRINTINGS_URL, printings_db, force)
                result = sync_cards(printings_db)
                typer.echo(result.summary())

            if prices_only:
                download_and_extract_xz(ALL_PRICES_URL, prices_db, force)
                result = sync_prices(prices_db)
                typer.echo(result.summary())

            if decks_only:
                download_and_extract_tar_xz(ALL_DECK_FILES_URL, ALL_DECK_FILES_DIR, force)
                result = sync_decks(ALL_DECK_FILES_DIR)
                typer.echo(result.summary())

            if keywords_only:
                download_and_extract_xz(KEYWORDS_URL, keywords_file, force)
                result = sync_keywords(keywords_file)
                typer.echo(result.summary())
                _sync_keyword_definitions(force)

            if keyword_definitions_only:
                _sync_keyword_definitions(force)

            if tags_only:
                tag_data = fetch_all_tags(force=force)
                sync_tags()
                typer.echo(f"Tags sync complete. {sum(len(v) for v in tag_data.values())} card-tag pairs.")
        else:
            sync_all(force=force)

        typer.echo(f"Data stored in {DB_PATH}")

    except Exception as e:
        typer.echo(f"Error during sync: {e}")
        raise typer.Exit(1)


def _sync_keyword_definitions(force: bool = False):
    """Sync keyword definitions from Comprehensive Rules, with JSON fallback."""
    from pathlib import Path as _Path

    from mtgdb.sync.comprehensive_rules import sync_definitions_from_rules
    from mtgdb.sync.tables import check_missing_keyword_definitions, sync_keyword_definitions

    # Primary: Comprehensive Rules
    rules_result = sync_definitions_from_rules(force)
    typer.echo(rules_result.summary())

    # Fallback: JSON file for keywords not in the rules (ability words, etc.)
    defs_file = _Path(__file__).parent.parent / "data" / "keyword-definitions.json"
    if defs_file.exists():
        defs_result = sync_keyword_definitions(defs_file)
        typer.echo(defs_result.summary())

    # Report coverage
    missing = check_missing_keyword_definitions()
    if missing:
        typer.echo(f"Warning: {len(missing)} keywords have no definition:")
        for m in missing:
            typer.echo(f"  [{m['type']}] {m['name']}")
    else:
        typer.echo("All keywords have definitions.")

    # Report source breakdown
    from mtgdb.models import MJKeywordDefinition
    from mtgdb.session import get_session
    from sqlmodel import func, select

    with get_session() as session:
        sources = session.exec(
            select(MJKeywordDefinition.source, func.count()).group_by(MJKeywordDefinition.source)
        ).all()
        typer.echo("Definition sources: " + ", ".join(f"{s}={c}" for s, c in sources))


@db_app.command("sync-17l-personal")
def db_sync_17l_personal(
    email: str = typer.Option(None, "--email", "-e", help="17Lands account email"),
    password: str = typer.Option(None, "--password", "-p", help="17Lands account password"),
    start_date: str | None = typer.Option(None, "--start", help="Start date (YYYY-MM-DD)"),
    end_date: str | None = typer.Option(None, "--end", help="End date (YYYY-MM-DD)"),
    expansion: str | None = typer.Option(None, "--expansion", help="Filter by expansion code"),
    event_format: str | None = typer.Option(None, "--format", help="Filter by event format"),
    skip_details: bool = typer.Option(False, "--skip-details", help="Only fetch event list, skip per-event details"),
    delay: float = typer.Option(5.0, "--delay", help="Seconds between API requests"),
):
    """Sync your personal 17Lands event history.

    Downloads your drafts, games, and deck data from 17Lands.
    Credentials are only used for this session and are not stored.

    Rate-limited to be respectful of the 17Lands API (5s delay by default).
    Incremental: only fetches events not already in the database.
    """
    import getpass

    from mtgdb.session import init_db
    from mtgdb.sync.seventeenlands_client import sync_personal_events

    init_db()

    if not email:
        email = typer.prompt("17Lands email")
    if not password:
        password = getpass.getpass("17Lands password: ")

    typer.echo(f"Syncing personal data (delay={delay}s between requests)...")

    try:
        count = sync_personal_events(
            email=email,
            password=password,
            start_date=start_date,
            end_date=end_date,
            expansion=expansion,
            event_format=event_format,
            fetch_details=not skip_details,
            delay=delay,
        )
        typer.echo(f"Synced {count} new events.")
    except RuntimeError as e:
        typer.echo(f"Error: {e}")
        raise typer.Exit(1)


@db_app.command("stats")
def db_stats():
    """Show database statistics."""
    import sqlite3

    if not DB_PATH.exists():
        typer.echo(f"Database not found at {DB_PATH}")
        typer.echo("Run 'mtgsim db sync' to create and populate it.")
        raise typer.Exit(1)

    conn = sqlite3.connect(DB_PATH)

    tables = [
        ("mj_set", "Sets"),
        ("mj_card", "Cards"),
        ("mj_card_identifier", "Card Identifiers"),
        ("mj_card_legality", "Card Legalities"),
        ("mj_card_price", "Card Prices"),
        ("mj_deck", "Decks"),
        ("mj_deck_card", "Deck Cards"),
        ("mj_keyword", "Keywords"),
        ("mj_card_tag", "Card Tags"),
        ("user_17l_event", "17Lands Personal Events"),
        ("user_card", "User Collection"),
        ("user_deck", "User Decks"),
        ("user_deck_card", "User Deck Cards"),
    ]

    typer.echo(f"Database: {DB_PATH}")
    typer.echo(f"Size: {DB_PATH.stat().st_size / 1024 / 1024:.1f} MB")
    typer.echo("")
    typer.echo("Table counts:")

    for table_name, label in tables:
        try:
            cursor = conn.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            typer.echo(f"  {label}: {count:,}")
        except sqlite3.OperationalError:
            typer.echo(f"  {label}: (table not found)")

    conn.close()


@db_app.command("reset")
def db_reset(
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
):
    """Reset the database (delete all data).

    This will delete the database file and re-initialize the schema.
    User collection data will be lost.
    """
    if not force:
        confirm = typer.confirm("This will delete all data including your collection. Continue?")
        if not confirm:
            typer.echo("Cancelled.")
            raise typer.Exit(0)

    if DB_PATH.exists():
        DB_PATH.unlink()
        typer.echo(f"Deleted {DB_PATH}")

    from mtgdb.session import init_db

    init_db()
    typer.echo(f"Database re-initialized at {DB_PATH}")
    typer.echo("Run 'mtgsim db sync' to populate with MTGJSON data.")

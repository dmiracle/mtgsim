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
    tags_only: bool = typer.Option(False, "--tags", help="Sync only Scryfall oracle tags"),
    seventeenlands: bool = typer.Option(False, "--17lands", help="Sync 17Lands public datasets"),
    seventeenlands_expansion: str | None = typer.Option(
        None, "--17l-expansion", help="Filter 17Lands sync to expansion"
    ),
    seventeenlands_metadata_only: bool = typer.Option(
        False, "--17l-metadata-only", help="Only sync 17Lands metadata, skip downloads"
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
            from mtgdb.sync.seventeenlands import download_dataset_files, sync_dataset_metadata

            ensure_dirs()
            init_db()
            count = sync_dataset_metadata()
            typer.echo(f"17Lands metadata synced: {count} datasets.")

            if not seventeenlands_metadata_only:
                downloaded = download_dataset_files(expansion=seventeenlands_expansion, force=force)
                typer.echo(f"17Lands files downloaded: {downloaded}.")
            return

        if cards_only or sets_only or prices_only or decks_only or keywords_only or tags_only:
            ensure_dirs()
            init_db()

            printings_db = MTGJSON_DIR / "AllPrintings.sqlite"
            prices_db = MTGJSON_DIR / "AllPricesToday.sqlite"
            keywords_file = MTGJSON_DIR / "Keywords.json"

            if sets_only:
                download_and_extract_xz(ALL_PRINTINGS_URL, printings_db, force)
                sync_sets(printings_db)
                typer.echo("Sets sync complete.")

            if cards_only:
                download_and_extract_xz(ALL_PRINTINGS_URL, printings_db, force)
                sync_cards(printings_db)
                typer.echo("Cards sync complete.")

            if prices_only:
                download_and_extract_xz(ALL_PRICES_URL, prices_db, force)
                sync_prices(prices_db)
                typer.echo("Prices sync complete.")

            if decks_only:
                download_and_extract_tar_xz(ALL_DECK_FILES_URL, ALL_DECK_FILES_DIR, force)
                sync_decks(ALL_DECK_FILES_DIR)
                typer.echo("Decks sync complete.")

            if keywords_only:
                download_and_extract_xz(KEYWORDS_URL, keywords_file, force)
                sync_keywords(keywords_file)
                typer.echo("Keywords sync complete.")

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

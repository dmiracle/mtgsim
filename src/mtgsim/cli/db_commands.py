"""Database CLI commands."""

import typer

from mtgsim.config import DB_PATH

db_app = typer.Typer(help="Database operations")


@db_app.command("init")
def db_init():
    """Initialize the unified database schema.

    Creates the database at ~/.mtgsim/mtgsim.sqlite with all tables.
    Run 'mtgsim db sync' after to populate with MTGJSON data.
    """
    import sqlite3

    from mtgsim.db.session import init_db

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
):
    """Sync MTGJSON data to unified database.

    Downloads latest MTGJSON data and populates all tables in the unified
    database at ~/.mtgsim/mtgsim.sqlite.

    This includes:
    - Cards (mj_card, mj_card_identifier, mj_card_legality)
    - Sets (mj_set)
    - Prices (mj_card_price)
    - Decks (mj_deck, mj_deck_card)

    By default syncs all data. Use flags to sync specific data types.
    """
    from mtgsim.config import ALL_DECK_FILES_DIR, MTGJSON_DIR
    from mtgsim.sync.unified import sync_all, sync_cards, sync_decks, sync_prices, sync_sets

    try:
        if cards_only or sets_only or prices_only or decks_only:
            # Selective sync - need to download files first
            from mtgsim.config import ALL_DECK_FILES_URL, ALL_PRICES_URL, ALL_PRINTINGS_URL, ensure_dirs
            from mtgsim.db.session import init_db
            from mtgsim.sync.mtgjson import download_and_extract, download_file, extract_tar_xz, should_update

            ensure_dirs()
            init_db()

            printings_db = MTGJSON_DIR / "AllPrintings.sqlite"
            prices_db = MTGJSON_DIR / "AllPricesToday.sqlite"

            if sets_only:
                if not printings_db.exists() or force:
                    download_and_extract(ALL_PRINTINGS_URL, printings_db, force)
                sync_sets(printings_db)
                typer.echo("Sets sync complete.")

            if cards_only:
                if not printings_db.exists() or force:
                    download_and_extract(ALL_PRINTINGS_URL, printings_db, force)
                sync_cards(printings_db)
                typer.echo("Cards sync complete.")

            if prices_only:
                if not prices_db.exists() or force:
                    download_and_extract(ALL_PRICES_URL, prices_db, force)
                sync_prices(prices_db)
                typer.echo("Prices sync complete.")

            if decks_only:
                all_decks_tar = MTGJSON_DIR / "AllDeckFiles.tar.xz"
                if should_update(ALL_DECK_FILES_DIR, force):
                    if download_file(ALL_DECK_FILES_URL, all_decks_tar):
                        extract_tar_xz(all_decks_tar, MTGJSON_DIR)
                        all_decks_tar.unlink(missing_ok=True)
                if ALL_DECK_FILES_DIR.exists():
                    sync_decks(ALL_DECK_FILES_DIR)
                typer.echo("Decks sync complete.")
        else:
            # Full sync
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
        ("mj_card", "Cards"),
        ("mj_card_identifier", "Card Identifiers"),
        ("mj_card_legality", "Card Legalities"),
        ("mj_card_price", "Card Prices"),
        ("mj_set", "Sets"),
        ("mj_deck", "Decks"),
        ("mj_deck_card", "Deck Cards"),
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

    from mtgsim.db.session import init_db

    init_db()
    typer.echo(f"Database re-initialized at {DB_PATH}")
    typer.echo("Run 'mtgsim db sync' to populate with MTGJSON data.")

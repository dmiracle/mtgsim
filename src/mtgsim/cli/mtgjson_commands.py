import sqlite3

import typer

from mtgsim.config import MERGED_DB_PATH, MTGJSON_DIR

mtgjson_app = typer.Typer(help="MTGJSON data operations")


@mtgjson_app.command("info")
def mtgjson_info():
    """Show MTGJSON reference data info."""
    if not MTGJSON_DIR.exists():
        typer.echo("No reference data found. Run 'mtgsim db sync' first.")
        return

    files = list(MTGJSON_DIR.glob("*.sqlite")) + list(MTGJSON_DIR.glob("*.json"))
    if not files:
        typer.echo("No reference databases found.")
        return

    typer.echo("MTGJSON Reference Data:")
    for f in sorted(files):
        size_mb = f.stat().st_size / (1024 * 1024)
        typer.echo(f"  {f.name}: {size_mb:.1f} MB")


@mtgjson_app.command("stats")
def mtgjson_stats():
    """Show statistics from reference database."""
    if not MERGED_DB_PATH.exists():
        typer.echo("Reference database not found. Run 'mtgsim db sync' first.")
        raise typer.Exit(1)

    conn = sqlite3.connect(MERGED_DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM cards")
    card_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(DISTINCT setCode) FROM cards")
    set_count = cursor.fetchone()[0]

    conn.close()

    typer.echo(f"Cards: {card_count:,}")
    typer.echo(f"Sets: {set_count:,}")

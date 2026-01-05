import typer

mtgjson_app = typer.Typer(help="MTGJSON data operations")


@mtgjson_app.command("info")
def mtgjson_info():
    """Show MTGJSON reference data info."""
    from pathlib import Path

    ref_dir = Path.home() / ".mtgsim" / "reference" / "mtgjson"

    if not ref_dir.exists():
        typer.echo("No reference data found. Run 'mtgsim db sync' first.")
        return

    files = list(ref_dir.glob("*.sqlite")) + list(ref_dir.glob("*.json"))
    if not files:
        typer.echo("No reference databases found.")
        return

    typer.echo("MTGJSON Reference Data:")
    for f in sorted(files):
        size_mb = f.stat().st_size / (1024 * 1024)
        typer.echo(f"  {f.name}: {size_mb:.1f} MB")


@mtgjson_app.command("stats")
def mtgjson_stats():
    """Show statistics from reference databases."""
    import sqlite3
    from pathlib import Path

    ref_dir = Path.home() / ".mtgsim" / "reference" / "mtgjson"
    all_printings = ref_dir / "AllPrintings.sqlite"

    if not all_printings.exists():
        typer.echo("AllPrintings.sqlite not found. Run 'mtgsim db sync' first.")
        raise typer.Exit(1)

    conn = sqlite3.connect(all_printings)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM cards")
    card_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(DISTINCT setCode) FROM cards")
    set_count = cursor.fetchone()[0]

    conn.close()

    typer.echo(f"Cards: {card_count:,}")
    typer.echo(f"Sets: {set_count:,}")

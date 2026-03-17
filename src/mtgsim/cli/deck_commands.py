"""Deck CLI commands."""

import sys
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

deck_app = typer.Typer(help="Deck management commands")
console = Console()


@deck_app.command("import")
def import_deck(
    file: Path | None = typer.Argument(None, help="Path to MTGA deck file (reads stdin if omitted)"),
    name: str = typer.Option(..., "--name", "-n", help="Deck name"),
):
    """Import a deck from MTGA export format.

    Reads from a file or stdin (pipe). Auto-detects format legality.

    Examples:
        mtgsim deck import deck.txt -n "Burn"
        cat deck.txt | mtgsim deck import -n "Burn"
    """
    from mtgsim.deck_import import import_mtga_deck

    if file:
        if not file.exists():
            console.print(f"[red]File not found: {file}[/red]")
            raise typer.Exit(1)
        text = file.read_text()
    elif not sys.stdin.isatty():
        text = sys.stdin.read()
    else:
        console.print("[red]Provide a file path or pipe deck text via stdin[/red]")
        raise typer.Exit(1)

    result = import_mtga_deck(text=text, name=name)

    console.print(f"\n[green]Deck created:[/green] {result.deck_name} (id={result.deck_id})")
    console.print(f"Total cards: {result.total_cards}")

    exact = [c for c in result.resolved if c.match_type == "exact"]
    fuzzy = [c for c in result.resolved if c.match_type == "fuzzy"]
    created = [c for c in result.resolved if c.match_type == "created"]
    console.print(f"Exact: {len(exact)}, Fuzzy: {len(fuzzy)}, Created: {len(created)}")

    if fuzzy:
        table = Table(title="Fuzzy Matches")
        table.add_column("Input Name")
        table.add_column("Matched To")
        table.add_column("Score")
        for card in fuzzy:
            table.add_row(card.name, card.matched_name or "", f"{card.match_score:.0f}")
        console.print(table)

    if created:
        table = Table(title="Created (not in database)")
        table.add_column("Count")
        table.add_column("Name")
        table.add_column("Set")
        table.add_column("UUID")
        for card in created:
            table.add_row(str(card.count), card.name, card.set_code or "-", card.card_uuid[:12] + "...")
        console.print(table)

    if result.legality:
        table = Table(title="Format Legality")
        table.add_column("Format")
        table.add_column("Legal")
        table.add_column("Reason")
        for lr in result.legality:
            status = "[green]Yes[/green]" if lr.legal else "[red]No[/red]"
            table.add_row(lr.format, status, lr.reason or "")
        console.print(table)

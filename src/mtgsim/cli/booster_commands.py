"""Booster pack CLI commands."""

import typer
from rich.console import Console
from rich.table import Table

booster_app = typer.Typer(help="Booster pack generation")
console = Console()


@booster_app.command("open")
def open_booster(
    set_code: str = typer.Argument(..., help="Set code (e.g., DSK, MH3, 2ED)"),
    count: int = typer.Option(1, "--count", "-c", help="Number of packs to open"),
    booster_type: str | None = typer.Option(None, "--type", "-t", help="Booster type: play, draft"),
):
    """Open booster pack(s) from a set."""
    from mtgsim.booster import generate_booster

    for i in range(count):
        try:
            pack = generate_booster(set_code.upper(), booster_type=booster_type)
        except ValueError as e:
            console.print(f"[red]{e}[/red]")
            raise typer.Exit(1)

        if count > 1:
            console.print(f"\n[bold]Pack {i + 1}[/bold] — {pack.set_name} ({pack.booster_type} booster)")
        else:
            console.print(f"\n[bold]{pack.set_name}[/bold] ({pack.booster_type} booster)")

        table = Table(show_header=True)
        table.add_column("Slot", style="dim")
        table.add_column("Name")
        table.add_column("Rarity")
        table.add_column("Type")
        table.add_column("Foil")

        rarity_colors = {
            "common": "white",
            "uncommon": "cyan",
            "rare": "yellow",
            "mythic": "red",
        }

        for card in pack.cards:
            color = rarity_colors.get(card.rarity, "white")
            foil = "[bright_magenta]FOIL[/bright_magenta]" if card.is_foil else ""
            table.add_row(
                card.slot,
                f"[{color}]{card.name}[/{color}]",
                card.rarity,
                card.type_line or "",
                foil,
            )

        console.print(table)

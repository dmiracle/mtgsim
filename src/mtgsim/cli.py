from pathlib import Path

import typer

from .ascii_card import render_card
from .card import Card, CardType, ManaCost, Rarity, Supertype
from .db import DATABASE_PATH, get_session, init_db
from .extract import get_pipeline
from .mtgjson.cli import mtgjson_app
from .repository import CardRepository, db_to_card
from .sync import update_decks, update_references

app = typer.Typer(help="MTG card simulator CLI")
db_app = typer.Typer(help="Database operations")
app.add_typer(db_app, name="db")
app.add_typer(mtgjson_app, name="mtgjson")


def parse_card_types(types: str) -> list[CardType]:
    return [CardType(t.strip()) for t in types.split(",")]


def parse_supertypes(types: str | None) -> list[Supertype]:
    if not types:
        return []
    return [Supertype(t.strip()) for t in types.split(",")]


def parse_subtypes(types: str | None) -> list[str]:
    if not types:
        return []
    return [t.strip() for t in types.split(",")]


@app.command()
def card(
    name: str = typer.Argument(..., help="Card name"),
    types: str = typer.Option(
        ...,
        "--types",
        "-t",
        help=(
            "Card types (comma-separated): Creature, Instant, Sorcery, Enchantment, Artifact, Land, Planeswalker, "
            "Battle"
        ),
    ),
    oracle: str = typer.Option("", "--oracle", "-o", help="Oracle text"),
    supertypes: str | None = typer.Option(
        None,
        "--supertypes",
        "-s",
        help="Supertypes (comma-separated): Basic, Legendary, Snow, World",
    ),
    subtypes: str | None = typer.Option(
        None,
        "--subtypes",
        help="Subtypes (comma-separated): e.g., Elf, Warrior, Forest",
    ),
    mana: str | None = typer.Option(
        None,
        "--mana",
        "-m",
        help="Mana cost: W=white, U=blue, B=black, R=red, G=green, C=colorless, number=generic. e.g., '2GG'",
    ),
    power: int | None = typer.Option(None, "--power", "-p", help="Power (creatures only)"),
    toughness: int | None = typer.Option(None, "--toughness", help="Toughness (creatures only)"),
    loyalty: int | None = typer.Option(None, "--loyalty", help="Loyalty (planeswalkers only)"),
    defense: int | None = typer.Option(None, "--defense", help="Defense (battles only)"),
    rarity: str = typer.Option("common", "--rarity", "-r", help="Rarity: common, uncommon, rare, mythic"),
):
    """Generate and display an ASCII card."""
    mana_cost = parse_mana_cost(mana) if mana else None

    c = Card(
        name=name,
        card_types=parse_card_types(types),
        supertypes=parse_supertypes(supertypes),
        subtypes=parse_subtypes(subtypes),
        mana_cost=mana_cost,
        oracle_text=oracle,
        power=power,
        toughness=toughness,
        loyalty=loyalty,
        defense=defense,
        rarity=Rarity(rarity),
    )

    typer.echo(render_card(c))


@app.command()
def extract(
    image_path: Path = typer.Argument(..., help="Path to card image file"),
    pipeline: str = typer.Option("mock", "--pipeline", "-p", help="Extraction pipeline to use"),
    output: str = typer.Option("ascii", "--output", "-o", help="Output format: ascii, json"),
    save: bool = typer.Option(False, "--save", "-s", help="Save extracted card to database"),
):
    """Extract card data from an image."""
    if not image_path.exists():
        typer.echo(f"Error: File not found: {image_path}")
        raise typer.Exit(1)

    extractor = get_pipeline(pipeline)
    card = extractor.extract(image_path)

    if output == "json":
        typer.echo(card.model_dump_json(indent=2))
    else:
        typer.echo(render_card(card))
        typer.echo()
        typer.echo(f"Source: {image_path}")
        if card.raw_text:
            typer.echo(f"Raw OCR: {card.raw_text}")

    if save:
        init_db()
        with get_session() as session:
            repo = CardRepository(session)
            db_card = repo.add(card)
            typer.echo(f"\nSaved to database with ID {db_card.id}")


def parse_mana_cost(mana_str: str) -> ManaCost:
    white = mana_str.count("W")
    blue = mana_str.count("U")
    black = mana_str.count("B")
    red = mana_str.count("R")
    green = mana_str.count("G")
    colorless = mana_str.count("C")

    # Extract generic mana (numbers)
    generic = 0
    num_str = ""
    for char in mana_str:
        if char.isdigit():
            num_str += char
        elif num_str:
            generic += int(num_str)
            num_str = ""
    if num_str:
        generic += int(num_str)

    return ManaCost(
        white=white,
        blue=blue,
        black=black,
        red=red,
        green=green,
        colorless=colorless,
        generic=generic,
    )


@db_app.command("init")
def db_init():
    """Initialize the database."""
    init_db()
    typer.echo(f"Database initialized at {DATABASE_PATH}")


@db_app.command("sync-decks")
def db_sync_decks(
    force: bool = typer.Option(False, "--force", "-f", help="Force sync even if up to date"),
):
    """Sync deck data from mtgjson using new Deck DB structure."""
    try:
        update_decks(force=force)
        typer.echo("Deck sync complete.")
    except Exception as e:
        typer.echo(f"Error during deck sync: {e}")
        raise typer.Exit(1)


@db_app.command("sync")
def db_sync(
    force: bool = typer.Option(False, "--force", "-f", help="Force sync even if up to date"),
):
    """Sync reference data from mtgjson using new reference DB structure."""
    try:
        update_references(force=force)
        typer.echo("Sync complete.")
    except Exception as e:
        typer.echo(f"Error during sync: {e}")
        raise typer.Exit(1)


@db_app.command("add")
def db_add(
    name: str = typer.Argument(..., help="Card name"),
    types: str = typer.Option(..., "--types", "-t", help="Card types (comma-separated)"),
    oracle: str = typer.Option("", "--oracle", "-o", help="Oracle text"),
    supertypes: str | None = typer.Option(None, "--supertypes", "-s", help="Supertypes (comma-separated)"),
    subtypes: str | None = typer.Option(None, "--subtypes", help="Subtypes (comma-separated)"),
    mana: str | None = typer.Option(None, "--mana", "-m", help="Mana cost"),
    power: int | None = typer.Option(None, "--power", "-p", help="Power"),
    toughness: int | None = typer.Option(None, "--toughness", help="Toughness"),
    loyalty: int | None = typer.Option(None, "--loyalty", help="Loyalty"),
    defense: int | None = typer.Option(None, "--defense", help="Defense"),
    rarity: str = typer.Option("common", "--rarity", "-r", help="Rarity"),
    set_code: str | None = typer.Option(None, "--set", help="Set code (e.g., 'MH3')"),
    set_name: str | None = typer.Option(None, "--set-name", help="Set name"),
    collector_number: str | None = typer.Option(None, "--collector", help="Collector number"),
    owned: bool = typer.Option(False, "--owned", help="Mark as owned"),
    quantity: int = typer.Option(1, "--quantity", "-q", help="Quantity owned"),
    wanted: bool = typer.Option(False, "--wanted", help="Mark as wanted"),
    foil: bool = typer.Option(False, "--foil", help="Mark as foil"),
):
    """Add a card to the database."""
    init_db()
    mana_cost = parse_mana_cost(mana) if mana else None

    c = Card(
        name=name,
        card_types=parse_card_types(types),
        supertypes=parse_supertypes(supertypes),
        subtypes=parse_subtypes(subtypes),
        mana_cost=mana_cost,
        oracle_text=oracle,
        power=power,
        toughness=toughness,
        loyalty=loyalty,
        defense=defense,
        rarity=Rarity(rarity),
    )

    with get_session() as session:
        repo = CardRepository(session)
        db_card = repo.add(
            c,
            set_code=set_code,
            set_name=set_name,
            collector_number=collector_number,
            is_owned=owned,
            quantity_owned=quantity if owned else 0,
            is_wanted=wanted,
            is_foil=foil,
        )
        typer.echo(f"Added card '{db_card.name}' with ID {db_card.id}")


@db_app.command("list")
def db_list(
    owned: bool = typer.Option(False, "--owned", help="Show only owned cards"),
    wanted: bool = typer.Option(False, "--wanted", help="Show only wanted cards"),
    set_code: str | None = typer.Option(None, "--set", help="Filter by set code"),
):
    """List cards in the database."""
    init_db()
    with get_session() as session:
        repo = CardRepository(session)
        if owned:
            cards = repo.get_owned()
        elif wanted:
            cards = repo.get_wanted()
        elif set_code:
            cards = repo.get_by_set(set_code)
        else:
            cards = repo.all()

        if not cards:
            typer.echo("No cards found.")
            return

        for db_card in cards:
            status = []
            if db_card.is_owned:
                status.append(f"owned:{db_card.quantity_owned}")
            if db_card.is_wanted:
                status.append("wanted")
            if db_card.is_foil:
                status.append("foil")
            status_str = f" [{', '.join(status)}]" if status else ""
            set_str = f" ({db_card.set_code})" if db_card.set_code else ""
            typer.echo(f"{db_card.id}: {db_card.name}{set_str}{status_str}")


@db_app.command("show")
def db_show(
    card_id: int = typer.Argument(..., help="Card ID"),
):
    """Show a card from the database as ASCII art."""
    init_db()
    with get_session() as session:
        repo = CardRepository(session)
        db_card = repo.get_by_id(card_id)
        if not db_card:
            typer.echo(f"Card with ID {card_id} not found.")
            raise typer.Exit(1)

        card = db_to_card(db_card)
        typer.echo(render_card(card))
        typer.echo()
        if db_card.set_code:
            typer.echo(f"Set: {db_card.set_name or db_card.set_code} ({db_card.set_code})")
        if db_card.collector_number:
            typer.echo(f"Collector #: {db_card.collector_number}")
        if db_card.is_owned:
            typer.echo(f"Owned: {db_card.quantity_owned}x" + (" (foil)" if db_card.is_foil else ""))
        if db_card.is_wanted:
            typer.echo("Wanted: Yes")


@db_app.command("search")
def db_search(
    query: str = typer.Argument(..., help="Search query (partial name match)"),
):
    """Search for cards by name."""
    init_db()
    with get_session() as session:
        repo = CardRepository(session)
        cards = repo.search_by_name(query)
        if not cards:
            typer.echo(f"No cards found matching '{query}'.")
            return

        for db_card in cards:
            set_str = f" ({db_card.set_code})" if db_card.set_code else ""
            typer.echo(f"{db_card.id}: {db_card.name}{set_str}")


@db_app.command("own")
def db_own(
    card_id: int = typer.Argument(..., help="Card ID"),
    quantity: int = typer.Option(1, "--quantity", "-q", help="Quantity owned"),
    remove: bool = typer.Option(False, "--remove", help="Remove from owned"),
):
    """Mark a card as owned."""
    init_db()
    with get_session() as session:
        repo = CardRepository(session)
        db_card = repo.set_owned(card_id, owned=not remove, quantity=quantity)
        if db_card:
            if remove:
                typer.echo(f"Removed '{db_card.name}' from owned cards.")
            else:
                typer.echo(f"Marked '{db_card.name}' as owned (x{quantity}).")
        else:
            typer.echo(f"Card with ID {card_id} not found.")


@db_app.command("want")
def db_want(
    card_id: int = typer.Argument(..., help="Card ID"),
    remove: bool = typer.Option(False, "--remove", help="Remove from wanted"),
):
    """Mark a card as wanted."""
    init_db()
    with get_session() as session:
        repo = CardRepository(session)
        db_card = repo.set_wanted(card_id, wanted=not remove)
        if db_card:
            if remove:
                typer.echo(f"Removed '{db_card.name}' from wanted cards.")
            else:
                typer.echo(f"Marked '{db_card.name}' as wanted.")
        else:
            typer.echo(f"Card with ID {card_id} not found.")


@db_app.command("delete")
def db_delete(
    card_id: int = typer.Argument(..., help="Card ID"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
):
    """Delete a card from the database."""
    init_db()
    with get_session() as session:
        repo = CardRepository(session)
        db_card = repo.get_by_id(card_id)
        if not db_card:
            typer.echo(f"Card with ID {card_id} not found.")
            raise typer.Exit(1)

        if not force:
            confirm = typer.confirm(f"Delete '{db_card.name}'?")
            if not confirm:
                typer.echo("Cancelled.")
                raise typer.Exit(0)

        repo.delete(card_id)
        typer.echo(f"Deleted '{db_card.name}'.")


def main():
    app()


if __name__ == "__main__":
    main()

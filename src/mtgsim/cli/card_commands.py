from pathlib import Path

import typer

from ..db.session import get_session, init_db
from ..domain.card import Card, CardType, ManaCost, Rarity, Supertype
from ..extract.pipelines import get_pipeline
from ..render.ascii import render_card
from ..repository.card_repository import CardRepository

card_app = typer.Typer(help="Card-related operations")


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


@typer.Typer().command()
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


@typer.Typer().command()
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
    card_data = extractor.extract(image_path)

    if output == "json":
        typer.echo(card_data.model_dump_json(indent=2))
    else:
        typer.echo(render_card(card_data))
        typer.echo()
        typer.echo(f"Source: {image_path}")
        if card_data.raw_text:
            typer.echo(f"Raw OCR: {card_data.raw_text}")

    if save:
        init_db()
        with get_session() as session:
            repo = CardRepository(session)
            db_card = repo.add(card_data)
            typer.echo(f"\nSaved to database with ID {db_card.id}")

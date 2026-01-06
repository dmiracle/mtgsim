from pathlib import Path

import typer

from ..db.session import DATABASE_PATH, get_session, init_db
from ..db.set_models import ALL_SETS_DB_PATH
from ..domain.card import Card, Rarity
from ..repository.card_repository import CardRepository, db_to_card
from ..sync.mtgjson import update_decks, update_references, update_sets

db_app = typer.Typer(help="Database operations")


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


@db_app.command("sync-sets")
def db_sync_sets(
    set_files_dir: Path = typer.Option(None, "--dir", "-d", help="Path to AllSetFiles directory"),
):
    """Sync set data from AllSetFiles JSON to SQLite database.

    This creates a reference database at ~/.mtgsim/reference/mtgjson/AllSets.sqlite
    from the AllSetFiles JSON files. This is faster for querying than loading JSON.

    By default, looks for AllSetFiles in the resources directory.
    """
    try:
        update_sets(set_files_dir)
        typer.echo(f"Sets database created at {ALL_SETS_DB_PATH}")
    except Exception as e:
        typer.echo(f"Error during set sync: {e}")
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
    from .card_commands import parse_card_types, parse_mana_cost, parse_subtypes, parse_supertypes

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
    from ..render.ascii import render_card

    init_db()
    with get_session() as session:
        repo = CardRepository(session)
        db_card = repo.get_by_id(card_id)
        if not db_card:
            typer.echo(f"Card with ID {card_id} not found.")
            raise typer.Exit(1)

        card_data = db_to_card(db_card)
        typer.echo(render_card(card_data))
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

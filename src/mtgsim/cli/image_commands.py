"""Card image download commands."""

import re
import time
from pathlib import Path

import httpx
import typer

images_app = typer.Typer(help="Card image downloads")

PNG_URL = "https://cards.scryfall.io/png/{face}/{a}/{b}/{scryfall_id}.png?v=1"

# Layouts whose b-side is a physical back face with its own image. Other multi-face
# layouts (split, adventure, flip, aftermath) print both faces on the front image.
BACK_FACE_LAYOUTS = {"transform", "modal_dfc", "meld", "reversible_card", "double_faced_token"}


def image_filename(name: str, set_code: str, number: str | None, side: str | None) -> str:
    safe_name = re.sub(r'[<>:"/\\|?*]', "_", name)
    suffix = f"-{side}" if side else ""
    return f"{safe_name} ({set_code}) {number or 'x'}{suffix}.png"


@images_app.command("fetch")
def fetch_images(
    names: list[str] = typer.Argument(None, help="Card names (case-insensitive)"),
    set_code: str = typer.Option(None, "--set", "-s", help="Limit to a set code; with no names, fetch the whole set"),
    all_printings: bool = typer.Option(False, "--all-printings", "-a", help="Every printing, not just the generic one"),
    out: Path = typer.Option(Path("card-images"), "--out", "-o", help="Output directory"),
):
    """Download card PNGs (745x1040, transparent corners) from Scryfall."""
    from mtgdb import get_session
    from mtgdb.models import MJCard, MJCardIdentifier
    from sqlmodel import func, or_, select

    if not names and not set_code:
        typer.echo("Provide card names or --set.")
        raise typer.Exit(1)

    with get_session() as session:
        query = (
            select(MJCard, MJCardIdentifier.scryfall_id)
            .join(MJCardIdentifier, MJCard.uuid == MJCardIdentifier.card_uuid)
            .where(MJCardIdentifier.scryfall_id.is_not(None))
        )
        if set_code:
            query = query.where(MJCard.set_code == set_code.upper())
        if names:
            # Match full names and single faces of "A // B" cards
            conditions = []
            for n in (n.lower() for n in names):
                conditions.append(func.lower(MJCard.name) == n)
                conditions.append(func.lower(MJCard.name).like(f"{n} //%"))
                conditions.append(func.lower(MJCard.name).like(f"%// {n}"))
            query = query.where(or_(*conditions))
        rows = session.exec(query.order_by(MJCard.name, MJCard.set_code, MJCard.number, MJCard.side)).all()

    if not rows:
        typer.echo("No matching cards found.")
        raise typer.Exit(1)

    if not all_printings:
        # One printing per name: the generic printing when flagged, else the first.
        # Multi-face printings keep all their rows (side a/b) so both faces download.
        by_name: dict[str, list] = {}
        for card, scryfall_id in rows:
            by_name.setdefault(card.name, []).append((card, scryfall_id))
        picked = []
        for printings in by_name.values():
            chosen_set = next(
                ((c.set_code, c.number) for c, _ in printings if c.is_default_printing),
                (printings[0][0].set_code, printings[0][0].number),
            )
            picked.extend(p for p in printings if (p[0].set_code, p[0].number) == chosen_set)
        rows = picked

    rows = [(c, sid) for c, sid in rows if not (c.side and c.side != "a" and c.layout not in BACK_FACE_LAYOUTS)]

    out.mkdir(parents=True, exist_ok=True)
    fetched = skipped = failed = 0
    for card, scryfall_id in rows:
        side = card.side if card.layout in BACK_FACE_LAYOUTS else None
        dest = out / image_filename(card.name, card.set_code, card.number, side)
        if dest.exists():
            skipped += 1
            continue
        url = PNG_URL.format(
            face="back" if side and side != "a" else "front",
            a=scryfall_id[0],
            b=scryfall_id[1],
            scryfall_id=scryfall_id,
        )
        response = httpx.get(url, headers={"User-Agent": "mtgsim/1.0", "Accept": "image/png"})
        if response.status_code != 200:
            typer.echo(f"  ✗ {card.name} ({card.set_code} {card.number}): HTTP {response.status_code}")
            failed += 1
            continue
        dest.write_bytes(response.content)
        typer.echo(f"  ✓ {dest.name}")
        fetched += 1
        time.sleep(0.1)

    typer.echo(f"{fetched} downloaded, {skipped} already present, {failed} failed -> {out}")
    if failed:
        raise typer.Exit(1)

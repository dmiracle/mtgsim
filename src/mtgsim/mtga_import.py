"""MTGA collection CSV importer.

Reads an MTG Arena collection export CSV and upserts cards into the
user_card table with quantity_owned_mtga / quantity_owned_mtga_foil.

CSV format (MTGA export):
    Id,Name,Set,Color,Rarity,Count,PrintCount
    9135,"Mind Stone",HA1,Colorless,Common,1,1
"""

import csv
import logging
from pathlib import Path

from mtgdb.models import MJCard, UserCard
from mtgdb.session import get_session
from pydantic import BaseModel
from sqlmodel import select

logger = logging.getLogger("mtgsim.mtga_import")


class MTGAImportResult(BaseModel):
    total_rows: int = 0
    matched: int = 0
    unmatched: int = 0
    skipped_zero: int = 0
    cards_created: int = 0
    cards_updated: int = 0
    unmatched_cards: list[dict] = []


def parse_mtga_csv(csv_path: Path) -> list[dict]:
    """Parse MTGA collection CSV into a list of card dicts."""
    cards = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            count = int(row.get("Count", 0))
            print_count = int(row.get("PrintCount", 0))
            if count == 0 and print_count == 0:
                continue
            cards.append(
                {
                    "arena_id": row.get("Id", ""),
                    "name": row.get("Name", "").strip('" '),
                    "set_code": row.get("Set", ""),
                    "color": row.get("Color", ""),
                    "rarity": row.get("Rarity", "").lower(),
                    "count": count,
                    "print_count": print_count,
                }
            )
    return cards


def _resolve_card(session, name: str, set_code: str) -> str | None:
    """Find a card UUID by name + set code, falling back to name only."""
    # Exact match on name + set
    uuid = session.exec(select(MJCard.uuid).where(MJCard.name == name, MJCard.set_code == set_code)).first()
    if uuid:
        return uuid

    # Try printed_name + set
    uuid = session.exec(select(MJCard.uuid).where(MJCard.printed_name == name, MJCard.set_code == set_code)).first()
    if uuid:
        return uuid

    # Fall back to name only (any set)
    uuid = session.exec(select(MJCard.uuid).where(MJCard.name == name)).first()
    if uuid:
        return uuid

    # Fall back to printed_name only
    uuid = session.exec(select(MJCard.uuid).where(MJCard.printed_name == name)).first()
    return uuid


def import_mtga_collection(csv_path: Path) -> MTGAImportResult:
    """Import an MTGA collection CSV, upserting into user_card with MTGA quantities."""
    parsed = parse_mtga_csv(csv_path)
    result = MTGAImportResult(total_rows=len(parsed))

    with get_session() as session:
        for card in parsed:
            if card["count"] == 0 and card["print_count"] == 0:
                result.skipped_zero += 1
                continue

            uuid = _resolve_card(session, card["name"], card["set_code"])
            if not uuid:
                result.unmatched += 1
                result.unmatched_cards.append({"name": card["name"], "set_code": card["set_code"]})
                continue

            result.matched += 1

            # Upsert UserCard
            user_card = session.exec(select(UserCard).where(UserCard.card_uuid == uuid)).first()
            if user_card:
                user_card.quantity_owned_mtga = card["count"]
                user_card.quantity_owned_mtga_foil = card["print_count"]
                session.add(user_card)
                result.cards_updated += 1
            else:
                session.add(
                    UserCard(
                        card_uuid=uuid,
                        quantity_owned_mtga=card["count"],
                        quantity_owned_mtga_foil=card["print_count"],
                    )
                )
                result.cards_created += 1

        session.commit()

    logger.info(
        f"MTGA import: {result.matched} matched, {result.unmatched} unmatched, "
        f"{result.cards_created} created, {result.cards_updated} updated"
    )
    return result

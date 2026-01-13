"""Table sync functions - transform MTGJSON data into mj_* tables."""

import json
import logging
import sqlite3
import uuid as uuid_lib
from datetime import datetime
from pathlib import Path

from sqlmodel import Session, delete

from mtgdb.models import (
    MJCard,
    MJCardIdentifier,
    MJCardLegality,
    MJCardPrice,
    MJDeck,
    MJDeckCard,
    MJKeyword,
    MJSet,
)
from mtgdb.session import get_engine

logger = logging.getLogger(__name__)

BATCH_SIZE = 10000


def _parse_json_array(value) -> list:
    """Parse a JSON array string, or return empty list."""
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, str):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return []
    return []


def _connect(db_path: Path):
    """Create a sqlite3 connection with Row factory."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


# =============================================================================
# Sets
# =============================================================================


def sync_sets(source_db: Path):
    """Sync sets table from AllPrintings.sqlite to mj_set."""
    logger.info("Syncing sets...")
    conn = _connect(source_db)
    engine = get_engine()

    with Session(engine) as session:
        session.exec(delete(MJSet))
        session.commit()

        cursor = conn.execute("""
            SELECT code, name, type, releaseDate, baseSetSize, totalSetSize,
                   block, parentCode, keyruneCode,
                   isFoilOnly, isOnlineOnly, isPartialPreview
            FROM sets
        """)

        count = 0
        for row in cursor:
            session.add(
                MJSet(
                    code=row["code"],
                    name=row["name"],
                    type=row["type"],
                    release_date=row["releaseDate"],
                    base_set_size=row["baseSetSize"] or 0,
                    total_set_size=row["totalSetSize"] or 0,
                    block=row["block"],
                    parent_code=row["parentCode"],
                    keyrune_code=row["keyruneCode"],
                    is_foil_only=bool(row["isFoilOnly"]),
                    is_online_only=bool(row["isOnlineOnly"]),
                    is_partial_preview=bool(row["isPartialPreview"]),
                )
            )
            count += 1

        session.commit()

    conn.close()
    logger.info(f"Synced {count} sets")


# =============================================================================
# Cards
# =============================================================================


def sync_cards(source_db: Path):
    """Sync cards, identifiers, and legalities from AllPrintings.sqlite."""
    conn = _connect(source_db)
    engine = get_engine()

    _sync_cards_table(conn, engine)
    _sync_identifiers(conn, engine)
    _sync_legalities(conn, engine)

    conn.close()


def _sync_cards_table(conn, engine):
    """Sync main cards table."""
    logger.info("Syncing cards...")

    with Session(engine) as session:
        session.exec(delete(MJCardLegality))
        session.exec(delete(MJCardIdentifier))
        session.exec(delete(MJCard))
        session.commit()

        cursor = conn.execute("""
            SELECT uuid, name, setCode, manaCost, manaValue, type, text,
                   power, toughness, loyalty, defense, rarity, number, artist,
                   layout, borderColor, frameVersion, flavorText,
                   colors, colorIdentity, types, subtypes, supertypes, keywords,
                   hasFoil, hasNonFoil, isReprint, isReserved, isPromo
            FROM cards
        """)

        count = 0
        for row in cursor:
            session.add(
                MJCard(
                    uuid=row["uuid"],
                    name=row["name"],
                    set_code=row["setCode"],
                    mana_cost=row["manaCost"],
                    mana_value=row["manaValue"],
                    type_line=row["type"],
                    oracle_text=row["text"],
                    power=row["power"],
                    toughness=row["toughness"],
                    loyalty=row["loyalty"],
                    defense=row["defense"],
                    rarity=row["rarity"],
                    number=row["number"],
                    artist=row["artist"],
                    layout=row["layout"],
                    border_color=row["borderColor"],
                    frame_version=row["frameVersion"],
                    flavor_text=row["flavorText"],
                    colors=_parse_json_array(row["colors"]),
                    color_identity=_parse_json_array(row["colorIdentity"]),
                    types=_parse_json_array(row["types"]),
                    subtypes=_parse_json_array(row["subtypes"]),
                    supertypes=_parse_json_array(row["supertypes"]),
                    keywords=_parse_json_array(row["keywords"]),
                    has_foil=bool(row["hasFoil"]),
                    has_non_foil=bool(row["hasNonFoil"]),
                    is_reprint=bool(row["isReprint"]),
                    is_reserved=bool(row["isReserved"]),
                    is_promo=bool(row["isPromo"]),
                )
            )
            count += 1

            if count % BATCH_SIZE == 0:
                session.commit()
                logger.info(f"  {count} cards...")

        session.commit()

    logger.info(f"Synced {count} cards")


def _sync_identifiers(conn, engine):
    """Sync card identifiers (Scryfall, TCGPlayer, etc.)."""
    logger.info("Syncing card identifiers...")

    cursor = conn.execute("""
        SELECT uuid, scryfallId, scryfallOracleId, scryfallIllustrationId,
               tcgplayerProductId, tcgplayerEtchedProductId,
               mcmId, mtgoId, mtgoFoilId, mtgjsonV4Id, multiverseId
        FROM cardIdentifiers
    """)

    with Session(engine) as session:
        count = 0
        for row in cursor:
            session.add(
                MJCardIdentifier(
                    card_uuid=row["uuid"],
                    scryfall_id=row["scryfallId"],
                    scryfall_oracle_id=row["scryfallOracleId"],
                    scryfall_illustration_id=row["scryfallIllustrationId"],
                    tcgplayer_product_id=row["tcgplayerProductId"],
                    tcgplayer_etched_product_id=row["tcgplayerEtchedProductId"],
                    cardmarket_id=row["mcmId"],
                    mtgo_id=row["mtgoId"],
                    mtgo_foil_id=row["mtgoFoilId"],
                    mtgjson_v4_id=row["mtgjsonV4Id"],
                    multiverse_id=row["multiverseId"],
                )
            )
            count += 1

            if count % BATCH_SIZE == 0:
                session.commit()
                logger.info(f"  {count} identifiers...")

        session.commit()

    logger.info(f"Synced {count} identifiers")


def _sync_legalities(conn, engine):
    """Sync card format legalities."""
    logger.info("Syncing card legalities...")

    # Get format columns dynamically
    cursor = conn.execute("PRAGMA table_info(cardLegalities)")
    format_columns = [row[1] for row in cursor if row[1] != "uuid"]

    cursor = conn.execute("SELECT * FROM cardLegalities")

    with Session(engine) as session:
        count = 0
        for row in cursor:
            card_uuid = row["uuid"]
            for format_name in format_columns:
                status = row[format_name]
                if status:
                    session.add(
                        MJCardLegality(
                            card_uuid=card_uuid,
                            format=format_name,
                            status=status,
                        )
                    )
                    count += 1

            if count % 50000 == 0:
                session.commit()
                logger.info(f"  {count} legalities...")

        session.commit()

    logger.info(f"Synced {count} legalities")


# =============================================================================
# Prices
# =============================================================================


def sync_prices(source_db: Path):
    """Sync prices from AllPricesToday.sqlite to mj_card_price."""
    logger.info("Syncing prices...")
    conn = _connect(source_db)
    engine = get_engine()

    with Session(engine) as session:
        session.exec(delete(MJCardPrice))
        session.commit()

        cursor = conn.execute("""
            SELECT uuid, priceProvider, providerListing, cardFinish, currency, date, price
            FROM cardPrices
            WHERE price IS NOT NULL
        """)

        count = 0
        for row in cursor:
            try:
                session.add(
                    MJCardPrice(
                        card_uuid=row["uuid"],
                        provider=row["priceProvider"],
                        listing_type=row["providerListing"],
                        finish=row["cardFinish"],
                        currency=row["currency"] or "USD",
                        price=float(row["price"]),
                        updated_at=datetime.fromisoformat(row["date"]) if row["date"] else None,
                    )
                )
                count += 1
            except (ValueError, TypeError):
                continue

            if count % 50000 == 0:
                session.commit()
                logger.info(f"  {count} prices...")

        session.commit()

    conn.close()
    logger.info(f"Synced {count} prices")


# =============================================================================
# Decks
# =============================================================================


def sync_decks(deck_dir: Path):
    """Sync preconstructed decks from AllDeckFiles directory."""
    logger.info("Syncing decks...")

    if not deck_dir.exists():
        logger.warning(f"Deck directory not found: {deck_dir}")
        return

    files = list(deck_dir.glob("*.json"))
    engine = get_engine()

    with Session(engine) as session:
        session.exec(delete(MJDeckCard))
        session.exec(delete(MJDeck))
        session.commit()

        for i, file_path in enumerate(files):
            _sync_deck_file(session, file_path)

            if (i + 1) % 100 == 0:
                session.commit()
                logger.info(f"  {i + 1}/{len(files)} decks...")

        session.commit()

    logger.info(f"Synced {len(files)} decks")


def _sync_deck_file(session: Session, file_path: Path):
    """Sync a single deck JSON file."""
    try:
        with open(file_path) as f:
            content = json.load(f)

        data = content.get("data", {})
        file_name = file_path.stem

        # Create deck
        deck = MJDeck(
            uuid=str(uuid_lib.uuid4()),
            file_name=file_name,
            name=data.get("name", file_name),
            code=data.get("code", ""),
            type=data.get("type"),
            release_date=data.get("releaseDate"),
            main_board_count=sum(c.get("count", 1) for c in data.get("mainBoard", [])),
            side_board_count=sum(c.get("count", 1) for c in data.get("sideBoard", [])),
            commander_count=sum(c.get("count", 1) for c in data.get("commander", [])),
        )
        session.add(deck)

        # Create deck cards
        for board in ["mainBoard", "sideBoard", "commander"]:
            for card in data.get(board, []):
                session.add(
                    MJDeckCard(
                        deck_uuid=deck.uuid,
                        card_uuid=card.get("uuid"),
                        name=card.get("name", ""),
                        board=board,
                        count=card.get("count", 1),
                        mana_cost=card.get("manaCost"),
                        mana_value=card.get("manaValue"),
                        colors=card.get("colors", []),
                        types=card.get("types", []),
                    )
                )

    except Exception as e:
        logger.warning(f"Error processing {file_path.name}: {e}")


# =============================================================================
# Keywords
# =============================================================================


def sync_keywords(keywords_file: Path):
    """Sync keywords from Keywords.json to mj_keyword."""
    logger.info("Syncing keywords...")

    if not keywords_file.exists():
        logger.warning(f"Keywords file not found: {keywords_file}")
        return

    with open(keywords_file) as f:
        content = json.load(f)

    data = content.get("data", {})
    engine = get_engine()

    with Session(engine) as session:
        session.exec(delete(MJKeyword))
        session.commit()

        count = 0
        for keyword_type, keywords in data.items():
            for keyword in keywords:
                session.add(MJKeyword(name=keyword, type=keyword_type))
                count += 1

        session.commit()

    logger.info(f"Synced {count} keywords")

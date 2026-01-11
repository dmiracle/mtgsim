"""Unified sync pipeline - writes to mj_* tables in unified database."""

import json
import logging
import uuid as uuid_lib
from datetime import datetime
from pathlib import Path

from sqlmodel import Session, delete

from mtgsim.config import ALL_DECK_FILES_DIR, DB_PATH, MTGJSON_DIR, MTGSIM_HOME
from mtgsim.db.models import (
    MJCard,
    MJCardIdentifier,
    MJCardLegality,
    MJCardPrice,
    MJDeck,
    MJDeckCard,
    MJSet,
)
from mtgsim.db.session import get_engine, init_db

logger = logging.getLogger(__name__)


def _parse_json_or_list(value) -> list:
    """Parse a JSON string or return list as-is."""
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


def sync_all(force: bool = False):
    """Run full sync to unified database.

    1. Download MTGJSON files if needed
    2. Sync sets from AllPrintings
    3. Sync cards from AllPrintings
    4. Sync prices from AllPricesToday
    5. Sync decks from AllDeckFiles
    """
    from mtgsim.config import ALL_DECK_FILES_URL, ALL_PRICES_URL, ALL_PRINTINGS_URL, ensure_dirs

    from .mtgjson import download_and_extract, download_file, extract_tar_xz, should_update

    ensure_dirs()
    init_db()

    # Download AllPrintings
    printings_db = MTGJSON_DIR / "AllPrintings.sqlite"
    if not download_and_extract(ALL_PRINTINGS_URL, printings_db, force):
        logger.error("Failed to download AllPrintings")
        return False

    # Download AllPricesToday
    prices_db = MTGJSON_DIR / "AllPricesToday.sqlite"
    if not download_and_extract(ALL_PRICES_URL, prices_db, force):
        logger.warning("Failed to download AllPricesToday, continuing without prices")

    # Download AllDeckFiles
    all_decks_tar = MTGJSON_DIR / "AllDeckFiles.tar.xz"
    if should_update(ALL_DECK_FILES_DIR, force):
        if download_file(ALL_DECK_FILES_URL, all_decks_tar):
            extract_tar_xz(all_decks_tar, MTGJSON_DIR)
            all_decks_tar.unlink(missing_ok=True)

    # Sync in order
    sync_sets(printings_db)
    sync_cards(printings_db)

    if prices_db.exists():
        sync_prices(prices_db)

    if ALL_DECK_FILES_DIR.exists():
        sync_decks(ALL_DECK_FILES_DIR)

    # Compute corpus word frequencies for wordcloud baseline
    compute_corpus_wordfreq()

    logger.info(f"Unified sync complete. Data in {DB_PATH}")
    return True


def sync_sets(source_db: Path):
    """Sync sets from AllPrintings.sqlite to mj_set."""
    import sqlite3

    logger.info("Syncing sets from AllPrintings...")

    conn = sqlite3.connect(source_db)
    conn.row_factory = sqlite3.Row

    engine = get_engine()

    with Session(engine) as session:
        # Clear existing
        session.exec(delete(MJSet))
        session.commit()

        cursor = conn.execute("""
            SELECT
                code, name, type, releaseDate, baseSetSize, totalSetSize,
                block, parentCode, keyruneCode,
                isFoilOnly, isOnlineOnly, isPartialPreview
            FROM sets
        """)

        count = 0
        for row in cursor:
            set_obj = MJSet(
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
            session.add(set_obj)
            count += 1

        session.commit()
        logger.info(f"Synced {count} sets")

    conn.close()


def sync_cards(source_db: Path):
    """Sync cards from AllPrintings.sqlite to unified database."""
    import sqlite3

    logger.info("Syncing cards from AllPrintings...")

    conn = sqlite3.connect(source_db)
    conn.row_factory = sqlite3.Row

    engine = get_engine()

    with Session(engine) as session:
        # Clear existing data
        session.exec(delete(MJCardLegality))
        session.exec(delete(MJCardIdentifier))
        session.exec(delete(MJCard))
        session.commit()

        # Query cards table from AllPrintings
        cursor = conn.execute("""
            SELECT
                uuid, name, setCode, manaCost, manaValue, type, text,
                power, toughness, loyalty, defense, rarity, number, artist,
                layout, borderColor, frameVersion,
                colors, colorIdentity, types, subtypes, supertypes, keywords,
                hasFoil, hasNonFoil, isReprint, isReserved, isPromo,
                flavorText
            FROM cards
        """)

        cards_added = 0
        for row in cursor:
            card = MJCard(
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
                colors=_parse_json_or_list(row["colors"]),
                color_identity=_parse_json_or_list(row["colorIdentity"]),
                types=_parse_json_or_list(row["types"]),
                subtypes=_parse_json_or_list(row["subtypes"]),
                supertypes=_parse_json_or_list(row["supertypes"]),
                keywords=_parse_json_or_list(row["keywords"]),
                has_foil=bool(row["hasFoil"]),
                has_non_foil=bool(row["hasNonFoil"]),
                is_reprint=bool(row["isReprint"]),
                is_reserved=bool(row["isReserved"]),
                is_promo=bool(row["isPromo"]),
            )
            session.add(card)
            cards_added += 1

            if cards_added % 10000 == 0:
                session.commit()
                logger.info(f"Synced {cards_added} cards...")

        session.commit()
        logger.info(f"Synced {cards_added} total cards")

    # Sync identifiers
    _sync_card_identifiers(conn, engine)

    # Sync legalities
    _sync_card_legalities(conn, engine)

    conn.close()


def _sync_card_identifiers(conn, engine):
    """Sync cardIdentifiers table to mj_card_identifier."""
    logger.info("Syncing card identifiers...")

    cursor = conn.execute("""
        SELECT
            uuid, scryfallId, scryfallOracleId, scryfallIllustrationId,
            tcgplayerProductId, tcgplayerEtchedProductId,
            mcmId, cardsphereId,
            mtgoId, mtgoFoilId, mtgjsonV4Id, multiverseId
        FROM cardIdentifiers
    """)

    with Session(engine) as session:
        count = 0
        for row in cursor:
            identifier = MJCardIdentifier(
                card_uuid=row["uuid"],
                scryfall_id=row["scryfallId"],
                scryfall_oracle_id=row["scryfallOracleId"],
                scryfall_illustration_id=row["scryfallIllustrationId"],
                tcgplayer_product_id=row["tcgplayerProductId"],
                tcgplayer_etched_product_id=row["tcgplayerEtchedProductId"],
                cardmarket_id=row["mcmId"],
                cardsphere_id=row["cardsphereId"],
                mtgo_id=row["mtgoId"],
                mtgo_foil_id=row["mtgoFoilId"],
                mtgjson_v4_id=row["mtgjsonV4Id"],
                multiverse_id=row["multiverseId"],
            )
            session.add(identifier)
            count += 1

            if count % 10000 == 0:
                session.commit()
                logger.info(f"Synced {count} identifiers...")

        session.commit()
        logger.info(f"Synced {count} card identifiers")


def _sync_card_legalities(conn, engine):
    """Sync cardLegalities table to mj_card_legality."""
    logger.info("Syncing card legalities...")

    # Get format columns (all columns except uuid)
    cursor = conn.execute("PRAGMA table_info(cardLegalities)")
    format_columns = [row[1] for row in cursor if row[1] != "uuid"]

    # Build query to get all legalities
    cursor = conn.execute("SELECT * FROM cardLegalities")

    with Session(engine) as session:
        count = 0
        for row in cursor:
            card_uuid = row["uuid"]
            for format_name in format_columns:
                status = row[format_name]
                if status:
                    legality = MJCardLegality(
                        card_uuid=card_uuid,
                        format=format_name,
                        status=status,
                    )
                    session.add(legality)
                    count += 1

            if count % 50000 == 0:
                session.commit()
                logger.info(f"Synced {count} legalities...")

        session.commit()
        logger.info(f"Synced {count} card legalities")


def sync_prices(source_db: Path):
    """Sync prices from AllPricesToday.sqlite to mj_card_price."""
    import sqlite3

    logger.info("Syncing prices from AllPricesToday...")

    conn = sqlite3.connect(source_db)
    conn.row_factory = sqlite3.Row

    engine = get_engine()

    with Session(engine) as session:
        # Clear existing
        session.exec(delete(MJCardPrice))
        session.commit()

        # cardPrices table structure:
        # uuid, priceProvider, providerListing, cardFinish, currency, date, price, gameAvailability
        cursor = conn.execute("""
            SELECT uuid, priceProvider, providerListing, cardFinish, currency, date, price
            FROM cardPrices
            WHERE price IS NOT NULL
        """)

        count = 0
        for row in cursor:
            try:
                price_obj = MJCardPrice(
                    card_uuid=row["uuid"],
                    provider=row["priceProvider"],
                    listing_type=row["providerListing"],
                    finish=row["cardFinish"],
                    currency=row["currency"] or "USD",
                    price=float(row["price"]),
                    updated_at=datetime.fromisoformat(row["date"]) if row["date"] else None,
                )
                session.add(price_obj)
                count += 1
            except (ValueError, TypeError):
                continue

            if count % 50000 == 0:
                session.commit()
                logger.info(f"Synced {count} price entries...")

        session.commit()
        logger.info(f"Synced {count} total price entries")

    conn.close()


def sync_decks(deck_dir: Path):
    """Sync decks from AllDeckFiles to mj_deck + mj_deck_card."""
    logger.info(f"Syncing decks from {deck_dir}...")

    if not deck_dir.exists():
        logger.warning(f"Deck directory not found: {deck_dir}")
        return

    files = list(deck_dir.glob("*.json"))
    logger.info(f"Found {len(files)} deck files")

    engine = get_engine()

    with Session(engine) as session:
        # Clear existing
        session.exec(delete(MJDeckCard))
        session.exec(delete(MJDeck))
        session.commit()

        for i, file_path in enumerate(files):
            if i % 100 == 0 and i > 0:
                logger.info(f"Processed {i}/{len(files)} decks")
                session.commit()

            _process_deck_file(session, file_path)

        session.commit()
        logger.info(f"Synced {len(files)} decks")


def _process_deck_file(session: Session, file_path: Path):
    """Process a single deck JSON file."""
    try:
        with open(file_path) as f:
            content = json.load(f)

        data = content.get("data", {})
        file_name = file_path.stem

        # Count cards in each board
        main_count = sum(c.get("count", 1) for c in data.get("mainBoard", []))
        side_count = sum(c.get("count", 1) for c in data.get("sideBoard", []))
        commander_count = sum(c.get("count", 1) for c in data.get("commander", []))

        deck = MJDeck(
            uuid=str(uuid_lib.uuid4()),
            file_name=file_name,
            name=data.get("name", file_name),
            code=data.get("code", ""),
            type=data.get("type"),
            release_date=data.get("releaseDate"),
            main_board_count=main_count,
            side_board_count=side_count,
            commander_count=commander_count,
        )
        session.add(deck)

        # Add cards from all boards
        for board_name in ["mainBoard", "sideBoard", "commander"]:
            for card_data in data.get(board_name, []):
                deck_card = MJDeckCard(
                    deck_uuid=deck.uuid,
                    card_uuid=card_data.get("uuid"),
                    name=card_data.get("name", ""),
                    board=board_name,
                    count=card_data.get("count", 1),
                    mana_cost=card_data.get("manaCost"),
                    mana_value=card_data.get("manaValue"),
                    colors=card_data.get("colors", []),
                    types=card_data.get("types", []),
                )
                session.add(deck_card)

    except Exception as e:
        logger.warning(f"Error processing {file_path.name}: {e}")


def compute_corpus_wordfreq():
    """Compute word frequencies from all card oracle text and save to JSON."""
    import re
    from collections import Counter

    from sqlmodel import select

    logger.info("Computing corpus word frequencies...")

    # Same stopwords as webapp
    stop_words = {
        "a", "an", "the", "and", "or", "but", "if", "then", "of", "to", "in", "on", "at", "for",
        "is", "it", "its", "this", "that", "with", "as", "be", "by", "from", "are", "was", "were",
        "you", "your", "may", "can", "has", "have", "do", "does", "each", "all", "any", "one",
        "two", "three", "four", "five", "up", "into", "when", "where", "until", "end", "turn",
        "would", "could", "they", "their", "them", "he", "she", "his", "her", "who", "which",
    }

    engine = get_engine()
    word_counts: Counter = Counter()
    total_words = 0

    with Session(engine) as session:
        stmt = select(MJCard.oracle_text)
        results = session.exec(stmt)

        for oracle_text in results:
            if not oracle_text:
                continue

            # Tokenize same as webapp
            text = oracle_text.lower()
            text = re.sub(r"[{}\(\)•—\-:;,.\"\\'!?]", " ", text)
            words = [
                w for w in text.split()
                if len(w) > 2 and w not in stop_words and not w.isdigit()
            ]
            word_counts.update(words)
            total_words += len(words)

    # Compute frequencies (count / total)
    word_freq = {word: count / total_words for word, count in word_counts.items()}

    # Save to JSON
    output_path = MTGSIM_HOME / "corpus_wordfreq.json"
    output_data = {
        "total_words": total_words,
        "unique_words": len(word_freq),
        "frequencies": word_freq,
    }

    with open(output_path, "w") as f:
        json.dump(output_data, f)

    logger.info(f"Saved corpus word frequencies: {len(word_freq)} unique words, {total_words} total words")

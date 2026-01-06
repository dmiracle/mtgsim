"""MTGJSON data synchronization with helpers and logging."""

import json
import logging
import lzma
import shutil
import sqlite3
import tarfile
import uuid
from pathlib import Path

import requests
from sqlmodel import Session, select

from mtgsim.config import (
    ALL_DECK_FILES_DIR,
    ALL_DECK_FILES_URL,
    ALL_PRICES_URL,
    ALL_PRINTINGS_URL,
    DECK_LIST_URL,
    KEYWORDS_URL,
    MERGED_DB_PATH,
    MTGJSON_DIR,
    ensure_dirs,
    get_resources_dir,
)
from mtgsim.db.deck_models import Deck, DeckCard, DeckList
from mtgsim.db.keyword_models import Keyword
from mtgsim.db.session import init_deck_db
from mtgsim.db.set_models import SetCardDB, SetDB, init_sets_db

logger = logging.getLogger(__name__)


def download_file(url: str, dest: Path) -> bool:
    """Download a file with progress indication."""
    logger.info(f"Downloading {url} to {dest}")
    try:
        with requests.get(url, stream=True, timeout=300) as r:
            r.raise_for_status()
            with open(dest, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        logger.info("Download complete")
        return True
    except requests.RequestException as e:
        logger.error(f"Download failed: {e}")
        return False


def extract_xz(source: Path, dest: Path) -> bool:
    """Extract an xz compressed file."""
    logger.info(f"Extracting {source} to {dest}")
    try:
        with lzma.open(source) as f_in:
            with open(dest, "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)
        logger.info("Extraction complete")
        return True
    except (lzma.LZMAError, OSError) as e:
        logger.error(f"Extraction failed: {e}")
        return False


def extract_tar_xz(source: Path, dest_dir: Path) -> bool:
    """Extract a tar.xz file."""
    logger.info(f"Extracting {source} to {dest_dir}")
    try:
        dest_dir.mkdir(parents=True, exist_ok=True)
        with tarfile.open(source, "r:xz") as tar:
            tar.extractall(path=dest_dir)
        logger.info("Extraction complete")
        return True
    except (tarfile.TarError, OSError) as e:
        logger.error(f"Extraction failed: {e}")
        return False


def should_update(dest: Path, force: bool = False) -> bool:
    """Check if a file should be updated."""
    if force:
        return True
    if not dest.exists():
        return True
    return False


def download_and_extract(url: str, dest: Path, force: bool = False) -> bool:
    """Download and extract an xz file if needed."""
    if not should_update(dest, force):
        logger.info(f"{dest.name} exists, skipping (use --force to update)")
        return True

    xz_path = dest.with_suffix(dest.suffix + ".xz")
    if not download_file(url, xz_path):
        return False

    if not extract_xz(xz_path, dest):
        return False

    xz_path.unlink(missing_ok=True)
    return True


def _init_merged_db():
    """Initialize the merged database if it doesn't exist."""
    ensure_dirs()
    if not MERGED_DB_PATH.exists():
        conn = sqlite3.connect(MERGED_DB_PATH)
        conn.close()
        logger.info(f"Created merged database at {MERGED_DB_PATH}")


def _copy_tables_from_source(source_db: Path, tables: list[str]):
    """Copy tables from a source database into the merged database."""
    if not source_db.exists():
        logger.error(f"Source database not found: {source_db}")
        return False

    _init_merged_db()

    conn = sqlite3.connect(MERGED_DB_PATH)
    try:
        # Attach the source database
        conn.execute(f"ATTACH DATABASE '{source_db}' AS source_db")

        for table in tables:
            # Check if table exists in source
            cursor = conn.execute(
                "SELECT name FROM source_db.sqlite_master WHERE type='table' AND name=?",
                [table],
            )
            if not cursor.fetchone():
                logger.warning(f"Table {table} not found in {source_db.name}")
                continue

            # Drop existing table in merged db if exists
            conn.execute(f"DROP TABLE IF EXISTS {table}")

            # Get the CREATE TABLE statement from source
            cursor = conn.execute(
                "SELECT sql FROM source_db.sqlite_master WHERE type='table' AND name=?",
                [table],
            )
            create_sql = cursor.fetchone()
            if create_sql and create_sql[0]:
                conn.execute(create_sql[0])
                logger.info(f"Created table {table}")

            # Copy data
            conn.execute(f"INSERT INTO {table} SELECT * FROM source_db.{table}")
            logger.info(f"Copied data to {table}")

        # Copy indexes
        cursor = conn.execute(
            "SELECT sql FROM source_db.sqlite_master WHERE type='index' AND sql IS NOT NULL"
        )
        for row in cursor.fetchall():
            if row[0]:
                try:
                    conn.execute(row[0])
                except sqlite3.OperationalError:
                    pass  # Index may already exist or reference non-existent table

        conn.commit()
        conn.execute("DETACH DATABASE source_db")
        logger.info(f"Successfully synced tables from {source_db.name}")
        return True

    except sqlite3.Error as e:
        logger.error(f"Database error: {e}")
        return False
    finally:
        conn.close()


def update_references(force: bool = False):
    """Download MTGJSON databases and sync tables into merged database."""
    ensure_dirs()

    # Download AllPrintings and sync its tables
    printings_temp = MTGJSON_DIR / "AllPrintings_temp.sqlite"
    if download_and_extract(ALL_PRINTINGS_URL, printings_temp, force):
        # AllPrintings contains: cards, sets, tokens, cardIdentifiers, etc.
        _copy_tables_from_source(
            printings_temp,
            ["cards", "sets", "tokens", "cardIdentifiers", "cardLegalities",
             "cardPurchaseUrls", "setTranslations", "meta"],
        )
        printings_temp.unlink(missing_ok=True)

    # Download AllPricesToday and sync its tables
    prices_temp = MTGJSON_DIR / "AllPricesToday_temp.sqlite"
    if download_and_extract(ALL_PRICES_URL, prices_temp, force):
        # AllPricesToday contains: cardPrices
        _copy_tables_from_source(prices_temp, ["cardPrices"])
        prices_temp.unlink(missing_ok=True)

    logger.info(f"Reference sync complete. Data stored in {MERGED_DB_PATH}")


def _get_merged_engine():
    """Get SQLModel engine for merged database."""
    from sqlmodel import create_engine
    _init_merged_db()
    return create_engine(f"sqlite:///{MERGED_DB_PATH}")


def _init_keywords_table(engine):
    """Initialize keywords table in merged database."""
    from sqlmodel import SQLModel
    SQLModel.metadata.create_all(engine, tables=[Keyword.__table__])


def update_keywords(force: bool = False):
    """Download and sync keywords data from MTGJSON."""
    ensure_dirs()

    keywords_json = MTGJSON_DIR / "Keywords.json"
    if not download_and_extract(KEYWORDS_URL, keywords_json, force):
        return

    engine = _get_merged_engine()
    _init_keywords_table(engine)

    with Session(engine) as session:
        logger.info("Populating keywords table")

        # Clear existing keywords
        existing = session.exec(select(Keyword)).all()
        for kw in existing:
            session.delete(kw)
        session.commit()

        # Load and insert new keywords
        with open(keywords_json) as f:
            content = json.load(f)
            data = content.get("data", {})

            keyword_types = ["abilityWords", "keywordAbilities", "keywordActions"]
            count = 0
            for kw_type in keyword_types:
                for keyword in data.get(kw_type, []):
                    session.add(Keyword(keyword=keyword, type=kw_type))
                    count += 1

        session.commit()
        logger.info(f"Populated {count} keywords")

    logger.info(f"Keywords sync complete. Data stored in {MERGED_DB_PATH}")


def update_decks(force: bool = False):
    """Sync deck data: DeckList.json -> DeckList table, AllDeckFiles -> Deck/DeckCard."""
    ensure_dirs()

    deck_list_json = MTGJSON_DIR / "DeckList.json"
    if not download_and_extract(DECK_LIST_URL, deck_list_json, force):
        return

    engine = init_deck_db()
    _populate_deck_list(engine, deck_list_json)

    all_decks_tar = MTGJSON_DIR / "AllDeckFiles.tar.xz"
    if should_update(ALL_DECK_FILES_DIR, force):
        if download_file(ALL_DECK_FILES_URL, all_decks_tar):
            extract_tar_xz(all_decks_tar, MTGJSON_DIR)
            all_decks_tar.unlink(missing_ok=True)

    if ALL_DECK_FILES_DIR.exists():
        process_deck_files(engine, ALL_DECK_FILES_DIR)

    logger.info(f"Deck sync complete. Data stored in {MERGED_DB_PATH}")


def _populate_deck_list(engine, deck_list_json: Path):
    """Populate DeckList table from JSON file."""
    with Session(engine) as session:
        logger.info("Populating DeckList table")
        with open(deck_list_json) as f:
            content = json.load(f)
            data = content.get("data", [])
            for item in data:
                deck_list = DeckList(
                    file_name=item.get("fileName"),
                    code=item.get("code"),
                    name=item.get("name"),
                    release_date=item.get("releaseDate"),
                    type=item.get("type"),
                )
                session.merge(deck_list)
        session.commit()
        logger.info("DeckList populated")


def process_deck_files(engine, deck_dir: Path):
    """Process all deck JSON files in the directory."""
    logger.info("Processing deck files")

    files = list(deck_dir.glob("*.json"))
    logger.info(f"Found {len(files)} deck files")

    with Session(engine) as session:
        for i, file_path in enumerate(files):
            if i % 100 == 0 and i > 0:
                logger.info(f"Processed {i}/{len(files)} decks")
                session.commit()

            _process_single_deck(session, file_path)

        session.commit()
    logger.info("Deck processing complete")


def _process_single_deck(session: Session, file_path: Path):
    """Process a single deck JSON file."""
    try:
        with open(file_path) as f:
            content = json.load(f)

        meta = content.get("meta", {})
        data = content.get("data", {})
        file_name = file_path.stem

        existing_deck = session.exec(select(Deck).where(Deck.file_name == file_name)).first()

        if existing_deck:
            deck_uuid = existing_deck.uuid
            deck = existing_deck
            _update_deck_from_data(deck, data, meta)
        else:
            deck_uuid = str(uuid.uuid4())
            deck = _create_deck_from_data(deck_uuid, file_name, data, meta)
            session.add(deck)

        # Delete existing cards and re-add
        cards_to_delete = session.exec(select(DeckCard).where(DeckCard.deck_uuid == deck_uuid)).all()
        for card in cards_to_delete:
            session.delete(card)

        _add_deck_cards(session, deck_uuid, data)

    except Exception as e:
        logger.warning(f"Error processing {file_path.name}: {e}")


def _update_deck_from_data(deck: Deck, data: dict, meta: dict):
    """Update existing deck with new data."""
    deck.code = data.get("code", "")
    deck.type = data.get("type")
    deck.release_date = data.get("releaseDate")
    deck.meta_json = meta
    deck.commander = data.get("commander", [])


def _create_deck_from_data(deck_uuid: str, file_name: str, data: dict, meta: dict) -> Deck:
    """Create a new Deck from data."""
    return Deck(
        uuid=deck_uuid,
        file_name=file_name,
        code=data.get("code", ""),
        name=file_name,
        type=data.get("type"),
        release_date=data.get("releaseDate"),
        meta_json=meta,
        commander=data.get("commander", []),
    )


def _add_deck_cards(session: Session, deck_uuid: str, data: dict):
    """Add cards from all boards to the deck."""
    boards = ["mainBoard", "sideBoard", "commander"]
    for board_name in boards:
        for card_data in data.get(board_name, []):
            deck_card = DeckCard(
                deck_uuid=deck_uuid,
                card_uuid=card_data.get("uuid"),
                board=board_name,
                count=card_data.get("count", 1),
                name=card_data.get("name", ""),
                mana_cost=card_data.get("manaCost"),
                mana_value=card_data.get("manaValue"),
                color_identity=card_data.get("colorIdentity", []),
                colors=card_data.get("colors", []),
                indicators=card_data.get("indicators", []),
                printings=card_data.get("printings", []),
                types=card_data.get("types", []),
                subtypes=card_data.get("subtypes", []),
                supertypes=card_data.get("supertypes", []),
                identifiers_json=card_data.get("identifiers", {}),
                legalities_json=card_data.get("legalities", {}),
                artist_ids_json=card_data.get("artistIds", []),
                availability_json=card_data.get("availability", []),
                finishes_json=card_data.get("finishes", []),
                foreign_data_json=card_data.get("foreignData", []),
                keywords_json=card_data.get("keywords", []),
                purchase_urls_json=card_data.get("purchaseUrls", {}),
                original_printings_json=card_data.get("originalPrintings", []),
                is_foil=card_data.get("isFoil", False),
                is_etched=card_data.get("isEtched", False),
                is_starter=card_data.get("isStarter", False),
                is_reprint=card_data.get("isReprint", False),
                has_foil=card_data.get("hasFoil", False),
                has_non_foil=card_data.get("hasNonFoil", False),
                layout=card_data.get("layout"),
                number=card_data.get("number"),
                original_text=card_data.get("originalText"),
                text=card_data.get("text"),
                original_release_date=card_data.get("originalReleaseDate"),
                power=card_data.get("power"),
                toughness=card_data.get("toughness"),
                loyalty=card_data.get("loyalty"),
                defense=card_data.get("defense"),
                rarity=card_data.get("rarity"),
                watermark=card_data.get("watermark"),
                artist=card_data.get("artist"),
                border_color=card_data.get("borderColor"),
                frame_version=card_data.get("frameVersion"),
                language=card_data.get("language"),
                signature=card_data.get("signature"),
                edhrec_rank=card_data.get("edhrecRank"),
                edhrec_saltiness=card_data.get("edhrecSaltiness"),
            )
            session.add(deck_card)


def update_sets(set_files_dir: Path | None = None):
    """Sync set data from AllSetFiles JSON to merged database."""
    if set_files_dir is None:
        set_files_dir = get_resources_dir() / "AllSetFiles"

    if not set_files_dir.exists():
        logger.error(f"AllSetFiles directory not found at {set_files_dir}")
        return

    engine = init_sets_db()
    process_set_files(engine, set_files_dir)
    logger.info(f"Set sync complete. Data stored in {MERGED_DB_PATH}")


def process_set_files(engine, set_dir: Path):
    """Process all set JSON files in the directory."""
    logger.info("Processing set files")

    files = list(set_dir.glob("*.json"))
    logger.info(f"Found {len(files)} set files")

    with Session(engine) as session:
        for i, file_path in enumerate(files):
            if i % 50 == 0 and i > 0:
                logger.info(f"Processed {i}/{len(files)} sets")
                session.commit()

            _process_single_set(session, file_path)

        session.commit()
    logger.info("Set processing complete")


def _process_single_set(session: Session, file_path: Path):
    """Process a single set JSON file."""
    try:
        with open(file_path) as f:
            content = json.load(f)

        data = content.get("data", {})
        set_code = data.get("code", file_path.stem)

        existing_set = session.exec(select(SetDB).where(SetDB.code == set_code)).first()

        if existing_set:
            _update_set_from_data(existing_set, data)
        else:
            set_db = _create_set_from_data(set_code, data)
            session.add(set_db)

        # Delete and re-add cards
        existing_cards = session.exec(select(SetCardDB).where(SetCardDB.set_code == set_code)).all()
        for card in existing_cards:
            session.delete(card)

        for card_data in data.get("cards", []):
            set_card = _create_set_card_from_data(set_code, card_data)
            session.add(set_card)

    except Exception as e:
        logger.warning(f"Error processing {file_path.name}: {e}")


def _update_set_from_data(set_db: SetDB, data: dict):
    """Update existing set with new data."""
    set_db.name = data.get("name", "")
    set_db.type = data.get("type", "")
    set_db.release_date = data.get("releaseDate")
    set_db.base_set_size = data.get("baseSetSize", 0)
    set_db.total_set_size = data.get("totalSetSize", 0)
    set_db.block = data.get("block")
    set_db.keyrune_code = data.get("keyruneCode")
    set_db.is_foil_only = data.get("isFoilOnly", False)
    set_db.is_online_only = data.get("isOnlineOnly", False)
    set_db.mtgo_code = data.get("mtgoCode")
    set_db.tcgplayer_group_id = data.get("tcgplayerGroupId")
    set_db.cardmarket_id = data.get("mcmId")
    set_db.cardsphere_set_id = data.get("cardsphereSetId")
    set_db.token_set_code = data.get("tokenSetCode")
    set_db.parent_code = data.get("parentCode")
    set_db.languages = data.get("languages", [])
    set_db.translations = data.get("translations", {})


def _create_set_from_data(set_code: str, data: dict) -> SetDB:
    """Create a new SetDB from data."""
    return SetDB(
        code=set_code,
        name=data.get("name", ""),
        type=data.get("type", ""),
        release_date=data.get("releaseDate"),
        base_set_size=data.get("baseSetSize", 0),
        total_set_size=data.get("totalSetSize", 0),
        block=data.get("block"),
        keyrune_code=data.get("keyruneCode"),
        is_foil_only=data.get("isFoilOnly", False),
        is_online_only=data.get("isOnlineOnly", False),
        mtgo_code=data.get("mtgoCode"),
        tcgplayer_group_id=data.get("tcgplayerGroupId"),
        cardmarket_id=data.get("mcmId"),
        cardsphere_set_id=data.get("cardsphereSetId"),
        token_set_code=data.get("tokenSetCode"),
        parent_code=data.get("parentCode"),
        languages=data.get("languages", []),
        translations=data.get("translations", {}),
    )


def _create_set_card_from_data(set_code: str, card_data: dict) -> SetCardDB:
    """Create a SetCardDB from card data."""
    return SetCardDB(
        uuid=card_data.get("uuid", ""),
        set_code=set_code,
        name=card_data.get("name", ""),
        mana_cost=card_data.get("manaCost"),
        mana_value=card_data.get("manaValue"),
        type=card_data.get("type"),
        text=card_data.get("text"),
        power=card_data.get("power"),
        toughness=card_data.get("toughness"),
        loyalty=card_data.get("loyalty"),
        defense=card_data.get("defense"),
        rarity=card_data.get("rarity"),
        number=card_data.get("number"),
        artist=card_data.get("artist"),
        flavor_text=card_data.get("flavorText"),
        layout=card_data.get("layout"),
        border_color=card_data.get("borderColor"),
        frame_version=card_data.get("frameVersion"),
        language=card_data.get("language"),
        colors=card_data.get("colors", []),
        color_identity=card_data.get("colorIdentity", []),
        types=card_data.get("types", []),
        subtypes=card_data.get("subtypes", []),
        supertypes=card_data.get("supertypes", []),
        keywords=card_data.get("keywords", []),
        finishes=card_data.get("finishes", []),
        printings=card_data.get("printings", []),
        legalities=card_data.get("legalities", {}),
        identifiers=card_data.get("identifiers", {}),
        purchase_urls=card_data.get("purchaseUrls", {}),
        has_foil=card_data.get("hasFoil", False),
        has_non_foil=card_data.get("hasNonFoil", False),
        is_reprint=card_data.get("isReprint", False),
        edhrec_rank=card_data.get("edhrecRank"),
        edhrec_saltiness=card_data.get("edhrecSaltiness"),
    )

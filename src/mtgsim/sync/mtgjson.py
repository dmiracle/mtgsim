import json
import lzma
import shutil
import tarfile
import uuid
from pathlib import Path

import requests
from sqlmodel import Session, select

from ..db.deck_models import Deck, DeckCard, DeckList
from ..db.session import init_deck_db
from ..db.set_models import SetCardDB, SetDB, init_sets_db

REFERENCE_BASE_DIR = Path.home() / ".mtgsim" / "reference"
MTGJSON_DIR = REFERENCE_BASE_DIR / "mtgjson"
ALL_DECK_FILES_DIR = MTGJSON_DIR / "AllDeckFiles"

ALL_PRINTINGS_URL = "https://mtgjson.com/api/v5/AllPrintings.sqlite.xz"
ALL_PRICES_URL = "https://mtgjson.com/api/v5/AllPricesToday.sqlite.xz"
DECK_LIST_URL = "https://mtgjson.com/api/v5/DeckList.json.xz"
ALL_DECK_FILES_URL = "https://mtgjson.com/api/v5/AllDeckFiles.tar.xz"


def download_file(url: str, dest: Path):
    """Download a file with progress indication."""
    print(f"Downloading {url} to {dest}...")
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(dest, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    print("Download complete.")


def extract_xz(source: Path, dest: Path):
    """Extract an xz compressed file."""
    print(f"Extracting {source} to {dest}...")
    with lzma.open(source) as f_in:
        with open(dest, "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)
    print("Extraction complete.")


def extract_tar_xz(source: Path, dest_dir: Path):
    """Extract a tar.xz file."""
    print(f"Extracting {source} to {dest_dir}...")
    dest_dir.mkdir(parents=True, exist_ok=True)
    with tarfile.open(source, "r:xz") as tar:
        tar.extractall(path=dest_dir)
    print("Extraction complete.")


def update_references(force: bool = False):
    """Download and extract reference databases from MTGJSON."""
    MTGJSON_DIR.mkdir(parents=True, exist_ok=True)

    files_to_sync = [
        ("AllPrintings.sqlite", ALL_PRINTINGS_URL),
        ("AllPricesToday.sqlite", ALL_PRICES_URL),
    ]

    for filename, url in files_to_sync:
        xz_filename = f"{filename}.xz"
        xz_path = MTGJSON_DIR / xz_filename
        final_path = MTGJSON_DIR / filename

        if final_path.exists() and not force:
            print(f"{filename} exists. Skipping (use --force to update).")
            continue

        try:
            download_file(url, xz_path)
            extract_xz(xz_path, final_path)
            xz_path.unlink()
        except Exception as e:
            print(f"Failed to sync {filename}: {e}")

    print("Reference sync complete.")


def update_decks(force: bool = False):
    """Sync deck data: DeckList.json -> DeckList table, AllDeckFiles -> Deck/DeckCard."""
    MTGJSON_DIR.mkdir(parents=True, exist_ok=True)

    deck_list_xz = MTGJSON_DIR / "DeckList.json.xz"
    deck_list_json = MTGJSON_DIR / "DeckList.json"

    if not deck_list_json.exists() or force:
        try:
            download_file(DECK_LIST_URL, deck_list_xz)
            extract_xz(deck_list_xz, deck_list_json)
            deck_list_xz.unlink()
        except Exception as e:
            print(f"Failed to download DeckList: {e}")
            return

    engine = init_deck_db()
    with Session(engine) as session:
        print("Populating DeckList table...")
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
        print("DeckList populated.")

    all_decks_tar = MTGJSON_DIR / "AllDeckFiles.tar.xz"

    if not ALL_DECK_FILES_DIR.exists() or force:
        try:
            download_file(ALL_DECK_FILES_URL, all_decks_tar)
            extract_tar_xz(all_decks_tar, MTGJSON_DIR)
            all_decks_tar.unlink()
        except Exception as e:
            print(f"Failed to download AllDeckFiles: {e}")
            return

    process_deck_files(engine, ALL_DECK_FILES_DIR)


def process_deck_files(engine, deck_dir: Path):
    """Process all deck JSON files in the directory."""
    print("Processing deck files...")

    files = list(deck_dir.glob("*.json"))
    print(f"Found {len(files)} deck files.")

    with Session(engine) as session:
        for i, file_path in enumerate(files):
            if i % 100 == 0:
                print(f"Processed {i}/{len(files)} decks...")
                session.commit()

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
                    deck.code = data.get("code", "")
                    deck.name = file_name
                    deck.type = data.get("type")
                    deck.release_date = data.get("releaseDate")
                    deck.meta_json = meta
                    deck.commander = data.get("commander", [])
                else:
                    deck_uuid = str(uuid.uuid4())
                    deck = Deck(
                        uuid=deck_uuid,
                        file_name=file_name,
                        code=data.get("code", ""),
                        name=file_name,
                        type=data.get("type"),
                        release_date=data.get("releaseDate"),
                        meta_json=meta,
                        commander=data.get("commander", []),
                    )
                    session.add(deck)

                cards_to_delete = session.exec(select(DeckCard).where(DeckCard.deck_uuid == deck_uuid)).all()
                for card in cards_to_delete:
                    session.delete(card)

                boards = ["mainBoard", "sideBoard", "commander"]
                for board_name in boards:
                    cards_data = data.get(board_name, [])
                    for card_data in cards_data:
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

            except Exception as e:
                print(f"Error processing {file_path.name}: {e}")

        session.commit()
    print("Deck processing complete.")


def update_sets(set_files_dir: Path | None = None):
    """
    Sync set data from AllSetFiles JSON to SQLite database.

    Args:
        set_files_dir: Path to AllSetFiles directory. If None, looks in
                       resources/AllSetFiles relative to the package.
    """
    if set_files_dir is None:
        # Default to resources/AllSetFiles in the project
        import mtgsim

        package_dir = Path(mtgsim.__file__).parent.parent.parent
        set_files_dir = package_dir / "resources" / "AllSetFiles"

    if not set_files_dir.exists():
        print(f"AllSetFiles directory not found at {set_files_dir}")
        print("Please ensure the AllSetFiles directory exists.")
        return

    engine = init_sets_db()
    process_set_files(engine, set_files_dir)


def process_set_files(engine, set_dir: Path):
    """Process all set JSON files in the directory."""
    print("Processing set files...")

    files = list(set_dir.glob("*.json"))
    print(f"Found {len(files)} set files.")

    with Session(engine) as session:
        for i, file_path in enumerate(files):
            if i % 50 == 0:
                print(f"Processed {i}/{len(files)} sets...")
                session.commit()

            try:
                with open(file_path) as f:
                    content = json.load(f)

                data = content.get("data", {})
                set_code = data.get("code", file_path.stem)

                # Check if set exists
                existing_set = session.exec(select(SetDB).where(SetDB.code == set_code)).first()

                if existing_set:
                    set_db = existing_set
                    # Update fields
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
                else:
                    set_db = SetDB(
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
                    session.add(set_db)

                # Delete existing cards for this set
                existing_cards = session.exec(select(SetCardDB).where(SetCardDB.set_code == set_code)).all()
                for card in existing_cards:
                    session.delete(card)

                # Add cards from the set
                cards_data = data.get("cards", [])
                for card_data in cards_data:
                    set_card = SetCardDB(
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
                    session.add(set_card)

            except Exception as e:
                print(f"Error processing {file_path.name}: {e}")

        session.commit()
    print("Set processing complete.")

import json
import lzma
import shutil
import tarfile
import uuid
from pathlib import Path

import requests
from sqlmodel import Session, select

from .deck_db import Deck, DeckCard, DeckList, init_deck_db

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

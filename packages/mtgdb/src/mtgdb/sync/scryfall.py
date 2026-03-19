"""Scryfall oracle tag sync.

Fetches card tags from Scryfall's search API (oracletag: queries),
caches them locally as JSON, and syncs to the mj_card_tag table.
"""

import json
import logging
import time
import urllib.request
from pathlib import Path

from sqlmodel import Session, delete

from mtgdb.config import SCRYFALL_DIR
from mtgdb.models import MJCardTag
from mtgdb.session import get_engine

logger = logging.getLogger(__name__)

SCRYFALL_API_BASE = "https://api.scryfall.com"
TAGS_FILE = SCRYFALL_DIR / "oracle_tags.json"

DEFAULT_TAGS = [
    "mana-dork",
    "mana-rock",
    "ramp",
    "removal",
    "boardwipe",
    "tutor",
    "counterspell",
    "draw",
    "lifegain",
]

BATCH_SIZE = 10000


def fetch_tag(tag: str) -> list[str]:
    """Fetch all card names for a given oracle tag from Scryfall.

    Paginates through search results, collecting unique card names.
    Respects Scryfall's rate limit with 100ms delay between pages.
    """
    card_names = []
    url = f"{SCRYFALL_API_BASE}/cards/search?q=oracletag%3A{tag}&unique=cards"

    while url:
        req = urllib.request.Request(url)
        req.add_header("User-Agent", "mtgsim/1.0")

        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())

        for card in data.get("data", []):
            name = card.get("name")
            if name:
                card_names.append(name)

        if data.get("has_more"):
            url = data.get("next_page")
            time.sleep(0.1)
        else:
            url = None

    return card_names


def fetch_all_tags(tags: list[str] | None = None, force: bool = False) -> dict[str, list[str]]:
    """Fetch all oracle tags from Scryfall and save to local JSON cache.

    Skips if cache file exists and force is False.
    """
    if tags is None:
        tags = DEFAULT_TAGS

    if TAGS_FILE.exists() and not force:
        logger.info(f"Tags file exists: {TAGS_FILE}, skipping fetch (use --force to re-download)")
        with open(TAGS_FILE) as f:
            return json.load(f)

    SCRYFALL_DIR.mkdir(parents=True, exist_ok=True)

    result = {}
    for tag in tags:
        logger.info(f"Fetching oracle tag: {tag}")
        names = fetch_tag(tag)
        result[tag] = names
        logger.info(f"  {tag}: {len(names)} cards")
        time.sleep(0.1)

    with open(TAGS_FILE, "w") as f:
        json.dump(result, f)

    logger.info(f"Saved tags to {TAGS_FILE}")
    return result


def sync_tags(tags_file: Path | None = None):
    """Sync oracle tags from JSON cache to mj_card_tag table."""
    if tags_file is None:
        tags_file = TAGS_FILE

    if not tags_file.exists():
        logger.warning(f"Tags file not found: {tags_file}")
        return

    logger.info("Syncing oracle tags...")

    with open(tags_file) as f:
        tag_data = json.load(f)

    engine = get_engine()

    with Session(engine) as session:
        session.exec(delete(MJCardTag))
        session.commit()

        count = 0
        for tag, card_names in tag_data.items():
            for name in card_names:
                session.add(MJCardTag(card_name=name, tag=tag))
                count += 1

                if count % BATCH_SIZE == 0:
                    session.commit()
                    logger.info(f"  {count} tags...")

        session.commit()

    logger.info(f"Synced {count} card tags")

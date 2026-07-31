"""Generate MTG flashcards and push them to the SRS system."""

import logging

from mtgdb.models import MJCard, MJCardIdentifier, MJKeyword, MJKeywordDefinition
from mtgdb.session import get_session
from sqlmodel import func, select
from srs import SRSClient

logger = logging.getLogger(__name__)

APP_NAME = "mtgsim"


def _get_or_create_app(client: SRSClient, user_id: str):
    try:
        rows = client.db.conn.execute(
            "SELECT id FROM applications WHERE user_id = ? AND name = ?",
            (user_id, APP_NAME),
        ).fetchone()
        if rows:
            return client.get_application(rows[0])
    except Exception:
        pass
    return client.create_application(user_id, APP_NAME)


def _get_or_create_collection(client: SRSClient, user_id: str, name: str, app_id: int):
    try:
        rows = client.db.conn.execute(
            "SELECT id FROM collections WHERE user_id = ? AND name = ? AND application_id = ?",
            (user_id, name, app_id),
        ).fetchone()
        if rows:
            return client.get_collection(rows[0])
    except Exception:
        pass
    return client.create_collection(user_id, name, application_id=app_id)


def _collection_has_flashcards(client: SRSClient, collection_id: int) -> bool:
    row = client.db.conn.execute(
        "SELECT COUNT(*) FROM flashcard_collections WHERE collection_id = ?",
        (collection_id,),
    ).fetchone()
    return row[0] > 0


def _build_image_url(scryfall_id: str | None) -> str | None:
    if not scryfall_id:
        return None
    return f"https://cards.scryfall.io/large/front/{scryfall_id[0]}/{scryfall_id[1]}/{scryfall_id}.jpg?v=1"


def generate_keyword_flashcards(
    client: SRSClient,
    user_id: str,
    collection_name: str | None = None,
    set_code: str | None = None,
) -> int:
    app = _get_or_create_app(client, user_id)

    with get_session() as session:
        keywords = session.exec(select(MJKeyword)).all()
        defs_rows = session.exec(select(MJKeywordDefinition.keyword, MJKeywordDefinition.definition)).all()
        definitions = dict(defs_rows)

        # If set_code provided, filter to keywords that appear on cards in that set
        if set_code:
            query = select(MJCard.keywords).where(MJCard.set_code == set_code, MJCard.keywords.is_not(None))
            set_keywords: set[str] = set()
            for kw_list in session.exec(query).all():
                if isinstance(kw_list, list):
                    set_keywords.update(kw_list)
            keywords = [kw for kw in keywords if kw.name in set_keywords]

    created = 0
    by_type: dict[str, list[dict]] = {}
    for kw in keywords:
        by_type.setdefault(kw.type, []).append(kw)

    for kw_type, kw_list in by_type.items():
        col_name = collection_name or f"keywords_{kw_type}"
        col = _get_or_create_collection(client, user_id, col_name, app.id)
        # Only skip if using auto-generated name and already populated
        if not collection_name and _collection_has_flashcards(client, col.id):
            logger.info(f"Collection {col_name} already populated, skipping")
            continue

        cards = []
        for kw in kw_list:
            definition = definitions.get(kw.name, f"Look up '{kw.name}' in the MTG comprehensive rules.")
            cards.append(
                {
                    "question": {
                        "card_type": "keyword_definition",
                        "keyword": kw.name,
                        "keyword_type": kw.type,
                    },
                    "answer": {"definition": definition},
                }
            )

        if cards:
            client.bulk_add_flashcards(user_id, cards, collection_ids=[col.id])
            created += len(cards)
            logger.info(f"Created {len(cards)} keyword flashcards for {kw_type}")

    return created


def generate_card_oracle_flashcards(
    client: SRSClient, user_id: str, set_code: str, rarity: str | None = None, collection_name: str | None = None
) -> int:
    app = _get_or_create_app(client, user_id)
    col_name = collection_name or f"card_oracle_{set_code}"
    col = _get_or_create_collection(client, user_id, col_name, app.id)

    if not collection_name and _collection_has_flashcards(client, col.id):
        logger.info(f"Collection {col_name} already populated, skipping")
        return 0

    with get_session() as session:
        query = (
            select(
                MJCard.uuid,
                MJCard.name,
                MJCard.oracle_text,
                MJCard.mana_cost,
                MJCard.type_line,
                MJCardIdentifier.scryfall_id,
            )
            .outerjoin(MJCardIdentifier, MJCard.uuid == MJCardIdentifier.card_uuid)
            .where(MJCard.set_code == set_code)
            .where(MJCard.oracle_text.is_not(None))
        )
        if rarity:
            query = query.where(MJCard.rarity == rarity)

        # Deduplicate by name
        subq = select(func.min(MJCard.uuid)).where(MJCard.set_code == set_code).group_by(MJCard.name)
        query = query.where(MJCard.uuid.in_(subq))

        results = session.exec(query).all()

    cards = []
    for uuid, name, oracle_text, mana_cost, type_line, scryfall_id in results:
        cards.append(
            {
                "question": {
                    "card_type": "card_oracle",
                    "card_name": name,
                    "uuid": uuid,
                    "set_code": set_code,
                    "image_url": _build_image_url(scryfall_id),
                },
                "answer": {
                    "oracle_text": oracle_text,
                    "mana_cost": mana_cost,
                    "type_line": type_line,
                    "image_url": _build_image_url(scryfall_id),
                },
            }
        )

    if cards:
        client.bulk_add_flashcards(user_id, cards, collection_ids=[col.id])
        logger.info(f"Created {len(cards)} oracle flashcards for {set_code}")

    return len(cards)


def generate_card_mana_cost_flashcards(
    client: SRSClient, user_id: str, set_code: str, collection_name: str | None = None
) -> int:
    app = _get_or_create_app(client, user_id)
    col_name = collection_name or f"card_mana_cost_{set_code}"
    col = _get_or_create_collection(client, user_id, col_name, app.id)

    if not collection_name and _collection_has_flashcards(client, col.id):
        logger.info(f"Collection {col_name} already populated, skipping")
        return 0

    with get_session() as session:
        subq = select(func.min(MJCard.uuid)).where(MJCard.set_code == set_code).group_by(MJCard.name)
        query = (
            select(
                MJCard.uuid,
                MJCard.name,
                MJCard.oracle_text,
                MJCard.mana_cost,
                MJCard.mana_value,
                MJCard.type_line,
                MJCardIdentifier.scryfall_id,
            )
            .outerjoin(MJCardIdentifier, MJCard.uuid == MJCardIdentifier.card_uuid)
            .where(MJCard.set_code == set_code)
            .where(MJCard.mana_cost.is_not(None))
            .where(MJCard.mana_cost != "")
            .where(MJCard.uuid.in_(subq))
        )
        results = session.exec(query).all()

    cards = []
    for uuid, name, oracle_text, mana_cost, mana_value, type_line, scryfall_id in results:
        cards.append(
            {
                "question": {
                    "card_type": "card_mana_cost",
                    "card_name": name,
                    "uuid": uuid,
                    "set_code": set_code,
                    "image_url": _build_image_url(scryfall_id),
                    "oracle_text": oracle_text,
                    "type_line": type_line,
                },
                "answer": {
                    "mana_cost": mana_cost,
                    "mana_value": mana_value,
                    "image_url": _build_image_url(scryfall_id),
                },
            }
        )

    if cards:
        client.bulk_add_flashcards(user_id, cards, collection_ids=[col.id])
        logger.info(f"Created {len(cards)} mana cost flashcards for {set_code}")

    return len(cards)


def generate_card_stats_flashcards(
    client: SRSClient, user_id: str, set_code: str, collection_name: str | None = None
) -> int:
    app = _get_or_create_app(client, user_id)
    col_name = collection_name or f"card_stats_{set_code}"
    col = _get_or_create_collection(client, user_id, col_name, app.id)

    if not collection_name and _collection_has_flashcards(client, col.id):
        logger.info(f"Collection {col_name} already populated, skipping")
        return 0

    with get_session() as session:
        subq = select(func.min(MJCard.uuid)).where(MJCard.set_code == set_code).group_by(MJCard.name)
        query = (
            select(
                MJCard.uuid,
                MJCard.name,
                MJCard.oracle_text,
                MJCard.type_line,
                MJCard.power,
                MJCard.toughness,
                MJCardIdentifier.scryfall_id,
            )
            .outerjoin(MJCardIdentifier, MJCard.uuid == MJCardIdentifier.card_uuid)
            .where(MJCard.set_code == set_code)
            .where(MJCard.power.is_not(None))
            .where(MJCard.toughness.is_not(None))
            .where(MJCard.uuid.in_(subq))
        )
        results = session.exec(query).all()

    cards = []
    for uuid, name, oracle_text, type_line, power, toughness, scryfall_id in results:
        cards.append(
            {
                "question": {
                    "card_type": "card_stats",
                    "card_name": name,
                    "uuid": uuid,
                    "set_code": set_code,
                    "image_url": _build_image_url(scryfall_id),
                    "oracle_text": oracle_text,
                    "type_line": type_line,
                },
                "answer": {
                    "power": power,
                    "toughness": toughness,
                    "image_url": _build_image_url(scryfall_id),
                },
            }
        )

    if cards:
        client.bulk_add_flashcards(user_id, cards, collection_ids=[col.id])
        logger.info(f"Created {len(cards)} stats flashcards for {set_code}")

    return len(cards)


def generate_card_rarity_flashcards(
    client: SRSClient, user_id: str, set_code: str, collection_name: str | None = None
) -> int:
    app = _get_or_create_app(client, user_id)
    col_name = collection_name or f"card_rarity_{set_code}"
    col = _get_or_create_collection(client, user_id, col_name, app.id)

    if not collection_name and _collection_has_flashcards(client, col.id):
        logger.info(f"Collection {col_name} already populated, skipping")
        return 0

    with get_session() as session:
        subq = select(func.min(MJCard.uuid)).where(MJCard.set_code == set_code).group_by(MJCard.name)
        query = (
            select(
                MJCard.uuid,
                MJCard.name,
                MJCard.oracle_text,
                MJCard.type_line,
                MJCard.rarity,
                MJCardIdentifier.scryfall_id,
            )
            .outerjoin(MJCardIdentifier, MJCard.uuid == MJCardIdentifier.card_uuid)
            .where(MJCard.set_code == set_code)
            .where(MJCard.rarity.is_not(None))
            .where(MJCard.uuid.in_(subq))
        )
        results = session.exec(query).all()

    cards = []
    for uuid, name, oracle_text, type_line, rarity, scryfall_id in results:
        cards.append(
            {
                "question": {
                    "card_type": "card_rarity",
                    "card_name": name,
                    "uuid": uuid,
                    "set_code": set_code,
                    "oracle_text": oracle_text,
                    "type_line": type_line,
                },
                "answer": {
                    "rarity": rarity,
                    "image_url": _build_image_url(scryfall_id),
                },
            }
        )

    if cards:
        client.bulk_add_flashcards(user_id, cards, collection_ids=[col.id])
        logger.info(f"Created {len(cards)} rarity flashcards for {set_code}")

    return len(cards)


def generate_card_recall_flashcards(
    client: SRSClient, user_id: str, set_code: str, collection_name: str | None = None
) -> int:
    app = _get_or_create_app(client, user_id)
    col_name = collection_name or f"card_recall_{set_code}"
    col = _get_or_create_collection(client, user_id, col_name, app.id)

    if not collection_name and _collection_has_flashcards(client, col.id):
        logger.info(f"Collection {col_name} already populated, skipping")
        return 0

    with get_session() as session:
        subq = select(func.min(MJCard.uuid)).where(MJCard.set_code == set_code).group_by(MJCard.name)
        query = (
            select(
                MJCard.uuid,
                MJCard.name,
                MJCard.mana_cost,
                MJCard.mana_value,
                MJCard.type_line,
                MJCard.oracle_text,
                MJCard.power,
                MJCard.toughness,
                MJCardIdentifier.scryfall_id,
            )
            .outerjoin(MJCardIdentifier, MJCard.uuid == MJCardIdentifier.card_uuid)
            .where(MJCard.set_code == set_code)
            .where(MJCard.uuid.in_(subq))
        )
        results = session.exec(query).all()

    cards = []
    for uuid, name, mana_cost, mana_value, type_line, oracle_text, power, toughness, scryfall_id in results:
        has_stats = power is not None and toughness is not None
        aspects = [
            {"key": "mana_cost", "label": "MV", "enabled": True},
            {"key": "type_line", "label": "Type", "enabled": True},
            {"key": "power_toughness", "label": "Stats", "enabled": has_stats},
            {"key": "oracle_text", "label": "Oracle", "enabled": True},
        ]
        cards.append(
            {
                "question": {
                    "card_type": "card_recall",
                    "card_name": name,
                    "uuid": uuid,
                    "set_code": set_code,
                    "image_url": _build_image_url(scryfall_id),
                    "aspects": aspects,
                },
                "answer": {
                    "mana_cost": mana_cost,
                    "mana_value": mana_value,
                    "type_line": type_line,
                    "oracle_text": oracle_text,
                    "power": power,
                    "toughness": toughness,
                    "image_url": _build_image_url(scryfall_id),
                },
            }
        )

    if cards:
        client.bulk_add_flashcards(user_id, cards, collection_ids=[col.id])
        logger.info(f"Created {len(cards)} recall flashcards for {set_code}")

    return len(cards)

"""Data access layer for card interactions."""

import logging
from collections import deque
from datetime import UTC, datetime

from mtgdb import MJCard, MJCardIdentifier, UserCardInteraction, get_session
from sqlalchemy import and_, func, or_
from sqlmodel import select

from .helpers import build_image_url

logger = logging.getLogger(__name__)


def _card_dict(card: MJCard, scryfall_id: str | None) -> dict:
    return {
        "uuid": card.uuid,
        "name": card.name,
        "type_line": card.type_line,
        "mana_cost": card.mana_cost,
        "image_url": build_image_url(scryfall_id),
    }


def _load_card(session, uuid: str) -> dict | None:
    row = session.exec(
        select(MJCard, MJCardIdentifier)
        .outerjoin(MJCardIdentifier, MJCardIdentifier.card_uuid == MJCard.uuid)
        .where(MJCard.uuid == uuid)
    ).first()
    if not row:
        return None
    card, ident = row
    return _card_dict(card, ident.scryfall_id if ident else None)


def _interaction_to_dict(interaction: UserCardInteraction, source_card: dict, target_card: dict) -> dict:
    return {
        "id": interaction.id,
        "source_card": source_card,
        "target_card": target_card,
        "interaction_type": interaction.interaction_type,
        "is_bidirectional": interaction.is_bidirectional,
        "description": interaction.description,
        "strength": interaction.strength,
        "extra": interaction.extra or {},
        "created_at": interaction.created_at.isoformat() if interaction.created_at else "",
        "updated_at": interaction.updated_at.isoformat() if interaction.updated_at else "",
    }


class InteractionsData:
    def create_interaction(
        self,
        source_card_uuid: str,
        target_card_uuid: str,
        interaction_type: str,
        is_bidirectional: bool = True,
        description: str | None = None,
        strength: int | None = None,
        extra: dict | None = None,
    ) -> dict | None:
        with get_session() as session:
            source_card = _load_card(session, source_card_uuid)
            if not source_card:
                return None
            target_card = _load_card(session, target_card_uuid)
            if not target_card:
                return None

            interaction = UserCardInteraction(
                source_card_uuid=source_card_uuid,
                target_card_uuid=target_card_uuid,
                interaction_type=interaction_type,
                is_bidirectional=is_bidirectional,
                description=description,
                strength=strength,
                extra=extra or {},
            )
            session.add(interaction)
            session.commit()
            session.refresh(interaction)
            return _interaction_to_dict(interaction, source_card, target_card)

    def get_interaction(self, interaction_id: int) -> dict | None:
        with get_session() as session:
            interaction = session.get(UserCardInteraction, interaction_id)
            if not interaction:
                return None
            source_card = _load_card(session, interaction.source_card_uuid)
            target_card = _load_card(session, interaction.target_card_uuid)
            return _interaction_to_dict(interaction, source_card or {}, target_card or {})

    def update_interaction(self, interaction_id: int, **fields) -> dict | None:
        with get_session() as session:
            interaction = session.get(UserCardInteraction, interaction_id)
            if not interaction:
                return None
            for key, value in fields.items():
                if value is not None:
                    setattr(interaction, key, value)
            interaction.updated_at = datetime.now(UTC)
            session.add(interaction)
            session.commit()
            session.refresh(interaction)
            source_card = _load_card(session, interaction.source_card_uuid)
            target_card = _load_card(session, interaction.target_card_uuid)
            return _interaction_to_dict(interaction, source_card or {}, target_card or {})

    def delete_interaction(self, interaction_id: int) -> bool:
        with get_session() as session:
            interaction = session.get(UserCardInteraction, interaction_id)
            if not interaction:
                return False
            session.delete(interaction)
            session.commit()
            return True

    def list_interactions(
        self,
        card_uuid: str | None = None,
        interaction_type: str | None = None,
        page: int = 1,
        limit: int = 50,
    ) -> tuple[list[dict], int]:
        with get_session() as session:
            query = select(UserCardInteraction)

            if card_uuid:
                query = query.where(
                    or_(
                        UserCardInteraction.source_card_uuid == card_uuid,
                        and_(
                            UserCardInteraction.target_card_uuid == card_uuid,
                            UserCardInteraction.is_bidirectional == True,  # noqa: E712
                        ),
                    )
                )
            if interaction_type:
                query = query.where(UserCardInteraction.interaction_type == interaction_type)

            count_query = select(func.count()).select_from(query.subquery())
            total = session.exec(count_query).one()

            offset = (page - 1) * limit
            query = query.order_by(UserCardInteraction.created_at.desc()).offset(offset).limit(limit)
            interactions = session.exec(query).all()

            results = []
            for interaction in interactions:
                source_card = _load_card(session, interaction.source_card_uuid)
                target_card = _load_card(session, interaction.target_card_uuid)
                results.append(_interaction_to_dict(interaction, source_card or {}, target_card or {}))

            return results, total

    def get_interaction_graph(self, card_uuid: str, depth: int = 1) -> dict | None:
        depth = min(depth, 3)
        max_nodes = 100

        with get_session() as session:
            root_card = _load_card(session, card_uuid)
            if not root_card:
                return None

            visited: set[str] = {card_uuid}
            queue: deque[tuple[str, int]] = deque([(card_uuid, 0)])
            nodes: list[dict] = []
            total_interactions = 0

            while queue and len(nodes) < max_nodes:
                current_uuid, current_depth = queue.popleft()
                if current_depth >= depth:
                    continue

                query = select(UserCardInteraction).where(
                    or_(
                        UserCardInteraction.source_card_uuid == current_uuid,
                        and_(
                            UserCardInteraction.target_card_uuid == current_uuid,
                            UserCardInteraction.is_bidirectional == True,  # noqa: E712
                        ),
                    )
                )
                interactions = session.exec(query).all()

                if not interactions:
                    continue

                current_card = _load_card(session, current_uuid) or {"uuid": current_uuid, "name": "Unknown"}
                interaction_dicts = []

                for interaction in interactions:
                    neighbor_uuid = (
                        interaction.target_card_uuid
                        if interaction.source_card_uuid == current_uuid
                        else interaction.source_card_uuid
                    )
                    source_card = _load_card(session, interaction.source_card_uuid)
                    target_card = _load_card(session, interaction.target_card_uuid)
                    interaction_dicts.append(_interaction_to_dict(interaction, source_card or {}, target_card or {}))

                    if neighbor_uuid not in visited:
                        visited.add(neighbor_uuid)
                        queue.append((neighbor_uuid, current_depth + 1))

                nodes.append({"card": current_card, "interactions": interaction_dicts})
                total_interactions += len(interaction_dicts)

            return {
                "root_card": root_card,
                "depth": depth,
                "nodes": nodes,
                "total_interactions": total_interactions,
            }


interactions_data = InteractionsData()

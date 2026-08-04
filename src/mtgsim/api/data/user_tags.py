"""Data access layer for user card tags and tag definitions."""

import logging
from datetime import UTC, datetime

from mtgdb import UserCardTag, UserTagDefinition, get_session
from sqlmodel import func, select

from .helpers import canonical_card_name, normalize_user_tag, resolve_default_printing

logger = logging.getLogger(__name__)


class UserTagsData:
    def list_tags(self, q: str | None = None, page: int = 1, limit: int = 50) -> tuple[list[dict], int]:
        """Tag vocabulary: distinct assigned tags + defined tags, with counts and descriptions."""
        with get_session() as session:
            counts = dict(session.exec(select(UserCardTag.tag, func.count()).group_by(UserCardTag.tag)).all())
            definitions = dict(session.exec(select(UserTagDefinition.tag, UserTagDefinition.description)).all())

            tags = sorted(set(counts) | set(definitions))
            if q:
                needle = normalize_user_tag(q)
                tags = [t for t in tags if needle in t]

            total = len(tags)
            offset = (page - 1) * limit
            page_tags = tags[offset : offset + limit]
            return [
                {"tag": t, "description": definitions.get(t), "card_count": counts.get(t, 0)} for t in page_tags
            ], total

    def cards_for_tag(self, tag: str, page: int = 1, limit: int = 50) -> tuple[list[dict], int]:
        with get_session() as session:
            tag = normalize_user_tag(tag)
            query = select(UserCardTag.card_name).where(UserCardTag.tag == tag).order_by(UserCardTag.card_name)
            names = session.exec(query).all()
            total = len(names)
            offset = (page - 1) * limit
            cards = []
            for name in names[offset : offset + limit]:
                card = resolve_default_printing(session, name)
                cards.append(card or {"uuid": None, "name": name})
            return cards, total

    def assign(self, card_name: str, tag: str) -> tuple[dict, bool] | None:
        """Assign a tag. Returns (assignment dict, created) or None if the card doesn't exist."""
        with get_session() as session:
            canonical = canonical_card_name(session, card_name)
            if not canonical:
                return None
            tag = normalize_user_tag(tag)

            existing = session.exec(
                select(UserCardTag).where(UserCardTag.card_name == canonical, UserCardTag.tag == tag)
            ).first()
            if existing:
                return {"card_name": canonical, "tag": tag}, False

            session.add(UserCardTag(card_name=canonical, tag=tag))
            session.commit()
            return {"card_name": canonical, "tag": tag}, True

    def unassign(self, card_name: str, tag: str) -> bool:
        with get_session() as session:
            canonical = canonical_card_name(session, card_name) or card_name
            tag = normalize_user_tag(tag)
            row = session.exec(
                select(UserCardTag).where(UserCardTag.card_name == canonical, UserCardTag.tag == tag)
            ).first()
            if not row:
                return False
            session.delete(row)
            session.commit()
            return True

    def set_definition(self, tag: str, description: str) -> dict:
        """Upsert the definition for a tag."""
        with get_session() as session:
            tag = normalize_user_tag(tag)
            existing = session.exec(select(UserTagDefinition).where(UserTagDefinition.tag == tag)).first()
            if existing:
                existing.description = description
                existing.updated_at = datetime.now(UTC)
                session.add(existing)
            else:
                session.add(UserTagDefinition(tag=tag, description=description))
            session.commit()
            count = session.exec(select(func.count()).where(UserCardTag.tag == tag)).one()
            return {"tag": tag, "description": description, "card_count": count}

    def delete_tag(self, tag: str) -> bool:
        """Remove a tag entirely: its definition and all assignments."""
        with get_session() as session:
            tag = normalize_user_tag(tag)
            assignments = session.exec(select(UserCardTag).where(UserCardTag.tag == tag)).all()
            definition = session.exec(select(UserTagDefinition).where(UserTagDefinition.tag == tag)).first()
            if not assignments and not definition:
                return False
            for row in assignments:
                session.delete(row)
            if definition:
                session.delete(definition)
            session.commit()
            return True

    def tags_for_card(self, card_name: str) -> list[str]:
        with get_session() as session:
            canonical = canonical_card_name(session, card_name) or card_name
            return list(
                session.exec(
                    select(UserCardTag.tag).where(UserCardTag.card_name == canonical).order_by(UserCardTag.tag)
                ).all()
            )


user_tags_data = UserTagsData()

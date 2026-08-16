"""Data access layer for user tier lists."""

import logging
from datetime import UTC, datetime

from mtgdb import UserTierList, UserTierListEntry, get_session
from sqlmodel import func, select

from .helpers import canonical_card_name, resolve_default_printing, tier_order

logger = logging.getLogger(__name__)


def _list_to_dict(tier_list: UserTierList, entry_count: int = 0) -> dict:
    return {
        "id": tier_list.id,
        "name": tier_list.name,
        "description": tier_list.description,
        "set_code": tier_list.set_code,
        "format": tier_list.format,
        "extra": tier_list.extra or {},
        "entry_count": entry_count,
        "created_at": tier_list.created_at.isoformat() if tier_list.created_at else "",
        "updated_at": tier_list.updated_at.isoformat() if tier_list.updated_at else "",
    }


def _entry_to_dict(entry: UserTierListEntry, card: dict | None) -> dict:
    return {
        "id": entry.id,
        "card_name": entry.card_name,
        "tier": entry.tier,
        "position": entry.position,
        "note": entry.note,
        "card": card,
    }


class TierListsData:
    def create_list(
        self,
        name: str,
        description: str | None = None,
        set_code: str | None = None,
        format: str | None = None,
    ) -> dict:
        with get_session() as session:
            tier_list = UserTierList(
                name=name, description=description, set_code=set_code.upper() if set_code else None, format=format
            )
            session.add(tier_list)
            session.commit()
            session.refresh(tier_list)
            return _list_to_dict(tier_list)

    def list_lists(
        self,
        set_code: str | None = None,
        format: str | None = None,
        page: int = 1,
        limit: int = 50,
    ) -> tuple[list[dict], int]:
        with get_session() as session:
            query = select(UserTierList)
            if set_code:
                query = query.where(UserTierList.set_code == set_code.upper())
            if format:
                query = query.where(UserTierList.format == format)

            total = session.exec(select(func.count()).select_from(query.subquery())).one()
            offset = (page - 1) * limit
            lists = session.exec(query.order_by(UserTierList.updated_at.desc()).offset(offset).limit(limit)).all()

            counts = dict(
                session.exec(
                    select(UserTierListEntry.tier_list_id, func.count()).group_by(UserTierListEntry.tier_list_id)
                ).all()
            )
            return [_list_to_dict(tl, counts.get(tl.id, 0)) for tl in lists], total

    def get_list(self, list_id: int) -> dict | None:
        with get_session() as session:
            tier_list = session.get(UserTierList, list_id)
            if not tier_list:
                return None
            entries = session.exec(
                select(UserTierListEntry)
                .where(UserTierListEntry.tier_list_id == list_id)
                .order_by(tier_order(), UserTierListEntry.position)
            ).all()
            result = _list_to_dict(tier_list, len(entries))
            result["entries"] = [_entry_to_dict(e, resolve_default_printing(session, e.card_name)) for e in entries]
            return result

    def update_list(self, list_id: int, **fields) -> dict | None:
        with get_session() as session:
            tier_list = session.get(UserTierList, list_id)
            if not tier_list:
                return None
            for key, value in fields.items():
                if value is not None:
                    setattr(tier_list, key, value.upper() if key == "set_code" else value)
            tier_list.updated_at = datetime.now(UTC)
            session.add(tier_list)
            session.commit()
            session.refresh(tier_list)
            count = session.exec(select(func.count()).where(UserTierListEntry.tier_list_id == list_id)).one()
            return _list_to_dict(tier_list, count)

    def delete_list(self, list_id: int) -> bool:
        with get_session() as session:
            tier_list = session.get(UserTierList, list_id)
            if not tier_list:
                return False
            for entry in session.exec(select(UserTierListEntry).where(UserTierListEntry.tier_list_id == list_id)).all():
                session.delete(entry)
            session.delete(tier_list)
            session.commit()
            return True

    def upsert_entry(
        self,
        list_id: int,
        card_name: str,
        tier: str,
        position: int | None = None,
        note: str | None = None,
    ) -> tuple[dict, bool] | None:
        """Add a card to a list or move it. Returns (entry dict, created) or None on missing list/card."""
        with get_session() as session:
            tier_list = session.get(UserTierList, list_id)
            if not tier_list:
                return None
            canonical = canonical_card_name(session, card_name)
            if not canonical:
                return None

            entry = session.exec(
                select(UserTierListEntry).where(
                    UserTierListEntry.tier_list_id == list_id, UserTierListEntry.card_name == canonical
                )
            ).first()
            created = entry is None
            if created:
                entry = UserTierListEntry(tier_list_id=list_id, card_name=canonical, tier=tier)
                session.add(entry)

            entry.tier = tier
            if note is not None:
                entry.note = note
            entry.updated_at = datetime.now(UTC)

            if position is None:
                max_pos = session.exec(
                    select(func.max(UserTierListEntry.position)).where(
                        UserTierListEntry.tier_list_id == list_id,
                        UserTierListEntry.tier == tier,
                        UserTierListEntry.card_name != canonical,
                    )
                ).one()
                entry.position = (max_pos if max_pos is not None else -1) + 1
            else:
                # renumber the target tier with the card inserted at the requested slot
                siblings = list(
                    session.exec(
                        select(UserTierListEntry)
                        .where(
                            UserTierListEntry.tier_list_id == list_id,
                            UserTierListEntry.tier == tier,
                            UserTierListEntry.card_name != canonical,
                        )
                        .order_by(UserTierListEntry.position)
                    ).all()
                )
                slot = max(0, min(position, len(siblings)))
                siblings.insert(slot, entry)
                for i, sibling in enumerate(siblings):
                    sibling.position = i
                    session.add(sibling)

            tier_list.updated_at = datetime.now(UTC)
            session.add(tier_list)
            session.commit()
            session.refresh(entry)
            return _entry_to_dict(entry, resolve_default_printing(session, canonical)), created

    def remove_entry(self, list_id: int, card_name: str) -> bool:
        with get_session() as session:
            canonical = canonical_card_name(session, card_name) or card_name
            entry = session.exec(
                select(UserTierListEntry).where(
                    UserTierListEntry.tier_list_id == list_id, UserTierListEntry.card_name == canonical
                )
            ).first()
            if not entry:
                return False
            session.delete(entry)
            session.commit()
            return True

    def reorder_tier(self, list_id: int, tier: str, ordered_card_names: list[str]) -> dict | None:
        """Bulk reorder a tier. Names not in the tier are ignored; unmentioned entries keep relative order after."""
        with get_session() as session:
            if not session.get(UserTierList, list_id):
                return None
            entries = list(
                session.exec(
                    select(UserTierListEntry)
                    .where(UserTierListEntry.tier_list_id == list_id, UserTierListEntry.tier == tier)
                    .order_by(UserTierListEntry.position)
                ).all()
            )
            by_name = {e.card_name: e for e in entries}
            ordered = [by_name[n] for n in ordered_card_names if n in by_name]
            remainder = [e for e in entries if e.card_name not in set(ordered_card_names)]
            for i, entry in enumerate(ordered + remainder):
                entry.position = i
                session.add(entry)
            session.commit()
            return {"tier": tier, "card_names": [e.card_name for e in ordered + remainder]}

    def placements_for_card(self, card_name: str) -> list[dict]:
        """Tier placements of a card across all lists."""
        with get_session() as session:
            canonical = canonical_card_name(session, card_name) or card_name
            rows = session.exec(
                select(UserTierListEntry, UserTierList)
                .join(UserTierList, UserTierListEntry.tier_list_id == UserTierList.id)
                .where(UserTierListEntry.card_name == canonical)
            ).all()
            return [
                {
                    "tier_list_id": tl.id,
                    "list_name": tl.name,
                    "tier": e.tier,
                    "set_code": tl.set_code,
                    "format": tl.format,
                }
                for e, tl in rows
            ]


tier_lists_data = TierListsData()

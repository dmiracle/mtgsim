"""Data access layer for user card notes."""

import logging
from datetime import UTC, datetime

from mtgdb import UserCardNote, get_session
from sqlalchemy import or_
from sqlmodel import func, select

from .helpers import canonical_card_name

logger = logging.getLogger(__name__)


def _note_to_dict(note: UserCardNote) -> dict:
    return {
        "id": note.id,
        "card_name": note.card_name,
        "kind": note.kind,
        "title": note.title,
        "body": note.body,
        "extra": note.extra or {},
        "created_at": note.created_at.isoformat() if note.created_at else "",
        "updated_at": note.updated_at.isoformat() if note.updated_at else "",
    }


class CardNotesData:
    def create_note(
        self,
        card_name: str,
        body: str,
        kind: str = "note",
        title: str | None = None,
        extra: dict | None = None,
    ) -> dict | None:
        with get_session() as session:
            canonical = canonical_card_name(session, card_name)
            if not canonical:
                return None
            note = UserCardNote(card_name=canonical, kind=kind, title=title, body=body, extra=extra or {})
            session.add(note)
            session.commit()
            session.refresh(note)
            return _note_to_dict(note)

    def get_note(self, note_id: int) -> dict | None:
        with get_session() as session:
            note = session.get(UserCardNote, note_id)
            return _note_to_dict(note) if note else None

    def update_note(self, note_id: int, **fields) -> dict | None:
        with get_session() as session:
            note = session.get(UserCardNote, note_id)
            if not note:
                return None
            for key, value in fields.items():
                if value is not None:
                    setattr(note, key, value)
            note.updated_at = datetime.now(UTC)
            session.add(note)
            session.commit()
            session.refresh(note)
            return _note_to_dict(note)

    def delete_note(self, note_id: int) -> bool:
        with get_session() as session:
            note = session.get(UserCardNote, note_id)
            if not note:
                return False
            session.delete(note)
            session.commit()
            return True

    def list_notes(
        self,
        card_name: str | None = None,
        kind: str | None = None,
        q: str | None = None,
        page: int = 1,
        limit: int = 50,
    ) -> tuple[list[dict], int]:
        with get_session() as session:
            query = select(UserCardNote)
            if card_name:
                canonical = canonical_card_name(session, card_name) or card_name
                query = query.where(UserCardNote.card_name == canonical)
            if kind:
                query = query.where(UserCardNote.kind == kind)
            if q:
                needle = f"%{q}%"
                query = query.where(or_(UserCardNote.title.like(needle), UserCardNote.body.like(needle)))

            total = session.exec(select(func.count()).select_from(query.subquery())).one()
            offset = (page - 1) * limit
            notes = session.exec(query.order_by(UserCardNote.updated_at.desc()).offset(offset).limit(limit)).all()
            return [_note_to_dict(n) for n in notes], total


card_notes_data = CardNotesData()

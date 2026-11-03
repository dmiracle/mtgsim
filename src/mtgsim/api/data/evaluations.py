"""Data access layer for situational card evaluations."""

from datetime import UTC, datetime

from mtgdb import UserCardEvaluation, UserEvaluationSet, get_session
from sqlmodel import func, select

from .helpers import canonical_card_name

SITUATIONS = ("developing", "parity", "behind", "ahead")


def _set_to_dict(evaluation_set: UserEvaluationSet, entry_count: int = 0) -> dict:
    return {
        "id": evaluation_set.id,
        "name": evaluation_set.name,
        "set_code": evaluation_set.set_code,
        "entry_count": entry_count,
        "created_at": evaluation_set.created_at.isoformat() if evaluation_set.created_at else "",
        "updated_at": evaluation_set.updated_at.isoformat() if evaluation_set.updated_at else "",
    }


def _entry_to_dict(entry: UserCardEvaluation) -> dict:
    return {"card_name": entry.card_name, **{s: getattr(entry, s) for s in SITUATIONS}}


class EvaluationsData:
    def create_set(self, name: str, set_code: str | None = None) -> dict:
        with get_session() as session:
            evaluation_set = UserEvaluationSet(name=name, set_code=set_code.upper() if set_code else None)
            session.add(evaluation_set)
            session.commit()
            session.refresh(evaluation_set)
            return _set_to_dict(evaluation_set)

    def list_sets(self) -> list[dict]:
        with get_session() as session:
            sets = session.exec(select(UserEvaluationSet).order_by(UserEvaluationSet.updated_at.desc())).all()
            counts = dict(
                session.exec(
                    select(UserCardEvaluation.evaluation_set_id, func.count()).group_by(
                        UserCardEvaluation.evaluation_set_id
                    )
                ).all()
            )
            return [_set_to_dict(s, counts.get(s.id, 0)) for s in sets]

    def get_set(self, set_id: int) -> dict | None:
        with get_session() as session:
            evaluation_set = session.get(UserEvaluationSet, set_id)
            if not evaluation_set:
                return None
            entries = session.exec(
                select(UserCardEvaluation)
                .where(UserCardEvaluation.evaluation_set_id == set_id)
                .order_by(UserCardEvaluation.card_name)
            ).all()
            result = _set_to_dict(evaluation_set, len(entries))
            result["entries"] = [_entry_to_dict(e) for e in entries]
            return result

    def put_evaluation(self, set_id: int, card_name: str, scores: dict) -> dict | None:
        """Replace a card's scores; an entry with every situation unrated is deleted. None if set/card is unknown."""
        with get_session() as session:
            evaluation_set = session.get(UserEvaluationSet, set_id)
            canonical = canonical_card_name(session, card_name)
            if not evaluation_set or not canonical:
                return None
            entry = session.exec(
                select(UserCardEvaluation).where(
                    UserCardEvaluation.evaluation_set_id == set_id, UserCardEvaluation.card_name == canonical
                )
            ).first() or UserCardEvaluation(evaluation_set_id=set_id, card_name=canonical)
            for situation in SITUATIONS:
                setattr(entry, situation, scores.get(situation))
            entry.updated_at = evaluation_set.updated_at = datetime.now(UTC)
            session.add(evaluation_set)
            if all(scores.get(s) is None for s in SITUATIONS):
                if entry.id:
                    session.delete(entry)
            else:
                session.add(entry)
            session.commit()
            return _entry_to_dict(entry)

    def delete_set(self, set_id: int) -> bool:
        with get_session() as session:
            evaluation_set = session.get(UserEvaluationSet, set_id)
            if not evaluation_set:
                return False
            entries = session.exec(select(UserCardEvaluation).where(UserCardEvaluation.evaluation_set_id == set_id))
            for entry in entries.all():
                session.delete(entry)
            session.delete(evaluation_set)
            session.commit()
            return True


evaluations_data = EvaluationsData()

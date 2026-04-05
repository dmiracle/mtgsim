"""Mana value proximity similarity strategy."""

from mtgdb.models import MJCard
from sqlmodel import select

from .base import ScoredCard, SimilarityStrategy, register_strategy


@register_strategy
class ManaCurveSimilarity(SimilarityStrategy):
    name = "mana_curve"
    description = "Cards at the same or adjacent mana values"

    def score(self, source: MJCard, session, limit: int = 100) -> list[ScoredCard]:
        if source.mana_value is None:
            return []

        mv = source.mana_value
        # Fetch cards within ±2 mana value
        rows = session.exec(
            select(MJCard.uuid, MJCard.mana_value)
            .where(MJCard.mana_value.is_not(None))
            .where(MJCard.mana_value >= mv - 2)
            .where(MJCard.mana_value <= mv + 2)
            .where(MJCard.uuid != source.uuid)
        ).all()

        scored = []
        for uuid, card_mv in rows:
            if card_mv is None:
                continue
            diff = abs(card_mv - mv)
            # Score: 1.0 for exact match, 0.5 for ±1, 0.25 for ±2
            score = 1.0 / (1.0 + diff)
            scored.append(ScoredCard(uuid=uuid, score=score))

        scored.sort(key=lambda s: s.score, reverse=True)
        return scored[:limit]

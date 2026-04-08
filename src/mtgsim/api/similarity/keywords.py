"""Keyword overlap similarity strategy."""

from mtgdb.models import MJCard
from sqlmodel import select

from .base import ScoredCard, SimilarityStrategy, register_strategy


@register_strategy
class KeywordSimilarity(SimilarityStrategy):
    name = "keywords"
    description = "Jaccard similarity on keyword abilities (flying, trample, etc.)"

    def score(self, source: MJCard, session, limit: int = 100) -> list[ScoredCard]:
        source_kw = set(source.keywords or [])
        if not source_kw:
            return []

        # Fetch cards that share at least one keyword
        # Use JSON containment for each keyword, union results
        from sqlalchemy import or_
        from sqlmodel import func

        conditions = [func.json_extract(MJCard.keywords, "$").contains(f'"{kw}"') for kw in source_kw]
        rows = session.exec(
            select(MJCard.uuid, MJCard.keywords).where(or_(*conditions)).where(MJCard.uuid != source.uuid)
        ).all()

        scored = []
        for uuid, kw_json in rows:
            card_kw = set(kw_json) if isinstance(kw_json, list) else set()
            intersection = source_kw & card_kw
            union = source_kw | card_kw
            if union:
                scored.append(ScoredCard(uuid=uuid, score=len(intersection) / len(union)))

        scored.sort(key=lambda s: s.score, reverse=True)
        return scored[:limit]

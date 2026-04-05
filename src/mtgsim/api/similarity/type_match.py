"""Type/subtype overlap similarity strategy."""

from mtgdb.models import MJCard
from sqlmodel import select

from .base import ScoredCard, SimilarityStrategy, register_strategy


@register_strategy
class TypeMatchSimilarity(SimilarityStrategy):
    name = "type_match"
    description = "Overlap on card types and subtypes (e.g. Elf Warrior matches other Elves)"

    def score(self, source: MJCard, session, limit: int = 100) -> list[ScoredCard]:
        source_types = set(source.types or [])
        source_subtypes = set(source.subtypes or [])
        all_source = source_types | source_subtypes
        if not all_source:
            return []

        # Fetch cards sharing at least one type or subtype via JSON containment
        from sqlalchemy import or_
        from sqlmodel import func

        conditions = []
        for t in source_types:
            conditions.append(func.json_extract(MJCard.types, "$").contains(f'"{t}"'))
        for st in source_subtypes:
            conditions.append(func.json_extract(MJCard.subtypes, "$").contains(f'"{st}"'))

        rows = session.exec(
            select(MJCard.uuid, MJCard.types, MJCard.subtypes).where(or_(*conditions)).where(MJCard.uuid != source.uuid)
        ).all()

        scored = []
        for uuid, types_json, subtypes_json in rows:
            card_types = set(types_json) if isinstance(types_json, list) else set()
            card_subtypes = set(subtypes_json) if isinstance(subtypes_json, list) else set()
            all_card = card_types | card_subtypes
            intersection = all_source & all_card
            union = all_source | all_card
            if union:
                scored.append(ScoredCard(uuid=uuid, score=len(intersection) / len(union)))

        scored.sort(key=lambda s: s.score, reverse=True)
        return scored[:limit]

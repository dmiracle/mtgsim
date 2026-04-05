"""Oracle tag overlap similarity strategy."""

from mtgdb.models import MJCard, MJCardTag
from sqlmodel import select

from .base import ScoredCard, SimilarityStrategy, register_strategy


@register_strategy
class TagSimilarity(SimilarityStrategy):
    name = "tags"
    description = "Jaccard similarity on Scryfall oracle tags (removal, ramp, etc.)"

    def score(self, source: MJCard, session, limit: int = 100) -> list[ScoredCard]:
        # Get source card's tags
        source_tags = set(session.exec(select(MJCardTag.tag).where(MJCardTag.card_name == source.name)).all())
        if not source_tags:
            return []

        # Find cards that share at least one tag
        shared_cards = session.exec(
            select(MJCardTag.card_name, MJCardTag.tag).where(MJCardTag.tag.in_(source_tags))
        ).all()

        # Group tags by card name
        card_tags: dict[str, set[str]] = {}
        for card_name, tag in shared_cards:
            if card_name != source.name:
                card_tags.setdefault(card_name, set()).add(tag)

        if not card_tags:
            return []

        # Score by Jaccard similarity
        name_scores: dict[str, float] = {}
        for card_name, tags in card_tags.items():
            intersection = source_tags & tags
            union = source_tags | tags
            if union:
                name_scores[card_name] = len(intersection) / len(union)

        # Resolve names to UUIDs (one per name, best score)
        top_names = sorted(name_scores.keys(), key=lambda n: name_scores[n], reverse=True)[: limit * 2]
        if not top_names:
            return []

        name_uuid_rows = session.exec(select(MJCard.name, MJCard.uuid).where(MJCard.name.in_(top_names))).all()

        # One UUID per name
        name_to_uuid: dict[str, str] = {}
        for name, uuid in name_uuid_rows:
            if name not in name_to_uuid:
                name_to_uuid[name] = uuid

        scored = [
            ScoredCard(uuid=name_to_uuid[name], score=name_scores[name]) for name in top_names if name in name_to_uuid
        ]
        scored.sort(key=lambda s: s.score, reverse=True)
        return scored[:limit]

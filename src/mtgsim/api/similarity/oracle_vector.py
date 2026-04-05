"""Oracle text vector similarity strategy using sqlite-vec embeddings."""

from mtgdb.models import MJCard

from .base import ScoredCard, SimilarityStrategy, register_strategy


@register_strategy
class OracleVectorSimilarity(SimilarityStrategy):
    name = "oracle_vector"
    description = "Semantic similarity on oracle text via vector embeddings"

    def score(self, source: MJCard, session, limit: int = 100) -> list[ScoredCard]:
        if not source.oracle_text:
            return []

        from mtgdb.embeddings.search import search_similar_cards

        results = search_similar_cards(session, query=source.oracle_text, field_source="oracle", limit=limit + 1)

        # Filter out the source card
        filtered = [(card, dist) for card, dist in results if card.uuid != source.uuid]
        if not filtered:
            return []

        # Min-max rescale distances to 0-1 scores within the result set.
        # Best match (min distance) gets score 1.0, worst gets ~0.0.
        # This spreads scores across the full range, making them comparable
        # to Jaccard-based strategies. Raw 1/(1+d) scores cluster around
        # 0.55 regardless of query, which breaks weighted score merging.
        distances = [d for _, d in filtered]
        d_min = min(distances)
        d_max = max(distances)
        d_range = d_max - d_min

        scored = []
        for card, distance in filtered:
            if d_range > 0:
                score = 1.0 - (distance - d_min) / d_range
            else:
                score = 1.0  # all distances identical
            scored.append(ScoredCard(uuid=card.uuid, score=score))
        return scored[:limit]

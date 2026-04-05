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

        # Convert L2 distance to 0-1 score: 1/(1+distance) maps [0,∞) → (0,1]
        scored = []
        for card, distance in results:
            if card.uuid == source.uuid:
                continue
            scored.append(ScoredCard(uuid=card.uuid, score=1.0 / (1.0 + distance)))
        return scored[:limit]

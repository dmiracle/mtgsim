"""Oracle text vector similarity strategy using sqlite-vec embeddings."""

import math

from mtgdb.models import MJCard

from .base import ScoredCard, SimilarityStrategy, register_strategy

# Distance thresholds calibrated from observed L2 distances on 384-dim embeddings.
# Near-identical text: ~0.1-0.3, functionally similar: ~0.5-0.7, loosely related: ~0.8+
D_EXCELLENT = 0.4  # distances below this get scores near 1.0
D_MIDPOINT = 0.75  # sigmoid midpoint — distance that maps to score 0.5
D_STEEPNESS = 8.0  # how sharply the sigmoid transitions


def _distance_to_score(distance: float) -> float:
    """Convert L2 distance to 0-1 score using a sigmoid curve.

    Produces scores that reflect absolute match quality:
    - d ≈ 0.0 → score ≈ 1.0 (near-identical text)
    - d ≈ 0.75 → score ≈ 0.5 (moderately similar)
    - d ≈ 1.0+ → score → 0.0 (dissimilar)
    """
    return 1.0 / (1.0 + math.exp(D_STEEPNESS * (distance - D_MIDPOINT)))


@register_strategy
class OracleVectorSimilarity(SimilarityStrategy):
    name = "oracle_vector"
    description = "Semantic similarity on oracle text via vector embeddings"

    def score(self, source: MJCard, session, limit: int = 100) -> list[ScoredCard]:
        if not source.oracle_text:
            return []

        from mtgdb.embeddings.search import search_similar_cards

        results = search_similar_cards(session, query=source.oracle_text, field_source="oracle", limit=limit + 1)

        scored = []
        for card, distance in results:
            if card.uuid == source.uuid:
                continue
            scored.append(ScoredCard(uuid=card.uuid, score=_distance_to_score(distance)))
        return scored[:limit]

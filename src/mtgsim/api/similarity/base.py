"""Base classes for card similarity strategies."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from mtgdb.models import MJCard


@dataclass
class ScoredCard:
    """A card with a similarity score from a specific strategy."""

    uuid: str
    score: float  # 0.0 to 1.0


@dataclass
class MergedScore:
    """A card with merged scores from multiple strategies."""

    uuid: str
    total_score: float
    strategy_scores: dict[str, float] = field(default_factory=dict)


class SimilarityStrategy(ABC):
    """Abstract base for card similarity strategies.

    Each strategy takes a source card and returns scored candidates.
    Scores are normalized 0.0-1.0 where 1.0 is most similar.
    """

    name: str
    description: str

    @abstractmethod
    def score(self, source: MJCard, session, limit: int = 100) -> list[ScoredCard]:
        """Return cards scored by similarity to source.

        Args:
            source: The card to find similar cards for
            session: Database session
            limit: Max candidates to return

        Returns:
            List of ScoredCard sorted by score descending
        """
        ...


_registry: dict[str, type[SimilarityStrategy]] = {}


def register_strategy(cls: type[SimilarityStrategy]) -> type[SimilarityStrategy]:
    """Decorator to register a strategy class in the global registry."""
    _registry[cls.name] = cls
    return cls


def get_strategy(name: str) -> SimilarityStrategy:
    """Instantiate a registered strategy by name."""
    if name not in _registry:
        available = ", ".join(sorted(_registry.keys()))
        raise ValueError(f"Unknown strategy: {name}. Available: {available}")
    return _registry[name]()


def list_strategies() -> list[dict[str, str]]:
    """Return metadata for all registered strategies."""
    return [{"name": cls.name, "description": cls.description} for cls in _registry.values()]

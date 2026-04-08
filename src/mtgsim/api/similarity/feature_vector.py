"""Card feature vector — encodes card attributes as a numeric vector.

Each card becomes an n-dimensional vector encoding its keywords, tags,
colors, types, subtypes, mana value, power, and toughness. This enables
cosine similarity, deck profiling, and collection analytics.

The vector is built from a fixed vocabulary that is loaded once from the
database. The vocabulary maps each distinct value to a dimension index.
"""

import logging

from mtgdb.models import MJCard, MJCardTag
from sqlmodel import select

logger = logging.getLogger("mtgsim.api.similarity.feature_vector")

# Core card types (ignore un-set junk)
CARD_TYPES = [
    "Artifact",
    "Battle",
    "Conspiracy",
    "Creature",
    "Enchantment",
    "Instant",
    "Kindred",
    "Land",
    "Phenomenon",
    "Plane",
    "Planeswalker",
    "Scheme",
    "Sorcery",
    "Tribal",
    "Vanguard",
]

COLORS = ["W", "U", "B", "R", "G"]

# Mana value is encoded as one-hot buckets: 0, 1, 2, 3, 4, 5, 6, 7+
MANA_VALUE_BUCKETS = ["mv_0", "mv_1", "mv_2", "mv_3", "mv_4", "mv_5", "mv_6", "mv_7+"]

# Power/toughness encoded as buckets: 0, 1, 2, 3, 4, 5, 6, 7+, and a "has_pt" flag
PT_BUCKETS = ["pt_0", "pt_1", "pt_2", "pt_3", "pt_4", "pt_5", "pt_6", "pt_7+"]


class FeatureVocabulary:
    """Maps card attribute values to vector dimension indices.

    Built lazily from the database on first use, then cached.
    """

    def __init__(self):
        self._built = False
        self._dimensions: list[str] = []
        self._index: dict[str, int] = {}

    @property
    def size(self) -> int:
        return len(self._dimensions)

    @property
    def dimension_names(self) -> list[str]:
        return list(self._dimensions)

    def build(self, session) -> None:
        """Build the vocabulary from the database."""
        if self._built:
            return

        dims: list[str] = []

        # Colors (5 dims)
        for c in COLORS:
            dims.append(f"color:{c}")

        # Card types (fixed set)
        for t in CARD_TYPES:
            dims.append(f"type:{t}")

        # Mana value buckets
        dims.extend(MANA_VALUE_BUCKETS)

        # Power/toughness buckets + flags
        dims.append("has_power_toughness")
        for b in PT_BUCKETS:
            dims.append(f"power:{b}")
        for b in PT_BUCKETS:
            dims.append(f"toughness:{b}")

        # Tags (small fixed set from mj_card_tag)
        tag_rows = session.exec(select(MJCardTag.tag).distinct().order_by(MJCardTag.tag)).all()
        for tag in tag_rows:
            dims.append(f"tag:{tag}")

        # Keywords and subtypes via raw SQL (json_each not easily expressed in SQLAlchemy)
        from sqlalchemy import text

        kw_rows = session.execute(
            text("SELECT DISTINCT value FROM mj_card, json_each(mj_card.keywords) WHERE value != '' ORDER BY value")
        ).fetchall()
        for (kw,) in kw_rows:
            dims.append(f"keyword:{kw}")

        st_rows = session.execute(
            text("SELECT DISTINCT value FROM mj_card, json_each(mj_card.subtypes) WHERE value != '' ORDER BY value")
        ).fetchall()
        for (st,) in st_rows:
            dims.append(f"subtype:{st}")

        self._dimensions = dims
        self._index = {name: i for i, name in enumerate(dims)}
        self._built = True
        logger.info(f"Feature vocabulary built: {len(dims)} dimensions")

    def encode(self, card: MJCard, tags: list[str] | None = None) -> list[float]:
        """Encode a card as a feature vector.

        Args:
            card: The MJCard to encode
            tags: Oracle tags for this card (from mj_card_tag). Pass None to skip.

        Returns:
            Float vector of length self.size with 1.0 for present features.
        """
        vec = [0.0] * self.size

        def _set(name: str, value: float = 1.0):
            idx = self._index.get(name)
            if idx is not None:
                vec[idx] = value

        # Colors
        for c in card.color_identity or []:
            _set(f"color:{c}")

        # Types
        for t in card.types or []:
            _set(f"type:{t}")

        # Mana value bucket
        if card.mana_value is not None:
            mv = int(min(card.mana_value, 7))
            if mv >= 7:
                _set("mv_7+")
            else:
                _set(f"mv_{mv}")

        # Power/toughness
        if card.power is not None and card.toughness is not None:
            _set("has_power_toughness")
            try:
                p = int(min(float(card.power), 7))
                _set(f"power:pt_{max(0, p) if p < 7 else '7+'}")
            except ValueError:
                pass
            try:
                t = int(min(float(card.toughness), 7))
                _set(f"toughness:pt_{max(0, t) if t < 7 else '7+'}")
            except ValueError:
                pass

        # Tags
        if tags:
            for tag in tags:
                _set(f"tag:{tag}")

        # Keywords
        for kw in card.keywords or []:
            _set(f"keyword:{kw}")

        # Subtypes
        for st in card.subtypes or []:
            _set(f"subtype:{st}")

        return vec


# Module-level singleton
_vocabulary = FeatureVocabulary()


def get_vocabulary() -> FeatureVocabulary:
    return _vocabulary


def encode_card(card: MJCard, session, tags: list[str] | None = None) -> list[float]:
    """Encode a card as a feature vector, building vocabulary if needed."""
    _vocabulary.build(session)
    return _vocabulary.encode(card, tags)

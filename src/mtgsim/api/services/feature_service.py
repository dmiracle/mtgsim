"""Feature vector service — batch encoding and aggregation."""

import logging
import math

from mtgdb.models import MJCard, MJCardLegality, MJCardTag, MJDeck, MJDeckCard, UserCard, UserDeck, UserDeckCard
from mtgdb.session import get_session
from sqlmodel import func, select

from mtgsim.api.data.helpers import add_price_join, apply_card_filters, fts_name_search_uuids
from mtgsim.api.similarity.compact_vector import compact_dimension_names, compact_size, encode_compact

logger = logging.getLogger("mtgsim.api.services.feature")


def _fetch_tags_map(session, card_names: list[str]) -> dict[str, list[str]]:
    """Batch fetch tags for card names."""
    if not card_names:
        return {}
    rows = session.exec(select(MJCardTag.card_name, MJCardTag.tag).where(MJCardTag.card_name.in_(card_names))).all()
    tags_map: dict[str, list[str]] = {}
    for name, tag in rows:
        tags_map.setdefault(name, []).append(tag)
    return tags_map


def _normalize_vector(vec: list[float]) -> list[float]:
    """L2-normalize a vector. Returns zero vector if input is all zeros."""
    magnitude = math.sqrt(sum(v * v for v in vec))
    if magnitude == 0:
        return vec
    return [v / magnitude for v in vec]


class FeatureService:
    def batch_compact_vectors(
        self,
        q: str | None = None,
        text: str | None = None,
        set_code: str | None = None,
        set_codes: list[str] | None = None,
        rarity: str | None = None,
        card_type: str | None = None,
        colors: list[str] | None = None,
        mana_values: list[int] | None = None,
        format_legal: str | None = None,
        keywords: list[str] | None = None,
        tags: list[str] | None = None,
        price_min: float | None = None,
        price_max: float | None = None,
        owns: bool | None = None,
        wants: bool | None = None,
        limit: int = 200,
    ) -> dict:
        """Get compact vectors for cards matching the given filters."""
        with get_session() as session:
            query = select(MJCard).outerjoin(UserCard, MJCard.uuid == UserCard.card_uuid)

            if q:
                name_uuids = fts_name_search_uuids(session, q)
                query = query.where(MJCard.uuid.in_(name_uuids))
            if format_legal:
                query = query.join(
                    MJCardLegality,
                    (MJCard.uuid == MJCardLegality.card_uuid)
                    & (MJCardLegality.format == format_legal)
                    & (MJCardLegality.status == "Legal"),
                )
            if set_code:
                query = query.where(MJCard.set_code == set_code)
            if set_codes:
                query = query.where(MJCard.set_code.in_(set_codes))
            if price_min is not None or price_max is not None:
                query, price_col = add_price_join(query)
                if price_min is not None:
                    query = query.where(price_col >= price_min)
                if price_max is not None:
                    query = query.where(price_col <= price_max)

            query = apply_card_filters(
                query,
                rarity=rarity,
                card_type=card_type,
                text=text,
                colors=colors,
                mana_values=mana_values,
                keywords=keywords,
                tags=tags,
                owns=owns,
                wants=wants,
                session=session,
            )

            # One printing per name
            min_uuid_subq = select(func.min(MJCard.uuid)).group_by(MJCard.name)
            query = query.where(MJCard.uuid.in_(min_uuid_subq))
            query = query.limit(limit)

            cards = session.exec(query).all()
            card_names = [c.name for c in cards]
            tags_map = _fetch_tags_map(session, card_names)

            results = []
            for card in cards:
                vec = encode_compact(card, tags=tags_map.get(card.name))
                results.append(
                    {
                        "uuid": card.uuid,
                        "name": card.printed_name or card.name,
                        "vector": vec,
                    }
                )

            return {
                "cards": results,
                "dimensions": compact_size(),
                "dimension_names": compact_dimension_names(),
                "total": len(results),
            }

    def aggregate_vectors(
        self,
        q: str | None = None,
        text: str | None = None,
        set_code: str | None = None,
        set_codes: list[str] | None = None,
        rarity: str | None = None,
        card_type: str | None = None,
        colors: list[str] | None = None,
        mana_values: list[int] | None = None,
        format_legal: str | None = None,
        keywords: list[str] | None = None,
        tags: list[str] | None = None,
        price_min: float | None = None,
        price_max: float | None = None,
        owns: bool | None = None,
        wants: bool | None = None,
    ) -> dict:
        """Compute normalized aggregate vector for cards matching filters."""
        batch = self.batch_compact_vectors(
            q=q,
            text=text,
            set_code=set_code,
            set_codes=set_codes,
            rarity=rarity,
            card_type=card_type,
            colors=colors,
            mana_values=mana_values,
            format_legal=format_legal,
            keywords=keywords,
            tags=tags,
            price_min=price_min,
            price_max=price_max,
            owns=owns,
            wants=wants,
            limit=4096,
        )

        dims = compact_size()
        summed = [0.0] * dims
        for card in batch["cards"]:
            for i, v in enumerate(card["vector"]):
                summed[i] += v

        normalized = _normalize_vector(summed)

        return {
            "vector": [round(v, 6) for v in normalized],
            "dimensions": dims,
            "dimension_names": compact_dimension_names(),
            "card_count": batch["total"],
        }

    def deck_vector(self, identifier: str) -> dict | None:
        """Compute normalized aggregate vector for a deck (weighted by card count)."""
        with get_session() as session:
            # Try user deck
            cards_with_counts = []
            try:
                deck_id = int(identifier)
                deck = session.exec(select(UserDeck).where(UserDeck.id == deck_id)).first()
                if deck:
                    rows = session.exec(
                        select(MJCard, UserDeckCard.count)
                        .join(UserDeckCard, MJCard.uuid == UserDeckCard.card_uuid)
                        .where(UserDeckCard.deck_id == deck_id)
                    ).all()
                    cards_with_counts = [(card, count or 1) for card, count in rows]
            except ValueError:
                pass

            # Try precon deck
            if not cards_with_counts:
                file_name = identifier
                if file_name.endswith(".json"):
                    file_name = file_name[:-5]
                deck = session.exec(select(MJDeck).where(MJDeck.file_name == file_name)).first()
                if not deck:
                    return None
                rows = session.exec(
                    select(MJCard, MJDeckCard.count)
                    .join(MJDeckCard, MJCard.uuid == MJDeckCard.card_uuid)
                    .where(MJDeckCard.deck_uuid == deck.uuid)
                ).all()
                cards_with_counts = [(card, count or 1) for card, count in rows]

            if not cards_with_counts:
                return None

            card_names = [c.name for c, _ in cards_with_counts]
            tags_map = _fetch_tags_map(session, card_names)

            dims = compact_size()
            summed = [0.0] * dims
            total_cards = 0
            for card, count in cards_with_counts:
                vec = encode_compact(card, tags=tags_map.get(card.name))
                for i, v in enumerate(vec):
                    summed[i] += v * count
                total_cards += count

            normalized = _normalize_vector(summed)

            return {
                "vector": [round(v, 6) for v in normalized],
                "dimensions": dims,
                "dimension_names": compact_dimension_names(),
                "card_count": total_cards,
            }

    def compute_grid_layout(self, sample_size: int = 5000) -> dict:
        """Compute optimal 8x8 grid positions for the 64 compact features.

        Uses PCA on the feature co-occurrence matrix to find natural 2D positions,
        then the Hungarian algorithm to snap features to grid cells while
        minimizing displacement.

        The result is deterministic for a given card database and can be cached.
        """
        import numpy as np
        from scipy.optimize import linear_sum_assignment
        from sklearn.decomposition import PCA

        with get_session() as session:
            cards = session.exec(select(MJCard).where(MJCard.oracle_text.is_not(None)).limit(sample_size)).all()
            card_names = [c.name for c in cards]
            tags_map = _fetch_tags_map(session, card_names)

            matrix = np.array([encode_compact(c, tags=tags_map.get(c.name)) for c in cards])

        # Co-occurrence matrix: how often features appear together
        cooc = matrix.T @ matrix  # 64×64

        # PCA to 2D
        pca = PCA(n_components=2)
        positions = pca.fit_transform(cooc)

        # Normalize to [0, 7] range
        for dim in range(2):
            mn, mx = positions[:, dim].min(), positions[:, dim].max()
            if mx > mn:
                positions[:, dim] = (positions[:, dim] - mn) / (mx - mn) * 7

        # Grid cell centers
        grid = np.array([(r, c) for r in range(8) for c in range(8)], dtype=float)

        # Cost matrix: Euclidean distance from PCA position to each grid cell
        cost = np.zeros((64, 64))
        for i in range(64):
            for j in range(64):
                cost[i, j] = np.sqrt((positions[i, 0] - grid[j, 0]) ** 2 + (positions[i, 1] - grid[j, 1]) ** 2)

        # Hungarian algorithm: optimal assignment minimizing total displacement
        feat_indices, grid_indices = linear_sum_assignment(cost)

        dim_names = compact_dimension_names()
        layout = []
        for feat_idx, grid_idx in zip(feat_indices, grid_indices, strict=True):
            r, c = int(grid[grid_idx, 0]), int(grid[grid_idx, 1])
            layout.append(
                {
                    "feature": dim_names[feat_idx],
                    "row": r,
                    "col": c,
                    "index": int(feat_idx),
                }
            )

        layout.sort(key=lambda x: (x["row"], x["col"]))

        return {
            "grid_size": 8,
            "dimensions": compact_size(),
            "layout": layout,
            "pca_variance_explained": [round(v, 4) for v in pca.explained_variance_ratio_.tolist()],
            "cards_sampled": len(cards),
        }


feature_service = FeatureService()

"""Similarity search service — orchestrates strategies and merges scores."""

import logging

from mtgdb.models import MJCard, MJCardIdentifier, UserCard
from mtgdb.session import get_session
from sqlmodel import select

from mtgsim.api.data.helpers import build_image_url
from mtgsim.api.similarity import MergedScore, get_strategy, list_strategies

logger = logging.getLogger("mtgsim.api.services.similarity")


def _build_card_summary(card: MJCard, scryfall_id: str | None, user_card=None) -> dict:
    """Build a lightweight card summary dict for similarity results."""
    owns = False
    total_owned = 0
    if user_card:
        total_owned = (user_card.quantity_owned or 0) + (user_card.quantity_owned_foil or 0)
        owns = total_owned > 0
    return {
        "uuid": card.uuid,
        "name": card.printed_name or card.name,
        "type": card.type_line,
        "mana_cost": card.mana_cost,
        "mana_value": card.mana_value,
        "rarity": card.rarity,
        "set_code": card.set_code,
        "color_identity": card.color_identity or [],
        "image_url": build_image_url(scryfall_id),
        "owns": owns,
        "total_owned": total_owned,
    }


class SimilarityService:
    def search_similar(
        self,
        card_uuid: str,
        strategy_names: list[str],
        weights: list[float] | None = None,
        limit: int = 20,
        candidate_limit: int = 200,
    ) -> dict | None:
        """Find cards similar to the given card using specified strategies.

        Returns dict with source card, strategies used, and scored results,
        or None if card not found.
        """
        if not weights:
            weights = [1.0] * len(strategy_names)

        if len(weights) != len(strategy_names):
            raise ValueError(f"Weights count ({len(weights)}) must match strategies count ({len(strategy_names)})")

        with get_session() as session:
            source = session.exec(select(MJCard).where(MJCard.uuid == card_uuid)).first()
            if not source:
                return None

            # Run each strategy and collect scored candidates
            all_scores: dict[str, dict[str, float]] = {}
            for name, weight in zip(strategy_names, weights, strict=True):
                strategy = get_strategy(name)
                candidates = strategy.score(source, session, limit=candidate_limit)
                for sc in candidates:
                    all_scores.setdefault(sc.uuid, {})[name] = sc.score * weight

            # Merge: weighted average
            total_weight = sum(weights)
            merged: list[MergedScore] = []
            for uuid, strat_scores in all_scores.items():
                total = sum(strat_scores.values())
                merged.append(
                    MergedScore(
                        uuid=uuid,
                        total_score=total / total_weight,
                        strategy_scores={k: round(v, 4) for k, v in strat_scores.items()},
                    )
                )

            merged.sort(key=lambda m: m.total_score, reverse=True)
            merged = merged[:limit]

            # Hydrate source and result cards with summary data
            result_uuids = [m.uuid for m in merged]
            all_uuids = [source.uuid] + result_uuids

            # Batch fetch identifiers and user cards
            ident_map = {}
            if all_uuids:
                for card_uuid_val, scryfall_id in session.exec(
                    select(MJCardIdentifier.card_uuid, MJCardIdentifier.scryfall_id).where(
                        MJCardIdentifier.card_uuid.in_(all_uuids)
                    )
                ).all():
                    ident_map[card_uuid_val] = scryfall_id

            user_map = {}
            if all_uuids:
                for uc in session.exec(select(UserCard).where(UserCard.card_uuid.in_(all_uuids))).all():
                    user_map[uc.card_uuid] = uc

            # Batch fetch result MJCard objects
            card_map = {source.uuid: source}
            if result_uuids:
                for card in session.exec(select(MJCard).where(MJCard.uuid.in_(result_uuids))).all():
                    card_map[card.uuid] = card

            source_summary = _build_card_summary(source, ident_map.get(source.uuid), user_map.get(source.uuid))

            results = []
            for m in merged:
                card = card_map.get(m.uuid)
                if not card:
                    continue
                results.append(
                    {
                        "card": _build_card_summary(card, ident_map.get(m.uuid), user_map.get(m.uuid)),
                        "score": round(m.total_score, 4),
                        "strategy_scores": m.strategy_scores,
                    }
                )

            return {
                "source": source_summary,
                "strategies_used": strategy_names,
                "results": results,
                "total": len(results),
            }

    def get_strategies(self) -> list[dict[str, str]]:
        return list_strategies()


similarity_service = SimilarityService()

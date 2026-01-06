"""Deck service - handles deck data access and processing."""

from mtgsim.api.data import decks_data
from mtgsim.api.models.common import KeywordCounts, Pagination
from mtgsim.api.models.deck import (
    DeckCard,
    DeckDetail,
    DeckFilters,
    DeckLegality,
    DeckListResponse,
    DeckMeta,
    DeckPrice,
    DeckStats,
    DeckSummary,
    PriceBySource,
)


class DeckService:
    """Service for deck-related operations."""

    async def list_decks(
        self,
        q: str | None = None,
        format: str | None = None,
        set_code: str | None = None,
        deck_type: str | None = None,
        colors: list[str] | None = None,
        card_count_min: int | None = None,
        card_count_max: int | None = None,
        price_min: float | None = None,
        price_max: float | None = None,
        sort: str = "name",
        order: str = "asc",
        page: int = 1,
        limit: int = 50,
    ) -> DeckListResponse:
        """List and filter decks with pagination."""
        decks, total = decks_data.list_decks(
            q=q,
            format_filter=format,
            set_code=set_code,
            deck_type=deck_type,
            colors=colors,
            card_count_min=card_count_min,
            card_count_max=card_count_max,
            price_min=price_min,
            price_max=price_max,
            sort=sort,
            order=order,
            page=page,
            limit=limit,
        )

        data = [
            DeckSummary(
                file=d["file"],
                name=d["name"],
                code=d["code"],
                card_count=d["card_count"],
                colors=d["colors"],
                price=d.get("price"),
                release_date=d["release_date"],
                legality=DeckLegality(),
            )
            for d in decks
        ]

        pages = (total + limit - 1) // limit if limit > 0 else 1

        return DeckListResponse(
            data=data,
            pagination=Pagination(page=page, limit=limit, total=total, pages=pages),
            filters=DeckFilters(
                formats=decks_data.get_available_formats(),
                sets=decks_data.get_available_sets(),
                color_combinations=[],
            ),
        )

    async def get_deck(self, file: str) -> DeckDetail | None:
        """Get full deck details including cards and statistics."""
        deck = decks_data.get_deck(file)
        if not deck:
            return None

        meta = deck["meta"]
        stats = deck["stats"]
        legality = deck["legality"]

        return DeckDetail(
            meta=DeckMeta(
                file=meta["file"],
                name=meta["name"],
                code=meta["code"],
                release_date=meta["release_date"],
            ),
            legality=DeckLegality(
                standard=legality.get("standard", False),
                pioneer=legality.get("pioneer", False),
                modern=legality.get("modern", False),
                legacy=legality.get("legacy", False),
                vintage=legality.get("vintage", False),
                commander=legality.get("commander", False),
            ),
            colors=deck["colors"],
            price=DeckPrice(
                total=deck.get("price") or 0,
                by_source=PriceBySource(),
            ),
            commander=[
                DeckCard(
                    uuid=c["uuid"],
                    name=c["name"],
                    count=c["count"],
                    mana_cost=c["mana_cost"],
                    mana_value=c["mana_value"],
                    type=c["type"],
                    rarity=c["rarity"],
                    text=c.get("text"),
                    price=c.get("price"),
                    image_url=c.get("image_url"),
                )
                for c in deck["commander"]
            ],
            main_board=[
                DeckCard(
                    uuid=c["uuid"],
                    name=c["name"],
                    count=c["count"],
                    mana_cost=c["mana_cost"],
                    mana_value=c["mana_value"],
                    type=c["type"],
                    rarity=c["rarity"],
                    text=c.get("text"),
                    price=c.get("price"),
                    image_url=c.get("image_url"),
                )
                for c in deck["main_board"]
            ],
            side_board=[
                DeckCard(
                    uuid=c["uuid"],
                    name=c["name"],
                    count=c["count"],
                    mana_cost=c["mana_cost"],
                    mana_value=c["mana_value"],
                    type=c["type"],
                    rarity=c["rarity"],
                    text=c.get("text"),
                    price=c.get("price"),
                    image_url=c.get("image_url"),
                )
                for c in deck["side_board"]
            ],
            stats=DeckStats(
                total_cards=stats["total_cards"],
                unique_cards=stats["unique_cards"],
                mana_curve=stats["mana_curve"],
                type_distribution=stats["type_distribution"],
                rarity_distribution=stats["rarity_distribution"],
                color_distribution=stats["color_distribution"],
                price_histogram=[],
                keywords=KeywordCounts(
                    ability_words={},
                    keyword_abilities={},
                    keyword_actions={},
                ),
            ),
        )

    async def get_deck_raw(self, file: str) -> dict | None:
        """Get raw deck data."""
        deck = decks_data.get_deck(file)
        if not deck:
            return None
        return deck

    async def get_available_sets(self) -> list[str]:
        """Get list of set codes that have decks."""
        return decks_data.get_available_sets()


# Singleton instance
deck_service = DeckService()

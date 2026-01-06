"""Deck service - handles deck data access and processing."""

from mtgsim.api.data import decks_data
from mtgsim.api.data.pricing import PriceUtility
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
from mtgsim.api.models.mappers import DTOMapper
from mtgsim.config import config
from mtgsim.reference.repository import ReferenceRepository


class DeckService:
    """Service for deck-related operations."""

    def __init__(self):
        """Initialize deck service with dependencies."""
        self.reference_repo = ReferenceRepository(config)
        self.price_utility = PriceUtility(self.reference_repo)
        self.dto_mapper = DTOMapper()

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

        # Use DTO mapper to convert decks to DeckSummary models
        data = []
        for d in decks:
            # Create a mock row object for the mapper
            row_dict = {
                "file": d["file"],
                "name": d["name"],
                "code": d["code"],
                "card_count": d["card_count"],
                "colors": d["colors"] if isinstance(d["colors"], str) else str(d["colors"]),
                "price": d.get("price"),
                "releaseDate": d["release_date"],
                "legalities": "{}"  # Default empty legalities
            }
            
            # Convert dict to sqlite3.Row-like object
            class MockRow:
                def __init__(self, data):
                    self._data = data
                def __getitem__(self, key):
                    return self._data[key]
                def get(self, key, default=None):
                    return self._data.get(key, default)
                def keys(self):
                    return self._data.keys()
            
            mock_row = MockRow(row_dict)
            data.append(self.dto_mapper.map_deck_summary(mock_row))

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

        # Calculate deck price using price utility
        all_cards = deck["commander"] + deck["main_board"] + deck["side_board"]
        deck_total_price = self.price_utility.calculate_deck_total(all_cards)

        # Get individual card prices for deck cards
        all_uuids = [c["uuid"] for c in all_cards if c.get("uuid")]
        price_map = self.price_utility.get_bulk_average_prices(all_uuids)

        def add_prices_to_cards(cards):
            """Add price information to deck cards."""
            result = []
            for c in cards:
                price = price_map.get(c["uuid"])
                result.append(DeckCard(
                    uuid=c["uuid"],
                    name=c["name"],
                    count=c["count"],
                    mana_cost=c["mana_cost"],
                    mana_value=c["mana_value"],
                    type=c["type"],
                    rarity=c["rarity"],
                    text=c.get("text"),
                    price=price,
                    image_url=c.get("image_url"),
                ))
            return result

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
                total=deck_total_price,
                by_source=PriceBySource(),
            ),
            commander=add_prices_to_cards(deck["commander"]),
            main_board=add_prices_to_cards(deck["main_board"]),
            side_board=add_prices_to_cards(deck["side_board"]),
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

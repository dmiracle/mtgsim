"""Card service - handles card data access and processing."""

from mtgsim.api.data import cards_data
from mtgsim.api.data.pricing import PriceUtility
from mtgsim.api.models.card import (
    CardAppearance,
    CardDetail,
    CardLegalities,
    CardListResponse,
    CardPrinting,
    CardSummary,
)
from mtgsim.api.models.common import Pagination
from mtgsim.api.models.deck import PriceBySource
from mtgsim.api.models.mappers import DTOMapper
from mtgsim.config import config
from mtgsim.reference.repository import ReferenceRepository


class CardService:
    """Service for card-related operations."""

    def __init__(self):
        """Initialize card service with dependencies."""
        self.reference_repo = ReferenceRepository(config)
        self.price_utility = PriceUtility(self.reference_repo)
        self.dto_mapper = DTOMapper()

    async def search_cards(
        self,
        q: str | None = None,
        set_code: str | None = None,
        rarity: str | None = None,
        card_type: str | None = None,
        colors: list[str] | None = None,
        price_min: float | None = None,
        price_max: float | None = None,
        sort: str = "name",
        order: str = "asc",
        page: int = 1,
        limit: int = 50,
    ) -> CardListResponse:
        """Search cards with filters."""
        cards, total = cards_data.search_cards(
            q=q,
            set_code=set_code,
            rarity=rarity,
            card_type=card_type,
            colors=colors,
            sort=sort,
            order=order,
            page=page,
            limit=limit,
        )

        # Get bulk prices for all cards
        uuids = [c["uuid"] for c in cards if c.get("uuid")]
        price_map = self.price_utility.get_bulk_average_prices(uuids)

        # Use DTO mapper to convert cards to CardSummary models
        data = []
        for c in cards:
            # Create a mock row object for the mapper
            row_dict = {
                "uuid": c["uuid"],
                "name": c["name"],
                "type": c["type"],
                "manaCost": c["mana_cost"],
                "manaValue": c["mana_value"],
                "rarity": c["rarity"],
                "setCode": c["set_code"],
                "colorIdentity": c["color_identity"],
                "text": c.get("text"),
                "image_url": c.get("image_url"),
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
            price = price_map.get(c["uuid"])
            data.append(self.dto_mapper.map_card_summary(mock_row, price))

        pages = (total + limit - 1) // limit if limit > 0 else 1

        return CardListResponse(
            data=data,
            pagination=Pagination(page=page, limit=limit, total=total, pages=pages),
        )

    async def get_card(self, uuid: str) -> CardDetail | None:
        """Get full card details."""
        card = cards_data.get_card(uuid)
        if not card:
            return None

        # Get legalities
        legalities = card.get("legalities", {})

        # Get prices using price utility
        tcg_price = self.price_utility.get_tcgplayer_price(uuid)

        # Get appearances in decks
        appearances = cards_data.get_card_appearances(uuid)

        # Get other printings
        other_printings = cards_data.get_other_printings(uuid)

        return CardDetail(
            uuid=card["uuid"],
            name=card["name"],
            mana_cost=card["mana_cost"],
            mana_value=card["mana_value"],
            type=card["type"],
            types=card["types"],
            subtypes=card["subtypes"],
            text=card["text"],
            flavor_text=card["flavor_text"],
            rarity=card["rarity"],
            set_code=card["set_code"],
            set_name=card["set_name"],
            color_identity=card["color_identity"],
            colors=card["colors"],
            power=card["power"],
            toughness=card["toughness"],
            image_url=card.get("image_url"),
            prices=PriceBySource(
                tcgplayer=tcg_price,
            ),
            legalities=CardLegalities(
                standard=legalities.get("standard", "Not Legal"),
                pioneer=legalities.get("pioneer", "Not Legal"),
                modern=legalities.get("modern", "Not Legal"),
                legacy=legalities.get("legacy", "Not Legal"),
                vintage=legalities.get("vintage", "Not Legal"),
                commander=legalities.get("commander", "Not Legal"),
            ),
            appears_in_decks=[
                CardAppearance(
                    file=a["file"],
                    name=a["name"],
                    count=a["count"],
                )
                for a in appearances
            ],
            other_printings=[
                CardPrinting(
                    set_code=p["set_code"],
                    set_name=p["set_name"],
                    uuid=p["uuid"],
                )
                for p in other_printings
            ],
        )

    async def get_card_by_name(self, name: str) -> list[CardSummary]:
        """Get all printings of a card by name."""
        cards = cards_data.get_cards_by_name(name)
        
        # Get bulk prices for all cards
        uuids = [c["uuid"] for c in cards if c.get("uuid")]
        price_map = self.price_utility.get_bulk_average_prices(uuids)
        
        # Use DTO mapper to convert cards to CardSummary models
        result = []
        for c in cards:
            # Create a mock row object for the mapper
            row_dict = {
                "uuid": c["uuid"],
                "name": c["name"],
                "type": "",
                "manaCost": None,
                "manaValue": None,
                "rarity": c["rarity"],
                "setCode": c["set_code"],
                "colorIdentity": "[]",
                "text": None,
                "image_url": None,
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
            price = price_map.get(c["uuid"])
            result.append(self.dto_mapper.map_card_summary(mock_row, price))
        
        return result

    async def get_cards_in_deck(self, deck_file: str) -> list[str]:
        """Get all card UUIDs in a deck."""
        return []


# Singleton instance
card_service = CardService()

"""Deck service - handles deck data access and processing."""

import logging

from mtgsim.api.data import decks_data
from mtgsim.api.data.keywords import keywords_data
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

logger = logging.getLogger("mtgsim.api.services.deck")


class DeckService:
    """Service for deck-related operations."""

    async def list_decks(
        self,
        q: str | None = None,
        format: str | None = None,
        set_code: str | None = None,
        deck_type: str | None = None,
        colors: list[str] | None = None,
        colors_mode: str = "subset",
        card_count_min: int | None = None,
        card_count_max: int | None = None,
        price_min: float | None = None,
        price_max: float | None = None,
        source: str | None = None,
        sort: str = "name",
        order: str = "asc",
        page: int = 1,
        limit: int = 50,
    ) -> DeckListResponse:
        """List and filter decks with pagination."""
        logger.debug(f"list_decks: q={q} format={format} set_code={set_code} sort={sort} page={page} limit={limit}")
        decks, total = decks_data.list_decks(
            q=q,
            set_code=set_code,
            deck_type=deck_type,
            source=source,
            colors=colors,
            colors_mode=colors_mode,
            card_count_min=card_count_min,
            card_count_max=card_count_max,
            sort=sort,
            order=order,
            page=page,
            limit=limit,
        )

        logger.debug(f"list_decks: got {len(decks)} decks, total={total}")
        data = []
        for d in decks:
            # Handle both precon and user deck formats
            file_name = d.get("file") or str(d.get("id"))
            data.append(
                DeckSummary(
                    uuid=d.get("uuid", ""),
                    file=file_name,
                    name=d["name"],
                    code=d.get("code", ""),
                    deck_type=d.get("deck_type"),
                    card_count=d.get("card_count", 0),
                    colors=d.get("colors", []),
                    price=d.get("price"),
                    release_date=d.get("release_date"),
                    legality=DeckLegality(),
                    source=d.get("source", "precon"),
                )
            )

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
        logger.debug(f"get_deck: loading file={file}")
        deck = decks_data.get_deck(file)
        if not deck:
            return None

        meta = deck.get("meta", {})
        stats = deck.get("stats", {})
        legality = deck.get("legality", {})

        # Handle both precon and user deck formats
        file_name = meta.get("file") or str(deck.get("id"))
        source = deck.get("source", "precon")

        def make_deck_card(c: dict, board: str | None = None) -> DeckCard:
            count = c.get("count", 1)
            owned_count = c.get("owned_count", 0)
            missing_count = max(0, count - owned_count)
            return DeckCard(
                uuid=c.get("card_uuid") or c.get("uuid", ""),
                name=c["name"],
                count=count,
                board=board,
                mana_cost=c.get("mana_cost"),
                mana_value=c.get("mana_value"),
                type=", ".join(c.get("types", [])) if c.get("types") else c.get("type", ""),
                types=c.get("types", []),
                colors=c.get("colors", []),
                rarity=c.get("rarity", ""),
                tags=c.get("tags", []),
                text=c.get("text"),
                price=c.get("price"),
                image_url=c.get("image_url"),
                owns_enough=c.get("owns_enough", False),
                owned_count=owned_count,
                missing_count=missing_count,
            )

        deck_uuid = deck.get("uuid", meta.get("uuid", ""))

        return DeckDetail(
            meta=DeckMeta(
                uuid=deck_uuid,
                file=file_name,
                name=meta.get("name", ""),
                code=meta.get("code", ""),
                deck_type=meta.get("deck_type"),
                release_date=meta.get("release_date"),
                description=meta.get("description"),
                format=meta.get("format"),
                source=source,
            ),
            legality=DeckLegality(
                standard=legality.get("standard", False),
                pioneer=legality.get("pioneer", False),
                modern=legality.get("modern", False),
                legacy=legality.get("legacy", False),
                vintage=legality.get("vintage", False),
                commander=legality.get("commander", False),
            ),
            colors=deck.get("colors", []),
            price=DeckPrice(
                total=deck.get("price") or 0,
                by_source=PriceBySource(),
            ),
            commander=[make_deck_card(c, "commander") for c in deck.get("commander", [])],
            main_board=[make_deck_card(c, "main") for c in deck.get("main_board", [])],
            side_board=[make_deck_card(c, "side") for c in deck.get("side_board", [])],
            stats=DeckStats(
                total_cards=stats.get("total_cards", 0),
                unique_cards=stats.get("unique_cards", 0),
                mana_curve=stats.get("mana_curve", {}),
                type_distribution=stats.get("type_distribution", {}),
                rarity_distribution=stats.get("rarity_distribution", {}),
                color_distribution=stats.get("color_distribution", {}),
                price_histogram=stats.get("price_histogram", []),
                keywords=KeywordCounts(**keywords_data.categorize_keyword_freq(stats.get("keyword_freq", {}))),
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

    async def create_user_deck(
        self,
        name: str,
        description: str | None = None,
        format: str | None = None,
    ) -> dict:
        """Create a new user deck."""
        return decks_data.create_user_deck(name=name, description=description, format=format)

    async def update_user_deck(
        self,
        deck_id: int,
        name: str | None = None,
        description: str | None = None,
        format: str | None = None,
    ) -> dict | None:
        """Update a user deck's metadata."""
        return decks_data.update_user_deck(deck_id, name=name, description=description, format=format)

    async def duplicate_deck(self, identifier: str) -> dict | None:
        """Duplicate any deck (user or precon) as a new user deck."""
        return decks_data.duplicate_deck(identifier)

    async def add_card_to_deck(
        self,
        deck_id: int,
        card_uuid: str,
        count: int = 1,
        board: str = "main",
        is_foil: bool = False,
    ) -> dict | None:
        """Add a card to a user deck."""
        return decks_data.add_card_to_deck(
            deck_id=deck_id,
            card_uuid=card_uuid,
            count=count,
            board=board,
            is_foil=is_foil,
        )

    async def remove_card_from_deck(
        self,
        deck_id: int,
        card_uuid: str,
        board: str | None = None,
    ) -> bool:
        """Remove a card from a user deck."""
        return decks_data.remove_card_from_deck(deck_id=deck_id, card_uuid=card_uuid, board=board)

    async def delete_user_deck(self, deck_id: int) -> bool:
        """Delete a user deck."""
        return decks_data.delete_user_deck(deck_id)

    async def get_pinned_decks(self) -> list[DeckSummary]:
        """Get summaries for all pinned decks in pin order."""
        summaries = decks_data.get_pinned_summaries()
        return [
            DeckSummary(
                uuid=d.get("uuid", ""),
                file=d.get("file") or str(d.get("id")),
                name=d["name"],
                code=d.get("code", ""),
                deck_type=d.get("deck_type"),
                card_count=d.get("card_count", 0),
                colors=d.get("colors", []),
                price=d.get("price"),
                release_date=d.get("release_date"),
                legality=DeckLegality(),
                source=d.get("source", "precon"),
            )
            for d in summaries
        ]

    async def pin_deck(self, deck_uuid: str) -> bool:
        """Pin a deck by UUID. Returns True if newly pinned."""
        return decks_data.pin_deck(deck_uuid)

    async def unpin_deck(self, deck_uuid: str) -> bool:
        """Unpin a deck by UUID. Returns True if was pinned."""
        return decks_data.unpin_deck(deck_uuid)


# Singleton instance
deck_service = DeckService()

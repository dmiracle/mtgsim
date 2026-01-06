"""Set service - handles set data access and processing."""

from mtgsim.api.data import sets_data
from mtgsim.api.models.common import KeywordCounts, Pagination
from mtgsim.api.models.deck import PriceBySource
from mtgsim.api.models.set import (
    ColorWordFrequencies,
    SetCard,
    SetCardsResponse,
    SetDetail,
    SetFilters,
    SetListResponse,
    SetMeta,
    SetPrice,
    SetStats,
    SetSummary,
)


class SetService:
    """Service for set-related operations."""

    async def list_sets(
        self,
        q: str | None = None,
        set_type: str | None = None,
        block: str | None = None,
        sort: str = "release_date",
        order: str = "desc",
        page: int = 1,
        limit: int = 50,
    ) -> SetListResponse:
        """List and filter sets with pagination."""
        sets, total = sets_data.list_sets(
            q=q,
            set_type=set_type,
            block=block,
            sort=sort,
            order=order,
            page=page,
            limit=limit,
        )

        data = [
            SetSummary(
                code=s["code"],
                name=s["name"],
                type=s["type"],
                release_date=s["release_date"],
                base_set_size=s["base_set_size"],
                total_set_size=s["total_set_size"],
                block=s["block"],
                keyrune_code=s["keyrune_code"],
            )
            for s in sets
        ]

        pages = (total + limit - 1) // limit if limit > 0 else 1

        return SetListResponse(
            data=data,
            pagination=Pagination(page=page, limit=limit, total=total, pages=pages),
            filters=SetFilters(
                types=sets_data.get_available_types(),
                blocks=sets_data.get_available_blocks(),
            ),
        )

    async def get_set(
        self,
        code: str,
        rarity: str | None = None,
        color: str | None = None,
        card_type: str | None = None,
        card_page: int = 1,
        card_limit: int = 50,
    ) -> SetDetail | None:
        """Get full set details including cards and statistics."""
        set_meta = sets_data.get_set(code)
        if not set_meta:
            return None

        # Get cards with filters
        cards, card_total = sets_data.get_set_cards(
            code=code,
            rarity=rarity,
            color=color,
            card_type=card_type,
            page=card_page,
            limit=card_limit,
        )

        # Get stats
        stats_data = sets_data.get_set_stats(code)

        card_pages = (card_total + card_limit - 1) // card_limit if card_limit > 0 else 1

        return SetDetail(
            meta=SetMeta(
                code=set_meta["code"],
                name=set_meta["name"],
                type=set_meta["type"],
                release_date=set_meta["release_date"],
                base_set_size=set_meta["base_set_size"],
                total_set_size=set_meta["total_set_size"],
                block=set_meta["block"],
                keyrune_code=set_meta["keyrune_code"],
            ),
            stats=SetStats(
                rarity_count=stats_data["rarity_count"],
                price=SetPrice(
                    total=stats_data.get("total_price") or 0,
                    by_source=PriceBySource(tcgplayer=stats_data.get("total_price")),
                ),
                price_histogram=[],
                keywords=KeywordCounts(
                    ability_words=stats_data.get("keywords", {}),
                    keyword_abilities={},
                    keyword_actions={},
                ),
                text_by_color=ColorWordFrequencies(
                    W=[],
                    U=[],
                    B=[],
                    R=[],
                    G=[],
                    C=[],
                ),
            ),
            cards=SetCardsResponse(
                data=[
                    SetCard(
                        uuid=c["uuid"],
                        name=c["name"],
                        type=c["type"],
                        rarity=c["rarity"],
                        color_identity=c["color_identity"],
                        text=c.get("text"),
                        price=c.get("price"),
                        image_url=c.get("image_url"),
                    )
                    for c in cards
                ],
                pagination=Pagination(page=card_page, limit=card_limit, total=card_total, pages=card_pages),
            ),
        )

    async def get_set_raw(self, code: str) -> dict | None:
        """Get raw set data."""
        set_data = sets_data.get_set(code)
        if not set_data:
            return None
        return set_data

    async def get_available_types(self) -> list[str]:
        """Get list of available set types."""
        return sets_data.get_available_types()

    async def get_available_blocks(self) -> list[str]:
        """Get list of available blocks."""
        return sets_data.get_available_blocks()


# Singleton instance
set_service = SetService()

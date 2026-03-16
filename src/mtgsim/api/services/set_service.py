"""Set service - handles set data access and processing."""

import logging

from mtgsim.api.data import sets_data
from mtgsim.api.data.keywords import keywords_data
from mtgsim.api.models.common import KeywordCounts, Pagination
from mtgsim.api.models.deck import PriceBySource
from mtgsim.api.models.set import (
    ColorWordFrequencies,
    SetCard,
    SetCardsResponse,
    SetCollectionStats,
    SetDetail,
    SetFilters,
    SetListResponse,
    SetMeta,
    SetPrice,
    SetStats,
    SetSummary,
)

logger = logging.getLogger("mtgsim.api.services.set")


class SetService:
    """Service for set-related operations."""

    async def list_sets(
        self,
        q: str | None = None,
        set_type: str | None = None,
        block: str | None = None,
        has_owned_cards: bool | None = None,
        sort: str = "release_date",
        order: str = "desc",
        page: int = 1,
        limit: int = 50,
    ) -> SetListResponse:
        """List and filter sets with pagination."""
        logger.debug(f"list_sets: q={q} set_type={set_type} block={block} sort={sort} page={page}")
        sets, total = sets_data.list_sets(
            q=q,
            set_type=set_type,
            block=block,
            has_owned_cards=has_owned_cards,
            sort=sort,
            order=order,
            page=page,
            limit=limit,
        )

        logger.debug(f"list_sets: got {len(sets)} sets, total={total}")
        data = []
        for s in sets:
            cs = s.get("collection_stats", {})
            collection_stats = None
            if cs:
                total_cards = cs.get("total_cards", 0)
                owned_cards = cs.get("owned_cards", 0)
                owned_pct = (owned_cards / total_cards * 100) if total_cards > 0 else 0.0
                collection_stats = SetCollectionStats(
                    total_cards=total_cards,
                    owned_cards=owned_cards,
                    owned_percentage=round(owned_pct, 1),
                    wanted_cards=cs.get("wanted_cards", 0),
                )
            data.append(
                SetSummary(
                    code=s["code"],
                    name=s["name"],
                    type=s.get("type", ""),
                    release_date=s.get("release_date"),
                    base_set_size=s.get("base_set_size", 0),
                    total_set_size=s.get("total_set_size", 0),
                    block=s.get("block"),
                    keyrune_code=s.get("keyrune_code"),
                    collection_stats=collection_stats,
                )
            )

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
        owns: bool | None = None,
        wants: bool | None = None,
        card_page: int = 1,
        card_limit: int = 50,
    ) -> SetDetail | None:
        """Get full set details including cards and statistics."""
        logger.debug(f"get_set: code={code} rarity={rarity} color={color} card_type={card_type}")
        set_meta = sets_data.get_set(code)
        if not set_meta:
            return None

        # Get cards with filters
        cards, card_total = sets_data.get_set_cards(
            code=code,
            rarity=rarity,
            color=color,
            card_type=card_type,
            owns=owns,
            wants=wants,
            page=card_page,
            limit=card_limit,
        )

        # Get stats
        stats_data = sets_data.get_set_stats(code)
        cs = set_meta.get("collection_stats", {})
        collection_stats = None
        if cs:
            total_cards = cs.get("total_cards", 0)
            owned_cards = cs.get("owned_cards", 0)
            owned_pct = (owned_cards / total_cards * 100) if total_cards > 0 else 0.0
            collection_stats = SetCollectionStats(
                total_cards=total_cards,
                owned_cards=owned_cards,
                owned_percentage=round(owned_pct, 1),
                wanted_cards=cs.get("wanted_cards", 0),
            )

        card_pages = (card_total + card_limit - 1) // card_limit if card_limit > 0 else 1

        return SetDetail(
            meta=SetMeta(
                code=set_meta["code"],
                name=set_meta["name"],
                type=set_meta.get("type", ""),
                release_date=set_meta.get("release_date"),
                base_set_size=set_meta.get("base_set_size", 0),
                total_set_size=set_meta.get("total_set_size", 0),
                block=set_meta.get("block"),
                keyrune_code=set_meta.get("keyrune_code"),
                collection_stats=collection_stats,
            ),
            stats=SetStats(
                rarity_count=stats_data.get("rarity_count", {}),
                price=SetPrice(
                    total=0,
                    by_source=PriceBySource(),
                ),
                price_histogram=[],
                keywords=KeywordCounts(**keywords_data.categorize_keyword_freq(stats_data.get("keyword_freq", {}))),
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
                        mana_cost=c.get("mana_cost"),
                        mana_value=c.get("mana_value"),
                        type=c.get("type", ""),
                        rarity=c.get("rarity", ""),
                        color_identity=c.get("color_identity", []),
                        colors=c.get("colors", []),
                        power=c.get("power"),
                        toughness=c.get("toughness"),
                        number=c.get("number"),
                        text=c.get("oracle_text"),
                        price=None,
                        image_url=c.get("image_url"),
                        owns=c.get("owns", False),
                        wants=c.get("wants", False),
                        total_owned=c.get("total_owned", 0),
                        total_wanted=c.get("total_wanted", 0),
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

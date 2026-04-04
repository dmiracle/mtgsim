"""Cards data access layer using unified database schema."""

import logging
from datetime import datetime

from mtgdb.models import (
    MJCard,
    MJCardIdentifier,
    MJCardLegality,
    MJCardPrice,
    MJCardTag,
    MJDeck,
    MJDeckCard,
    MJSet,
    UserCard,
    UserCardRating,
)
from mtgdb.session import get_session
from sqlmodel import func, select

from .helpers import add_price_join, apply_card_filters, build_image_url, card_to_api_dict

logger = logging.getLogger("mtgsim.api.data.cards")

_standard_cutoff_cache: str | None = None


def _standard_cutoff_date(session) -> str | None:
    """Find the oldest release date among current standard-legal expansion/core sets.

    Uses a heuristic: find the earliest release_date of expansion/core sets
    that contain cards legal in standard, limited to the most recent sets.
    Standard keeps ~3 years of sets since 2024 rotation change.
    """
    global _standard_cutoff_cache
    if _standard_cutoff_cache is not None:
        return _standard_cutoff_cache

    # Get all expansion/core sets that have standard-legal cards, ordered by release
    q = (
        select(MJSet.release_date)
        .join(MJCard, MJCard.set_code == MJSet.code)
        .join(
            MJCardLegality,
            (MJCard.uuid == MJCardLegality.card_uuid)
            & (MJCardLegality.format == "standard")
            & (MJCardLegality.status == "Legal"),
        )
        .where(MJSet.type.in_(["expansion", "core"]))
        .distinct()
        .order_by(MJSet.release_date.asc())
    )
    dates = list(session.exec(q).all())
    if not dates:
        return None

    # Keep only sets from the last 3 years (standard rotation window)
    from datetime import datetime

    now = datetime.now().strftime("%Y-%m-%d")
    three_years_ago = str(int(now[:4]) - 3) + now[4:]
    recent = [d for d in dates if d and d >= three_years_ago]
    cutoff = recent[0] if recent else dates[-1]
    _standard_cutoff_cache = cutoff
    return cutoff


class CardsData:
    """Data access for cards using unified schema."""

    def search_cards(
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
        unique: bool = False,
        price_mode: str = "min",
        sort: str = "name",
        order: str = "asc",
        page: int = 1,
        limit: int = 50,
    ) -> tuple[list[dict], int]:
        """Search cards with filters. Returns: (list of cards, total count)"""
        logger.debug(f"search_cards: q={q} set_code={set_code} rarity={rarity} format={format_legal}")
        with get_session() as session:
            # Base query with LEFT JOINs
            query = (
                select(MJCard, MJCardIdentifier, UserCard)
                .outerjoin(MJCardIdentifier, MJCard.uuid == MJCardIdentifier.card_uuid)
                .outerjoin(UserCard, MJCard.uuid == UserCard.card_uuid)
            )
            query, price_col = add_price_join(query)
            query = query.add_columns(price_col)

            # Format legality filter
            if format_legal:
                query = query.join(
                    MJCardLegality,
                    (MJCard.uuid == MJCardLegality.card_uuid)
                    & (MJCardLegality.format == format_legal)
                    & (MJCardLegality.status == "Legal"),
                )
                # Restrict to expansion/core sets; for standard also limit to rotation window
                query = query.join(MJSet, MJCard.set_code == MJSet.code).where(MJSet.type.in_(["expansion", "core"]))
                if format_legal == "standard":
                    # Standard rotation: find the cutoff from the 3rd-newest fall set
                    # Simpler: only include sets released in last ~2.5 years
                    cutoff = _standard_cutoff_date(session)
                    if cutoff:
                        query = query.where(MJSet.release_date >= cutoff)

            # Text search (name, printed_name, type, oracle text)
            if q:
                query = query.where(
                    (MJCard.name.contains(q))
                    | (MJCard.printed_name.contains(q))
                    | (MJCard.type_line.contains(q))
                    | (MJCard.oracle_text.contains(q))
                )

            # Set filter (single)
            if set_code:
                query = query.where(MJCard.set_code == set_code)

            # Set filter (multi)
            if set_codes:
                query = query.where(MJCard.set_code.in_(set_codes))

            # Common card filters
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
            )

            # Price range filters
            if price_min is not None:
                query = query.where(price_col >= price_min)
            if price_max is not None:
                query = query.where(price_col <= price_max)

            # Sorting
            sort_map = {
                "name": MJCard.name,
                "mana_value": MJCard.mana_value,
                "rarity": MJCard.rarity,
                "set_code": MJCard.set_code,
                "price": price_col,
            }
            sort_field = sort_map.get(sort, MJCard.name)

            # Unique filter: one printing per card name, selected by price_mode
            if unique:
                from sqlalchemy.orm import aliased

                MJCard2 = aliased(MJCard)
                MJCardPrice2 = aliased(MJCardPrice)

                # Pick price ordering based on price_mode
                if price_mode == "max":
                    price_order = MJCardPrice2.price.desc().nulls_last()
                else:
                    price_order = MJCardPrice2.price.asc().nulls_last()

                # Row number: rank printings per card name by price
                row_num = (
                    func.row_number()
                    .over(
                        partition_by=MJCard2.name,
                        order_by=[price_order, MJCard2.uuid.asc()],
                    )
                    .label("rn")
                )

                ranked = select(MJCard2.uuid.label("ranked_uuid"), row_num).outerjoin(
                    MJCardPrice2,
                    (MJCardPrice2.card_uuid == MJCard2.uuid)
                    & (MJCardPrice2.provider == "tcgplayer")
                    & (MJCardPrice2.finish == "normal")
                    & (MJCardPrice2.listing_type == "retail"),
                )

                # Apply same filters to the ranking subquery
                if set_code:
                    ranked = ranked.where(MJCard2.set_code == set_code)
                if set_codes:
                    ranked = ranked.where(MJCard2.set_code.in_(set_codes))
                if format_legal:
                    MJCardLegality2 = aliased(MJCardLegality)
                    ranked = ranked.join(
                        MJCardLegality2,
                        (MJCard2.uuid == MJCardLegality2.card_uuid)
                        & (MJCardLegality2.format == format_legal)
                        & (MJCardLegality2.status == "Legal"),
                    )
                    MJSet2 = aliased(MJSet)
                    ranked = ranked.join(MJSet2, MJCard2.set_code == MJSet2.code).where(
                        MJSet2.type.in_(["expansion", "core"])
                    )
                    if format_legal == "standard":
                        cutoff = _standard_cutoff_date(session)
                        if cutoff:
                            ranked = ranked.where(MJSet2.release_date >= cutoff)

                ranked_subq = ranked.subquery()
                best_uuids = select(ranked_subq.c.ranked_uuid).where(ranked_subq.c.rn == 1)
                query = query.where(MJCard.uuid.in_(best_uuids))

            # Count total before pagination
            count_query = select(func.count()).select_from(query.subquery())
            total = session.exec(count_query).one()

            if order == "desc":
                query = query.order_by(sort_field.desc(), MJCard.name.asc())
            else:
                query = query.order_by(sort_field.asc(), MJCard.name.asc())

            # Pagination
            offset = (page - 1) * limit
            query = query.offset(offset).limit(limit)

            # Execute
            results = session.exec(query).all()

            # Convert to API format
            logger.debug(f"search_cards: query returned {len(results)} results, total={total}")

            # Batch-fetch tags for all card names in results
            card_names = [r[0].name for r in results]
            tags_map = self._get_tags_for_names(session, card_names)

            cards = []
            for mj_card, identifier, user_card, best_price in results:
                card_tags = tags_map.get(mj_card.name, [])
                cards.append(card_to_api_dict(mj_card, identifier, user_card, price=best_price, tags=card_tags))

            return cards, total

    def get_card_stats(
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
        unique: bool = False,
    ) -> dict:
        """Get aggregated stats for filtered cards."""
        with get_session() as session:
            # Build base filtered query (same filters as search_cards)
            query = select(MJCard.uuid).outerjoin(UserCard, MJCard.uuid == UserCard.card_uuid)
            query, price_col = add_price_join(query)

            if format_legal:
                query = query.join(
                    MJCardLegality,
                    (MJCard.uuid == MJCardLegality.card_uuid)
                    & (MJCardLegality.format == format_legal)
                    & (MJCardLegality.status == "Legal"),
                )
                query = query.join(MJSet, MJCard.set_code == MJSet.code).where(MJSet.type.in_(["expansion", "core"]))
                if format_legal == "standard":
                    cutoff = _standard_cutoff_date(session)
                    if cutoff:
                        query = query.where(MJSet.release_date >= cutoff)

            if q:
                query = query.where(
                    (MJCard.name.contains(q))
                    | (MJCard.printed_name.contains(q))
                    | (MJCard.type_line.contains(q))
                    | (MJCard.oracle_text.contains(q))
                )
            if set_code:
                query = query.where(MJCard.set_code == set_code)
            if set_codes:
                query = query.where(MJCard.set_code.in_(set_codes))

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
            )

            if price_min is not None:
                query = query.where(price_col >= price_min)
            if price_max is not None:
                query = query.where(price_col <= price_max)

            if unique:
                subq = select(func.min(MJCard.uuid)).group_by(MJCard.name)
                if set_code:
                    subq = subq.where(MJCard.set_code == set_code)
                if set_codes:
                    subq = subq.where(MJCard.set_code.in_(set_codes))
                query = query.where(MJCard.uuid.in_(subq))

            # Collect matching UUIDs once, then aggregate in Python + 1 price query
            uuid_rows = session.exec(query).all()
            matching_uuids = [row if isinstance(row, str) else row[0] for row in uuid_rows]
            total = len(matching_uuids)

            if not matching_uuids:
                return {
                    "total": 0,
                    "mana_curve": {},
                    "type_distribution": {},
                    "rarity_distribution": {},
                    "color_distribution": {},
                    "price_stats": {"total": 0, "average": 0, "median": 0, "count_with_price": 0},
                }

            # Single query: fetch mana_value, type_line, rarity, colors for all matches
            card_rows = session.exec(
                select(MJCard.mana_value, MJCard.type_line, MJCard.rarity, MJCard.colors).where(
                    MJCard.uuid.in_(matching_uuids)
                )
            ).all()

            # Aggregate in Python (single pass)
            mana_curve: dict[str, int] = {}
            type_dist: dict[str, int] = {}
            rarity_dist: dict[str, int] = {}
            color_dist: dict[str, int] = {}

            for mv, type_line, rarity, colors_json in card_rows:
                # Mana curve
                if mv is not None:
                    key = str(int(mv))
                    mana_curve[key] = mana_curve.get(key, 0) + 1

                # Type distribution
                if type_line:
                    primary = type_line.split("—")[0].split("//")[0].strip()
                    matched = False
                    for t in [
                        "Creature",
                        "Instant",
                        "Sorcery",
                        "Enchantment",
                        "Artifact",
                        "Planeswalker",
                        "Land",
                        "Battle",
                    ]:
                        if t in primary:
                            type_dist[t] = type_dist.get(t, 0) + 1
                            matched = True
                            break
                    if not matched:
                        type_dist["Other"] = type_dist.get("Other", 0) + 1

                # Rarity
                if rarity:
                    rarity_dist[rarity] = rarity_dist.get(rarity, 0) + 1

                # Colors
                if isinstance(colors_json, list):
                    for c in colors_json:
                        color_dist[c] = color_dist.get(c, 0) + 1
                    if not colors_json:
                        color_dist["C"] = color_dist.get("C", 0) + 1

            # Price stats: single query with count/sum/avg + median via percentile
            price_query = (
                select(
                    func.count(MJCardPrice.price),
                    func.sum(MJCardPrice.price),
                    func.avg(MJCardPrice.price),
                )
                .where(MJCardPrice.card_uuid.in_(matching_uuids))
                .where(MJCardPrice.provider == "tcgplayer")
                .where(MJCardPrice.finish == "normal")
                .where(MJCardPrice.listing_type == "retail")
                .where(MJCardPrice.price.is_not(None))
            )
            price_row = session.exec(price_query).one()
            price_count = price_row[0] or 0
            price_total = round(price_row[1] or 0, 2)
            price_avg = round(price_row[2] or 0, 2)

            # Median via offset/limit (avoids loading all prices)
            if price_count > 0:
                mid = price_count // 2
                median_row = session.exec(
                    select(MJCardPrice.price)
                    .where(MJCardPrice.card_uuid.in_(matching_uuids))
                    .where(MJCardPrice.provider == "tcgplayer")
                    .where(MJCardPrice.finish == "normal")
                    .where(MJCardPrice.listing_type == "retail")
                    .where(MJCardPrice.price.is_not(None))
                    .order_by(MJCardPrice.price)
                    .offset(mid)
                    .limit(1)
                ).first()
                price_median = round(median_row, 2) if median_row else 0
            else:
                price_median = 0

            return {
                "total": total,
                "mana_curve": mana_curve,
                "type_distribution": type_dist,
                "rarity_distribution": rarity_dist,
                "color_distribution": color_dist,
                "price_stats": {
                    "total": price_total,
                    "average": price_avg,
                    "median": price_median,
                    "count_with_price": price_count,
                },
            }

    def get_available_tags(
        self,
        set_code: str | None = None,
        format_legal: str | None = None,
        colors: list[str] | None = None,
        card_type: str | None = None,
        rarity: str | None = None,
    ) -> list[dict]:
        """Get distinct tags with card counts, optionally filtered."""
        with get_session() as session:
            query = select(MJCardTag.tag, func.count(func.distinct(MJCardTag.card_name))).join(
                MJCard, MJCardTag.card_name == MJCard.name
            )

            if set_code:
                query = query.where(MJCard.set_code == set_code)
            if format_legal:
                query = query.join(
                    MJCardLegality,
                    (MJCard.uuid == MJCardLegality.card_uuid)
                    & (MJCardLegality.format == format_legal)
                    & (MJCardLegality.status == "Legal"),
                )
            if rarity:
                query = query.where(MJCard.rarity == rarity)
            if card_type:
                query = query.where(MJCard.type_line.contains(card_type))
            if colors:
                from sqlalchemy import or_

                query = query.where(
                    or_(*[func.json_extract(MJCard.color_identity, "$").contains(f'"{c}"') for c in colors])
                )

            query = query.group_by(MJCardTag.tag).order_by(MJCardTag.tag)
            results = session.exec(query).all()
            return [{"tag": tag, "count": count} for tag, count in results]

    def get_keyword_frequencies(
        self,
        set_code: str | None = None,
        set_codes: list[str] | None = None,
        format_legal: str | None = None,
        rarity: str | None = None,
        colors: list[str] | None = None,
        card_type: str | None = None,
    ) -> dict[str, int]:
        """Get keyword frequencies for a filtered set of cards."""
        with get_session() as session:
            query = select(MJCard.keywords).where(MJCard.keywords.is_not(None))

            if format_legal:
                query = query.join(
                    MJCardLegality,
                    (MJCard.uuid == MJCardLegality.card_uuid)
                    & (MJCardLegality.format == format_legal)
                    & (MJCardLegality.status == "Legal"),
                )
                query = query.join(MJSet, MJCard.set_code == MJSet.code).where(MJSet.type.in_(["expansion", "core"]))
                if format_legal == "standard":
                    cutoff = _standard_cutoff_date(session)
                    if cutoff:
                        query = query.where(MJSet.release_date >= cutoff)
            if set_code:
                query = query.where(MJCard.set_code == set_code)
            if set_codes:
                query = query.where(MJCard.set_code.in_(set_codes))
            query = apply_card_filters(query, rarity=rarity, card_type=card_type, colors=colors)

            # Deduplicate by name
            min_uuid_subq = select(func.min(MJCard.uuid)).group_by(MJCard.name)
            if set_code:
                min_uuid_subq = min_uuid_subq.where(MJCard.set_code == set_code)
            if set_codes:
                min_uuid_subq = min_uuid_subq.where(MJCard.set_code.in_(set_codes))
            if format_legal:
                min_uuid_subq = min_uuid_subq.join(
                    MJCardLegality,
                    (MJCard.uuid == MJCardLegality.card_uuid)
                    & (MJCardLegality.format == format_legal)
                    & (MJCardLegality.status == "Legal"),
                )
            query = query.where(MJCard.uuid.in_(min_uuid_subq))

            results = session.exec(query).all()
            freq = {}
            for keywords in results:
                if isinstance(keywords, list):
                    for kw in keywords:
                        freq[kw] = freq.get(kw, 0) + 1
            return freq

    def get_card(self, uuid: str) -> dict | None:
        """Get single card with collection status, prices, and legalities."""
        with get_session() as session:
            query = (
                select(MJCard, MJCardIdentifier, UserCard)
                .outerjoin(MJCardIdentifier, MJCard.uuid == MJCardIdentifier.card_uuid)
                .outerjoin(UserCard, MJCard.uuid == UserCard.card_uuid)
                .where(MJCard.uuid == uuid)
            )

            result = session.exec(query).first()
            if not result:
                return None

            mj_card, identifier, user_card = result

            # Get set name
            set_name = None
            if mj_card.set_code:
                set_query = select(MJSet.name).where(MJSet.code == mj_card.set_code)
                set_name = session.exec(set_query).first()

            # Get legalities
            legalities = self._get_card_legalities(session, uuid)

            # Get prices as structured entries
            all_prices = self._get_card_price_entries(session, uuid)

            # Get quadrant ratings
            rating_query = select(UserCardRating).where(UserCardRating.card_uuid == uuid)
            rating = session.exec(rating_query).first()

            # Pick best price: TCGPlayer normal retail, then any
            best = None
            for p in all_prices:
                if p["provider"] == "tcgplayer" and p["finish"] == "normal" and p["listing_type"] == "retail":
                    best = p["price"]
                    break
            if best is None and all_prices:
                best = all_prices[0]["price"]

            # Get tags
            tags_map = self._get_tags_for_names(session, [mj_card.name])
            card_tags = tags_map.get(mj_card.name, [])

            card_dict = card_to_api_dict(mj_card, identifier, user_card, set_name=set_name, price=best, tags=card_tags)
            card_dict["legalities"] = legalities
            card_dict["all_prices"] = all_prices
            if rating:
                card_dict["quadrant_rating"] = {
                    "developing": rating.developing,
                    "ahead": rating.ahead,
                    "behind": rating.behind,
                    "parity": rating.parity,
                    "notes": rating.notes,
                }
            return card_dict

    def _get_tags_for_names(self, session, card_names: list[str]) -> dict[str, list[str]]:
        """Get tags for a list of card names, returned as {name: [tag, ...]}."""
        if not card_names:
            return {}
        query = select(MJCardTag.card_name, MJCardTag.tag).where(MJCardTag.card_name.in_(card_names))
        results = session.exec(query).all()
        tags_map: dict[str, list[str]] = {}
        for name, tag in results:
            tags_map.setdefault(name, []).append(tag)
        return tags_map

    def _get_card_legalities(self, session, uuid: str) -> dict[str, str]:
        """Get format legalities for a card."""
        query = select(MJCardLegality).where(MJCardLegality.card_uuid == uuid)
        results = session.exec(query).all()
        return {r.format: r.status for r in results}

    def _get_card_price_entries(self, session, uuid: str) -> list[dict]:
        """Get all price entries for a card."""
        query = select(MJCardPrice).where(MJCardPrice.card_uuid == uuid)
        results = session.exec(query).all()
        return [
            {
                "provider": p.provider,
                "finish": p.finish,
                "listing_type": p.listing_type,
                "price": p.price,
            }
            for p in results
            if p.price
        ]

    def get_cards_by_name(self, name: str) -> list[dict]:
        """Get all printings of a card by exact name."""
        with get_session() as session:
            query = (
                select(MJCard, MJCardIdentifier, UserCard)
                .outerjoin(MJCardIdentifier, MJCard.uuid == MJCardIdentifier.card_uuid)
                .outerjoin(UserCard, MJCard.uuid == UserCard.card_uuid)
                .where(MJCard.name == name)
                .order_by(MJCard.set_code)
            )

            results = session.exec(query).all()

            cards = []
            for mj_card, identifier, user_card in results:
                # Get set name
                set_name = None
                if mj_card.set_code:
                    set_query = select(MJSet.name).where(MJSet.code == mj_card.set_code)
                    set_name = session.exec(set_query).first()

                total_owned = 0
                if user_card:
                    total_owned = (user_card.quantity_owned or 0) + (user_card.quantity_owned_foil or 0)

                cards.append(
                    {
                        "uuid": mj_card.uuid,
                        "name": mj_card.printed_name or mj_card.name,
                        "set_code": mj_card.set_code,
                        "set_name": set_name,
                        "rarity": mj_card.rarity,
                        "number": mj_card.number,
                        "image_url": build_image_url(identifier.scryfall_id if identifier else None),
                        "owns": total_owned > 0,
                        "total_owned": total_owned,
                    }
                )

            return cards

    def get_card_appearances(self, uuid: str) -> list[dict]:
        """Get decks that contain this card."""
        with get_session() as session:
            # Get the card name
            card_query = select(MJCard.name).where(MJCard.uuid == uuid)
            card_name = session.exec(card_query).first()

            if not card_name:
                return []

            # Find decks containing this card by name
            deck_query = (
                select(MJDeck.file_name, MJDeck.name, MJDeckCard.count)
                .join(MJDeckCard, MJDeck.uuid == MJDeckCard.deck_uuid)
                .where(MJDeckCard.name == card_name)
                .order_by(MJDeck.name)
                .limit(20)
            )

            results = session.exec(deck_query).all()

            appearances = []
            for file_name, deck_name, count in results:
                appearances.append(
                    {
                        "file": file_name + ".json",
                        "name": deck_name,
                        "count": count,
                    }
                )

            return appearances

    def get_other_printings(self, uuid: str) -> list[dict]:
        """Get other printings of the same card."""
        with get_session() as session:
            card_query = select(MJCard.name).where(MJCard.uuid == uuid)
            card_name = session.exec(card_query).first()

            if not card_name:
                return []

            query = (
                select(MJCard, MJCardIdentifier, UserCard, MJSet.name)
                .outerjoin(MJCardIdentifier, MJCard.uuid == MJCardIdentifier.card_uuid)
                .outerjoin(UserCard, MJCard.uuid == UserCard.card_uuid)
                .outerjoin(MJSet, MJCard.set_code == MJSet.code)
                .where((MJCard.name == card_name) & (MJCard.uuid != uuid))
                .order_by(MJCard.set_code)
                .limit(50)
            )
            query, price_col = add_price_join(query)
            query = query.add_columns(price_col)

            results = session.exec(query).all()

            printings = []
            for mj_card, identifier, user_card, set_name, best_price in results:
                total_owned = (user_card.quantity_owned or 0) + (user_card.quantity_owned_foil or 0) if user_card else 0
                printings.append(
                    {
                        "uuid": mj_card.uuid,
                        "set_code": mj_card.set_code,
                        "set_name": set_name,
                        "rarity": mj_card.rarity,
                        "number": mj_card.number,
                        "image_url": build_image_url(identifier.scryfall_id if identifier else None),
                        "price": best_price,
                        "owns": total_owned > 0,
                        "total_owned": total_owned,
                    }
                )

            return printings

    def add_to_collection(
        self,
        card_uuid: str,
        quantity_owned: int = 0,
        quantity_owned_foil: int = 0,
        quantity_wanted: int = 0,
        quantity_wanted_foil: int = 0,
        condition: str = "NM",
        notes: str | None = None,
    ) -> dict | None:
        """Add or update a card in user's collection."""
        with get_session() as session:
            # Verify card exists
            card_exists = session.exec(select(MJCard.uuid).where(MJCard.uuid == card_uuid)).first()
            if not card_exists:
                return None

            # Check if already in collection
            existing = session.exec(select(UserCard).where(UserCard.card_uuid == card_uuid)).first()

            if existing:
                # Update existing
                existing.quantity_owned = quantity_owned
                existing.quantity_owned_foil = quantity_owned_foil
                existing.quantity_wanted = quantity_wanted
                existing.quantity_wanted_foil = quantity_wanted_foil
                existing.condition = condition
                existing.notes = notes
                session.add(existing)
            else:
                # Create new
                user_card = UserCard(
                    card_uuid=card_uuid,
                    quantity_owned=quantity_owned,
                    quantity_owned_foil=quantity_owned_foil,
                    quantity_wanted=quantity_wanted,
                    quantity_wanted_foil=quantity_wanted_foil,
                    condition=condition,
                    notes=notes,
                )
                session.add(user_card)

            session.commit()

            # Return updated card
            return self.get_card(card_uuid)

    def remove_from_collection(self, card_uuid: str) -> bool:
        """Remove a card from user's collection."""
        with get_session() as session:
            existing = session.exec(select(UserCard).where(UserCard.card_uuid == card_uuid)).first()

            if not existing:
                return False

            session.delete(existing)
            session.commit()
            return True

    def get_collection_stats(self) -> dict:
        """Get overall collection statistics."""
        with get_session() as session:
            # Total owned cards
            owned_query = select(func.sum(UserCard.quantity_owned + UserCard.quantity_owned_foil))
            total_owned = session.exec(owned_query).first() or 0

            # Unique cards owned
            unique_owned_query = select(func.count(UserCard.id)).where(
                (UserCard.quantity_owned > 0) | (UserCard.quantity_owned_foil > 0)
            )
            unique_owned = session.exec(unique_owned_query).first() or 0

            # Total wanted
            wanted_query = select(func.sum(UserCard.quantity_wanted + UserCard.quantity_wanted_foil))
            total_wanted = session.exec(wanted_query).first() or 0

            # Unique cards wanted
            unique_wanted_query = select(func.count(UserCard.id)).where(
                (UserCard.quantity_wanted > 0) | (UserCard.quantity_wanted_foil > 0)
            )
            unique_wanted = session.exec(unique_wanted_query).first() or 0

            return {
                "total_owned": total_owned,
                "unique_owned": unique_owned,
                "total_wanted": total_wanted,
                "unique_wanted": unique_wanted,
            }

    def set_quadrant_rating(
        self,
        card_uuid: str,
        developing: float | None = None,
        ahead: float | None = None,
        behind: float | None = None,
        parity: float | None = None,
        notes: str | None = None,
    ) -> dict | None:
        """Set or update quadrant theory rating for a card."""
        with get_session() as session:
            # Verify card exists
            card = session.exec(select(MJCard.uuid).where(MJCard.uuid == card_uuid)).first()
            if not card:
                return None

            rating = session.exec(select(UserCardRating).where(UserCardRating.card_uuid == card_uuid)).first()

            if rating:
                if developing is not None:
                    rating.developing = developing
                if ahead is not None:
                    rating.ahead = ahead
                if behind is not None:
                    rating.behind = behind
                if parity is not None:
                    rating.parity = parity
                if notes is not None:
                    rating.notes = notes
                rating.updated_at = datetime.utcnow()
            else:
                rating = UserCardRating(
                    card_uuid=card_uuid,
                    developing=developing,
                    ahead=ahead,
                    behind=behind,
                    parity=parity,
                    notes=notes,
                )
                session.add(rating)

            session.commit()
            session.refresh(rating)

            return {
                "developing": rating.developing,
                "ahead": rating.ahead,
                "behind": rating.behind,
                "parity": rating.parity,
                "notes": rating.notes,
            }

    def get_quadrant_rating(self, card_uuid: str) -> dict | None:
        """Get quadrant theory rating for a card."""
        with get_session() as session:
            rating = session.exec(select(UserCardRating).where(UserCardRating.card_uuid == card_uuid)).first()
            if not rating:
                return None
            return {
                "developing": rating.developing,
                "ahead": rating.ahead,
                "behind": rating.behind,
                "parity": rating.parity,
                "notes": rating.notes,
            }


# Singleton instance
cards_data = CardsData()

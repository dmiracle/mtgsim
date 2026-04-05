"""Decks data access layer using unified database schema."""

import logging

from mtgdb.models import (
    MJCard,
    MJCardIdentifier,
    MJCardPrice,
    MJCardTag,
    MJDeck,
    MJDeckCard,
    PinnedDeck,
    UserCard,
    UserDeck,
    UserDeckCard,
)
from mtgdb.session import get_session
from sqlmodel import func, select

from .helpers import build_image_url, deck_card_to_api_dict, deck_to_api_dict

logger = logging.getLogger("mtgsim.api.data.decks")


class DecksData:
    """Data access for decks using unified schema."""

    def list_decks(
        self,
        q: str | None = None,
        set_code: str | None = None,
        deck_type: str | None = None,
        source: str | None = None,
        colors: list[str] | None = None,
        colors_mode: str = "subset",
        card_count_min: int | None = None,
        card_count_max: int | None = None,
        sort: str = "name",
        order: str = "asc",
        page: int = 1,
        limit: int = 50,
    ) -> tuple[list[dict], int]:
        """List decks with filtering and pagination."""
        logger.debug(f"list_decks: q={q} set_code={set_code} deck_type={deck_type} source={source} sort={sort}")

        is_user_source = source and source != "precon"

        with get_session() as session:
            if is_user_source:
                decks, total = self._list_user_decks(
                    session,
                    q,
                    card_count_min,
                    card_count_max,
                    sort,
                    order,
                    source=source,
                )
                offset = (page - 1) * limit
                decks = decks[offset : offset + limit]
            elif source == "precon":
                decks, total = self._list_precon_decks(
                    session,
                    q,
                    set_code,
                    deck_type,
                    colors,
                    colors_mode,
                    card_count_min,
                    card_count_max,
                    sort,
                    order,
                    page,
                    limit,
                )
            else:
                # All sources
                precon_decks, precon_total = self._list_precon_decks(
                    session,
                    q,
                    set_code,
                    deck_type,
                    colors,
                    colors_mode,
                    card_count_min,
                    card_count_max,
                    sort,
                    order,
                    page,
                    limit,
                )
                user_decks, user_total = self._list_user_decks(
                    session,
                    q,
                    card_count_min,
                    card_count_max,
                    sort,
                    order,
                )
                # Apply color filter to user decks
                if colors:
                    requested = set(colors)
                    filtered_user = []
                    for d in user_decks:
                        deck_colors = set(d.get("colors", []))
                        if colors_mode == "subset" and deck_colors.issubset(requested):
                            filtered_user.append(d)
                        elif colors_mode == "exact" and deck_colors == requested:
                            filtered_user.append(d)
                        elif colors_mode == "any" and deck_colors & requested:
                            filtered_user.append(d)
                    user_total = len(filtered_user)
                    user_decks = filtered_user
                # Prepend user decks on first page
                if page == 1:
                    decks = user_decks + precon_decks
                else:
                    decks = precon_decks
                total = precon_total + user_total

        logger.debug(f"list_decks: {len(decks)} decks, total={total}")
        return decks, total

    def _list_precon_decks(
        self,
        session,
        q: str | None,
        set_code: str | None,
        deck_type: str | None,
        colors: list[str] | None,
        colors_mode: str,
        card_count_min: int | None,
        card_count_max: int | None,
        sort: str,
        order: str,
        page: int = 1,
        limit: int = 50,
    ) -> tuple[list[dict], int]:
        """List preconstructed decks from MTGJSON with DB-level pagination."""
        logger.debug(f"_list_precon_decks: q={q} set_code={set_code} deck_type={deck_type}")
        query = select(MJDeck)

        if q:
            query = query.where((MJDeck.name.contains(q)) | (MJDeck.file_name.contains(q)))
        if set_code:
            query = query.where(MJDeck.code == set_code)
        if deck_type:
            query = query.where(MJDeck.type == deck_type)
        if card_count_min is not None:
            query = query.where((MJDeck.main_board_count + MJDeck.side_board_count) >= card_count_min)
        if card_count_max is not None:
            query = query.where((MJDeck.main_board_count + MJDeck.side_board_count) <= card_count_max)

        # Color filter: compute matching deck UUIDs first, then filter the query
        if colors:
            matching_uuids = self._filter_decks_by_color(session, query, colors, colors_mode)
            query = query.where(MJDeck.uuid.in_(matching_uuids))

        # Count total after color filter
        count_query = select(func.count()).select_from(query.subquery())
        total = session.exec(count_query).one()

        # Sort at DB level
        sort_map = {
            "name": MJDeck.name,
            "release_date": MJDeck.release_date,
            "code": MJDeck.code,
            "card_count": MJDeck.main_board_count + MJDeck.side_board_count,
        }
        sort_field = sort_map.get(sort, MJDeck.name)
        query = query.order_by(sort_field.desc() if order == "desc" else sort_field.asc())

        # Paginate at DB level
        offset = (page - 1) * limit
        query = query.offset(offset).limit(limit)

        results = session.exec(query).all()

        # Batch-fetch colors and prices for just this page of decks
        deck_uuids = [d.uuid for d in results]
        colors_map = self._get_batch_deck_colors(session, deck_uuids)
        price_map = self._get_batch_deck_prices(session, deck_uuids)

        decks = []
        for deck in results:
            deck_colors = colors_map.get(deck.uuid, [])
            deck_dict = deck_to_api_dict(deck, deck_colors, price_map.get(deck.uuid))
            deck_dict["source"] = "precon"
            decks.append(deck_dict)

        return decks, total

    def _filter_decks_by_color(self, session, base_query, colors: list[str], colors_mode: str) -> list[str]:
        """Get deck UUIDs matching the color filter.

        Aggregates colors from MJDeckCard per deck, then applies the filter mode.
        """
        candidate_uuids = [r.uuid for r in session.exec(base_query).all()]

        if not candidate_uuids:
            return []

        all_colors_map = self._get_batch_deck_colors(session, candidate_uuids)
        requested = set(colors)
        matching = []

        for uuid in candidate_uuids:
            deck_colors = set(all_colors_map.get(uuid, []))
            if colors_mode == "subset" and deck_colors.issubset(requested):
                matching.append(uuid)
            elif colors_mode == "exact" and deck_colors == requested:
                matching.append(uuid)
            elif colors_mode == "any" and deck_colors & requested:
                matching.append(uuid)

        return matching

    def _get_batch_deck_colors(self, session, deck_uuids: list[str]) -> dict[str, list[str]]:
        """Get colors for multiple decks in a single query."""
        if not deck_uuids:
            return {}

        query = select(MJDeckCard.deck_uuid, MJDeckCard.colors).where(MJDeckCard.deck_uuid.in_(deck_uuids)).distinct()
        results = session.exec(query).all()

        deck_colors: dict[str, set[str]] = {}
        for deck_uuid, color_list in results:
            if color_list:
                deck_colors.setdefault(deck_uuid, set()).update(color_list)

        wubrg = ["W", "U", "B", "R", "G"]
        return {uuid: sorted(c, key=lambda x: wubrg.index(x) if x in wubrg else 99) for uuid, c in deck_colors.items()}

    def _get_batch_deck_prices(self, session, deck_uuids: list[str]) -> dict[str, float | None]:
        """Get total deck prices for multiple decks in batch."""
        if not deck_uuids:
            return {}

        # Get all deck cards with their counts
        cards_query = select(MJDeckCard.deck_uuid, MJDeckCard.card_uuid, MJDeckCard.count).where(
            MJDeckCard.deck_uuid.in_(deck_uuids),
            MJDeckCard.board.in_(["mainBoard", "sideBoard"]),
        )
        deck_cards = session.exec(cards_query).all()

        # Collect all unique card UUIDs
        all_card_uuids = list({card_uuid for _, card_uuid, _ in deck_cards if card_uuid})

        if not all_card_uuids:
            return {}

        # Single query for all prices
        price_query = select(MJCardPrice.card_uuid, MJCardPrice.price).where(
            MJCardPrice.card_uuid.in_(all_card_uuids),
            MJCardPrice.provider == "tcgplayer",
            MJCardPrice.listing_type == "retail",
            MJCardPrice.finish == "normal",
        )
        price_map = dict(session.exec(price_query).all())

        # Calculate per-deck totals
        deck_totals: dict[str, float] = {}
        for deck_uuid, card_uuid, count in deck_cards:
            if card_uuid and card_uuid in price_map:
                deck_totals[deck_uuid] = deck_totals.get(deck_uuid, 0.0) + price_map[card_uuid] * count

        return {uuid: round(total, 2) for uuid, total in deck_totals.items()}

    def _list_user_decks(
        self,
        session,
        q: str | None,
        card_count_min: int | None,
        card_count_max: int | None,
        sort: str,
        order: str,
        source: str | None = None,
    ) -> tuple[list[dict], int]:
        """List user-created decks."""
        query = select(UserDeck)

        if q:
            query = query.where(UserDeck.name.contains(q))
        if source:
            query = query.where(UserDeck.source == source)

        # Count
        count_query = select(func.count()).select_from(query.subquery())
        total = session.exec(count_query).one()

        # Execute
        results = session.exec(query).all()
        deck_ids = [d.id for d in results]

        # Batch: card counts per deck
        card_count_map = {}
        if deck_ids:
            count_query = (
                select(UserDeckCard.deck_id, func.sum(UserDeckCard.count))
                .where(UserDeckCard.deck_id.in_(deck_ids))
                .group_by(UserDeckCard.deck_id)
            )
            card_count_map = dict(session.exec(count_query).all())

        # Batch: colors per deck
        colors_map = self._get_batch_user_deck_colors(session, deck_ids)

        # Batch: prices per deck
        price_map = self._get_batch_user_deck_prices(session, deck_ids)

        decks = []
        for deck in results:
            card_count = card_count_map.get(deck.id, 0)

            if card_count_min is not None and card_count < card_count_min:
                total -= 1
                continue
            if card_count_max is not None and card_count > card_count_max:
                total -= 1
                continue

            decks.append(
                {
                    "id": deck.id,
                    "name": deck.name,
                    "description": deck.description,
                    "format": deck.format,
                    "card_count": card_count,
                    "colors": colors_map.get(deck.id, []),
                    "price": price_map.get(deck.id),
                    "created_at": deck.created_at.isoformat() if deck.created_at else None,
                    "updated_at": deck.updated_at.isoformat() if deck.updated_at else None,
                    "source": deck.source,
                }
            )

        return decks, total

    def _get_deck_colors(self, session, deck_uuid: str) -> list[str]:
        """Get combined color identity for a precon deck."""
        query = select(MJDeckCard.colors).where(MJDeckCard.deck_uuid == deck_uuid).distinct()
        results = session.exec(query).all()

        colors = set()
        for color_list in results:
            if color_list:
                colors.update(color_list)

        # Sort in WUBRG order
        order = ["W", "U", "B", "R", "G"]
        return sorted(colors, key=lambda c: order.index(c) if c in order else 99)

    def _get_user_deck_colors(self, session, deck_id: int) -> list[str]:
        """Get combined color identity for a user deck."""
        query = (
            select(MJCard.color_identity)
            .join(UserDeckCard, MJCard.uuid == UserDeckCard.card_uuid)
            .where(UserDeckCard.deck_id == deck_id)
            .distinct()
        )
        results = session.exec(query).all()

        colors = set()
        for color_list in results:
            if color_list:
                colors.update(color_list)

        order = ["W", "U", "B", "R", "G"]
        return sorted(colors, key=lambda c: order.index(c) if c in order else 99)

    def _get_batch_user_deck_colors(self, session, deck_ids: list[int]) -> dict[int, list[str]]:
        """Get colors for multiple user decks in a single query."""
        if not deck_ids:
            return {}

        query = (
            select(UserDeckCard.deck_id, MJCard.color_identity)
            .join(MJCard, UserDeckCard.card_uuid == MJCard.uuid)
            .where(UserDeckCard.deck_id.in_(deck_ids))
            .distinct()
        )
        results = session.exec(query).all()

        deck_colors: dict[int, set[str]] = {}
        for deck_id, color_list in results:
            if color_list:
                deck_colors.setdefault(deck_id, set()).update(color_list)

        wubrg = ["W", "U", "B", "R", "G"]
        return {did: sorted(c, key=lambda x: wubrg.index(x) if x in wubrg else 99) for did, c in deck_colors.items()}

    def _get_batch_user_deck_prices(self, session, deck_ids: list[int]) -> dict[int, float | None]:
        """Get total prices for multiple user decks in batch."""
        if not deck_ids:
            return {}

        # Get all user deck cards with counts
        cards_query = select(UserDeckCard.deck_id, UserDeckCard.card_uuid, UserDeckCard.count).where(
            UserDeckCard.deck_id.in_(deck_ids)
        )
        deck_cards = session.exec(cards_query).all()

        all_card_uuids = list({card_uuid for _, card_uuid, _ in deck_cards if card_uuid})
        if not all_card_uuids:
            return {}

        # Single query for all prices
        price_query = select(MJCardPrice.card_uuid, MJCardPrice.price).where(
            MJCardPrice.card_uuid.in_(all_card_uuids),
            MJCardPrice.provider == "tcgplayer",
            MJCardPrice.listing_type == "retail",
            MJCardPrice.finish == "normal",
        )
        price_map = dict(session.exec(price_query).all())

        # Calculate per-deck totals
        deck_totals: dict[int, float] = {}
        for deck_id, card_uuid, count in deck_cards:
            if card_uuid and card_uuid in price_map:
                deck_totals[deck_id] = deck_totals.get(deck_id, 0.0) + price_map[card_uuid] * count

        return {did: round(total, 2) for did, total in deck_totals.items()}

    def _calculate_deck_price(self, session, deck_uuid: str) -> float | None:
        """Calculate total deck price from card prices."""
        # Get cards in deck
        cards_query = select(MJDeckCard.card_uuid, MJDeckCard.count).where(
            (MJDeckCard.deck_uuid == deck_uuid) & (MJDeckCard.board.in_(["mainBoard", "sideBoard"]))
        )
        cards = session.exec(cards_query).all()

        if not cards:
            return None

        uuids = [card_uuid for card_uuid, _ in cards if card_uuid]
        if not uuids:
            return None

        # Get prices (tcgplayer retail normal)
        price_query = select(MJCardPrice.card_uuid, MJCardPrice.price).where(
            (MJCardPrice.card_uuid.in_(uuids))
            & (MJCardPrice.provider == "tcgplayer")
            & (MJCardPrice.listing_type == "retail")
            & (MJCardPrice.finish == "normal")
        )
        price_results = session.exec(price_query).all()
        price_map = {uuid: price for uuid, price in price_results if price}

        # Calculate total
        total = 0.0
        for card_uuid, count in cards:
            if card_uuid and card_uuid in price_map:
                total += price_map[card_uuid] * count

        return round(total, 2) if total > 0 else None

    def get_deck(self, identifier: str) -> dict | None:
        """
        Get deck by identifier.

        For precon decks: file_name (with or without .json)
        For user decks: numeric id
        """
        # Try as user deck id first
        try:
            deck_id = int(identifier)
            return self._get_user_deck(deck_id)
        except ValueError:
            pass

        # Try as precon deck file name
        return self._get_precon_deck(identifier)

    def _get_precon_deck(self, file_name: str) -> dict | None:
        """Get preconstructed deck details."""
        # Remove .json extension if present
        if file_name.endswith(".json"):
            file_name = file_name[:-5]

        with get_session() as session:
            query = select(MJDeck).where(MJDeck.file_name == file_name)
            deck = session.exec(query).first()

            if not deck:
                return None

            # Get cards by board
            main_board = self._get_deck_cards(session, deck.uuid, "mainBoard")
            side_board = self._get_deck_cards(session, deck.uuid, "sideBoard")
            commander = self._get_deck_cards(session, deck.uuid, "commander")

            # Stats
            stats = self._calculate_deck_stats(session, deck.uuid)

            # Colors
            colors = self._get_deck_colors(session, deck.uuid)

            # Price
            price = self._calculate_deck_price(session, deck.uuid)

            return {
                "uuid": deck.uuid,
                "meta": {
                    "file": deck.file_name + ".json",
                    "name": deck.name,
                    "code": deck.code,
                    "type": deck.type,
                    "release_date": deck.release_date,
                },
                "colors": colors,
                "commander": commander,
                "main_board": main_board,
                "side_board": side_board,
                "stats": stats,
                "price": price,
                "source": "precon",
            }

    def _get_user_deck(self, deck_id: int) -> dict | None:
        """Get user-created deck details."""
        with get_session() as session:
            query = select(UserDeck).where(UserDeck.id == deck_id)
            deck = session.exec(query).first()

            if not deck:
                return None

            # Get cards by board
            main_board = self._get_user_deck_cards(session, deck.id, "main")
            side_board = self._get_user_deck_cards(session, deck.id, "side")
            commander = self._get_user_deck_cards(session, deck.id, "commander")

            # Colors
            colors = self._get_user_deck_colors(session, deck.id)

            # Calculate stats and price from card data
            all_cards = main_board + side_board
            total_price = 0.0
            for c in all_cards:
                if c.get("price"):
                    total_price += c["price"] * c.get("count", 1)

            stats = self._calculate_user_deck_stats(main_board, side_board)

            return {
                "id": deck.id,
                "meta": {
                    "name": deck.name,
                    "description": deck.description,
                    "format": deck.format,
                },
                "colors": colors,
                "commander": commander,
                "main_board": main_board,
                "side_board": side_board,
                "stats": stats,
                "price": round(total_price, 2) if total_price > 0 else None,
                "created_at": deck.created_at.isoformat() if deck.created_at else None,
                "updated_at": deck.updated_at.isoformat() if deck.updated_at else None,
                "source": deck.source,
            }

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

    def _get_deck_cards(self, session, deck_uuid: str, board: str) -> list[dict]:
        """Get cards from a precon deck board with ownership status."""
        query = (
            select(MJDeckCard)
            .where((MJDeckCard.deck_uuid == deck_uuid) & (MJDeckCard.board == board))
            .order_by(MJDeckCard.mana_value, MJDeckCard.name)
        )
        deck_cards = session.exec(query).all()

        if not deck_cards:
            return []

        # Get ownership counts
        uuids = [c.card_uuid for c in deck_cards if c.card_uuid]
        ownership_map = {}
        if uuids:
            ownership_query = select(UserCard.card_uuid, UserCard.quantity_owned, UserCard.quantity_owned_foil).where(
                UserCard.card_uuid.in_(uuids)
            )
            for card_uuid, owned, owned_foil in session.exec(ownership_query).all():
                ownership_map[card_uuid] = (owned or 0) + (owned_foil or 0)

        # Get image URLs
        image_map = {}
        if uuids:
            image_query = select(MJCardIdentifier.card_uuid, MJCardIdentifier.scryfall_id).where(
                MJCardIdentifier.card_uuid.in_(uuids)
            )
            for card_uuid, scryfall_id in session.exec(image_query).all():
                image_map[card_uuid] = build_image_url(scryfall_id)

        # Get prices
        price_map = {}
        if uuids:
            price_query = select(MJCardPrice.card_uuid, MJCardPrice.price).where(
                (MJCardPrice.card_uuid.in_(uuids))
                & (MJCardPrice.provider == "tcgplayer")
                & (MJCardPrice.listing_type == "retail")
                & (MJCardPrice.finish == "normal")
            )
            for card_uuid, price in session.exec(price_query).all():
                price_map[card_uuid] = price

        # Get tags
        card_names = [dc.name for dc in deck_cards]
        tags_map = self._get_tags_for_names(session, card_names)

        cards = []
        for dc in deck_cards:
            owned_count = ownership_map.get(dc.card_uuid, 0)
            image_url = image_map.get(dc.card_uuid)
            price = price_map.get(dc.card_uuid)

            d = deck_card_to_api_dict(dc, owned_count, image_url, price)
            d["tags"] = tags_map.get(dc.name, [])
            cards.append(d)

        return cards

    def _get_user_deck_cards(self, session, deck_id: int, board: str) -> list[dict]:
        """Get cards from a user deck board."""
        query = (
            select(UserDeckCard, MJCard, MJCardIdentifier)
            .join(MJCard, UserDeckCard.card_uuid == MJCard.uuid)
            .outerjoin(MJCardIdentifier, MJCard.uuid == MJCardIdentifier.card_uuid)
            .where((UserDeckCard.deck_id == deck_id) & (UserDeckCard.board == board))
            .order_by(MJCard.mana_value, MJCard.name)
        )
        results = session.exec(query).all()

        if not results:
            return []

        # Get ownership and prices
        uuids = [r[1].uuid for r in results]
        ownership_query = select(UserCard.card_uuid, UserCard.quantity_owned, UserCard.quantity_owned_foil).where(
            UserCard.card_uuid.in_(uuids)
        )
        ownership_map = {}
        for card_uuid, owned, owned_foil in session.exec(ownership_query).all():
            ownership_map[card_uuid] = (owned or 0) + (owned_foil or 0)

        price_map = {}
        if uuids:
            price_query = select(MJCardPrice.card_uuid, MJCardPrice.price).where(
                MJCardPrice.card_uuid.in_(uuids),
                MJCardPrice.provider == "tcgplayer",
                MJCardPrice.listing_type == "retail",
                MJCardPrice.finish == "normal",
            )
            for card_uuid, price in session.exec(price_query).all():
                price_map[card_uuid] = price

        # Get tags
        card_names = [r[1].name for r in results]
        tags_map = self._get_tags_for_names(session, card_names)

        cards = []
        for deck_card, mj_card, identifier in results:
            owned_count = ownership_map.get(mj_card.uuid, 0)
            count = deck_card.count or 1

            cards.append(
                {
                    "card_uuid": mj_card.uuid,
                    "name": mj_card.printed_name or mj_card.name,
                    "count": count,
                    "board": deck_card.board,
                    "mana_cost": mj_card.mana_cost,
                    "mana_value": mj_card.mana_value,
                    "type": mj_card.type_line or "",
                    "types": mj_card.types or [],
                    "colors": mj_card.colors or [],
                    "rarity": mj_card.rarity or "",
                    "keywords": mj_card.keywords or [],
                    "tags": tags_map.get(mj_card.name, []),
                    "image_url": build_image_url(identifier.scryfall_id if identifier else None),
                    "price": price_map.get(mj_card.uuid),
                    "is_foil": deck_card.is_foil,
                    "owns_enough": owned_count >= count,
                    "owned_count": owned_count,
                    "missing_count": max(0, count - owned_count),
                }
            )

        return cards

    def _calculate_deck_stats(self, session, deck_uuid: str) -> dict:
        """Calculate statistics for a precon deck."""
        cards_query = select(MJDeckCard).where(
            (MJDeckCard.deck_uuid == deck_uuid) & (MJDeckCard.board.in_(["mainBoard", "sideBoard"]))
        )
        cards = session.exec(cards_query).all()

        total_cards = sum(c.count for c in cards)
        unique_cards = len(cards)

        # Mana curve (mainBoard only)
        main_cards = [c for c in cards if c.board == "mainBoard"]
        mana_curve = {}
        for card in main_cards:
            mv = card.mana_value
            if mv is None:
                key = "X"
            elif mv >= 7:
                key = "7+"
            else:
                key = str(int(mv))
            mana_curve[key] = mana_curve.get(key, 0) + card.count

        # Type distribution
        type_dist = {}
        for card in main_cards:
            types = card.types or []
            for t in types:
                type_dist[t] = type_dist.get(t, 0) + card.count

        # Color distribution
        color_dist = {"W": 0, "U": 0, "B": 0, "R": 0, "G": 0, "C": 0}
        for card in main_cards:
            colors = card.colors or []
            if not colors:
                color_dist["C"] += card.count
            else:
                for c in colors:
                    if c in color_dist:
                        color_dist[c] += card.count

        # Keyword frequencies (need to join MJCard for keywords)
        card_uuids = [c.card_uuid for c in main_cards if c.card_uuid]
        keyword_freq = {}
        if card_uuids:
            kw_query = select(MJCard.uuid, MJCard.keywords).where(MJCard.uuid.in_(card_uuids))
            kw_results = session.exec(kw_query).all()
            kw_map = {uuid: keywords or [] for uuid, keywords in kw_results}
            for card in main_cards:
                for kw in kw_map.get(card.card_uuid, []):
                    keyword_freq[kw] = keyword_freq.get(kw, 0) + card.count

        return {
            "total_cards": total_cards,
            "unique_cards": unique_cards,
            "mana_curve": mana_curve,
            "type_distribution": type_dist,
            "color_distribution": color_dist,
            "keyword_freq": keyword_freq,
        }

    def _calculate_mana_curve(self, cards: list[dict]) -> dict:
        """Calculate mana curve from card list."""
        mana_curve = {}
        for card in cards:
            mv = card.get("mana_value")
            count = card.get("count", 1)
            if mv is None:
                key = "X"
            elif mv >= 7:
                key = "7+"
            else:
                key = str(int(mv))
            mana_curve[key] = mana_curve.get(key, 0) + count
        return mana_curve

    def _calculate_user_deck_stats(self, main_board: list[dict], side_board: list[dict]) -> dict:
        """Calculate statistics for a user deck from card dicts."""
        all_cards = main_board + side_board

        # Type distribution (main board only)
        type_dist = {}
        for card in main_board:
            for t in card.get("types") or []:
                type_dist[t] = type_dist.get(t, 0) + card.get("count", 1)
            # Fallback: parse type_line if types is empty
            if not card.get("types") and card.get("type"):
                for t in ["Creature", "Instant", "Sorcery", "Enchantment", "Artifact", "Planeswalker", "Land"]:
                    if t in (card.get("type") or ""):
                        type_dist[t] = type_dist.get(t, 0) + card.get("count", 1)

        # Rarity distribution
        rarity_dist = {}
        for card in main_board:
            r = card.get("rarity")
            if r:
                rarity_dist[r] = rarity_dist.get(r, 0) + card.get("count", 1)

        # Color distribution (main board only)
        color_dist = {"W": 0, "U": 0, "B": 0, "R": 0, "G": 0, "C": 0}
        for card in main_board:
            colors = card.get("colors") or []
            if not colors:
                color_dist["C"] += card.get("count", 1)
            else:
                for c in colors:
                    if c in color_dist:
                        color_dist[c] += card.get("count", 1)

        # Price histogram
        price_histogram = []
        price_buckets = [0, 0.5, 1, 2, 5, 10, 25, 50, 100]
        for i in range(len(price_buckets)):
            lo = price_buckets[i]
            hi = price_buckets[i + 1] if i + 1 < len(price_buckets) else None
            count = 0
            for card in all_cards:
                p = card.get("price") or 0
                if hi is None:
                    if p >= lo:
                        count += card.get("count", 1)
                elif lo <= p < hi:
                    count += card.get("count", 1)
            if count > 0:
                range_str = f"${lo}+" if hi is None else f"${lo}-${hi}"
                price_histogram.append({"range": range_str, "count": count})

        # Keyword frequencies
        keyword_freq = {}
        for card in main_board:
            for kw in card.get("keywords") or []:
                keyword_freq[kw] = keyword_freq.get(kw, 0) + card.get("count", 1)

        return {
            "total_cards": sum(c.get("count", 1) for c in all_cards),
            "unique_cards": len(all_cards),
            "mana_curve": self._calculate_mana_curve(main_board),
            "type_distribution": type_dist,
            "rarity_distribution": rarity_dist,
            "color_distribution": color_dist,
            "price_histogram": price_histogram,
            "keyword_freq": keyword_freq,
        }

    # User deck management

    def create_user_deck(
        self,
        name: str,
        description: str | None = None,
        format: str | None = None,
        source: str = "user",
    ) -> dict:
        """Create a new user deck."""
        with get_session() as session:
            deck = UserDeck(
                name=name,
                description=description,
                format=format,
                source=source,
            )
            session.add(deck)
            session.commit()
            session.refresh(deck)

            return {
                "id": deck.id,
                "name": deck.name,
                "description": deck.description,
                "format": deck.format,
                "card_count": 0,
                "colors": [],
                "created_at": deck.created_at.isoformat() if deck.created_at else None,
                "source": deck.source,
            }

    def duplicate_deck(self, identifier: str) -> dict | None:
        """Duplicate any deck (user or precon) as a new user deck.

        Args:
            identifier: numeric deck ID (user deck) or file name (precon deck)

        Returns new deck dict or None if not found.
        """
        # Try as user deck first
        try:
            deck_id = int(identifier)
            return self._duplicate_user_deck(deck_id)
        except ValueError:
            pass
        # Try as precon deck
        return self._duplicate_precon_deck(identifier)

    def _duplicate_user_deck(self, deck_id: int) -> dict | None:
        with get_session() as session:
            original = session.exec(select(UserDeck).where(UserDeck.id == deck_id)).first()
            if not original:
                return None

            new_deck = UserDeck(
                name=f"{original.name} (Copy)",
                description=original.description,
                format=original.format,
                source="user",
            )
            session.add(new_deck)
            session.flush()

            cards = session.exec(select(UserDeckCard).where(UserDeckCard.deck_id == deck_id)).all()
            for card in cards:
                session.add(
                    UserDeckCard(
                        deck_id=new_deck.id,
                        card_uuid=card.card_uuid,
                        board=card.board,
                        count=card.count,
                        is_foil=card.is_foil,
                    )
                )

            session.commit()
            session.refresh(new_deck)

            total = sum(c.count for c in cards)
            return {
                "id": new_deck.id,
                "name": new_deck.name,
                "description": new_deck.description,
                "format": new_deck.format,
                "card_count": total,
                "source": new_deck.source,
            }

    def _duplicate_precon_deck(self, file_name: str) -> dict | None:
        if file_name.endswith(".json"):
            file_name = file_name[:-5]

        with get_session() as session:
            deck = session.exec(select(MJDeck).where(MJDeck.file_name == file_name)).first()
            if not deck:
                return None

            new_deck = UserDeck(
                name=f"{deck.name} (Copy)",
                source="user",
            )
            session.add(new_deck)
            session.flush()

            # Map precon board names to user deck board names
            board_map = {"mainBoard": "main", "sideBoard": "side", "commander": "commander"}
            precon_cards = session.exec(select(MJDeckCard).where(MJDeckCard.deck_uuid == deck.uuid)).all()

            for card in precon_cards:
                if not card.card_uuid:
                    continue
                session.add(
                    UserDeckCard(
                        deck_id=new_deck.id,
                        card_uuid=card.card_uuid,
                        board=board_map.get(card.board, "main"),
                        count=card.count or 1,
                    )
                )

            session.commit()
            session.refresh(new_deck)

            total = sum((c.count or 1) for c in precon_cards if c.card_uuid)
            return {
                "id": new_deck.id,
                "name": new_deck.name,
                "description": new_deck.description,
                "format": new_deck.format,
                "card_count": total,
                "source": new_deck.source,
            }

    def update_user_deck(
        self,
        deck_id: int,
        name: str | None = None,
        description: str | None = None,
        format: str | None = None,
    ) -> dict | None:
        """Update a user deck's metadata."""
        with get_session() as session:
            deck = session.exec(select(UserDeck).where(UserDeck.id == deck_id)).first()
            if not deck:
                return None

            if name is not None:
                deck.name = name
            if description is not None:
                deck.description = description
            if format is not None:
                deck.format = format

            session.add(deck)
            session.commit()

            return self._get_user_deck(deck_id)

    def delete_user_deck(self, deck_id: int) -> bool:
        """Delete a user deck and all its cards."""
        with get_session() as session:
            deck = session.exec(select(UserDeck).where(UserDeck.id == deck_id)).first()
            if not deck:
                return False

            # Delete deck cards first
            cards = session.exec(select(UserDeckCard).where(UserDeckCard.deck_id == deck_id)).all()
            for card in cards:
                session.delete(card)

            session.delete(deck)
            session.commit()
            return True

    def add_card_to_deck(
        self,
        deck_id: int,
        card_uuid: str,
        count: int = 1,
        board: str = "main",
        is_foil: bool = False,
    ) -> dict | None:
        """Add a card to a user deck."""
        with get_session() as session:
            # Verify deck exists
            deck = session.exec(select(UserDeck).where(UserDeck.id == deck_id)).first()
            if not deck:
                return None

            # Verify card exists
            card_exists = session.exec(select(MJCard.uuid).where(MJCard.uuid == card_uuid)).first()
            if not card_exists:
                return None

            # Check if card already in deck at this board
            existing = session.exec(
                select(UserDeckCard).where(
                    (UserDeckCard.deck_id == deck_id)
                    & (UserDeckCard.card_uuid == card_uuid)
                    & (UserDeckCard.board == board)
                )
            ).first()

            if existing:
                existing.count = (existing.count or 0) + count
                existing.is_foil = is_foil
                session.add(existing)
            else:
                deck_card = UserDeckCard(
                    deck_id=deck_id,
                    card_uuid=card_uuid,
                    count=count,
                    board=board,
                    is_foil=is_foil,
                )
                session.add(deck_card)

            session.commit()
            return self._get_user_deck(deck_id)

    def remove_card_from_deck(
        self,
        deck_id: int,
        card_uuid: str,
        board: str | None = None,
    ) -> bool:
        """Remove a card from a user deck."""
        with get_session() as session:
            query = select(UserDeckCard).where(
                (UserDeckCard.deck_id == deck_id) & (UserDeckCard.card_uuid == card_uuid)
            )
            if board:
                query = query.where(UserDeckCard.board == board)

            cards = session.exec(query).all()
            if not cards:
                return False

            for card in cards:
                session.delete(card)

            session.commit()
            return True

    def get_available_sets(self) -> list[str]:
        """Get list of set codes that have precon decks."""
        with get_session() as session:
            query = select(MJDeck.code).distinct().order_by(MJDeck.code)
            results = session.exec(query).all()
            return [c for c in results if c]

    def get_available_formats(self) -> list[str]:
        """Get list of distinct formats from card legality data."""
        from mtgdb.models import MJCardLegality

        with get_session() as session:
            query = select(MJCardLegality.format).distinct().order_by(MJCardLegality.format)
            return [f for f in session.exec(query).all() if f]

    def get_available_types(self) -> list[str]:
        """Get list of deck types."""
        with get_session() as session:
            query = select(MJDeck.type).distinct().where(MJDeck.type.is_not(None)).order_by(MJDeck.type)
            results = session.exec(query).all()
            return [t for t in results if t]

    # ── Pinned decks ──────────────────────────────────────────────────

    def get_pinned_files(self) -> list[str]:
        """Return all pinned deck file identifiers ordered by pin time."""
        with get_session() as session:
            query = select(PinnedDeck.deck_file).order_by(PinnedDeck.pinned_at.asc())
            return list(session.exec(query).all())

    def is_pinned(self, deck_file: str) -> bool:
        with get_session() as session:
            row = session.exec(select(PinnedDeck).where(PinnedDeck.deck_file == deck_file)).first()
            return row is not None

    def pin_deck(self, deck_file: str) -> bool:
        """Pin a deck. Returns True if newly pinned, False if already pinned."""
        with get_session() as session:
            existing = session.exec(select(PinnedDeck).where(PinnedDeck.deck_file == deck_file)).first()
            if existing:
                return False
            session.add(PinnedDeck(deck_file=deck_file))
            session.commit()
            return True

    def unpin_deck(self, deck_file: str) -> bool:
        """Unpin a deck. Returns True if unpinned, False if wasn't pinned."""
        with get_session() as session:
            existing = session.exec(select(PinnedDeck).where(PinnedDeck.deck_file == deck_file)).first()
            if not existing:
                return False
            session.delete(existing)
            session.commit()
            return True

    def get_pinned_summaries(self) -> list[dict]:
        """Return full deck summaries for all pinned decks, in pin order."""
        pinned_files = self.get_pinned_files()
        if not pinned_files:
            return []

        summaries = []
        with get_session() as session:
            for deck_file in pinned_files:
                summary = self._get_pinned_deck_summary(session, deck_file)
                if summary:
                    summaries.append(summary)
        return summaries

    def _get_pinned_deck_summary(self, session, deck_file: str) -> dict | None:
        """Get a single deck summary by file identifier (precon or user)."""
        # Try user deck (numeric id)
        try:
            deck_id = int(deck_file)
            user_deck = session.exec(select(UserDeck).where(UserDeck.id == deck_id)).first()
            if user_deck:
                card_count_row = session.exec(
                    select(func.sum(UserDeckCard.count)).where(UserDeckCard.deck_id == deck_id)
                ).first()
                colors_map = self._get_batch_user_deck_colors(session, [deck_id])
                price_map = self._get_batch_user_deck_prices(session, [deck_id])
                return {
                    "file": str(user_deck.id),
                    "name": user_deck.name,
                    "code": "",
                    "card_count": card_count_row or 0,
                    "colors": colors_map.get(deck_id, []),
                    "price": price_map.get(deck_id),
                    "release_date": None,
                    "source": user_deck.source,
                }
        except ValueError:
            pass

        # Try precon deck
        file_name = deck_file
        if file_name.endswith(".json"):
            file_name = file_name[:-5]

        deck = session.exec(select(MJDeck).where(MJDeck.file_name == file_name)).first()
        if not deck:
            return None

        deck_colors = self._get_batch_deck_colors(session, [deck.uuid]).get(deck.uuid, [])
        deck_price = self._get_batch_deck_prices(session, [deck.uuid]).get(deck.uuid)
        result = deck_to_api_dict(deck, deck_colors, deck_price)
        result["source"] = "precon"
        return result


# Singleton instance
decks_data = DecksData()

"""Decks data access layer using unified database schema."""

import logging

from mtgdb.models import (
    MJCard,
    MJCardIdentifier,
    MJCardPrice,
    MJDeck,
    MJDeckCard,
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
        card_count_min: int | None = None,
        card_count_max: int | None = None,
        sort: str = "name",
        order: str = "asc",
        page: int = 1,
        limit: int = 50,
    ) -> tuple[list[dict], int]:
        """List decks with filtering and pagination."""
        logger.debug(f"list_decks: q={q} set_code={set_code} deck_type={deck_type} source={source} sort={sort}")

        with get_session() as session:
            if source == "user":
                decks, total = self._list_user_decks(session, q, card_count_min, card_count_max, sort, order)
                offset = (page - 1) * limit
                decks = decks[offset : offset + limit]
            elif source == "precon":
                decks, total = self._list_precon_decks(
                    session, q, set_code, deck_type, colors, card_count_min, card_count_max,
                    sort, order, page, limit,
                )
            else:
                # Both sources
                precon_decks, precon_total = self._list_precon_decks(
                    session, q, set_code, deck_type, colors, card_count_min, card_count_max,
                    sort, order, page, limit,
                )
                user_decks, user_total = self._list_user_decks(
                    session, q, card_count_min, card_count_max, sort, order,
                )
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

        # Count total
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

            if colors and not all(c in deck_colors for c in colors):
                total -= 1
                continue

            deck_dict = deck_to_api_dict(deck, deck_colors, price_map.get(deck.uuid))
            deck_dict["source"] = "precon"
            decks.append(deck_dict)

        return decks, total

    def _get_batch_deck_colors(self, session, deck_uuids: list[str]) -> dict[str, list[str]]:
        """Get colors for multiple decks in a single query."""
        if not deck_uuids:
            return {}

        query = (
            select(MJDeckCard.deck_uuid, MJDeckCard.colors)
            .where(MJDeckCard.deck_uuid.in_(deck_uuids))
            .distinct()
        )
        results = session.exec(query).all()

        deck_colors: dict[str, set[str]] = {}
        for deck_uuid, color_list in results:
            if color_list:
                deck_colors.setdefault(deck_uuid, set()).update(color_list)

        wubrg = ["W", "U", "B", "R", "G"]
        return {
            uuid: sorted(c, key=lambda x: wubrg.index(x) if x in wubrg else 99)
            for uuid, c in deck_colors.items()
        }

    def _get_batch_deck_prices(self, session, deck_uuids: list[str]) -> dict[str, float | None]:
        """Get total deck prices for multiple decks in batch."""
        if not deck_uuids:
            return {}

        # Get all deck cards with their counts
        cards_query = (
            select(MJDeckCard.deck_uuid, MJDeckCard.card_uuid, MJDeckCard.count)
            .where(
                MJDeckCard.deck_uuid.in_(deck_uuids),
                MJDeckCard.board.in_(["mainBoard", "sideBoard"]),
            )
        )
        deck_cards = session.exec(cards_query).all()

        # Collect all unique card UUIDs
        all_card_uuids = list({card_uuid for _, card_uuid, _ in deck_cards if card_uuid})

        if not all_card_uuids:
            return {}

        # Single query for all prices
        price_query = (
            select(MJCardPrice.card_uuid, MJCardPrice.price)
            .where(
                MJCardPrice.card_uuid.in_(all_card_uuids),
                MJCardPrice.provider == "tcgplayer",
                MJCardPrice.listing_type == "retail",
                MJCardPrice.finish == "normal",
            )
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
    ) -> tuple[list[dict], int]:
        """List user-created decks."""
        query = select(UserDeck)

        if q:
            query = query.where(UserDeck.name.contains(q))

        # Count
        count_query = select(func.count()).select_from(query.subquery())
        total = session.exec(count_query).one()

        # Execute
        results = session.exec(query).all()

        decks = []
        for deck in results:
            # Count cards in deck
            card_count_query = select(func.sum(UserDeckCard.count)).where(UserDeckCard.deck_id == deck.id)
            card_count = session.exec(card_count_query).first() or 0

            # Filter by card count
            if card_count_min is not None and card_count < card_count_min:
                total -= 1
                continue
            if card_count_max is not None and card_count > card_count_max:
                total -= 1
                continue

            # Get colors
            colors = self._get_user_deck_colors(session, deck.id)

            decks.append(
                {
                    "id": deck.id,
                    "name": deck.name,
                    "description": deck.description,
                    "format": deck.format,
                    "card_count": card_count,
                    "colors": colors,
                    "created_at": deck.created_at.isoformat() if deck.created_at else None,
                    "updated_at": deck.updated_at.isoformat() if deck.updated_at else None,
                    "source": "user",
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

            # Calculate stats
            all_cards = main_board + side_board
            stats = {
                "total_cards": sum(c["count"] for c in all_cards),
                "unique_cards": len(all_cards),
                "mana_curve": self._calculate_mana_curve(main_board),
            }

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
                "created_at": deck.created_at.isoformat() if deck.created_at else None,
                "updated_at": deck.updated_at.isoformat() if deck.updated_at else None,
                "source": "user",
            }

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

        cards = []
        for dc in deck_cards:
            owned_count = ownership_map.get(dc.card_uuid, 0)
            image_url = image_map.get(dc.card_uuid)
            price = price_map.get(dc.card_uuid)

            cards.append(deck_card_to_api_dict(dc, owned_count, image_url, price))

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

        # Get ownership
        uuids = [r[1].uuid for r in results]
        ownership_query = select(UserCard.card_uuid, UserCard.quantity_owned, UserCard.quantity_owned_foil).where(
            UserCard.card_uuid.in_(uuids)
        )
        ownership_map = {}
        for card_uuid, owned, owned_foil in session.exec(ownership_query).all():
            ownership_map[card_uuid] = (owned or 0) + (owned_foil or 0)

        cards = []
        for deck_card, mj_card, identifier in results:
            owned_count = ownership_map.get(mj_card.uuid, 0)
            count = deck_card.count or 1

            cards.append(
                {
                    "card_uuid": mj_card.uuid,
                    "name": mj_card.name,
                    "count": count,
                    "board": deck_card.board,
                    "mana_cost": mj_card.mana_cost,
                    "mana_value": mj_card.mana_value,
                    "colors": mj_card.colors or [],
                    "types": mj_card.types or [],
                    "image_url": build_image_url(identifier.scryfall_id if identifier else None),
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

        return {
            "total_cards": total_cards,
            "unique_cards": unique_cards,
            "mana_curve": mana_curve,
            "type_distribution": type_dist,
            "color_distribution": color_dist,
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

    # User deck management

    def create_user_deck(
        self,
        name: str,
        description: str | None = None,
        format: str | None = None,
    ) -> dict:
        """Create a new user deck."""
        with get_session() as session:
            deck = UserDeck(
                name=name,
                description=description,
                format=format,
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
                "source": "user",
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

    def get_available_types(self) -> list[str]:
        """Get list of deck types."""
        with get_session() as session:
            query = select(MJDeck.type).distinct().where(MJDeck.type.is_not(None)).order_by(MJDeck.type)
            results = session.exec(query).all()
            return [t for t in results if t]


# Singleton instance
decks_data = DecksData()

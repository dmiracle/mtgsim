"""Decks data access layer."""

from sqlmodel import Session, func, select

from mtgsim.db.domain_models import DomainDeck, DomainDeckCard
from mtgsim.db.domain_session import get_domain_session
from mtgsim.db.reference_models import MTGJsonDeck, MTGJsonDeckCard


def _get_deck_price(deck_uuid: str, scope: str = "user") -> float | None:
    """Calculate total deck price from domain database."""
    try:
        with get_domain_session() as session:
            if scope == "reference":
                # Get card UUIDs and counts from reference deck
                deck_cards_query = select(MTGJsonDeckCard.card_uuid, MTGJsonDeckCard.count).where(
                    (MTGJsonDeckCard.deck_uuid == deck_uuid) & (MTGJsonDeckCard.board.in_(["mainBoard", "sideBoard"]))
                )
                cards = session.exec(deck_cards_query).all()
            else:
                # Get card UUIDs and counts from domain deck
                deck_cards_query = select(DomainDeckCard.card_uuid, DomainDeckCard.count).where(
                    (DomainDeckCard.deck_uuid == deck_uuid) & (DomainDeckCard.board.in_(["mainBoard", "sideBoard"]))
                )
                cards = session.exec(deck_cards_query).all()

            if not cards:
                return None

            # Get prices from domain cards (only domain cards have pricing)
            from mtgsim.db.domain_models import DomainCard

            uuids = [card_uuid for card_uuid, count in cards if card_uuid]
            if not uuids:
                return None

            price_query = select(DomainCard.uuid, DomainCard.tcgplayer_price_usd).where(DomainCard.uuid.in_(uuids))
            price_results = session.exec(price_query).all()
            price_map = {uuid: price for uuid, price in price_results if price}

            # Calculate total
            total = 0.0
            for card_uuid, count in cards:
                if card_uuid and card_uuid in price_map:
                    total += price_map[card_uuid] * count

            return round(total, 2) if total > 0 else None
    except Exception as e:
        # Maintain backward compatibility - if domain database fails, return None
        # This matches the original behavior when pricing database was unavailable
        if "no such table" in str(e).lower() or "database" in str(e).lower():
            return None
        else:
            # Re-raise unexpected errors
            raise


class DecksData:
    """Data access for decks."""

    def list_decks(
        self,
        q: str | None = None,
        format_filter: str | None = None,
        set_code: str | None = None,
        deck_type: str | None = None,
        colors: str | None = None,
        card_count_min: int | None = None,
        card_count_max: int | None = None,
        price_min: float | None = None,
        price_max: float | None = None,
        sort: str = "name",
        order: str = "asc",
        page: int = 1,
        limit: int = 50,
        scope: str = "user",  # "user", "reference", "combined"
    ) -> tuple[list[dict], int]:
        """
        List decks with filtering and pagination using domain database.

        Returns: (list of decks, total count)
        """
        try:
            with get_domain_session() as session:
                if scope == "reference":
                    return self._list_reference_decks(
                        session,
                        q,
                        format_filter,
                        set_code,
                        deck_type,
                        colors,
                        card_count_min,
                        card_count_max,
                        price_min,
                        price_max,
                        sort,
                        order,
                        page,
                        limit,
                    )
                elif scope == "combined":
                    return self._list_combined_decks(
                        session,
                        q,
                        format_filter,
                        set_code,
                        deck_type,
                        colors,
                        card_count_min,
                        card_count_max,
                        price_min,
                        price_max,
                        sort,
                        order,
                        page,
                        limit,
                    )
                else:  # scope == "user" (default)
                    return self._list_domain_decks(
                        session,
                        q,
                        format_filter,
                        set_code,
                        deck_type,
                        colors,
                        card_count_min,
                        card_count_max,
                        price_min,
                        price_max,
                        sort,
                        order,
                        page,
                        limit,
                    )
        except Exception as e:
            # Maintain backward compatibility - if domain database fails, return empty results
            if "no such table" in str(e).lower() or "database" in str(e).lower():
                return [], 0
            else:
                # Re-raise unexpected errors
                raise

    def _list_domain_decks(
        self,
        session: Session,
        q: str | None = None,
        format_filter: str | None = None,
        set_code: str | None = None,
        deck_type: str | None = None,
        colors: str | None = None,
        card_count_min: int | None = None,
        card_count_max: int | None = None,
        price_min: float | None = None,
        price_max: float | None = None,
        sort: str = "name",
        order: str = "asc",
        page: int = 1,
        limit: int = 50,
    ) -> tuple[list[dict], int]:
        """List user's domain decks."""
        query = select(DomainDeck)

        # Apply filters
        if q:
            query = query.where((DomainDeck.name.contains(q)) | (DomainDeck.file_name.contains(q)))

        if set_code:
            query = query.where(DomainDeck.code == set_code)

        if deck_type:
            query = query.where(DomainDeck.type == deck_type)

        if card_count_min is not None:
            query = query.where((DomainDeck.main_board_count + DomainDeck.side_board_count) >= card_count_min)

        if card_count_max is not None:
            query = query.where((DomainDeck.main_board_count + DomainDeck.side_board_count) <= card_count_max)

        if price_min is not None:
            query = query.where(DomainDeck.total_price_usd >= price_min)

        if price_max is not None:
            query = query.where(DomainDeck.total_price_usd <= price_max)

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total = session.exec(count_query).one()

        # Apply sorting
        sort_map = {
            "name": DomainDeck.name,
            "release_date": DomainDeck.release_date,
            "code": DomainDeck.code,
            "card_count": (DomainDeck.main_board_count + DomainDeck.side_board_count),
        }
        sort_field = sort_map.get(sort, DomainDeck.name)

        if order == "desc":
            query = query.order_by(sort_field.desc())
        else:
            query = query.order_by(sort_field.asc())

        # Apply pagination
        offset = (page - 1) * limit
        query = query.offset(offset).limit(limit)

        # Execute query
        results = session.exec(query).all()

        # Convert to dict format for API compatibility
        decks = []
        for deck in results:
            decks.append(
                {
                    "file": deck.file_name + ".json",
                    "name": deck.name,
                    "code": deck.code,
                    "type": deck.type,
                    "release_date": deck.release_date,
                    "card_count": deck.main_board_count + deck.side_board_count,
                    "colors": deck.color_identity,
                    "price": deck.total_price_usd,
                    "in_collection": True,
                }
            )

        return decks, total

    def _list_reference_decks(
        self,
        session: Session,
        q: str | None = None,
        format_filter: str | None = None,
        set_code: str | None = None,
        deck_type: str | None = None,
        colors: str | None = None,
        card_count_min: int | None = None,
        card_count_max: int | None = None,
        price_min: float | None = None,
        price_max: float | None = None,
        sort: str = "name",
        order: str = "asc",
        page: int = 1,
        limit: int = 50,
    ) -> tuple[list[dict], int]:
        """List reference decks."""
        query = select(MTGJsonDeck)

        # Apply filters
        if q:
            query = query.where((MTGJsonDeck.name.contains(q)) | (MTGJsonDeck.file_name.contains(q)))

        if set_code:
            query = query.where(MTGJsonDeck.code == set_code)

        if deck_type:
            query = query.where(MTGJsonDeck.type == deck_type)

        if card_count_min is not None:
            query = query.where((MTGJsonDeck.main_board_count + MTGJsonDeck.side_board_count) >= card_count_min)

        if card_count_max is not None:
            query = query.where((MTGJsonDeck.main_board_count + MTGJsonDeck.side_board_count) <= card_count_max)

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total = session.exec(count_query).one()

        # Apply sorting
        sort_map = {
            "name": MTGJsonDeck.name,
            "release_date": MTGJsonDeck.release_date,
            "code": MTGJsonDeck.code,
            "card_count": (MTGJsonDeck.main_board_count + MTGJsonDeck.side_board_count),
        }
        sort_field = sort_map.get(sort, MTGJsonDeck.name)

        if order == "desc":
            query = query.order_by(sort_field.desc())
        else:
            query = query.order_by(sort_field.asc())

        # Apply pagination
        offset = (page - 1) * limit
        query = query.offset(offset).limit(limit)

        # Execute query
        results = session.exec(query).all()

        # Convert to dict format for API compatibility
        decks = []
        for deck in results:
            # Get color identity for deck
            colors = self._get_deck_colors(session, deck.uuid, "reference")

            decks.append(
                {
                    "file": deck.file_name + ".json",
                    "name": deck.name,
                    "code": deck.code,
                    "type": deck.type,
                    "release_date": deck.release_date,
                    "card_count": deck.main_board_count + deck.side_board_count,
                    "colors": colors,
                    "price": None,  # No pricing for reference decks
                    "in_collection": False,
                }
            )

        return decks, total

    def _list_combined_decks(
        self,
        session: Session,
        q: str | None = None,
        format_filter: str | None = None,
        set_code: str | None = None,
        deck_type: str | None = None,
        colors: str | None = None,
        card_count_min: int | None = None,
        card_count_max: int | None = None,
        price_min: float | None = None,
        price_max: float | None = None,
        sort: str = "name",
        order: str = "asc",
        page: int = 1,
        limit: int = 50,
    ) -> tuple[list[dict], int]:
        """List both domain and reference decks."""
        # Get domain decks first
        domain_decks, _ = self._list_domain_decks(
            session,
            q,
            format_filter,
            set_code,
            deck_type,
            colors,
            card_count_min,
            card_count_max,
            price_min,
            price_max,
            sort,
            order,
            1,
            1000,
        )

        # Get reference decks, excluding those already in domain
        domain_uuids = {deck["file"].replace(".json", "") for deck in domain_decks}

        ref_query = select(MTGJsonDeck)
        if domain_uuids:
            ref_query = ref_query.where(MTGJsonDeck.file_name.not_in(domain_uuids))

        # Apply same filters to reference query
        if q:
            ref_query = ref_query.where((MTGJsonDeck.name.contains(q)) | (MTGJsonDeck.file_name.contains(q)))

        if set_code:
            ref_query = ref_query.where(MTGJsonDeck.code == set_code)

        if deck_type:
            ref_query = ref_query.where(MTGJsonDeck.type == deck_type)

        if card_count_min is not None:
            ref_query = ref_query.where((MTGJsonDeck.main_board_count + MTGJsonDeck.side_board_count) >= card_count_min)

        if card_count_max is not None:
            ref_query = ref_query.where((MTGJsonDeck.main_board_count + MTGJsonDeck.side_board_count) <= card_count_max)

        ref_results = session.exec(ref_query).all()

        # Convert reference decks to dict format
        ref_decks = []
        for deck in ref_results:
            colors = self._get_deck_colors(session, deck.uuid, "reference")

            ref_decks.append(
                {
                    "file": deck.file_name + ".json",
                    "name": deck.name,
                    "code": deck.code,
                    "type": deck.type,
                    "release_date": deck.release_date,
                    "card_count": deck.main_board_count + deck.side_board_count,
                    "colors": colors,
                    "price": None,
                    "in_collection": False,
                }
            )

        # Combine and sort all decks
        all_decks = domain_decks + ref_decks

        # Apply sorting to combined results
        sort_key_map = {
            "name": lambda x: x["name"] or "",
            "release_date": lambda x: x["release_date"] or "",
            "code": lambda x: x["code"] or "",
            "card_count": lambda x: x["card_count"] or 0,
        }
        sort_key = sort_key_map.get(sort, sort_key_map["name"])

        all_decks.sort(key=sort_key, reverse=(order == "desc"))

        # Apply pagination to combined results
        total = len(all_decks)
        offset = (page - 1) * limit
        paginated_decks = all_decks[offset : offset + limit]

        return paginated_decks, total

    def _get_deck_colors(self, session: Session, deck_uuid: str, scope: str = "user") -> list[str]:
        """Get combined color identity for a deck from domain database."""
        if scope == "reference":
            query = select(MTGJsonDeckCard.color_identity).where(MTGJsonDeckCard.deck_uuid == deck_uuid).distinct()
        else:
            query = select(DomainDeckCard.color_identity).where(DomainDeckCard.deck_uuid == deck_uuid).distinct()

        results = session.exec(query).all()

        colors = set()
        for color_identity in results:
            if color_identity:
                colors.update(color_identity)

        # Sort in WUBRG order
        order = ["W", "U", "B", "R", "G"]
        return sorted(colors, key=lambda c: order.index(c) if c in order else 99)

    def get_deck(self, file_name: str, scope: str = "user") -> dict | None:
        """Get full deck details by file name from domain database."""
        try:
            with get_domain_session() as session:
                if scope == "reference":
                    return self._get_reference_deck(session, file_name)
                elif scope == "combined":
                    # Try domain first, then reference
                    deck = self._get_domain_deck(session, file_name)
                    if deck:
                        return deck
                    return self._get_reference_deck(session, file_name)
                else:  # scope == "user" (default)
                    return self._get_domain_deck(session, file_name)
        except Exception as e:
            # Maintain backward compatibility - if domain database fails, return None
            if "no such table" in str(e).lower() or "database" in str(e).lower():
                return None
            else:
                # Re-raise unexpected errors
                raise

    def _get_domain_deck(self, session: Session, file_name: str) -> dict | None:
        """Get domain deck details by file name."""
        # Remove .json extension if present
        if file_name.endswith(".json"):
            file_name = file_name[:-5]

        query = select(DomainDeck).where(DomainDeck.file_name == file_name)
        deck = session.exec(query).first()

        if not deck:
            return None

        # Get cards by board
        main_board = self._get_deck_cards(session, deck.uuid, "mainBoard", "user")
        side_board = self._get_deck_cards(session, deck.uuid, "sideBoard", "user")
        commander = self._get_deck_cards(session, deck.uuid, "commander", "user")

        # Calculate stats
        stats = self._calculate_deck_stats(session, deck.uuid, "user")

        # Get colors
        colors = self._get_deck_colors(session, deck.uuid, "user")

        # Calculate legality
        legality = self._calculate_deck_legality(session, deck.uuid, "user")

        return {
            "meta": {
                "file": deck.file_name + ".json",
                "name": deck.name,
                "code": deck.code,
                "type": deck.type,
                "release_date": deck.release_date,
            },
            "colors": colors,
            "legality": legality,
            "commander": commander,
            "main_board": main_board,
            "side_board": side_board,
            "stats": stats,
            "price": deck.total_price_usd,
            "in_collection": True,
        }

    def _get_reference_deck(self, session: Session, file_name: str) -> dict | None:
        """Get reference deck details by file name."""
        # Remove .json extension if present
        if file_name.endswith(".json"):
            file_name = file_name[:-5]

        query = select(MTGJsonDeck).where(MTGJsonDeck.file_name == file_name)
        deck = session.exec(query).first()

        if not deck:
            return None

        # Get cards by board
        main_board = self._get_deck_cards(session, deck.uuid, "mainBoard", "reference")
        side_board = self._get_deck_cards(session, deck.uuid, "sideBoard", "reference")
        commander = self._get_deck_cards(session, deck.uuid, "commander", "reference")

        # Calculate stats
        stats = self._calculate_deck_stats(session, deck.uuid, "reference")

        # Get colors
        colors = self._get_deck_colors(session, deck.uuid, "reference")

        # Calculate legality
        legality = self._calculate_deck_legality(session, deck.uuid, "reference")

        return {
            "meta": {
                "file": deck.file_name + ".json",
                "name": deck.name,
                "code": deck.code,
                "type": deck.type,
                "release_date": deck.release_date,
            },
            "colors": colors,
            "legality": legality,
            "commander": commander,
            "main_board": main_board,
            "side_board": side_board,
            "stats": stats,
            "price": None,  # No pricing for reference decks
            "in_collection": False,
        }

    def _get_deck_cards(self, session: Session, deck_uuid: str, board: str, scope: str = "user") -> list[dict]:
        """Get cards from a specific board using domain database."""
        if scope == "reference":
            query = (
                select(MTGJsonDeckCard)
                .where((MTGJsonDeckCard.deck_uuid == deck_uuid) & (MTGJsonDeckCard.board == board))
                .order_by(MTGJsonDeckCard.mana_value, MTGJsonDeckCard.name)
            )
            deck_cards = session.exec(query).all()
        else:
            query = (
                select(DomainDeckCard)
                .where((DomainDeckCard.deck_uuid == deck_uuid) & (DomainDeckCard.board == board))
                .order_by(DomainDeckCard.mana_value, DomainDeckCard.name)
            )
            deck_cards = session.exec(query).all()

        if not deck_cards:
            return []

        # Get prices for domain cards only (reference cards don't have pricing)
        price_map = {}
        if scope == "user":
            from mtgsim.db.domain_models import DomainCard

            uuids = [card.card_uuid for card in deck_cards if card.card_uuid]
            if uuids:
                price_query = select(DomainCard.uuid, DomainCard.tcgplayer_price_usd).where(DomainCard.uuid.in_(uuids))
                price_results = session.exec(price_query).all()
                price_map = {uuid: price for uuid, price in price_results if price}

        cards = []
        for card in deck_cards:
            cards.append(
                {
                    "uuid": card.card_uuid,
                    "name": card.name,
                    "count": card.count,
                    "mana_cost": card.mana_cost,
                    "mana_value": card.mana_value,
                    "type": ", ".join(card.types) if card.types else card.type_line,
                    "rarity": card.rarity,
                    "color_identity": card.color_identity,
                    "text": getattr(card, "text", None),  # May not be available in all models
                    "image_url": self._build_image_url_from_name(card.name),  # Fallback image URL
                    "price": price_map.get(card.card_uuid) if scope == "user" else None,
                    "in_collection": scope == "user",
                }
            )

        return cards

    def _build_image_url_from_name(self, card_name: str) -> str | None:
        """Build a fallback image URL from card name (placeholder implementation)."""
        # This is a placeholder - in a real implementation, you'd need to look up
        # the scryfall_id from the card name
        return None

    def _calculate_deck_stats(self, session: Session, deck_uuid: str, scope: str = "user") -> dict:
        """Calculate deck statistics using domain database."""
        if scope == "reference":
            # Get cards from reference deck
            cards_query = select(MTGJsonDeckCard).where(
                (MTGJsonDeckCard.deck_uuid == deck_uuid) & (MTGJsonDeckCard.board.in_(["mainBoard", "sideBoard"]))
            )
            cards = session.exec(cards_query).all()
        else:
            # Get cards from domain deck
            cards_query = select(DomainDeckCard).where(
                (DomainDeckCard.deck_uuid == deck_uuid) & (DomainDeckCard.board.in_(["mainBoard", "sideBoard"]))
            )
            cards = session.exec(cards_query).all()

        # Total cards
        total_cards = sum(card.count for card in cards)
        unique_cards = len(cards)

        # Mana curve (mainBoard only)
        main_board_cards = [card for card in cards if card.board == "mainBoard"]
        mana_curve = {}
        for card in main_board_cards:
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
        for card in main_board_cards:
            types = card.types or []
            for t in types:
                type_dist[t] = type_dist.get(t, 0) + card.count

        # Rarity distribution
        rarity_dist = {}
        for card in main_board_cards:
            if card.rarity:
                rarity_dist[card.rarity] = rarity_dist.get(card.rarity, 0) + card.count

        # Color distribution
        color_dist = {"W": 0, "U": 0, "B": 0, "R": 0, "G": 0, "C": 0}
        for card in main_board_cards:
            colors = card.color_identity or []
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
            "rarity_distribution": rarity_dist,
            "color_distribution": color_dist,
        }

    def _calculate_deck_legality(self, session: Session, deck_uuid: str, scope: str = "user") -> dict:
        """Calculate deck legality across formats using domain database."""
        # For now, return a placeholder implementation
        # In a full implementation, this would check card legalities
        formats = ["standard", "pioneer", "modern", "legacy", "vintage", "commander"]
        legality = dict.fromkeys(formats, True)

        # TODO: Implement actual legality checking by looking up card legalities
        # This would require joining with card data to check individual card legalities

        return legality

    def get_available_sets(self, scope: str = "user") -> list[str]:
        """Get list of set codes that have decks from domain database."""
        try:
            with get_domain_session() as session:
                if scope == "reference":
                    query = select(MTGJsonDeck.code).distinct().order_by(MTGJsonDeck.code)
                elif scope == "combined":
                    # Get both domain and reference set codes
                    domain_query = select(DomainDeck.code).distinct()
                    ref_query = select(MTGJsonDeck.code).distinct()

                    domain_codes = set(session.exec(domain_query).all())
                    ref_codes = set(session.exec(ref_query).all())

                    all_codes = sorted(domain_codes.union(ref_codes))
                    return [c for c in all_codes if c]
                else:  # scope == "user" (default)
                    query = select(DomainDeck.code).distinct().order_by(DomainDeck.code)

                results = session.exec(query).all()
                return [c for c in results if c]
        except Exception as e:
            # Maintain backward compatibility - if domain database fails, return empty list
            if "no such table" in str(e).lower() or "database" in str(e).lower():
                return []
            else:
                # Re-raise unexpected errors
                raise

    def get_available_formats(self) -> list[str]:
        """Get list of formats decks are legal in."""
        return ["standard", "pioneer", "modern", "legacy", "vintage", "commander"]


# Singleton instance
decks_data = DecksData()

"""Cards data access layer using unified database schema."""

from sqlmodel import func, select

from mtgdb.models import MJCard, MJCardIdentifier, MJCardPrice, MJDeck, MJDeckCard, MJSet, UserCard
from mtgdb.session import get_session

from .helpers import build_image_url, card_to_api_dict


class CardsData:
    """Data access for cards using unified schema."""

    def search_cards(
        self,
        q: str | None = None,
        set_code: str | None = None,
        rarity: str | None = None,
        card_type: str | None = None,
        colors: list[str] | None = None,
        owns: bool | None = None,
        wants: bool | None = None,
        sort: str = "name",
        order: str = "asc",
        page: int = 1,
        limit: int = 50,
    ) -> tuple[list[dict], int]:
        """
        Search cards with automatic collection status.

        Args:
            q: Text search in name and type
            set_code: Filter by set code
            rarity: Filter by rarity
            card_type: Filter by card type
            colors: Filter by colors (card must have ALL specified colors)
            owns: Filter to owned (True) or not owned (False) cards
            wants: Filter to wanted (True) or not wanted (False) cards
            sort: Sort field (name, mana_value, rarity, set_code)
            order: Sort order (asc, desc)
            page: Page number (1-indexed)
            limit: Results per page

        Returns: (list of cards, total count)
        """
        with get_session() as session:
            # Base query with LEFT JOINs
            query = (
                select(MJCard, MJCardIdentifier, UserCard)
                .outerjoin(MJCardIdentifier, MJCard.uuid == MJCardIdentifier.card_uuid)
                .outerjoin(UserCard, MJCard.uuid == UserCard.card_uuid)
            )

            # Text search
            if q:
                query = query.where(
                    (MJCard.name.contains(q)) | (MJCard.type_line.contains(q)) | (MJCard.oracle_text.contains(q))
                )

            # Set filter
            if set_code:
                query = query.where(MJCard.set_code == set_code)

            # Rarity filter
            if rarity:
                query = query.where(MJCard.rarity == rarity)

            # Type filter
            if card_type:
                query = query.where(MJCard.type_line.contains(card_type))

            # Color filter (card must have ALL specified colors)
            if colors:
                for color in colors:
                    query = query.where(func.json_extract(MJCard.colors, "$").contains(f'"{color}"'))

            # Ownership filter
            if owns is True:
                query = query.where((UserCard.quantity_owned > 0) | (UserCard.quantity_owned_foil > 0))
            elif owns is False:
                query = query.where(
                    (UserCard.id.is_(None)) | ((UserCard.quantity_owned == 0) & (UserCard.quantity_owned_foil == 0))
                )

            # Wants filter
            if wants is True:
                query = query.where((UserCard.quantity_wanted > 0) | (UserCard.quantity_wanted_foil > 0))
            elif wants is False:
                query = query.where(
                    (UserCard.id.is_(None)) | ((UserCard.quantity_wanted == 0) & (UserCard.quantity_wanted_foil == 0))
                )

            # Count total before pagination
            count_query = select(func.count()).select_from(query.subquery())
            total = session.exec(count_query).one()

            # Sorting
            sort_map = {
                "name": MJCard.name,
                "mana_value": MJCard.mana_value,
                "rarity": MJCard.rarity,
                "set_code": MJCard.set_code,
            }
            sort_field = sort_map.get(sort, MJCard.name)

            if order == "desc":
                query = query.order_by(sort_field.desc())
            else:
                query = query.order_by(sort_field.asc())

            # Pagination
            offset = (page - 1) * limit
            query = query.offset(offset).limit(limit)

            # Execute
            results = session.exec(query).all()

            # Convert to API format
            cards = []
            for mj_card, identifier, user_card in results:
                cards.append(card_to_api_dict(mj_card, identifier, user_card))

            return cards, total

    def get_card(self, uuid: str) -> dict | None:
        """Get single card with collection status and prices."""
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

            # Get prices
            prices = self._get_card_prices(session, uuid)

            return card_to_api_dict(mj_card, identifier, user_card, prices, set_name)

    def _get_card_prices(self, session, uuid: str) -> dict | None:
        """Get prices for a card."""
        query = select(MJCardPrice).where(MJCardPrice.card_uuid == uuid)
        results = session.exec(query).all()

        if not results:
            return None

        prices = {}
        for price in results:
            provider = price.provider
            if provider not in prices:
                prices[provider] = {}
            prices[provider][price.finish] = price.price

        return prices

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
                        "name": mj_card.name,
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
            # Get the card name
            card_query = select(MJCard.name).where(MJCard.uuid == uuid)
            card_name = session.exec(card_query).first()

            if not card_name:
                return []

            # Find other printings
            query = (
                select(MJCard, MJCardIdentifier, UserCard)
                .outerjoin(MJCardIdentifier, MJCard.uuid == MJCardIdentifier.card_uuid)
                .outerjoin(UserCard, MJCard.uuid == UserCard.card_uuid)
                .where((MJCard.name == card_name) & (MJCard.uuid != uuid))
                .order_by(MJCard.set_code)
            )

            results = session.exec(query).all()

            printings = []
            for mj_card, identifier, user_card in results:
                # Get set name
                set_name = None
                if mj_card.set_code:
                    set_query = select(MJSet.name).where(MJSet.code == mj_card.set_code)
                    set_name = session.exec(set_query).first()

                total_owned = (user_card.quantity_owned or 0) + (user_card.quantity_owned_foil or 0) if user_card else 0

                printings.append(
                    {
                        "uuid": mj_card.uuid,
                        "set_code": mj_card.set_code,
                        "set_name": set_name,
                        "rarity": mj_card.rarity,
                        "number": mj_card.number,
                        "image_url": build_image_url(identifier.scryfall_id if identifier else None),
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


# Singleton instance
cards_data = CardsData()

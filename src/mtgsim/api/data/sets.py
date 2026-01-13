"""Sets data access layer using unified database schema."""

from sqlmodel import func, select

from mtgdb.models import MJCard, MJCardIdentifier, MJSet, UserCard
from mtgdb.session import get_session

from .helpers import build_image_url, set_to_api_dict


class SetsData:
    """Data access for sets using unified schema."""

    def list_sets(
        self,
        q: str | None = None,
        set_type: str | None = None,
        block: str | None = None,
        has_owned_cards: bool | None = None,
        sort: str = "release_date",
        order: str = "desc",
        page: int = 1,
        limit: int = 50,
    ) -> tuple[list[dict], int]:
        """
        List sets with filtering and pagination.

        Args:
            q: Text search in name and code
            set_type: Filter by set type (expansion, core, etc.)
            block: Filter by block name
            has_owned_cards: Filter to sets with owned cards
            sort: Sort field (name, release_date, code, size)
            order: Sort order (asc, desc)
            page: Page number (1-indexed)
            limit: Results per page

        Returns: (list of sets, total count)
        """
        with get_session() as session:
            query = select(MJSet)

            # Text search
            if q:
                query = query.where((MJSet.name.contains(q)) | (MJSet.code.contains(q)))

            # Type filter
            if set_type:
                query = query.where(MJSet.type == set_type)

            # Block filter
            if block:
                query = query.where(MJSet.block == block)

            # Count total before pagination
            count_query = select(func.count()).select_from(query.subquery())
            total = session.exec(count_query).one()

            # Sorting
            sort_map = {
                "name": MJSet.name,
                "release_date": MJSet.release_date,
                "code": MJSet.code,
                "size": MJSet.total_set_size,
            }
            sort_field = sort_map.get(sort, MJSet.release_date)

            if order == "desc":
                query = query.order_by(sort_field.desc())
            else:
                query = query.order_by(sort_field.asc())

            # Pagination
            offset = (page - 1) * limit
            query = query.offset(offset).limit(limit)

            # Execute
            results = session.exec(query).all()

            # Convert to API format with collection stats
            sets = []
            for mj_set in results:
                collection_stats = self._get_set_collection_stats(session, mj_set.code)

                # Filter by has_owned_cards if specified
                if has_owned_cards is True and collection_stats["owned_cards"] == 0:
                    total -= 1
                    continue
                elif has_owned_cards is False and collection_stats["owned_cards"] > 0:
                    total -= 1
                    continue

                sets.append(set_to_api_dict(mj_set, collection_stats))

            return sets, total

    def _get_set_collection_stats(self, session, set_code: str) -> dict:
        """Get collection statistics for a set."""
        # Total cards in set
        total_query = select(func.count(MJCard.uuid)).where(MJCard.set_code == set_code)
        total_cards = session.exec(total_query).first() or 0

        # Owned cards
        owned_query = (
            select(func.count(MJCard.uuid))
            .join(UserCard, MJCard.uuid == UserCard.card_uuid)
            .where(MJCard.set_code == set_code)
            .where((UserCard.quantity_owned > 0) | (UserCard.quantity_owned_foil > 0))
        )
        owned_cards = session.exec(owned_query).first() or 0

        # Wanted cards
        wanted_query = (
            select(func.count(MJCard.uuid))
            .join(UserCard, MJCard.uuid == UserCard.card_uuid)
            .where(MJCard.set_code == set_code)
            .where((UserCard.quantity_wanted > 0) | (UserCard.quantity_wanted_foil > 0))
        )
        wanted_cards = session.exec(wanted_query).first() or 0

        owned_percentage = round((owned_cards / total_cards * 100), 1) if total_cards > 0 else 0

        return {
            "total_cards": total_cards,
            "owned_cards": owned_cards,
            "owned_percentage": owned_percentage,
            "wanted_cards": wanted_cards,
        }

    def get_set(self, code: str) -> dict | None:
        """Get set metadata with collection stats."""
        with get_session() as session:
            query = select(MJSet).where(MJSet.code == code)
            mj_set = session.exec(query).first()

            if not mj_set:
                return None

            collection_stats = self._get_set_collection_stats(session, code)
            return set_to_api_dict(mj_set, collection_stats)

    def get_set_cards(
        self,
        code: str,
        rarity: str | None = None,
        color: str | None = None,
        card_type: str | None = None,
        owns: bool | None = None,
        wants: bool | None = None,
        sort: str = "number",
        order: str = "asc",
        page: int = 1,
        limit: int = 50,
    ) -> tuple[list[dict], int]:
        """
        Get cards in a set with filtering and collection status.

        Returns: (list of cards, total count)
        """
        with get_session() as session:
            query = (
                select(MJCard, MJCardIdentifier, UserCard)
                .outerjoin(MJCardIdentifier, MJCard.uuid == MJCardIdentifier.card_uuid)
                .outerjoin(UserCard, MJCard.uuid == UserCard.card_uuid)
                .where(MJCard.set_code == code)
            )

            # Rarity filter
            if rarity:
                query = query.where(MJCard.rarity == rarity)

            # Color filter
            if color:
                query = query.where(func.json_extract(MJCard.color_identity, "$").contains(f'"{color}"'))

            # Type filter
            if card_type:
                query = query.where(MJCard.type_line.contains(card_type))

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
                "number": MJCard.number,
                "mana_value": MJCard.mana_value,
                "rarity": MJCard.rarity,
            }
            sort_field = sort_map.get(sort, MJCard.number)

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
                total_owned = 0
                total_wanted = 0
                if user_card:
                    total_owned = (user_card.quantity_owned or 0) + (user_card.quantity_owned_foil or 0)
                    total_wanted = (user_card.quantity_wanted or 0) + (user_card.quantity_wanted_foil or 0)

                cards.append(
                    {
                        "uuid": mj_card.uuid,
                        "name": mj_card.name,
                        "mana_cost": mj_card.mana_cost,
                        "mana_value": mj_card.mana_value,
                        "type": mj_card.type_line,
                        "rarity": mj_card.rarity,
                        "color_identity": mj_card.color_identity or [],
                        "colors": mj_card.colors or [],
                        "power": mj_card.power,
                        "toughness": mj_card.toughness,
                        "number": mj_card.number,
                        "oracle_text": mj_card.oracle_text,
                        "image_url": build_image_url(identifier.scryfall_id if identifier else None),
                        "owns": total_owned > 0,
                        "wants": total_wanted > 0,
                        "total_owned": total_owned,
                        "total_wanted": total_wanted,
                    }
                )

            return cards, total

    def get_set_stats(self, code: str) -> dict:
        """Calculate statistics for a set."""
        with get_session() as session:
            cards_query = select(MJCard).where(MJCard.set_code == code)
            cards = session.exec(cards_query).all()

            if not cards:
                return {
                    "rarity_count": {},
                    "color_distribution": {},
                    "type_distribution": {},
                    "mana_curve": {},
                }

            # Rarity distribution
            rarity_count = {}
            for card in cards:
                rarity = card.rarity or "unknown"
                rarity_count[rarity] = rarity_count.get(rarity, 0) + 1

            # Color distribution
            color_count = {"W": 0, "U": 0, "B": 0, "R": 0, "G": 0, "C": 0}
            for card in cards:
                colors = card.color_identity or []
                if not colors:
                    color_count["C"] += 1
                else:
                    for c in colors:
                        if c in color_count:
                            color_count[c] += 1

            # Type distribution
            type_count = {}
            for card in cards:
                types = card.types or []
                for t in types:
                    type_count[t] = type_count.get(t, 0) + 1

            # Mana curve
            mana_curve = {}
            for card in cards:
                mv = card.mana_value
                if mv is None:
                    key = "X"
                elif mv >= 7:
                    key = "7+"
                else:
                    key = str(int(mv))
                mana_curve[key] = mana_curve.get(key, 0) + 1

            return {
                "rarity_count": rarity_count,
                "color_distribution": color_count,
                "type_distribution": type_count,
                "mana_curve": mana_curve,
            }

    def get_available_types(self) -> list[str]:
        """Get list of unique set types."""
        with get_session() as session:
            query = select(MJSet.type).distinct().where(MJSet.type.is_not(None)).order_by(MJSet.type)
            results = session.exec(query).all()
            return [t for t in results if t]

    def get_available_blocks(self) -> list[str]:
        """Get list of unique blocks."""
        with get_session() as session:
            query = select(MJSet.block).distinct().where(MJSet.block.is_not(None)).order_by(MJSet.block)
            results = session.exec(query).all()
            return [b for b in results if b]


# Singleton instance
sets_data = SetsData()

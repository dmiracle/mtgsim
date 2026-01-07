"""Sets data access layer."""

from sqlmodel import Session, func, select

from mtgsim.db.domain_models import DomainCard, DomainSet
from mtgsim.db.domain_session import get_domain_session
from mtgsim.db.reference_models import MTGJsonCard, MTGJsonSet


class SetsData:
    """Data access for sets."""

    def list_sets(
        self,
        q: str | None = None,
        set_type: str | None = None,
        block: str | None = None,
        sort: str = "release_date",
        order: str = "desc",
        page: int = 1,
        limit: int = 50,
        scope: str = "user",  # "user", "reference", "combined"
    ) -> tuple[list[dict], int]:
        """
        List sets with filtering and pagination using domain database.

        Returns: (list of sets, total count)
        """
        try:
            with get_domain_session() as session:
                if scope == "reference":
                    return self._list_reference_sets(session, q, set_type, block, sort, order, page, limit)
                elif scope == "combined":
                    return self._list_combined_sets(session, q, set_type, block, sort, order, page, limit)
                else:  # scope == "user" (default)
                    return self._list_domain_sets(session, q, set_type, block, sort, order, page, limit)
        except Exception as e:
            # Maintain backward compatibility - if domain database fails, return empty results
            if "no such table" in str(e).lower() or "database" in str(e).lower():
                return [], 0
            else:
                # Re-raise unexpected errors
                raise

    def _list_domain_sets(
        self,
        session: Session,
        q: str | None = None,
        set_type: str | None = None,
        block: str | None = None,
        sort: str = "release_date",
        order: str = "desc",
        page: int = 1,
        limit: int = 50,
    ) -> tuple[list[dict], int]:
        """List user's domain sets."""
        query = select(DomainSet)

        # Apply filters
        if q:
            query = query.where((DomainSet.name.contains(q)) | (DomainSet.code.contains(q)))

        if set_type:
            query = query.where(DomainSet.type == set_type)

        if block:
            query = query.where(DomainSet.block == block)

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total = session.exec(count_query).one()

        # Apply sorting
        sort_map = {
            "name": DomainSet.name,
            "release_date": DomainSet.release_date,
            "code": DomainSet.code,
            "size": DomainSet.total_set_size,
        }
        sort_field = sort_map.get(sort, DomainSet.release_date)

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
        sets = []
        for set_obj in results:
            sets.append(
                {
                    "code": set_obj.code,
                    "name": set_obj.name,
                    "type": set_obj.type,
                    "release_date": set_obj.release_date,
                    "base_set_size": set_obj.base_set_size,
                    "total_set_size": set_obj.total_set_size,
                    "block": set_obj.block,
                    "keyrune_code": set_obj.keyrune_code,
                    "in_collection": True,
                }
            )

        return sets, total

    def _list_reference_sets(
        self,
        session: Session,
        q: str | None = None,
        set_type: str | None = None,
        block: str | None = None,
        sort: str = "release_date",
        order: str = "desc",
        page: int = 1,
        limit: int = 50,
    ) -> tuple[list[dict], int]:
        """List reference sets."""
        query = select(MTGJsonSet)

        # Apply filters
        if q:
            query = query.where((MTGJsonSet.name.contains(q)) | (MTGJsonSet.code.contains(q)))

        if set_type:
            query = query.where(MTGJsonSet.type == set_type)

        if block:
            query = query.where(MTGJsonSet.block == block)

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total = session.exec(count_query).one()

        # Apply sorting
        sort_map = {
            "name": MTGJsonSet.name,
            "release_date": MTGJsonSet.release_date,
            "code": MTGJsonSet.code,
            "size": MTGJsonSet.total_set_size,
        }
        sort_field = sort_map.get(sort, MTGJsonSet.release_date)

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
        sets = []
        for set_obj in results:
            sets.append(
                {
                    "code": set_obj.code,
                    "name": set_obj.name,
                    "type": set_obj.type,
                    "release_date": set_obj.release_date,
                    "base_set_size": set_obj.base_set_size,
                    "total_set_size": set_obj.total_set_size,
                    "block": set_obj.block,
                    "keyrune_code": set_obj.keyrune_code,
                    "in_collection": False,
                }
            )

        return sets, total

    def _list_combined_sets(
        self,
        session: Session,
        q: str | None = None,
        set_type: str | None = None,
        block: str | None = None,
        sort: str = "release_date",
        order: str = "desc",
        page: int = 1,
        limit: int = 50,
    ) -> tuple[list[dict], int]:
        """List both domain and reference sets."""
        # Get domain sets first
        domain_sets, _ = self._list_domain_sets(session, q, set_type, block, sort, order, 1, 1000)

        # Get reference sets, excluding those already in domain
        domain_codes = {s["code"] for s in domain_sets}

        ref_query = select(MTGJsonSet)
        if domain_codes:
            ref_query = ref_query.where(MTGJsonSet.code.not_in(domain_codes))

        # Apply same filters to reference query
        if q:
            ref_query = ref_query.where((MTGJsonSet.name.contains(q)) | (MTGJsonSet.code.contains(q)))

        if set_type:
            ref_query = ref_query.where(MTGJsonSet.type == set_type)

        if block:
            ref_query = ref_query.where(MTGJsonSet.block == block)

        ref_results = session.exec(ref_query).all()

        # Convert reference sets to dict format
        ref_sets = []
        for set_obj in ref_results:
            ref_sets.append(
                {
                    "code": set_obj.code,
                    "name": set_obj.name,
                    "type": set_obj.type,
                    "release_date": set_obj.release_date,
                    "base_set_size": set_obj.base_set_size,
                    "total_set_size": set_obj.total_set_size,
                    "block": set_obj.block,
                    "keyrune_code": set_obj.keyrune_code,
                    "in_collection": False,
                }
            )

        # Combine and sort all sets
        all_sets = domain_sets + ref_sets

        # Apply sorting to combined results
        sort_key_map = {
            "name": lambda x: x["name"] or "",
            "release_date": lambda x: x["release_date"] or "",
            "code": lambda x: x["code"] or "",
            "size": lambda x: x["total_set_size"] or 0,
        }
        sort_key = sort_key_map.get(sort, sort_key_map["release_date"])

        all_sets.sort(key=sort_key, reverse=(order == "desc"))

        # Apply pagination to combined results
        total = len(all_sets)
        offset = (page - 1) * limit
        paginated_sets = all_sets[offset : offset + limit]

        return paginated_sets, total

    def get_set(self, code: str, scope: str = "user") -> dict | None:
        """Get set metadata by code from domain database."""
        try:
            with get_domain_session() as session:
                if scope == "reference":
                    return self._get_reference_set(session, code)
                elif scope == "combined":
                    # Try domain first, then reference
                    set_data = self._get_domain_set(session, code)
                    if set_data:
                        return set_data
                    return self._get_reference_set(session, code)
                else:  # scope == "user" (default)
                    return self._get_domain_set(session, code)
        except Exception as e:
            # Maintain backward compatibility - if domain database fails, return None
            if "no such table" in str(e).lower() or "database" in str(e).lower():
                return None
            else:
                # Re-raise unexpected errors
                raise

    def _get_domain_set(self, session: Session, code: str) -> dict | None:
        """Get domain set metadata by code."""
        query = select(DomainSet).where(DomainSet.code == code)
        set_obj = session.exec(query).first()

        if not set_obj:
            return None

        return {
            "code": set_obj.code,
            "name": set_obj.name,
            "type": set_obj.type,
            "release_date": set_obj.release_date,
            "base_set_size": set_obj.base_set_size,
            "total_set_size": set_obj.total_set_size,
            "block": set_obj.block,
            "keyrune_code": set_obj.keyrune_code,
            "is_foil_only": set_obj.is_foil_only,
            "is_online_only": set_obj.is_online_only,
            "mtgo_code": set_obj.mtgo_code,
            "tcgplayer_group_id": set_obj.tcgplayer_group_id,
            "cardmarket_id": set_obj.cardmarket_id,
            "languages": set_obj.languages,
            "translations": set_obj.translations,
            "in_collection": True,
        }

    def _get_reference_set(self, session: Session, code: str) -> dict | None:
        """Get reference set metadata by code."""
        query = select(MTGJsonSet).where(MTGJsonSet.code == code)
        set_obj = session.exec(query).first()

        if not set_obj:
            return None

        return {
            "code": set_obj.code,
            "name": set_obj.name,
            "type": set_obj.type,
            "release_date": set_obj.release_date,
            "base_set_size": set_obj.base_set_size,
            "total_set_size": set_obj.total_set_size,
            "block": set_obj.block,
            "keyrune_code": set_obj.keyrune_code,
            "is_foil_only": set_obj.is_foil_only,
            "is_online_only": set_obj.is_online_only,
            "mtgo_code": set_obj.mtgo_code,
            "tcgplayer_group_id": set_obj.tcgplayer_group_id,
            "cardmarket_id": set_obj.cardmarket_id,
            "languages": set_obj.languages,
            "translations": set_obj.translations,
            "in_collection": False,
        }

    def get_set_cards(
        self,
        code: str,
        rarity: str | None = None,
        color: str | None = None,
        card_type: str | None = None,
        page: int = 1,
        limit: int = 50,
        scope: str = "user",
    ) -> tuple[list[dict], int]:
        """
        Get cards in a set with filtering and pagination using domain database.

        Returns: (list of cards, total count)
        """
        with get_domain_session() as session:
            if scope == "reference":
                return self._get_reference_set_cards(session, code, rarity, color, card_type, page, limit)
            elif scope == "combined":
                return self._get_combined_set_cards(session, code, rarity, color, card_type, page, limit)
            else:  # scope == "user" (default)
                return self._get_domain_set_cards(session, code, rarity, color, card_type, page, limit)

    def _get_domain_set_cards(
        self,
        session: Session,
        code: str,
        rarity: str | None = None,
        color: str | None = None,
        card_type: str | None = None,
        page: int = 1,
        limit: int = 50,
    ) -> tuple[list[dict], int]:
        """Get cards in a domain set."""
        query = select(DomainCard).where(DomainCard.set_code == code)

        # Apply filters
        if rarity:
            query = query.where(DomainCard.rarity == rarity)

        if color:
            query = query.where(func.json_extract(DomainCard.color_identity, "$").contains(f'"{color}"'))

        if card_type:
            query = query.where(DomainCard.type_line.contains(card_type))

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total = session.exec(count_query).one()

        # Apply sorting by collector number
        query = query.order_by(DomainCard.collector_number)

        # Apply pagination
        offset = (page - 1) * limit
        query = query.offset(offset).limit(limit)

        # Execute query
        results = session.exec(query).all()

        # Convert to dict format for API compatibility
        cards = []
        for card in results:
            cards.append(
                {
                    "uuid": card.uuid,
                    "name": card.name,
                    "mana_cost": card.mana_cost,
                    "mana_value": card.mana_value,
                    "type": card.type_line,
                    "rarity": card.rarity,
                    "color_identity": card.color_identity,
                    "colors": card.colors,
                    "power": card.power,
                    "toughness": card.toughness,
                    "number": card.collector_number,
                    "text": card.oracle_text,
                    "image_url": card.image_url or self._build_image_url(card.scryfall_id),
                    "price": card.tcgplayer_price_usd,
                    "in_collection": True,
                }
            )

        return cards, total

    def _get_reference_set_cards(
        self,
        session: Session,
        code: str,
        rarity: str | None = None,
        color: str | None = None,
        card_type: str | None = None,
        page: int = 1,
        limit: int = 50,
    ) -> tuple[list[dict], int]:
        """Get cards in a reference set."""
        query = select(MTGJsonCard).where(MTGJsonCard.set_code == code)

        # Apply filters
        if rarity:
            query = query.where(MTGJsonCard.rarity == rarity)

        if color:
            query = query.where(func.json_extract(MTGJsonCard.color_identity, "$").contains(f'"{color}"'))

        if card_type:
            query = query.where(MTGJsonCard.type.contains(card_type))

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total = session.exec(count_query).one()

        # Apply sorting by collector number
        query = query.order_by(MTGJsonCard.number)

        # Apply pagination
        offset = (page - 1) * limit
        query = query.offset(offset).limit(limit)

        # Execute query
        results = session.exec(query).all()

        # Convert to dict format for API compatibility
        cards = []
        for card in results:
            cards.append(
                {
                    "uuid": card.uuid,
                    "name": card.name,
                    "mana_cost": card.mana_cost,
                    "mana_value": card.mana_value,
                    "type": card.type,
                    "rarity": card.rarity,
                    "color_identity": card.color_identity,
                    "colors": card.colors,
                    "power": card.power,
                    "toughness": card.toughness,
                    "number": card.number,
                    "text": card.oracle_text or card.text,
                    "image_url": self._build_image_url(card.scryfall_id),
                    "price": None,  # No pricing for reference cards
                    "in_collection": False,
                }
            )

        return cards, total

    def _get_combined_set_cards(
        self,
        session: Session,
        code: str,
        rarity: str | None = None,
        color: str | None = None,
        card_type: str | None = None,
        page: int = 1,
        limit: int = 50,
    ) -> tuple[list[dict], int]:
        """Get cards from both domain and reference sets."""
        # Get domain cards first
        domain_cards, _ = self._get_domain_set_cards(session, code, rarity, color, card_type, 1, 1000)

        # Get reference cards, excluding those already in domain
        domain_uuids = {card["uuid"] for card in domain_cards}

        ref_query = select(MTGJsonCard).where(MTGJsonCard.set_code == code)
        if domain_uuids:
            ref_query = ref_query.where(MTGJsonCard.uuid.not_in(domain_uuids))

        # Apply same filters to reference query
        if rarity:
            ref_query = ref_query.where(MTGJsonCard.rarity == rarity)

        if color:
            ref_query = ref_query.where(func.json_extract(MTGJsonCard.color_identity, "$").contains(f'"{color}"'))

        if card_type:
            ref_query = ref_query.where(MTGJsonCard.type.contains(card_type))

        ref_results = session.exec(ref_query).all()

        # Convert reference cards to dict format
        ref_cards = []
        for card in ref_results:
            ref_cards.append(
                {
                    "uuid": card.uuid,
                    "name": card.name,
                    "mana_cost": card.mana_cost,
                    "mana_value": card.mana_value,
                    "type": card.type,
                    "rarity": card.rarity,
                    "color_identity": card.color_identity,
                    "colors": card.colors,
                    "power": card.power,
                    "toughness": card.toughness,
                    "number": card.number,
                    "text": card.oracle_text or card.text,
                    "image_url": self._build_image_url(card.scryfall_id),
                    "price": None,
                    "in_collection": False,
                }
            )

        # Combine and sort all cards by collector number
        all_cards = domain_cards + ref_cards
        all_cards.sort(key=lambda x: (x["number"] or ""))

        # Apply pagination to combined results
        total = len(all_cards)
        offset = (page - 1) * limit
        paginated_cards = all_cards[offset : offset + limit]

        return paginated_cards, total

    def _build_image_url(self, scryfall_id: str | None) -> str | None:
        """Build Scryfall image URL from scryfall_id."""
        if not scryfall_id:
            return None
        return f"https://cards.scryfall.io/large/front/{scryfall_id[0]}/{scryfall_id[1]}/{scryfall_id}.jpg"

    def get_set_stats(self, code: str, scope: str = "user") -> dict:
        """Calculate statistics for a set using domain database."""
        with get_domain_session() as session:
            if scope == "reference":
                return self._get_reference_set_stats(session, code)
            elif scope == "combined":
                return self._get_combined_set_stats(session, code)
            else:  # scope == "user" (default)
                return self._get_domain_set_stats(session, code)

    def _get_domain_set_stats(self, session: Session, code: str) -> dict:
        """Calculate statistics for a domain set."""
        # Check if set has precomputed stats
        set_query = select(DomainSet).where(DomainSet.code == code)
        set_obj = session.exec(set_query).first()

        if set_obj and set_obj.card_count_by_rarity:
            return {
                "rarity_count": set_obj.card_count_by_rarity,
                "color_distribution": set_obj.color_distribution,
                "type_distribution": {},  # TODO: Add to domain model
                "keywords": {},  # TODO: Add to domain model
                "total_price": set_obj.total_price_usd,
            }

        # Calculate stats on the fly
        cards_query = select(DomainCard).where(DomainCard.set_code == code)
        cards = session.exec(cards_query).all()

        # Rarity distribution
        rarity_count = {}
        for card in cards:
            rarity_count[card.rarity] = rarity_count.get(card.rarity, 0) + 1

        # Color distribution
        color_count = {"W": 0, "U": 0, "B": 0, "R": 0, "G": 0, "C": 0}
        for card in cards:
            colors = card.color_identity
            if not colors:
                color_count["C"] += 1
            else:
                for c in colors:
                    if c in color_count:
                        color_count[c] += 1

        # Type distribution
        type_count = {}
        for card in cards:
            types = card.type_list
            for t in types:
                type_count[t] = type_count.get(t, 0) + 1

        # Calculate total set price
        total_price = sum(card.tcgplayer_price_usd or 0 for card in cards)

        return {
            "rarity_count": rarity_count,
            "color_distribution": color_count,
            "type_distribution": type_count,
            "keywords": {},  # TODO: Add keywords support
            "total_price": round(total_price, 2) if total_price > 0 else None,
        }

    def _get_reference_set_stats(self, session: Session, code: str) -> dict:
        """Calculate statistics for a reference set."""
        cards_query = select(MTGJsonCard).where(MTGJsonCard.set_code == code)
        cards = session.exec(cards_query).all()

        # Rarity distribution
        rarity_count = {}
        for card in cards:
            rarity_count[card.rarity] = rarity_count.get(card.rarity, 0) + 1

        # Color distribution
        color_count = {"W": 0, "U": 0, "B": 0, "R": 0, "G": 0, "C": 0}
        for card in cards:
            colors = card.color_identity
            if not colors:
                color_count["C"] += 1
            else:
                for c in colors:
                    if c in color_count:
                        color_count[c] += 1

        # Type distribution
        type_count = {}
        for card in cards:
            types = card.types
            for t in types:
                type_count[t] = type_count.get(t, 0) + 1

        # Keywords
        keyword_count = {}
        for card in cards:
            keywords = card.keywords
            for k in keywords:
                keyword_count[k] = keyword_count.get(k, 0) + 1

        return {
            "rarity_count": rarity_count,
            "color_distribution": color_count,
            "type_distribution": type_count,
            "keywords": keyword_count,
            "total_price": None,  # No pricing for reference sets
        }

    def _get_combined_set_stats(self, session: Session, code: str) -> dict:
        """Calculate statistics for combined domain and reference sets."""
        # For combined stats, prioritize domain stats if available
        domain_stats = self._get_domain_set_stats(session, code)
        ref_stats = self._get_reference_set_stats(session, code)

        # Merge stats (domain takes precedence)
        combined_stats = {
            "rarity_count": {**ref_stats["rarity_count"], **domain_stats["rarity_count"]},
            "color_distribution": {**ref_stats["color_distribution"], **domain_stats["color_distribution"]},
            "type_distribution": {**ref_stats["type_distribution"], **domain_stats["type_distribution"]},
            "keywords": ref_stats["keywords"],  # Use reference keywords
            "total_price": domain_stats["total_price"],  # Use domain pricing
        }

        return combined_stats

    def get_available_types(self, scope: str = "user") -> list[str]:
        """Get list of unique set types from domain database."""
        with get_domain_session() as session:
            if scope == "reference":
                query = select(MTGJsonSet.type).distinct().order_by(MTGJsonSet.type)
            elif scope == "combined":
                # Get both domain and reference types
                domain_query = select(DomainSet.type).distinct()
                ref_query = select(MTGJsonSet.type).distinct()

                domain_types = set(session.exec(domain_query).all())
                ref_types = set(session.exec(ref_query).all())

                all_types = sorted(domain_types.union(ref_types))
                return [t for t in all_types if t]
            else:  # scope == "user" (default)
                query = select(DomainSet.type).distinct().order_by(DomainSet.type)

            results = session.exec(query).all()
            return [t for t in results if t]

    def get_available_blocks(self, scope: str = "user") -> list[str]:
        """Get list of unique blocks from domain database."""
        with get_domain_session() as session:
            if scope == "reference":
                query = (
                    select(MTGJsonSet.block).distinct().where(MTGJsonSet.block.is_not(None)).order_by(MTGJsonSet.block)
                )
            elif scope == "combined":
                # Get both domain and reference blocks
                domain_query = select(DomainSet.block).distinct().where(DomainSet.block.is_not(None))
                ref_query = select(MTGJsonSet.block).distinct().where(MTGJsonSet.block.is_not(None))

                domain_blocks = set(session.exec(domain_query).all())
                ref_blocks = set(session.exec(ref_query).all())

                all_blocks = sorted(domain_blocks.union(ref_blocks))
                return [b for b in all_blocks if b]
            else:  # scope == "user" (default)
                query = select(DomainSet.block).distinct().where(DomainSet.block.is_not(None)).order_by(DomainSet.block)

            results = session.exec(query).all()
            return [b for b in results if b]


# Singleton instance
sets_data = SetsData()

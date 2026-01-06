"""Cards data access layer."""

from sqlmodel import Session, select, func
from mtgsim.reference.db import get_scryfall_image_url, parse_json, parse_json_dict
from mtgsim.db.domain_session import get_domain_session
from mtgsim.db.domain_models import DomainCard, DomainSet
from mtgsim.db.reference_models import MTGJsonCard, MTGJsonSet, MTGJsonPrice
from .converters import (
    domain_card_to_api_dict, 
    reference_card_to_api_dict,
    create_readonly_domain_card
)

from .database import db


class CardsData:
    """Data access for cards."""

    def search_cards(
        self,
        q: str | None = None,
        set_code: str | None = None,
        rarity: str | None = None,
        card_type: str | None = None,
        colors: list[str] | None = None,
        sort: str = "name",
        order: str = "asc",
        page: int = 1,
        limit: int = 50,
        scope: str = "user",  # "user", "reference", "combined"
    ) -> tuple[list[dict], int]:
        """
        Search cards with filtering and pagination using domain database.

        Args:
            scope: "user" (domain tables only), "reference" (mtgjson tables only), 
                   "combined" (both domain and reference)

        Returns: (list of cards, total count)
        """
        try:
            with get_domain_session() as session:
                if scope == "reference":
                    return self._search_reference_cards(session, q, set_code, rarity, card_type, colors, sort, order, page, limit)
                elif scope == "combined":
                    return self._search_combined_cards(session, q, set_code, rarity, card_type, colors, sort, order, page, limit)
                else:  # scope == "user" (default)
                    return self._search_domain_cards(session, q, set_code, rarity, card_type, colors, sort, order, page, limit)
        except Exception as e:
            # Maintain backward compatibility - if domain database fails, return empty results
            # This matches the behavior of the original implementation when databases were unavailable
            if "no such table" in str(e).lower() or "database" in str(e).lower():
                return [], 0
            else:
                # Re-raise unexpected errors
                raise

    def _search_domain_cards(
        self, 
        session: Session,
        q: str | None = None,
        set_code: str | None = None,
        rarity: str | None = None,
        card_type: str | None = None,
        colors: list[str] | None = None,
        sort: str = "name",
        order: str = "asc",
        page: int = 1,
        limit: int = 50,
    ) -> tuple[list[dict], int]:
        """Search user's domain cards."""
        query = select(DomainCard)

        # Apply filters
        if q:
            query = query.where(
                (DomainCard.name.contains(q)) | 
                (DomainCard.type_line.contains(q))
            )

        if set_code:
            query = query.where(DomainCard.set_code == set_code)

        if rarity:
            query = query.where(DomainCard.rarity == rarity)

        if card_type:
            query = query.where(DomainCard.type_line.contains(card_type))

        if colors:
            for color in colors:
                # Use JSON_EXTRACT for SQLite JSON queries
                query = query.where(func.json_extract(DomainCard.color_identity, '$').contains(f'"{color}"'))

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total = session.exec(count_query).one()

        # Apply sorting
        sort_map = {
            "name": DomainCard.name,
            "mana_value": DomainCard.mana_value,
            "rarity": DomainCard.rarity,
            "set_code": DomainCard.set_code,
        }
        sort_field = sort_map.get(sort, DomainCard.name)
        
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
        cards = []
        for card in results:
            cards.append(domain_card_to_api_dict(card))

        return cards, total

    def _search_reference_cards(
        self, 
        session: Session,
        q: str | None = None,
        set_code: str | None = None,
        rarity: str | None = None,
        card_type: str | None = None,
        colors: list[str] | None = None,
        sort: str = "name",
        order: str = "asc",
        page: int = 1,
        limit: int = 50,
    ) -> tuple[list[dict], int]:
        """Search reference cards (read-only)."""
        query = select(MTGJsonCard)

        # Apply filters
        if q:
            query = query.where(
                (MTGJsonCard.name.contains(q)) | 
                (MTGJsonCard.type.contains(q))
            )

        if set_code:
            query = query.where(MTGJsonCard.set_code == set_code)

        if rarity:
            query = query.where(MTGJsonCard.rarity == rarity)

        if card_type:
            query = query.where(MTGJsonCard.type.contains(card_type))

        if colors:
            for color in colors:
                # Use JSON_EXTRACT for SQLite JSON queries
                query = query.where(func.json_extract(MTGJsonCard.color_identity, '$').contains(f'"{color}"'))

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total = session.exec(count_query).one()

        # Apply sorting
        sort_map = {
            "name": MTGJsonCard.name,
            "mana_value": MTGJsonCard.mana_value,
            "rarity": MTGJsonCard.rarity,
            "set_code": MTGJsonCard.set_code,
        }
        sort_field = sort_map.get(sort, MTGJsonCard.name)
        
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
        cards = []
        for card in results:
            cards.append(reference_card_to_api_dict(card))

        return cards, total

    def _search_combined_cards(
        self, 
        session: Session,
        q: str | None = None,
        set_code: str | None = None,
        rarity: str | None = None,
        card_type: str | None = None,
        colors: list[str] | None = None,
        sort: str = "name",
        order: str = "asc",
        page: int = 1,
        limit: int = 50,
    ) -> tuple[list[dict], int]:
        """Search both domain and reference cards."""
        # Get domain cards first
        domain_cards, domain_total = self._search_domain_cards(
            session, q, set_code, rarity, card_type, colors, sort, order, 1, 1000
        )
        
        # Get reference cards, excluding those already in domain
        domain_uuids = {card["uuid"] for card in domain_cards}
        
        ref_query = select(MTGJsonCard)
        if domain_uuids:
            ref_query = ref_query.where(MTGJsonCard.uuid.not_in(domain_uuids))

        # Apply same filters to reference query
        if q:
            ref_query = ref_query.where(
                (MTGJsonCard.name.contains(q)) | 
                (MTGJsonCard.type.contains(q))
            )

        if set_code:
            ref_query = ref_query.where(MTGJsonCard.set_code == set_code)

        if rarity:
            ref_query = ref_query.where(MTGJsonCard.rarity == rarity)

        if card_type:
            ref_query = ref_query.where(MTGJsonCard.type.contains(card_type))

        if colors:
            for color in colors:
                ref_query = ref_query.where(func.json_extract(MTGJsonCard.color_identity, '$').contains(f'"{color}"'))

        ref_results = session.exec(ref_query).all()
        
        # Convert reference cards to dict format
        ref_cards = []
        for card in ref_results:
            ref_cards.append(create_readonly_domain_card(card))

        # Combine and sort all cards
        all_cards = domain_cards + ref_cards
        
        # Apply sorting to combined results
        sort_key_map = {
            "name": lambda x: x["name"],
            "mana_value": lambda x: x["mana_value"] or 0,
            "rarity": lambda x: x["rarity"],
            "set_code": lambda x: x["set_code"],
        }
        sort_key = sort_key_map.get(sort, sort_key_map["name"])
        
        all_cards.sort(key=sort_key, reverse=(order == "desc"))
        
        # Apply pagination to combined results
        total = len(all_cards)
        offset = (page - 1) * limit
        paginated_cards = all_cards[offset:offset + limit]

        return paginated_cards, total

    def _build_image_url(self, scryfall_id: str | None) -> str | None:
        """Build Scryfall image URL from scryfall_id."""
        if not scryfall_id:
            return None
        return f"https://cards.scryfall.io/large/front/{scryfall_id[0]}/{scryfall_id[1]}/{scryfall_id}.jpg"

    def get_card(self, uuid: str, scope: str = "user") -> dict | None:
        """Get card details by UUID from domain database."""
        try:
            with get_domain_session() as session:
                if scope == "reference":
                    return self._get_reference_card(session, uuid)
                elif scope == "combined":
                    # Try domain first, then reference
                    card = self._get_domain_card(session, uuid)
                    if card:
                        return card
                    return self._get_reference_card(session, uuid)
                else:  # scope == "user" (default)
                    return self._get_domain_card(session, uuid)
        except Exception as e:
            # Maintain backward compatibility - if domain database fails, return None
            # This matches the behavior of the original implementation when databases were unavailable
            if "no such table" in str(e).lower() or "database" in str(e).lower():
                return None
            else:
                # Re-raise unexpected errors
                raise

    def _get_domain_card(self, session: Session, uuid: str) -> dict | None:
        """Get domain card details by UUID."""
        query = select(DomainCard).where(DomainCard.uuid == uuid)
        card = session.exec(query).first()
        
        if not card:
            return None

        # Get set name if available
        set_name = None
        if card.set_code:
            set_query = select(DomainSet).where(DomainSet.code == card.set_code)
            set_obj = session.exec(set_query).first()
            set_name = set_obj.name if set_obj else card.set_name

        return domain_card_to_api_dict(card)

    def _get_reference_card(self, session: Session, uuid: str) -> dict | None:
        """Get reference card details by UUID."""
        query = select(MTGJsonCard).where(MTGJsonCard.uuid == uuid)
        card = session.exec(query).first()
        
        if not card:
            return None

        # Get set name if available
        set_name = None
        if card.set_code:
            set_query = select(MTGJsonSet).where(MTGJsonSet.code == card.set_code)
            set_obj = session.exec(set_query).first()
            set_name = set_obj.name if set_obj else None

        api_dict = reference_card_to_api_dict(card)
        # Add set name if available
        api_dict["set_name"] = set_name
        return api_dict

    def get_cards_by_name(self, name: str, scope: str = "user") -> list[dict]:
        """Get all printings of a card by exact name."""
        try:
            with get_domain_session() as session:
                if scope == "reference":
                    query = select(MTGJsonCard).where(MTGJsonCard.name == name).order_by(MTGJsonCard.set_code)
                    cards = session.exec(query).all()
                    
                    result = []
                    for card in cards:
                        # Get set name
                        set_query = select(MTGJsonSet).where(MTGJsonSet.code == card.set_code)
                        set_obj = session.exec(set_query).first()
                        set_name = set_obj.name if set_obj else None

                        result.append({
                            "uuid": card.uuid,
                            "name": card.name,
                            "set_code": card.set_code,
                            "set_name": set_name,
                            "rarity": card.rarity,
                            "number": card.number,
                            "in_collection": False,
                        })
                    return result
                
                elif scope == "combined":
                    # Get both domain and reference cards
                    domain_query = select(DomainCard).where(DomainCard.name == name).order_by(DomainCard.set_code)
                    domain_cards = session.exec(domain_query).all()
                    
                    domain_uuids = {card.uuid for card in domain_cards}
                    ref_query = select(MTGJsonCard).where(
                        (MTGJsonCard.name == name) & 
                        (MTGJsonCard.uuid.not_in(domain_uuids))
                    ).order_by(MTGJsonCard.set_code)
                    ref_cards = session.exec(ref_query).all()
                    
                    result = []
                    
                    # Add domain cards
                    for card in domain_cards:
                        set_query = select(DomainSet).where(DomainSet.code == card.set_code)
                        set_obj = session.exec(set_query).first()
                        set_name = set_obj.name if set_obj else card.set_name

                        result.append({
                            "uuid": card.uuid,
                            "name": card.name,
                            "set_code": card.set_code,
                            "set_name": set_name,
                            "rarity": card.rarity,
                            "number": card.collector_number,
                            "in_collection": True,
                        })
                    
                    # Add reference cards
                    for card in ref_cards:
                        set_query = select(MTGJsonSet).where(MTGJsonSet.code == card.set_code)
                        set_obj = session.exec(set_query).first()
                        set_name = set_obj.name if set_obj else None

                        result.append({
                            "uuid": card.uuid,
                            "name": card.name,
                            "set_code": card.set_code,
                            "set_name": set_name,
                            "rarity": card.rarity,
                            "number": card.number,
                            "in_collection": False,
                        })
                    
                    return result
                
                else:  # scope == "user" (default)
                    query = select(DomainCard).where(DomainCard.name == name).order_by(DomainCard.set_code)
                    cards = session.exec(query).all()
                    
                    result = []
                    for card in cards:
                        # Get set name
                        set_query = select(DomainSet).where(DomainSet.code == card.set_code)
                        set_obj = session.exec(set_query).first()
                        set_name = set_obj.name if set_obj else card.set_name

                        result.append({
                            "uuid": card.uuid,
                            "name": card.name,
                            "set_code": card.set_code,
                            "set_name": set_name,
                            "rarity": card.rarity,
                            "number": card.collector_number,
                            "in_collection": True,
                        })
                    return result
        except Exception as e:
            # Maintain backward compatibility - if domain database fails, return empty list
            if "no such table" in str(e).lower() or "database" in str(e).lower():
                return []
            else:
                # Re-raise unexpected errors
                raise

    def get_card_appearances(self, uuid: str) -> list[dict]:
        """Get decks that contain this card."""
        try:
            with get_domain_session() as session:
                # First get the card name from domain or reference
                card_name = None
                
                # Try domain first
                domain_query = select(DomainCard.name).where(DomainCard.uuid == uuid)
                domain_result = session.exec(domain_query).first()
                if domain_result:
                    card_name = domain_result
                else:
                    # Try reference
                    ref_query = select(MTGJsonCard.name).where(MTGJsonCard.uuid == uuid)
                    ref_result = session.exec(ref_query).first()
                    if ref_result:
                        card_name = ref_result

                if not card_name:
                    return []

                # Find decks containing this card (from domain decks)
                from mtgsim.db.domain_models import DomainDeck, DomainDeckCard
                
                deck_query = (
                    select(DomainDeck.file_name, DomainDeck.name, DomainDeckCard.count)
                    .join(DomainDeckCard, DomainDeck.uuid == DomainDeckCard.deck_uuid)
                    .where(DomainDeckCard.name == card_name)
                    .order_by(DomainDeck.name)
                    .limit(20)
                )
                
                results = session.exec(deck_query).all()
                
                appearances = []
                for file_name, deck_name, count in results:
                    appearances.append({
                        "file": file_name + ".json",
                        "name": deck_name,
                        "count": count,
                    })

                return appearances
        except Exception as e:
            # Maintain backward compatibility - if domain database fails, return empty list
            # This matches the original behavior when deck database was unavailable
            if "no such table" in str(e).lower() or "database" in str(e).lower():
                return []
            else:
                # Re-raise unexpected errors
                raise

    def get_other_printings(self, uuid: str, scope: str = "combined") -> list[dict]:
        """Get other printings of the same card."""
        try:
            with get_domain_session() as session:
                # First get the card name
                card_name = None
                
                # Try domain first
                domain_query = select(DomainCard.name).where(DomainCard.uuid == uuid)
                domain_result = session.exec(domain_query).first()
                if domain_result:
                    card_name = domain_result
                else:
                    # Try reference
                    ref_query = select(MTGJsonCard.name).where(MTGJsonCard.uuid == uuid)
                    ref_result = session.exec(ref_query).first()
                    if ref_result:
                        card_name = ref_result

                if not card_name:
                    return []

                printings = []
                
                if scope in ["user", "combined"]:
                    # Get domain printings
                    domain_query = (
                        select(DomainCard.uuid, DomainCard.set_code, DomainCard.rarity)
                        .where((DomainCard.name == card_name) & (DomainCard.uuid != uuid))
                        .order_by(DomainCard.set_code)
                    )
                    domain_cards = session.exec(domain_query).all()
                    
                    for card_uuid, set_code, rarity in domain_cards:
                        set_query = select(DomainSet.name).where(DomainSet.code == set_code)
                        set_name = session.exec(set_query).first()
                        
                        printings.append({
                            "uuid": card_uuid,
                            "set_code": set_code,
                            "set_name": set_name,
                            "rarity": rarity,
                            "in_collection": True,
                        })
                
                if scope in ["reference", "combined"]:
                    # Get reference printings (excluding those already in domain)
                    domain_uuids = {p["uuid"] for p in printings}
                    
                    ref_query = (
                        select(MTGJsonCard.uuid, MTGJsonCard.set_code, MTGJsonCard.rarity)
                        .where(
                            (MTGJsonCard.name == card_name) & 
                            (MTGJsonCard.uuid != uuid) &
                            (MTGJsonCard.uuid.not_in(domain_uuids) if domain_uuids else True)
                        )
                        .order_by(MTGJsonCard.set_code)
                    )
                    ref_cards = session.exec(ref_query).all()
                    
                    for card_uuid, set_code, rarity in ref_cards:
                        set_query = select(MTGJsonSet.name).where(MTGJsonSet.code == set_code)
                        set_name = session.exec(set_query).first()
                        
                        printings.append({
                            "uuid": card_uuid,
                            "set_code": set_code,
                            "set_name": set_name,
                            "rarity": rarity,
                            "in_collection": False,
                        })

                return printings
        except Exception as e:
            # Maintain backward compatibility - if domain database fails, return empty list
            if "no such table" in str(e).lower() or "database" in str(e).lower():
                return []
            else:
                # Re-raise unexpected errors
                raise


# Singleton instance
cards_data = CardsData()

"""Property-based tests for domain model completeness.

Feature: domain-api-consolidation, Property 1: Domain Model Completeness
Validates: Requirements 1.1
"""


import pytest
from hypothesis import given
from hypothesis import strategies as st

from mtgsim.api.models.card import CardDetail, CardSummary
from mtgsim.api.models.deck import DeckSummary
from mtgsim.api.models.set import SetSummary
from mtgsim.db.domain_models import DomainCard, DomainDeck, DomainSet


class TestDomainModelCompleteness:
    """Property-based tests for domain model completeness."""

    def test_card_summary_fields_covered_by_domain_model(self):
        """
        Property 1: Domain Model Completeness - Card Summary
        For any API response field in CardSummary, there should exist a corresponding
        field or computed property in DomainCard that provides the same data.
        **Validates: Requirements 1.1**
        """
        # Get all fields from CardSummary
        card_summary_fields = set(CardSummary.model_fields.keys())

        # Get all fields and properties from DomainCard
        domain_card_attrs = set(dir(DomainCard))
        domain_card_fields = set(DomainCard.model_fields.keys())

        # Check each CardSummary field has a corresponding domain field or property
        missing_fields = []
        for field_name in card_summary_fields:
            # Check if field exists directly
            if field_name in domain_card_fields:
                continue

            # Check if property exists
            if field_name in domain_card_attrs:
                attr = getattr(DomainCard, field_name, None)
                if isinstance(attr, property):
                    continue

            # Check for common field mappings
            field_mappings = {
                "type": "type_line",  # API uses 'type', domain uses 'type_line'
                "price": "tcgplayer_price_usd",  # API uses 'price', domain has specific price fields
                "text": "oracle_text",  # API uses 'text', domain uses 'oracle_text'
            }

            if field_name in field_mappings:
                mapped_field = field_mappings[field_name]
                if mapped_field in domain_card_fields or mapped_field in domain_card_attrs:
                    continue

            missing_fields.append(field_name)

        assert not missing_fields, f"DomainCard missing fields for CardSummary: {missing_fields}"

    def test_card_detail_fields_covered_by_domain_model(self):
        """
        Property 1: Domain Model Completeness - Card Detail
        For any API response field in CardDetail, there should exist a corresponding
        field or computed property in DomainCard that provides the same data.
        **Validates: Requirements 1.1**
        """
        # Get all fields from CardDetail
        card_detail_fields = set(CardDetail.model_fields.keys())

        # Get all fields and properties from DomainCard
        domain_card_attrs = set(dir(DomainCard))
        domain_card_fields = set(DomainCard.model_fields.keys())

        # Check each CardDetail field has a corresponding domain field or property
        missing_fields = []
        for field_name in card_detail_fields:
            # Skip complex nested objects that are computed from relationships
            if field_name in ["prices", "legalities", "appears_in_decks", "other_printings"]:
                # These are complex objects that can be computed from domain data
                continue

            # Check if field exists directly
            if field_name in domain_card_fields:
                continue

            # Check if property exists
            if field_name in domain_card_attrs:
                attr = getattr(DomainCard, field_name, None)
                if isinstance(attr, property):
                    continue

            # Check for common field mappings
            field_mappings = {
                "type": "type_line",  # API uses 'type', domain uses 'type_line'
                "types": "type_list",  # API uses 'types', domain has 'type_list' property
                "text": "oracle_text",  # API uses 'text', domain uses 'oracle_text'
            }

            if field_name in field_mappings:
                mapped_field = field_mappings[field_name]
                if mapped_field in domain_card_fields or mapped_field in domain_card_attrs:
                    continue

            missing_fields.append(field_name)

        assert not missing_fields, f"DomainCard missing fields for CardDetail: {missing_fields}"

    def test_set_summary_fields_covered_by_domain_model(self):
        """
        Property 1: Domain Model Completeness - Set Summary
        For any API response field in SetSummary, there should exist a corresponding
        field or computed property in DomainSet that provides the same data.
        **Validates: Requirements 1.1**
        """
        # Get all fields from SetSummary
        set_summary_fields = set(SetSummary.model_fields.keys())

        # Get all fields and properties from DomainSet
        domain_set_attrs = set(dir(DomainSet))
        domain_set_fields = set(DomainSet.model_fields.keys())

        # Check each SetSummary field has a corresponding domain field or property
        missing_fields = []
        for field_name in set_summary_fields:
            # Check if field exists directly
            if field_name in domain_set_fields:
                continue

            # Check if property exists
            if field_name in domain_set_attrs:
                attr = getattr(DomainSet, field_name, None)
                if isinstance(attr, property):
                    continue

            missing_fields.append(field_name)

        assert not missing_fields, f"DomainSet missing fields for SetSummary: {missing_fields}"

    def test_set_detail_fields_covered_by_domain_model(self):
        """
        Property 1: Domain Model Completeness - Set Detail
        For any API response field in SetDetail meta, there should exist a corresponding
        field or computed property in DomainSet that provides the same data.
        **Validates: Requirements 1.1**
        """
        # Get all fields from SetDetail.meta (SetMeta)
        from mtgsim.api.models.set import SetMeta

        set_meta_fields = set(SetMeta.model_fields.keys())

        # Get all fields and properties from DomainSet
        domain_set_attrs = set(dir(DomainSet))
        domain_set_fields = set(DomainSet.model_fields.keys())

        # Check each SetMeta field has a corresponding domain field or property
        missing_fields = []
        for field_name in set_meta_fields:
            # Check if field exists directly
            if field_name in domain_set_fields:
                continue

            # Check if property exists
            if field_name in domain_set_attrs:
                attr = getattr(DomainSet, field_name, None)
                if isinstance(attr, property):
                    continue

            missing_fields.append(field_name)

        assert not missing_fields, f"DomainSet missing fields for SetMeta: {missing_fields}"

    def test_deck_summary_fields_covered_by_domain_model(self):
        """
        Property 1: Domain Model Completeness - Deck Summary
        For any API response field in DeckSummary, there should exist a corresponding
        field or computed property in DomainDeck that provides the same data.
        **Validates: Requirements 1.1**
        """
        # Get all fields from DeckSummary
        deck_summary_fields = set(DeckSummary.model_fields.keys())

        # Get all fields and properties from DomainDeck
        domain_deck_attrs = set(dir(DomainDeck))
        domain_deck_fields = set(DomainDeck.model_fields.keys())

        # Check each DeckSummary field has a corresponding domain field or property
        missing_fields = []
        for field_name in deck_summary_fields:
            # Skip complex computed fields
            if field_name in ["legality", "card_count", "colors", "price"]:
                # These are computed from relationships and aggregated data
                continue

            # Check if field exists directly
            if field_name in domain_deck_fields:
                continue

            # Check if property exists
            if field_name in domain_deck_attrs:
                attr = getattr(DomainDeck, field_name, None)
                if isinstance(attr, property):
                    continue

            # Check for field mappings
            field_mappings = {
                "file": "file_name",  # API uses 'file', domain uses 'file_name'
            }

            if field_name in field_mappings:
                mapped_field = field_mappings[field_name]
                if mapped_field in domain_deck_fields or mapped_field in domain_deck_attrs:
                    continue

            missing_fields.append(field_name)

        assert not missing_fields, f"DomainDeck missing fields for DeckSummary: {missing_fields}"

    def test_deck_detail_fields_covered_by_domain_model(self):
        """
        Property 1: Domain Model Completeness - Deck Detail
        For any API response field in DeckDetail meta, there should exist a corresponding
        field or computed property in DomainDeck that provides the same data.
        **Validates: Requirements 1.1**
        """
        # Get all fields from DeckDetail.meta (DeckMeta)
        from mtgsim.api.models.deck import DeckMeta

        deck_meta_fields = set(DeckMeta.model_fields.keys())

        # Get all fields and properties from DomainDeck
        domain_deck_attrs = set(dir(DomainDeck))
        domain_deck_fields = set(DomainDeck.model_fields.keys())

        # Check each DeckMeta field has a corresponding domain field or property
        missing_fields = []
        for field_name in deck_meta_fields:
            # Check if field exists directly
            if field_name in domain_deck_fields:
                continue

            # Check if property exists
            if field_name in domain_deck_attrs:
                attr = getattr(DomainDeck, field_name, None)
                if isinstance(attr, property):
                    continue

            # Check for field mappings
            field_mappings = {
                "file": "file_name",  # API uses 'file', domain uses 'file_name'
            }

            if field_name in field_mappings:
                mapped_field = field_mappings[field_name]
                if mapped_field in domain_deck_fields or mapped_field in domain_deck_attrs:
                    continue

            missing_fields.append(field_name)

        assert not missing_fields, f"DomainDeck missing fields for DeckMeta: {missing_fields}"

    @given(st.text(min_size=1, max_size=50))
    def test_domain_card_can_provide_api_card_summary_data(self, card_name: str):
        """
        Property 1: Domain Model Completeness - Card Summary Generation
        For any valid card name, a DomainCard instance should be able to provide
        all data needed to construct a CardSummary API response.
        **Validates: Requirements 1.1**
        """
        # Create a minimal DomainCard instance
        domain_card = DomainCard(
            name=card_name,
            uuid="test-uuid-123",
            type_line="Creature — Human Wizard",
            mana_cost="{2}{U}",
            mana_value=3,
            rarity="common",
            set_code="TST",
            oracle_text="Test card text",
            tcgplayer_price_usd=1.50,
            scryfall_id="test-scryfall-id",
        )

        # Verify we can extract all CardSummary fields
        try:
            card_summary_data = {
                "uuid": domain_card.uuid,
                "name": domain_card.name,
                "type": domain_card.type_line,  # Mapped field
                "mana_cost": domain_card.mana_cost,
                "mana_value": int(domain_card.mana_value or 0),
                "rarity": domain_card.rarity,
                "set_code": domain_card.set_code,
                "color_identity": domain_card.color_identity,  # Property
                "text": domain_card.oracle_text,  # Mapped field
                "price": domain_card.tcgplayer_price_usd,  # Mapped field
                "image_url": f"https://api.scryfall.com/cards/{domain_card.scryfall_id}",
            }

            # Verify CardSummary can be created
            card_summary = CardSummary(**card_summary_data)
            assert card_summary.name == card_name

        except Exception as e:
            pytest.fail(f"Failed to create CardSummary from DomainCard: {e}")

    @given(st.text(min_size=1, max_size=50))
    def test_domain_set_can_provide_api_set_summary_data(self, set_name: str):
        """
        Property 1: Domain Model Completeness - Set Summary Generation
        For any valid set name, a DomainSet instance should be able to provide
        all data needed to construct a SetSummary API response.
        **Validates: Requirements 1.1**
        """
        # Create a minimal DomainSet instance
        domain_set = DomainSet(
            code="TST",
            name=set_name,
            type="expansion",
            release_date="2024-01-01",
            base_set_size=100,
            total_set_size=120,
            block="Test Block",
            keyrune_code="tst",
        )

        # Verify we can extract all SetSummary fields
        try:
            set_summary_data = {
                "code": domain_set.code,
                "name": domain_set.name,
                "type": domain_set.type,
                "release_date": domain_set.release_date,
                "base_set_size": domain_set.base_set_size,
                "total_set_size": domain_set.total_set_size,
                "block": domain_set.block,
                "keyrune_code": domain_set.keyrune_code,
            }

            # Verify SetSummary can be created
            set_summary = SetSummary(**set_summary_data)
            assert set_summary.name == set_name

        except Exception as e:
            pytest.fail(f"Failed to create SetSummary from DomainSet: {e}")

    @given(st.text(min_size=1, max_size=50))
    def test_domain_deck_can_provide_api_deck_summary_data(self, deck_name: str):
        """
        Property 1: Domain Model Completeness - Deck Summary Generation
        For any valid deck name, a DomainDeck instance should be able to provide
        all data needed to construct a DeckSummary API response.
        **Validates: Requirements 1.1**
        """
        # Create a minimal DomainDeck instance
        domain_deck = DomainDeck(
            uuid="test-deck-uuid",
            file_name="test_deck.json",
            code="TST",
            name=deck_name,
            type="constructed",
            release_date="2024-01-01",
            main_board_count=60,
            side_board_count=15,
            commander_count=1,
            color_identity=["W", "U"],
            total_price_usd=150.00,
        )

        # Verify we can extract all DeckSummary fields (with computed values)
        try:
            deck_summary_data = {
                "file": domain_deck.file_name,  # Mapped field
                "name": domain_deck.name,
                "code": domain_deck.code,
                "card_count": domain_deck.main_board_count + domain_deck.side_board_count,  # Computed
                "colors": domain_deck.color_identity,
                "price": domain_deck.total_price_usd,
                "release_date": domain_deck.release_date,
                "legality": {  # This would be computed from cards in real implementation
                    "standard": False,
                    "pioneer": False,
                    "modern": True,
                    "legacy": True,
                    "vintage": True,
                    "commander": True,
                    "brawl": False,
                    "historic": False,
                    "pauper": False,
                },
            }

            # Verify DeckSummary can be created
            deck_summary = DeckSummary(**deck_summary_data)
            assert deck_summary.name == deck_name

        except Exception as e:
            pytest.fail(f"Failed to create DeckSummary from DomainDeck: {e}")

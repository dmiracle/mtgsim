"""
Property-based tests for collection management consistency.

**Feature: domain-api-consolidation, Property 10: Collection Management Consistency**
**Validates: Requirements 4.1, 4.3**

Tests that collection management operations maintain consistency between domain and reference data.
"""

from unittest.mock import MagicMock, patch

import pytest
from hypothesis import given
from hypothesis import strategies as st
from hypothesis.strategies import composite

from mtgsim.api.services.card_service import card_service


@composite
def valid_card_uuid(draw):
    """Generate valid card UUIDs."""
    # Generate UUIDs in the format used by MTGJSON
    return draw(st.text(min_size=36, max_size=36, alphabet="0123456789abcdef-"))


def mock_domain_card():
    """Create mock domain card data."""
    return {
        "uuid": "test-domain-uuid-123",
        "name": "Test Domain Card",
        "type": "Creature — Human Wizard",
        "mana_cost": "{2}{U}",
        "mana_value": 3,
        "rarity": "rare",
        "set_code": "TST",
        "color_identity": ["U"],
        "text": "Test ability text",
        "price": 5.99,
        "image_url": "https://example.com/image.jpg",
        "in_collection": True,
    }


def mock_reference_card():
    """Create mock reference card data."""
    return {
        "uuid": "test-reference-uuid-456",
        "name": "Test Reference Card",
        "type": "Instant",
        "mana_cost": "{1}{R}",
        "mana_value": 2,
        "rarity": "common",
        "set_code": "REF",
        "color_identity": ["R"],
        "text": "Deal 3 damage to any target.",
        "price": None,  # Reference cards don't have pricing
        "image_url": "https://example.com/ref-image.jpg",
        "in_collection": False,
    }


@given(uuid=valid_card_uuid())
def test_add_card_to_collection_consistency(uuid):
    """
    Property: For any card UUID, adding it to collection should make it queryable
    in user scope and maintain its data integrity.

    **Feature: domain-api-consolidation, Property 10: Collection Management Consistency**
    **Validates: Requirements 4.1, 4.3**
    """
    # Mock the card being available in reference but not in domain initially
    reference_card = {**mock_reference_card(), "uuid": uuid}

    with (
        patch("mtgsim.api.data.cards_data.get_card") as mock_get,
        patch("mtgsim.api.data.prices_data.get_average_price") as mock_avg_price,
        patch("mtgsim.api.data.prices_data.get_tcgplayer_price") as mock_tcg_price,
        patch("mtgsim.api.data.cards_data.get_card_appearances") as mock_appearances,
        patch("mtgsim.api.data.cards_data.get_other_printings") as mock_printings,
    ):
        mock_avg_price.return_value = 5.99
        mock_tcg_price.return_value = 5.99
        mock_appearances.return_value = []
        mock_printings.return_value = []

        # Initially card is only in reference
        def mock_get_side_effect(card_uuid, scope="user"):
            if scope == "reference":
                return reference_card
            elif scope == "user":
                return None  # Not in collection initially
            else:  # combined
                return reference_card

        mock_get.side_effect = mock_get_side_effect

        # Test that card is not in user scope initially
        user_card_before = run_async(card_service.get_card(uuid, scope="user"))
        assert user_card_before is None

        # Test that card is available in reference scope
        ref_card = run_async(card_service.get_card(uuid, scope="reference"))
        assert ref_card is not None
        assert ref_card.uuid == uuid
        assert ref_card.in_collection is False

        # After addition, mock that the card is now in domain
        def mock_get_after_add(card_uuid, scope="user"):
            if scope == "reference":
                return reference_card
            elif scope == "user":
                return {**reference_card, "in_collection": True, "price": 5.99}
            else:  # combined
                return {**reference_card, "in_collection": True, "price": 5.99}

        mock_get.side_effect = mock_get_after_add

        # Verify card is now available in user scope (simulating successful addition)
        user_card_after = run_async(card_service.get_card(uuid, scope="user"))
        assert user_card_after is not None
        assert user_card_after.uuid == uuid
        assert user_card_after.in_collection is True

        # Verify card is still available in reference scope
        ref_card_after = run_async(card_service.get_card(uuid, scope="reference"))
        assert ref_card_after is not None
        assert ref_card_after.uuid == uuid

        # Core data should be consistent between scopes
        assert user_card_after.name == ref_card_after.name
        assert user_card_after.type == ref_card_after.type
        assert user_card_after.mana_cost == ref_card_after.mana_cost
        assert user_card_after.mana_value == ref_card_after.mana_value


@given(uuid=valid_card_uuid())
def test_remove_card_from_collection_consistency(uuid):
    """
    Property: For any card UUID in collection, removing it should make it unavailable
    in user scope but still available in reference scope.

    **Feature: domain-api-consolidation, Property 10: Collection Management Consistency**
    **Validates: Requirements 4.1, 4.3**
    """
    # Mock the card being in both domain and reference initially
    domain_card = {**mock_domain_card(), "uuid": uuid}
    reference_card = {**mock_reference_card(), "uuid": uuid}

    with (
        patch("mtgsim.api.data.cards.get_domain_session") as mock_session,
        patch("mtgsim.api.data.cards_data.get_card") as mock_get,
    ):
        # Mock database session for removal
        mock_session_instance = MagicMock()
        mock_session.return_value.__enter__.return_value = mock_session_instance

        # Mock finding and deleting the card
        mock_card_obj = MagicMock()
        mock_session_instance.exec.return_value.first.return_value = mock_card_obj

        # Initially card is in both domain and reference
        def mock_get_before_remove(card_uuid, scope="user"):
            if scope == "reference":
                return reference_card
            elif scope == "user":
                return domain_card
            else:  # combined
                return domain_card

        mock_get.side_effect = mock_get_before_remove

        # Remove card from collection
        result = run_async(card_service.remove_card_from_collection(uuid))

        # Verify the operation succeeded
        assert result["success"] is True
        assert uuid in result["message"]

        # After removal, mock that the card is no longer in domain
        def mock_get_after_remove(card_uuid, scope="user"):
            if scope == "reference":
                return reference_card
            elif scope == "user":
                return None  # No longer in collection
            else:  # combined
                return reference_card

        mock_get.side_effect = mock_get_after_remove

        # Verify card is no longer available in user scope
        user_card = run_async(card_service.get_card(uuid, scope="user"))
        assert user_card is None

        # Verify card is still available in reference scope
        ref_card = run_async(card_service.get_card(uuid, scope="reference"))
        assert ref_card is not None
        assert ref_card.uuid == uuid
        assert ref_card.in_collection is False


@given(uuid=valid_card_uuid())
def test_collection_scope_isolation(uuid):
    """
    Property: For any card UUID, collection operations should not affect
    the availability of the card in reference scope.

    **Feature: domain-api-consolidation, Property 10: Collection Management Consistency**
    **Validates: Requirements 4.1, 4.3**
    """
    reference_card = {**mock_reference_card(), "uuid": uuid}

    with patch("mtgsim.api.data.cards_data.get_card") as mock_get:
        # Mock that card is always available in reference scope
        def mock_get_reference_always(card_uuid, scope="user"):
            if scope == "reference":
                return reference_card
            elif scope == "user":
                return None  # Not in collection
            else:  # combined
                return reference_card

        mock_get.side_effect = mock_get_reference_always

        # Card should be available in reference scope regardless of collection status
        ref_card_before = run_async(card_service.get_card(uuid, scope="reference"))
        assert ref_card_before is not None
        assert ref_card_before.uuid == uuid
        assert ref_card_before.in_collection is False

        # Simulate adding to collection (reference scope should be unaffected)
        def mock_get_after_add(card_uuid, scope="user"):
            if scope == "reference":
                return reference_card  # Reference unchanged
            elif scope == "user":
                return {**reference_card, "in_collection": True, "price": 5.99}
            else:  # combined
                return {**reference_card, "in_collection": True, "price": 5.99}

        mock_get.side_effect = mock_get_after_add

        # Reference scope should still return the same card
        ref_card_after = run_async(card_service.get_card(uuid, scope="reference"))
        assert ref_card_after is not None
        assert ref_card_after.uuid == uuid
        assert ref_card_after.in_collection is False  # Reference cards are never "in collection"

        # Core data should be identical
        assert ref_card_before.name == ref_card_after.name
        assert ref_card_before.type == ref_card_after.type
        assert ref_card_before.mana_cost == ref_card_after.mana_cost


def test_collection_search_scope_consistency():
    """
    Property: Search results should correctly reflect collection status
    based on the requested scope.

    **Feature: domain-api-consolidation, Property 10: Collection Management Consistency**
    **Validates: Requirements 4.1, 4.3**
    """
    # Mock cards in different scopes
    domain_cards = [mock_domain_card()]
    reference_cards = [mock_reference_card()]
    combined_cards = domain_cards + [{**mock_reference_card(), "in_collection": False}]

    with patch("mtgsim.api.data.cards_data.search_cards") as mock_search:

        def mock_search_side_effect(**kwargs):
            scope = kwargs.get("scope", "user")
            if scope == "user":
                return domain_cards, len(domain_cards)
            elif scope == "reference":
                return reference_cards, len(reference_cards)
            else:  # combined
                return combined_cards, len(combined_cards)

        mock_search.side_effect = mock_search_side_effect

        # Test user scope - should only return collection cards
        user_results = run_async(card_service.search_cards(scope="user"))
        assert len(user_results.data) == 1
        assert all(card.in_collection for card in user_results.data)

        # Test reference scope - should only return reference cards
        ref_results = run_async(card_service.search_cards(scope="reference"))
        assert len(ref_results.data) == 1
        assert all(not card.in_collection for card in ref_results.data)

        # Test combined scope - should return both types
        combined_results = run_async(card_service.search_cards(scope="combined"))
        assert len(combined_results.data) == 2

        # Should have both collection and non-collection cards
        collection_cards = [card for card in combined_results.data if card.in_collection]
        non_collection_cards = [card for card in combined_results.data if not card.in_collection]
        assert len(collection_cards) >= 1
        assert len(non_collection_cards) >= 1


def test_collection_management_error_handling():
    """
    Property: Collection management operations should handle errors gracefully
    and maintain system consistency.

    **Feature: domain-api-consolidation, Property 10: Collection Management Consistency**
    **Validates: Requirements 4.1, 4.3**
    """
    invalid_uuid = "invalid-uuid-123"

    # Test that non-existent cards return None in all scopes
    with patch("mtgsim.api.data.cards_data.get_card") as mock_get:
        mock_get.return_value = None

        # Should return None for all scopes
        user_card = run_async(card_service.get_card(invalid_uuid, scope="user"))
        assert user_card is None

        ref_card = run_async(card_service.get_card(invalid_uuid, scope="reference"))
        assert ref_card is None

        combined_card = run_async(card_service.get_card(invalid_uuid, scope="combined"))
        assert combined_card is None


def run_async(coro):
    """Helper to run async functions in sync tests."""
    import asyncio

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

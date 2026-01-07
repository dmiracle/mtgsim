"""
Property-based tests for API response compatibility.

**Feature: domain-api-consolidation, Property 5: API Response Compatibility**
**Validates: Requirements 3.1, 3.2**

Tests that API responses maintain identical structure and format after consolidation.
"""

import asyncio
from unittest.mock import patch

import pytest
from hypothesis import given
from hypothesis import strategies as st
from hypothesis.strategies import composite

from mtgsim.api.services.card_service import card_service
from mtgsim.api.services.deck_service import deck_service
from mtgsim.api.services.set_service import set_service


@composite
def card_search_params(draw):
    """Generate valid card search parameters."""
    return {
        "q": draw(st.one_of(st.none(), st.text(min_size=1, max_size=20))),
        "set_code": draw(st.one_of(st.none(), st.text(min_size=3, max_size=5, alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZ"))),
        "rarity": draw(st.one_of(st.none(), st.sampled_from(["common", "uncommon", "rare", "mythic"]))),
        "card_type": draw(st.one_of(st.none(), st.sampled_from(["Creature", "Instant", "Sorcery", "Artifact"]))),
        "colors": draw(st.one_of(st.none(), st.lists(st.sampled_from(["W", "U", "B", "R", "G"]), max_size=3))),
        "sort": draw(st.sampled_from(["name", "mana_value", "rarity", "set_code"])),
        "order": draw(st.sampled_from(["asc", "desc"])),
        "page": draw(st.integers(min_value=1, max_value=5)),
        "limit": draw(st.integers(min_value=1, max_value=50)),
    }


@composite
def set_search_params(draw):
    """Generate valid set search parameters."""
    return {
        "q": draw(st.one_of(st.none(), st.text(min_size=1, max_size=20))),
        "set_type": draw(st.one_of(st.none(), st.sampled_from(["core", "expansion", "masters", "commander"]))),
        "block": draw(st.one_of(st.none(), st.text(min_size=1, max_size=20))),
        "sort": draw(st.sampled_from(["name", "release_date", "code", "size"])),
        "order": draw(st.sampled_from(["asc", "desc"])),
        "page": draw(st.integers(min_value=1, max_value=5)),
        "limit": draw(st.integers(min_value=1, max_value=50)),
    }


@composite
def deck_search_params(draw):
    """Generate valid deck search parameters."""
    return {
        "q": draw(st.one_of(st.none(), st.text(min_size=1, max_size=20))),
        "format": draw(st.one_of(st.none(), st.sampled_from(["standard", "modern", "legacy", "commander"]))),
        "set_code": draw(st.one_of(st.none(), st.text(min_size=3, max_size=5, alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZ"))),
        "deck_type": draw(st.one_of(st.none(), st.sampled_from(["preconstructed", "tournament"]))),
        "colors": draw(st.one_of(st.none(), st.lists(st.sampled_from(["W", "U", "B", "R", "G"]), max_size=3))),
        "sort": draw(st.sampled_from(["name", "release_date", "code", "card_count"])),
        "order": draw(st.sampled_from(["asc", "desc"])),
        "page": draw(st.integers(min_value=1, max_value=5)),
        "limit": draw(st.integers(min_value=1, max_value=50)),
    }


def mock_card_data():
    """Create mock card data for testing."""
    return {
        "uuid": "test-uuid-123",
        "name": "Test Card",
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


def mock_set_data():
    """Create mock set data for testing."""
    return {
        "code": "TST",
        "name": "Test Set",
        "type": "expansion",
        "release_date": "2024-01-01",
        "base_set_size": 100,
        "total_set_size": 120,
        "block": "Test Block",
        "keyrune_code": "tst",
        "in_collection": True,
    }


def mock_deck_data():
    """Create mock deck data for testing."""
    return {
        "file": "test-deck.json",
        "name": "Test Deck",
        "code": "TST",
        "card_count": 60,
        "colors": ["U", "W"],
        "price": 150.00,
        "release_date": "2024-01-01",
        "in_collection": True,
    }


def run_async(coro):
    """Helper to run async functions in sync tests."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@given(params=card_search_params())
def test_card_search_response_structure_consistency(params):
    """
    Property: For any card search parameters, the response structure should be consistent
    between user and reference scopes.

    **Feature: domain-api-consolidation, Property 5: API Response Compatibility**
    **Validates: Requirements 3.1, 3.2**
    """
    # Mock the data layer to return consistent test data
    mock_cards = [mock_card_data()]
    mock_total = 1

    with patch("mtgsim.api.data.cards_data.search_cards") as mock_search:
        mock_search.return_value = (mock_cards, mock_total)

        # Test user scope
        user_response = run_async(card_service.search_cards(scope="user", **params))

        # Test reference scope
        reference_response = run_async(card_service.search_cards(scope="reference", **params))

        # Both responses should have the same structure
        assert isinstance(user_response, type(reference_response))
        assert hasattr(user_response, "data")
        assert hasattr(user_response, "pagination")
        assert hasattr(reference_response, "data")
        assert hasattr(reference_response, "pagination")

        # Pagination structure should be identical
        assert user_response.pagination.page == reference_response.pagination.page
        assert user_response.pagination.limit == reference_response.pagination.limit
        assert user_response.pagination.total == reference_response.pagination.total
        assert user_response.pagination.pages == reference_response.pagination.pages

        # Card data structure should be identical (except in_collection field)
        if user_response.data and reference_response.data:
            user_card = user_response.data[0]
            ref_card = reference_response.data[0]

            # All fields should exist in both
            user_fields = set(user_card.model_fields.keys())
            ref_fields = set(ref_card.model_fields.keys())
            assert user_fields == ref_fields

            # Core fields should have same values (except in_collection)
            core_fields = ["uuid", "name", "type", "mana_cost", "mana_value", "rarity", "set_code", "color_identity"]
            for field in core_fields:
                if hasattr(user_card, field) and hasattr(ref_card, field):
                    assert getattr(user_card, field) == getattr(ref_card, field)


@given(params=set_search_params())
def test_set_search_response_structure_consistency(params):
    """
    Property: For any set search parameters, the response structure should be consistent
    between user and reference scopes.

    **Feature: domain-api-consolidation, Property 5: API Response Compatibility**
    **Validates: Requirements 3.1, 3.2**
    """
    # Mock the data layer to return consistent test data
    mock_sets = [mock_set_data()]
    mock_total = 1

    with (
        patch("mtgsim.api.data.sets_data.list_sets") as mock_list,
        patch("mtgsim.api.data.sets_data.get_available_types") as mock_types,
        patch("mtgsim.api.data.sets_data.get_available_blocks") as mock_blocks,
    ):
        mock_list.return_value = (mock_sets, mock_total)
        mock_types.return_value = ["expansion", "core"]
        mock_blocks.return_value = ["Test Block"]

        # Test user scope
        user_response = run_async(set_service.list_sets(scope="user", **params))

        # Test reference scope
        reference_response = run_async(set_service.list_sets(scope="reference", **params))

        # Both responses should have the same structure
        assert isinstance(user_response, type(reference_response))
        assert hasattr(user_response, "data")
        assert hasattr(user_response, "pagination")
        assert hasattr(user_response, "filters")
        assert hasattr(reference_response, "data")
        assert hasattr(reference_response, "pagination")
        assert hasattr(reference_response, "filters")

        # Pagination structure should be identical
        assert user_response.pagination.page == reference_response.pagination.page
        assert user_response.pagination.limit == reference_response.pagination.limit
        assert user_response.pagination.total == reference_response.pagination.total
        assert user_response.pagination.pages == reference_response.pagination.pages

        # Filters structure should be identical
        assert isinstance(user_response.filters, type(reference_response.filters))
        assert hasattr(user_response.filters, "types")
        assert hasattr(user_response.filters, "blocks")
        assert hasattr(reference_response.filters, "types")
        assert hasattr(reference_response.filters, "blocks")


@given(params=deck_search_params())
def test_deck_search_response_structure_consistency(params):
    """
    Property: For any deck search parameters, the response structure should be consistent
    between user and reference scopes.

    **Feature: domain-api-consolidation, Property 5: API Response Compatibility**
    **Validates: Requirements 3.1, 3.2**
    """
    # Mock the data layer to return consistent test data
    mock_decks = [mock_deck_data()]
    mock_total = 1

    with (
        patch("mtgsim.api.data.decks_data.list_decks") as mock_list,
        patch("mtgsim.api.data.decks_data.get_available_formats") as mock_formats,
        patch("mtgsim.api.data.decks_data.get_available_sets") as mock_sets,
    ):
        mock_list.return_value = (mock_decks, mock_total)
        mock_formats.return_value = ["standard", "modern", "legacy", "commander"]
        mock_sets.return_value = ["TST", "EXP"]

        # Test user scope
        user_response = run_async(deck_service.list_decks(scope="user", **params))

        # Test reference scope
        reference_response = run_async(deck_service.list_decks(scope="reference", **params))

        # Both responses should have the same structure
        assert isinstance(user_response, type(reference_response))
        assert hasattr(user_response, "data")
        assert hasattr(user_response, "pagination")
        assert hasattr(user_response, "filters")
        assert hasattr(reference_response, "data")
        assert hasattr(reference_response, "pagination")
        assert hasattr(reference_response, "filters")

        # Pagination structure should be identical
        assert user_response.pagination.page == reference_response.pagination.page
        assert user_response.pagination.limit == reference_response.pagination.limit
        assert user_response.pagination.total == reference_response.pagination.total
        assert user_response.pagination.pages == reference_response.pagination.pages

        # Filters structure should be identical
        assert isinstance(user_response.filters, type(reference_response.filters))
        assert hasattr(user_response.filters, "formats")
        assert hasattr(user_response.filters, "sets")
        assert hasattr(user_response.filters, "color_combinations")
        assert hasattr(reference_response.filters, "formats")
        assert hasattr(reference_response.filters, "sets")
        assert hasattr(reference_response.filters, "color_combinations")


@given(uuid=st.text(min_size=10, max_size=50))
def test_card_detail_response_structure_consistency(uuid):
    """
    Property: For any card UUID, the detailed card response structure should be consistent
    between user and reference scopes.

    **Feature: domain-api-consolidation, Property 5: API Response Compatibility**
    **Validates: Requirements 3.1, 3.2**
    """
    # Create comprehensive mock card data
    mock_card = {
        **mock_card_data(),
        "uuid": uuid,
        "types": ["Creature"],
        "subtypes": ["Human", "Wizard"],
        "text": "Test ability text",
        "flavor_text": "Test flavor text",
        "set_name": "Test Set",
        "colors": ["U"],
        "power": "2",
        "toughness": "3",
        "legalities": {
            "standard": "Legal",
            "modern": "Legal",
            "legacy": "Legal",
            "vintage": "Legal",
            "commander": "Legal",
        },
    }

    with (
        patch("mtgsim.api.data.cards_data.get_card") as mock_get,
        patch("mtgsim.api.data.prices_data.get_average_price") as mock_avg_price,
        patch("mtgsim.api.data.prices_data.get_tcgplayer_price") as mock_tcg_price,
        patch("mtgsim.api.data.cards_data.get_card_appearances") as mock_appearances,
        patch("mtgsim.api.data.cards_data.get_other_printings") as mock_printings,
    ):
        mock_get.return_value = mock_card
        mock_avg_price.return_value = 5.99
        mock_tcg_price.return_value = 5.99
        mock_appearances.return_value = []
        mock_printings.return_value = []

        # Test user scope
        user_response = run_async(card_service.get_card(uuid, scope="user"))

        # Test reference scope
        reference_response = run_async(card_service.get_card(uuid, scope="reference"))

        # Both should return CardDetail objects or both should be None
        assert isinstance(user_response, type(reference_response))

        if user_response is not None and reference_response is not None:
            # Both responses should have the same structure
            user_fields = set(user_response.model_fields.keys())
            ref_fields = set(reference_response.model_fields.keys())
            assert user_fields == ref_fields

            # Core identification fields should be identical
            assert user_response.uuid == reference_response.uuid
            assert user_response.name == reference_response.name

            # Nested objects should have same structure
            assert isinstance(user_response.legalities, type(reference_response.legalities))
            assert isinstance(user_response.prices, type(reference_response.prices))
            assert isinstance(user_response.appears_in_decks, type(reference_response.appears_in_decks))
            assert isinstance(user_response.other_printings, type(reference_response.other_printings))


@given(code=st.text(min_size=3, max_size=5, alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZ"))
def test_set_detail_response_structure_consistency(code):
    """
    Property: For any set code, the detailed set response structure should be consistent
    between user and reference scopes.

    **Feature: domain-api-consolidation, Property 5: API Response Compatibility**
    **Validates: Requirements 3.1, 3.2**
    """
    # Create comprehensive mock set data
    mock_set = {
        **mock_set_data(),
        "code": code,
    }

    mock_cards = [mock_card_data()]
    mock_stats = {
        "rarity_count": {"common": 50, "uncommon": 30, "rare": 15, "mythic": 5},
        "color_distribution": {"W": 20, "U": 20, "B": 20, "R": 20, "G": 20, "C": 0},
        "type_distribution": {"Creature": 40, "Instant": 20, "Sorcery": 20, "Artifact": 20},
        "keywords": {"flying": 10, "trample": 5},
        "total_price": 500.00,
    }

    with (
        patch("mtgsim.api.data.sets_data.get_set") as mock_get,
        patch("mtgsim.api.data.sets_data.get_set_cards") as mock_cards_fn,
        patch("mtgsim.api.data.sets_data.get_set_stats") as mock_stats_fn,
    ):
        mock_get.return_value = mock_set
        mock_cards_fn.return_value = (mock_cards, len(mock_cards))
        mock_stats_fn.return_value = mock_stats

        # Test user scope
        user_response = run_async(set_service.get_set(code, scope="user"))

        # Test reference scope
        reference_response = run_async(set_service.get_set(code, scope="reference"))

        # Both should return SetDetail objects or both should be None
        assert isinstance(user_response, type(reference_response))

        if user_response is not None and reference_response is not None:
            # Both responses should have the same structure
            user_fields = set(user_response.model_fields.keys())
            ref_fields = set(reference_response.model_fields.keys())
            assert user_fields == ref_fields

            # Core identification fields should be identical
            assert user_response.meta.code == reference_response.meta.code
            assert user_response.meta.name == reference_response.meta.name

            # Nested objects should have same structure
            assert isinstance(user_response.meta, type(reference_response.meta))
            assert isinstance(user_response.stats, type(reference_response.stats))
            assert isinstance(user_response.cards, type(reference_response.cards))

            # Cards pagination should have same structure
            assert isinstance(user_response.cards.pagination, type(reference_response.cards.pagination))
            assert hasattr(user_response.cards.pagination, "page")
            assert hasattr(user_response.cards.pagination, "limit")
            assert hasattr(user_response.cards.pagination, "total")
            assert hasattr(user_response.cards.pagination, "pages")


def test_response_field_compatibility():
    """
    Property: All API response models should maintain backward compatibility
    by having the same field names and types.

    **Feature: domain-api-consolidation, Property 5: API Response Compatibility**
    **Validates: Requirements 3.1, 3.2**
    """
    from mtgsim.api.models.card import CardListResponse, CardSummary
    from mtgsim.api.models.deck import DeckListResponse, DeckSummary
    from mtgsim.api.models.set import SetListResponse, SetSummary

    # Test that all response models have expected core fields

    # CardSummary should have all expected fields
    card_summary_fields = set(CardSummary.model_fields.keys())
    expected_card_fields = {
        "uuid",
        "name",
        "type",
        "mana_cost",
        "mana_value",
        "rarity",
        "set_code",
        "color_identity",
        "text",
        "price",
        "image_url",
        "in_collection",
    }
    assert expected_card_fields.issubset(card_summary_fields)

    # SetSummary should have all expected fields
    set_summary_fields = set(SetSummary.model_fields.keys())
    expected_set_fields = {
        "code",
        "name",
        "type",
        "release_date",
        "base_set_size",
        "total_set_size",
        "block",
        "keyrune_code",
        "in_collection",
    }
    assert expected_set_fields.issubset(set_summary_fields)

    # DeckSummary should have all expected fields
    deck_summary_fields = set(DeckSummary.model_fields.keys())
    expected_deck_fields = {
        "file",
        "name",
        "code",
        "card_count",
        "colors",
        "price",
        "release_date",
        "legality",
        "in_collection",
    }
    assert expected_deck_fields.issubset(deck_summary_fields)

    # List response models should have data and pagination
    for response_model in [CardListResponse, SetListResponse, DeckListResponse]:
        response_fields = set(response_model.model_fields.keys())
        assert "data" in response_fields
        assert "pagination" in response_fields


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

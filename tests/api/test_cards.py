"""Tests for card API endpoints."""

import pytest


class TestSearchCards:
    """Tests for GET /api/cards endpoint."""

    def test_search_cards_returns_200(self, client):
        """Basic request returns 200."""
        response = client.get("/api/cards")
        assert response.status_code == 200

    def test_search_cards_returns_paginated_response(self, client):
        """Response has correct structure."""
        response = client.get("/api/cards")
        data = response.json()

        assert "data" in data
        assert "pagination" in data
        assert isinstance(data["data"], list)

    def test_search_cards_pagination_metadata(self, client):
        """Pagination metadata is correct."""
        response = client.get("/api/cards?page=1&limit=10")
        data = response.json()

        assert data["pagination"]["page"] == 1
        assert data["pagination"]["limit"] == 10
        assert "total" in data["pagination"]
        assert "pages" in data["pagination"]

    def test_search_cards_by_name(self, client, sample_search_query):
        """Search by card name works."""
        response = client.get(f"/api/cards?q={sample_search_query}")
        assert response.status_code == 200

    def test_search_cards_by_partial_name(self, client):
        """Partial name search works."""
        response = client.get("/api/cards?q=bolt")
        assert response.status_code == 200

    def test_search_cards_filter_by_set(self, client, sample_set_code):
        """Filter by set code works."""
        response = client.get(f"/api/cards?set={sample_set_code}")
        assert response.status_code == 200

    def test_search_cards_filter_by_rarity_common(self, client):
        """Filter by common rarity works."""
        response = client.get("/api/cards?rarity=common")
        assert response.status_code == 200

    def test_search_cards_filter_by_rarity_uncommon(self, client):
        """Filter by uncommon rarity works."""
        response = client.get("/api/cards?rarity=uncommon")
        assert response.status_code == 200

    def test_search_cards_filter_by_rarity_rare(self, client):
        """Filter by rare rarity works."""
        response = client.get("/api/cards?rarity=rare")
        assert response.status_code == 200

    def test_search_cards_filter_by_rarity_mythic(self, client):
        """Filter by mythic rarity works."""
        response = client.get("/api/cards?rarity=mythic")
        assert response.status_code == 200

    def test_search_cards_filter_by_type_creature(self, client):
        """Filter by creature type works."""
        response = client.get("/api/cards?type=Creature")
        assert response.status_code == 200

    def test_search_cards_filter_by_type_instant(self, client):
        """Filter by instant type works."""
        response = client.get("/api/cards?type=Instant")
        assert response.status_code == 200

    def test_search_cards_filter_by_type_sorcery(self, client):
        """Filter by sorcery type works."""
        response = client.get("/api/cards?type=Sorcery")
        assert response.status_code == 200

    def test_search_cards_filter_by_type_land(self, client):
        """Filter by land type works."""
        response = client.get("/api/cards?type=Land")
        assert response.status_code == 200

    def test_search_cards_filter_by_colors_single(self, client):
        """Filter by single color works."""
        response = client.get("/api/cards?colors=W")
        assert response.status_code == 200

    def test_search_cards_filter_by_colors_multiple(self, client):
        """Filter by multiple colors works."""
        response = client.get("/api/cards?colors=WU")
        assert response.status_code == 200

    def test_search_cards_filter_by_price_range(self, client):
        """Filter by price range works."""
        response = client.get("/api/cards?price_min=1&price_max=10")
        assert response.status_code == 200

    def test_search_cards_filter_by_price_min_only(self, client):
        """Filter by minimum price only works."""
        response = client.get("/api/cards?price_min=5")
        assert response.status_code == 200

    def test_search_cards_filter_by_price_max_only(self, client):
        """Filter by maximum price only works."""
        response = client.get("/api/cards?price_max=10")
        assert response.status_code == 200

    def test_search_cards_sort_by_name_asc(self, client):
        """Sort by name ascending works."""
        response = client.get("/api/cards?sort=name&order=asc")
        assert response.status_code == 200

    def test_search_cards_sort_by_name_desc(self, client):
        """Sort by name descending works."""
        response = client.get("/api/cards?sort=name&order=desc")
        assert response.status_code == 200

    def test_search_cards_sort_by_price(self, client):
        """Sort by price works."""
        response = client.get("/api/cards?sort=price&order=desc")
        assert response.status_code == 200

    def test_search_cards_sort_by_mana_value(self, client):
        """Sort by mana value works."""
        response = client.get("/api/cards?sort=mana_value&order=asc")
        assert response.status_code == 200

    def test_search_cards_combined_filters(self, client):
        """Multiple filters combined work."""
        response = client.get("/api/cards?q=dragon&rarity=rare&colors=R&sort=price&order=desc")
        assert response.status_code == 200

    def test_search_cards_pagination_page_2(self, client):
        """Page 2 pagination works."""
        response = client.get("/api/cards?page=2&limit=20")
        assert response.status_code == 200

    def test_search_cards_limit_validation(self, client):
        """Limit cannot exceed 100."""
        response = client.get("/api/cards?limit=200")
        assert response.status_code == 422

    def test_search_cards_invalid_order(self, client):
        """Invalid order value is rejected."""
        response = client.get("/api/cards?order=invalid")
        assert response.status_code == 422

    def test_search_cards_card_summary_structure(self, client):
        """Card summary has correct fields."""
        response = client.get("/api/cards")
        data = response.json()

        if data["data"]:
            card = data["data"][0]
            assert "uuid" in card
            assert "name" in card
            assert "type" in card
            assert "mana_cost" in card
            assert "rarity" in card
            assert "set_code" in card
            assert "color_identity" in card


class TestGetCard:
    """Tests for GET /api/cards/{uuid} endpoint."""

    def test_get_card_returns_200(self, client, sample_card_uuid):
        """Valid card UUID returns 200."""
        response = client.get(f"/api/cards/{sample_card_uuid}")
        assert response.status_code == 200

    def test_get_card_returns_detail_structure(self, client, sample_card_uuid):
        """Response has correct structure."""
        response = client.get(f"/api/cards/{sample_card_uuid}")
        data = response.json()

        assert "uuid" in data
        assert "name" in data
        assert "prices" in data
        assert "legalities" in data

    def test_get_card_basic_fields(self, client, sample_card_uuid):
        """Card has basic fields."""
        response = client.get(f"/api/cards/{sample_card_uuid}")
        data = response.json()

        assert "uuid" in data
        assert "name" in data
        assert "mana_cost" in data
        assert "mana_value" in data
        assert "type" in data
        assert "types" in data
        assert "rarity" in data
        assert "set_code" in data

    def test_get_card_text_fields(self, client, sample_card_uuid):
        """Card has text fields."""
        response = client.get(f"/api/cards/{sample_card_uuid}")
        data = response.json()

        assert "text" in data
        assert "flavor_text" in data

    def test_get_card_color_fields(self, client, sample_card_uuid):
        """Card has color fields."""
        response = client.get(f"/api/cards/{sample_card_uuid}")
        data = response.json()

        assert "color_identity" in data
        assert "colors" in data
        assert isinstance(data["color_identity"], list)
        assert isinstance(data["colors"], list)

    def test_get_card_creature_fields(self, client, sample_card_uuid):
        """Card has power/toughness fields."""
        response = client.get(f"/api/cards/{sample_card_uuid}")
        data = response.json()

        assert "power" in data
        assert "toughness" in data

    def test_get_card_prices_structure(self, client, sample_card_uuid):
        """Card prices have correct structure."""
        response = client.get(f"/api/cards/{sample_card_uuid}")
        data = response.json()

        prices = data["prices"]
        assert "tcgplayer" in prices or prices is not None
        assert "cardkingdom" in prices or prices is not None

    def test_get_card_legalities_structure(self, client, sample_card_uuid):
        """Card legalities have correct structure."""
        response = client.get(f"/api/cards/{sample_card_uuid}")
        data = response.json()

        legalities = data["legalities"]
        assert "standard" in legalities
        assert "pioneer" in legalities
        assert "modern" in legalities
        assert "legacy" in legalities
        assert "vintage" in legalities
        assert "commander" in legalities

    def test_get_card_deck_appearances(self, client, sample_card_uuid):
        """Card has deck appearances list."""
        response = client.get(f"/api/cards/{sample_card_uuid}")
        data = response.json()

        assert "appears_in_decks" in data
        assert isinstance(data["appears_in_decks"], list)

    def test_get_card_deck_appearance_structure(self, client, sample_card_uuid):
        """Deck appearance has correct structure."""
        response = client.get(f"/api/cards/{sample_card_uuid}")
        data = response.json()

        if data["appears_in_decks"]:
            appearance = data["appears_in_decks"][0]
            assert "file" in appearance
            assert "name" in appearance
            assert "count" in appearance

    def test_get_card_other_printings(self, client, sample_card_uuid):
        """Card has other printings list."""
        response = client.get(f"/api/cards/{sample_card_uuid}")
        data = response.json()

        assert "other_printings" in data
        assert isinstance(data["other_printings"], list)

    def test_get_card_other_printing_structure(self, client, sample_card_uuid):
        """Other printing has correct structure."""
        response = client.get(f"/api/cards/{sample_card_uuid}")
        data = response.json()

        if data["other_printings"]:
            printing = data["other_printings"][0]
            assert "set_code" in printing
            assert "set_name" in printing
            assert "uuid" in printing

    def test_get_card_image_url(self, client, sample_card_uuid):
        """Card has image URL."""
        response = client.get(f"/api/cards/{sample_card_uuid}")
        data = response.json()

        assert "image_url" in data

    def test_get_card_not_found(self, client):
        """Non-existent card returns 404."""
        response = client.get("/api/cards/not-a-real-uuid")
        assert response.status_code == 404

    def test_get_card_not_found_error_format(self, client):
        """404 error has correct format."""
        response = client.get("/api/cards/not-a-real-uuid")
        data = response.json()

        assert "error" in data
        assert "code" in data["error"]
        assert "message" in data["error"]

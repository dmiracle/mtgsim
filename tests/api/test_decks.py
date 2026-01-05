"""Tests for deck API endpoints."""

import pytest


class TestListDecks:
    """Tests for GET /api/decks endpoint."""

    def test_list_decks_returns_200(self, client):
        """Basic request returns 200."""
        response = client.get("/api/decks")
        assert response.status_code == 200

    def test_list_decks_returns_paginated_response(self, client):
        """Response has correct structure."""
        response = client.get("/api/decks")
        data = response.json()

        assert "data" in data
        assert "pagination" in data
        assert "filters" in data
        assert isinstance(data["data"], list)

    def test_list_decks_pagination_metadata(self, client):
        """Pagination metadata is correct."""
        response = client.get("/api/decks?page=1&limit=10")
        data = response.json()

        assert data["pagination"]["page"] == 1
        assert data["pagination"]["limit"] == 10
        assert "total" in data["pagination"]
        assert "pages" in data["pagination"]

    def test_list_decks_search_by_name(self, client):
        """Search by deck name works."""
        response = client.get("/api/decks?q=aggro")
        assert response.status_code == 200

    def test_list_decks_filter_by_format(self, client):
        """Filter by format legality works."""
        response = client.get("/api/decks?format=modern")
        assert response.status_code == 200

    def test_list_decks_filter_by_set(self, client):
        """Filter by set code works."""
        response = client.get("/api/decks?set=KLD")
        assert response.status_code == 200

    def test_list_decks_filter_by_deck_type_60(self, client):
        """Filter by 60-card deck type works."""
        response = client.get("/api/decks?type=60")
        assert response.status_code == 200

    def test_list_decks_filter_by_deck_type_100(self, client):
        """Filter by 100-card (commander) deck type works."""
        response = client.get("/api/decks?type=100")
        assert response.status_code == 200

    def test_list_decks_filter_by_colors(self, client):
        """Filter by color identity works."""
        response = client.get("/api/decks?colors=WU")
        assert response.status_code == 200

    def test_list_decks_filter_by_price_range(self, client):
        """Filter by price range works."""
        response = client.get("/api/decks?price_min=50&price_max=100")
        assert response.status_code == 200

    def test_list_decks_sort_by_name_asc(self, client):
        """Sort by name ascending works."""
        response = client.get("/api/decks?sort=name&order=asc")
        assert response.status_code == 200

    def test_list_decks_sort_by_name_desc(self, client):
        """Sort by name descending works."""
        response = client.get("/api/decks?sort=name&order=desc")
        assert response.status_code == 200

    def test_list_decks_sort_by_release_date(self, client):
        """Sort by release date works."""
        response = client.get("/api/decks?sort=release_date&order=desc")
        assert response.status_code == 200

    def test_list_decks_sort_by_price(self, client):
        """Sort by price works."""
        response = client.get("/api/decks?sort=price&order=desc")
        assert response.status_code == 200

    def test_list_decks_sort_by_card_count(self, client):
        """Sort by card count works."""
        response = client.get("/api/decks?sort=card_count&order=desc")
        assert response.status_code == 200

    def test_list_decks_combined_filters(self, client):
        """Multiple filters combined work."""
        response = client.get("/api/decks?format=modern&colors=WU&price_min=50&sort=price&order=desc")
        assert response.status_code == 200

    def test_list_decks_pagination_page_2(self, client):
        """Page 2 pagination works."""
        response = client.get("/api/decks?page=2&limit=20")
        assert response.status_code == 200

    def test_list_decks_limit_validation(self, client):
        """Limit cannot exceed 100."""
        response = client.get("/api/decks?limit=200")
        assert response.status_code == 422  # Validation error

    def test_list_decks_invalid_order(self, client):
        """Invalid order value is rejected."""
        response = client.get("/api/decks?order=invalid")
        assert response.status_code == 422

    def test_list_decks_deck_summary_structure(self, client):
        """Deck summary has correct fields."""
        response = client.get("/api/decks")
        data = response.json()

        if data["data"]:
            deck = data["data"][0]
            assert "file" in deck
            assert "name" in deck
            assert "code" in deck
            assert "card_count" in deck
            assert "colors" in deck
            assert "legality" in deck

    def test_list_decks_filters_include_formats(self, client):
        """Filters include available formats."""
        response = client.get("/api/decks")
        data = response.json()

        assert "formats" in data["filters"]
        assert isinstance(data["filters"]["formats"], list)

    def test_list_decks_filters_include_sets(self, client):
        """Filters include available sets."""
        response = client.get("/api/decks")
        data = response.json()

        assert "sets" in data["filters"]
        assert isinstance(data["filters"]["sets"], list)


class TestGetDeck:
    """Tests for GET /api/decks/{file} endpoint."""

    def test_get_deck_returns_200(self, client, sample_deck_file):
        """Valid deck file returns 200."""
        response = client.get(f"/api/decks/{sample_deck_file}")
        assert response.status_code == 200

    def test_get_deck_returns_detail_structure(self, client, sample_deck_file):
        """Response has correct structure."""
        response = client.get(f"/api/decks/{sample_deck_file}")
        data = response.json()

        assert "meta" in data
        assert "legality" in data
        assert "colors" in data
        assert "price" in data
        assert "commander" in data
        assert "main_board" in data
        assert "side_board" in data
        assert "stats" in data

    def test_get_deck_meta_fields(self, client, sample_deck_file):
        """Deck meta has correct fields."""
        response = client.get(f"/api/decks/{sample_deck_file}")
        data = response.json()

        assert "file" in data["meta"]
        assert "name" in data["meta"]
        assert "code" in data["meta"]

    def test_get_deck_legality_fields(self, client, sample_deck_file):
        """Deck legality has format fields."""
        response = client.get(f"/api/decks/{sample_deck_file}")
        data = response.json()

        legality = data["legality"]
        assert "standard" in legality
        assert "pioneer" in legality
        assert "modern" in legality
        assert "legacy" in legality
        assert "vintage" in legality
        assert "commander" in legality

    def test_get_deck_price_breakdown(self, client, sample_deck_file):
        """Deck price has total and breakdown."""
        response = client.get(f"/api/decks/{sample_deck_file}")
        data = response.json()

        assert "total" in data["price"]
        assert "by_source" in data["price"]

    def test_get_deck_cards_structure(self, client, sample_deck_file):
        """Cards have correct structure."""
        response = client.get(f"/api/decks/{sample_deck_file}")
        data = response.json()

        if data["main_board"]:
            card = data["main_board"][0]
            assert "uuid" in card
            assert "name" in card
            assert "count" in card

    def test_get_deck_stats_structure(self, client, sample_deck_file):
        """Stats have correct structure."""
        response = client.get(f"/api/decks/{sample_deck_file}")
        data = response.json()

        stats = data["stats"]
        assert "total_cards" in stats
        assert "unique_cards" in stats
        assert "mana_curve" in stats
        assert "type_distribution" in stats
        assert "rarity_distribution" in stats
        assert "color_distribution" in stats
        assert "price_histogram" in stats
        assert "keywords" in stats

    def test_get_deck_not_found(self, client):
        """Non-existent deck returns 404."""
        response = client.get("/api/decks/NonExistentDeck.json")
        assert response.status_code == 404

    def test_get_deck_not_found_error_format(self, client):
        """404 error has correct format."""
        response = client.get("/api/decks/NonExistentDeck.json")
        data = response.json()

        assert "error" in data
        assert "code" in data["error"]
        assert "message" in data["error"]


class TestGetDeckRaw:
    """Tests for GET /api/decks/{file}/raw endpoint."""

    def test_get_deck_raw_returns_200(self, client, sample_deck_file):
        """Valid deck file returns 200."""
        response = client.get(f"/api/decks/{sample_deck_file}/raw")
        assert response.status_code == 200

    def test_get_deck_raw_returns_json(self, client, sample_deck_file):
        """Response is JSON."""
        response = client.get(f"/api/decks/{sample_deck_file}/raw")
        assert response.headers["content-type"] == "application/json"

    def test_get_deck_raw_not_found(self, client):
        """Non-existent deck returns 404."""
        response = client.get("/api/decks/NonExistentDeck.json/raw")
        assert response.status_code == 404

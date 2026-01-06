"""Tests for set API endpoints."""


class TestListSets:
    """Tests for GET /api/sets endpoint."""

    def test_list_sets_returns_200(self, client):
        """Basic request returns 200."""
        response = client.get("/api/sets")
        assert response.status_code == 200

    def test_list_sets_returns_paginated_response(self, client):
        """Response has correct structure."""
        response = client.get("/api/sets")
        data = response.json()

        assert "data" in data
        assert "pagination" in data
        assert "filters" in data
        assert isinstance(data["data"], list)

    def test_list_sets_pagination_metadata(self, client):
        """Pagination metadata is correct."""
        response = client.get("/api/sets?page=1&limit=10")
        data = response.json()

        assert data["pagination"]["page"] == 1
        assert data["pagination"]["limit"] == 10
        assert "total" in data["pagination"]
        assert "pages" in data["pagination"]

    def test_list_sets_search_by_name(self, client):
        """Search by set name works."""
        response = client.get("/api/sets?q=kaladesh")
        assert response.status_code == 200

    def test_list_sets_search_by_code(self, client):
        """Search by set code works."""
        response = client.get("/api/sets?q=KLD")
        assert response.status_code == 200

    def test_list_sets_filter_by_type_core(self, client):
        """Filter by core set type works."""
        response = client.get("/api/sets?type=core")
        assert response.status_code == 200

    def test_list_sets_filter_by_type_expansion(self, client):
        """Filter by expansion type works."""
        response = client.get("/api/sets?type=expansion")
        assert response.status_code == 200

    def test_list_sets_filter_by_type_masters(self, client):
        """Filter by masters type works."""
        response = client.get("/api/sets?type=masters")
        assert response.status_code == 200

    def test_list_sets_filter_by_type_commander(self, client):
        """Filter by commander type works."""
        response = client.get("/api/sets?type=commander")
        assert response.status_code == 200

    def test_list_sets_filter_by_block(self, client):
        """Filter by block works."""
        response = client.get("/api/sets?block=Kaladesh")
        assert response.status_code == 200

    def test_list_sets_sort_by_name_asc(self, client):
        """Sort by name ascending works."""
        response = client.get("/api/sets?sort=name&order=asc")
        assert response.status_code == 200

    def test_list_sets_sort_by_name_desc(self, client):
        """Sort by name descending works."""
        response = client.get("/api/sets?sort=name&order=desc")
        assert response.status_code == 200

    def test_list_sets_sort_by_release_date_desc(self, client):
        """Sort by release date descending (newest first) works."""
        response = client.get("/api/sets?sort=release_date&order=desc")
        assert response.status_code == 200

    def test_list_sets_sort_by_release_date_asc(self, client):
        """Sort by release date ascending (oldest first) works."""
        response = client.get("/api/sets?sort=release_date&order=asc")
        assert response.status_code == 200

    def test_list_sets_sort_by_size(self, client):
        """Sort by set size works."""
        response = client.get("/api/sets?sort=size&order=desc")
        assert response.status_code == 200

    def test_list_sets_combined_filters(self, client):
        """Multiple filters combined work."""
        response = client.get("/api/sets?type=expansion&sort=release_date&order=desc")
        assert response.status_code == 200

    def test_list_sets_pagination_page_2(self, client):
        """Page 2 pagination works."""
        response = client.get("/api/sets?page=2&limit=20")
        assert response.status_code == 200

    def test_list_sets_limit_validation(self, client):
        """Limit cannot exceed 100."""
        response = client.get("/api/sets?limit=200")
        assert response.status_code == 422

    def test_list_sets_invalid_order(self, client):
        """Invalid order value is rejected."""
        response = client.get("/api/sets?order=invalid")
        assert response.status_code == 422

    def test_list_sets_set_summary_structure(self, client):
        """Set summary has correct fields."""
        response = client.get("/api/sets")
        data = response.json()

        if data["data"]:
            set_data = data["data"][0]
            assert "code" in set_data
            assert "name" in set_data
            assert "type" in set_data
            assert "base_set_size" in set_data
            assert "total_set_size" in set_data
            assert "keyrune_code" in set_data

    def test_list_sets_filters_include_types(self, client):
        """Filters include available types."""
        response = client.get("/api/sets")
        data = response.json()

        assert "types" in data["filters"]
        assert isinstance(data["filters"]["types"], list)

    def test_list_sets_filters_include_blocks(self, client):
        """Filters include available blocks."""
        response = client.get("/api/sets")
        data = response.json()

        assert "blocks" in data["filters"]
        assert isinstance(data["filters"]["blocks"], list)


class TestGetSet:
    """Tests for GET /api/sets/{code} endpoint."""

    def test_get_set_returns_200(self, client, sample_set_code):
        """Valid set code returns 200."""
        response = client.get(f"/api/sets/{sample_set_code}")
        assert response.status_code == 200

    def test_get_set_returns_detail_structure(self, client, sample_set_code):
        """Response has correct structure."""
        response = client.get(f"/api/sets/{sample_set_code}")
        data = response.json()

        assert "meta" in data
        assert "stats" in data
        assert "cards" in data

    def test_get_set_meta_fields(self, client, sample_set_code):
        """Set meta has correct fields."""
        response = client.get(f"/api/sets/{sample_set_code}")
        data = response.json()

        meta = data["meta"]
        assert "code" in meta
        assert "name" in meta
        assert "type" in meta
        assert "base_set_size" in meta
        assert "total_set_size" in meta
        assert "keyrune_code" in meta

    def test_get_set_stats_rarity_count(self, client, sample_set_code):
        """Set stats include rarity count."""
        response = client.get(f"/api/sets/{sample_set_code}")
        data = response.json()

        assert "rarity_count" in data["stats"]
        rarity = data["stats"]["rarity_count"]
        assert "common" in rarity or isinstance(rarity, dict)

    def test_get_set_stats_price(self, client, sample_set_code):
        """Set stats include price breakdown."""
        response = client.get(f"/api/sets/{sample_set_code}")
        data = response.json()

        assert "price" in data["stats"]
        assert "total" in data["stats"]["price"]
        assert "by_source" in data["stats"]["price"]

    def test_get_set_stats_price_histogram(self, client, sample_set_code):
        """Set stats include price histogram."""
        response = client.get(f"/api/sets/{sample_set_code}")
        data = response.json()

        assert "price_histogram" in data["stats"]
        assert isinstance(data["stats"]["price_histogram"], list)

    def test_get_set_stats_keywords(self, client, sample_set_code):
        """Set stats include keyword counts."""
        response = client.get(f"/api/sets/{sample_set_code}")
        data = response.json()

        assert "keywords" in data["stats"]
        keywords = data["stats"]["keywords"]
        assert "ability_words" in keywords
        assert "keyword_abilities" in keywords
        assert "keyword_actions" in keywords

    def test_get_set_stats_text_by_color(self, client, sample_set_code):
        """Set stats include text by color for word clouds."""
        response = client.get(f"/api/sets/{sample_set_code}")
        data = response.json()

        assert "text_by_color" in data["stats"]

    def test_get_set_cards_paginated(self, client, sample_set_code):
        """Set cards are paginated."""
        response = client.get(f"/api/sets/{sample_set_code}")
        data = response.json()

        assert "data" in data["cards"]
        assert "pagination" in data["cards"]

    def test_get_set_cards_structure(self, client, sample_set_code):
        """Set cards have correct structure."""
        response = client.get(f"/api/sets/{sample_set_code}")
        data = response.json()

        if data["cards"]["data"]:
            card = data["cards"]["data"][0]
            assert "uuid" in card
            assert "name" in card
            assert "rarity" in card
            assert "color_identity" in card

    def test_get_set_filter_cards_by_rarity(self, client, sample_set_code):
        """Filter cards by rarity works."""
        response = client.get(f"/api/sets/{sample_set_code}?rarity=rare")
        assert response.status_code == 200

    def test_get_set_filter_cards_by_color(self, client, sample_set_code):
        """Filter cards by color works."""
        response = client.get(f"/api/sets/{sample_set_code}?color=W")
        assert response.status_code == 200

    def test_get_set_filter_cards_by_type(self, client, sample_set_code):
        """Filter cards by type works."""
        response = client.get(f"/api/sets/{sample_set_code}?type=Creature")
        assert response.status_code == 200

    def test_get_set_cards_pagination(self, client, sample_set_code):
        """Card pagination works."""
        response = client.get(f"/api/sets/{sample_set_code}?card_page=2&card_limit=20")
        assert response.status_code == 200

    def test_get_set_not_found(self, client):
        """Non-existent set returns 404."""
        response = client.get("/api/sets/NOTASET")
        assert response.status_code == 404

    def test_get_set_not_found_error_format(self, client):
        """404 error has correct format."""
        response = client.get("/api/sets/NOTASET")
        data = response.json()

        assert "error" in data
        assert "code" in data["error"]
        assert "message" in data["error"]


class TestGetSetRaw:
    """Tests for GET /api/sets/{code}/raw endpoint."""

    def test_get_set_raw_returns_200(self, client, sample_set_code):
        """Valid set code returns 200."""
        response = client.get(f"/api/sets/{sample_set_code}/raw")
        assert response.status_code == 200

    def test_get_set_raw_returns_json(self, client, sample_set_code):
        """Response is JSON."""
        response = client.get(f"/api/sets/{sample_set_code}/raw")
        assert response.headers["content-type"] == "application/json"

    def test_get_set_raw_not_found(self, client):
        """Non-existent set returns 404."""
        response = client.get("/api/sets/NOTASET/raw")
        assert response.status_code == 404

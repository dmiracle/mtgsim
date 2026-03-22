"""Tests for price scoping to filtered sets (Issue #23)."""


class TestPriceSortWithSetFilter:
    """Tests for sort=price scoping when sets filter is active."""

    def test_sort_by_price_with_set_filter_returns_200(self, client, sample_set_code):
        """Sort by price with set filter returns 200."""
        response = client.get(f"/api/cards?set={sample_set_code}&sort=price&order=desc")
        assert response.status_code == 200

    def test_sort_by_price_with_sets_filter_returns_200(self, client, sample_set_code):
        """Sort by price with multi-set filter returns 200."""
        response = client.get(f"/api/cards?sets={sample_set_code}&sort=price&order=desc")
        assert response.status_code == 200

    def test_sort_by_price_with_set_filter_unique(self, client, sample_set_code):
        """Sort by price with set filter and unique=true returns 200."""
        response = client.get(f"/api/cards?set={sample_set_code}&sort=price&order=desc&unique=true")
        assert response.status_code == 200

    def test_price_field_present_in_results(self, client, sample_set_code):
        """Cards returned with set filter have price field."""
        response = client.get(f"/api/cards?set={sample_set_code}&sort=price&order=desc")
        data = response.json()
        if data["data"]:
            card = data["data"][0]
            assert "price" in card

    def test_sort_by_price_desc_ordering(self, client, sample_set_code):
        """Cards sorted by price desc have non-increasing prices."""
        response = client.get(f"/api/cards?set={sample_set_code}&sort=price&order=desc&limit=20")
        data = response.json()
        prices = [c["price"] for c in data["data"] if c.get("price") is not None]
        if len(prices) > 1:
            for i in range(len(prices) - 1):
                assert prices[i] >= prices[i + 1]

    def test_sort_by_price_asc_ordering(self, client, sample_set_code):
        """Cards sorted by price asc have non-decreasing prices."""
        response = client.get(f"/api/cards?set={sample_set_code}&sort=price&order=asc&limit=20")
        data = response.json()
        prices = [c["price"] for c in data["data"] if c.get("price") is not None]
        if len(prices) > 1:
            for i in range(len(prices) - 1):
                assert prices[i] <= prices[i + 1]


class TestSetEndpointSortByPrice:
    """Tests for sort=price on GET /api/sets/{code}."""

    def test_set_sort_by_price_returns_200(self, client, sample_set_code):
        """Sort by price on set endpoint returns 200."""
        response = client.get(f"/api/sets/{sample_set_code}?sort=price&order=desc")
        assert response.status_code == 200

    def test_set_sort_by_price_has_cards(self, client, sample_set_code):
        """Set endpoint with sort=price returns cards."""
        response = client.get(f"/api/sets/{sample_set_code}?sort=price&order=desc")
        data = response.json()
        assert "cards" in data
        assert "data" in data["cards"]
        assert isinstance(data["cards"]["data"], list)

    def test_set_sort_by_price_desc_ordering(self, client, sample_set_code):
        """Set cards sorted by price desc have non-increasing prices."""
        response = client.get(f"/api/sets/{sample_set_code}?sort=price&order=desc&card_limit=20")
        data = response.json()
        cards = data.get("cards", {}).get("data", [])
        prices = [c["price"] for c in cards if c.get("price") is not None]
        if len(prices) > 1:
            for i in range(len(prices) - 1):
                assert prices[i] >= prices[i + 1]


class TestOtherPrintingsPrice:
    """Tests for price field in other_printings."""

    def test_other_printings_has_price_field(self, client, sample_card_uuid):
        """Other printings include price field."""
        response = client.get(f"/api/cards/{sample_card_uuid}")
        data = response.json()
        if data.get("other_printings"):
            printing = data["other_printings"][0]
            assert "price" in printing

    def test_other_printings_price_is_number_or_null(self, client, sample_card_uuid):
        """Other printings price is a number or null."""
        response = client.get(f"/api/cards/{sample_card_uuid}")
        data = response.json()
        for printing in data.get("other_printings", []):
            assert printing["price"] is None or isinstance(printing["price"], (int, float))


class TestPriceMinMaxFiltering:
    """Tests for price_min/price_max filtering on GET /api/cards."""

    def test_price_min_filters_results(self, client):
        """Cards with price_min have prices >= min."""
        response = client.get("/api/cards?price_min=5&sort=price&order=asc&limit=20")
        data = response.json()
        for card in data["data"]:
            if card.get("price") is not None:
                assert card["price"] >= 5

    def test_price_max_filters_results(self, client):
        """Cards with price_max have prices <= max."""
        response = client.get("/api/cards?price_max=1&sort=price&order=desc&limit=20")
        data = response.json()
        for card in data["data"]:
            if card.get("price") is not None:
                assert card["price"] <= 1

    def test_price_range_filters_results(self, client):
        """Cards with price range have prices in range."""
        response = client.get("/api/cards?price_min=1&price_max=10&sort=price&order=asc&limit=20")
        data = response.json()
        for card in data["data"]:
            if card.get("price") is not None:
                assert 1 <= card["price"] <= 10

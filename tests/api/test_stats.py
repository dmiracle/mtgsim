"""Tests for statistics API endpoints."""


class TestGetHomeStats:
    """Tests for GET /api/stats/home endpoint."""

    def test_get_home_stats_returns_200(self, client):
        """Basic request returns 200."""
        response = client.get("/api/stats/home")
        assert response.status_code == 200

    def test_get_home_stats_has_counts(self, client):
        """Response has count fields."""
        response = client.get("/api/stats/home")
        data = response.json()

        assert "total_decks" in data
        assert "total_sets" in data
        assert "total_cards" in data
        assert "total_cards_with_prices" in data

    def test_get_home_stats_counts_are_integers(self, client):
        """Count fields are integers."""
        response = client.get("/api/stats/home")
        data = response.json()

        assert isinstance(data["total_decks"], int)
        assert isinstance(data["total_sets"], int)
        assert isinstance(data["total_cards"], int)
        assert isinstance(data["total_cards_with_prices"], int)

    def test_get_home_stats_counts_non_negative(self, client):
        """Count fields are non-negative."""
        response = client.get("/api/stats/home")
        data = response.json()

        assert data["total_decks"] >= 0
        assert data["total_sets"] >= 0
        assert data["total_cards"] >= 0
        assert data["total_cards_with_prices"] >= 0

    def test_get_home_stats_has_format_distribution(self, client):
        """Response has format distribution."""
        response = client.get("/api/stats/home")
        data = response.json()

        assert "format_distribution" in data
        assert isinstance(data["format_distribution"], dict)

    def test_get_home_stats_format_distribution_structure(self, client):
        """Format distribution has deck types (not game formats)."""
        response = client.get("/api/stats/home")
        data = response.json()

        formats = data["format_distribution"]
        # format_distribution contains deck types like "Commander Deck", "Secret Lair Drop", etc.
        # Just verify it's a dict with string keys
        for key in formats.keys():
            assert isinstance(key, str)

    def test_get_home_stats_format_distribution_values(self, client):
        """Format distribution values are integers."""
        response = client.get("/api/stats/home")
        data = response.json()

        for _fmt, count in data["format_distribution"].items():
            assert isinstance(count, int)
            assert count >= 0

    def test_get_home_stats_has_price_histogram(self, client):
        """Response has price histogram."""
        response = client.get("/api/stats/home")
        data = response.json()

        assert "price_histogram" in data
        assert isinstance(data["price_histogram"], list)

    def test_get_home_stats_histogram_bucket_structure(self, client):
        """Histogram buckets have correct structure."""
        response = client.get("/api/stats/home")
        data = response.json()

        if data["price_histogram"]:
            bucket = data["price_histogram"][0]
            assert "range" in bucket
            assert "count" in bucket

    def test_get_home_stats_histogram_bucket_range(self, client):
        """Histogram bucket range is a string."""
        response = client.get("/api/stats/home")
        data = response.json()

        if data["price_histogram"]:
            bucket = data["price_histogram"][0]
            assert isinstance(bucket["range"], str)

    def test_get_home_stats_histogram_bucket_count(self, client):
        """Histogram bucket count is an integer."""
        response = client.get("/api/stats/home")
        data = response.json()

        if data["price_histogram"]:
            bucket = data["price_histogram"][0]
            assert isinstance(bucket["count"], int)
            assert bucket["count"] >= 0

    def test_get_home_stats_has_recent_sets(self, client):
        """Response has recent sets."""
        response = client.get("/api/stats/home")
        data = response.json()

        assert "recent_sets" in data
        assert isinstance(data["recent_sets"], list)

    def test_get_home_stats_recent_sets_structure(self, client):
        """Recent sets have correct structure."""
        response = client.get("/api/stats/home")
        data = response.json()

        if data["recent_sets"]:
            set_data = data["recent_sets"][0]
            assert "code" in set_data
            assert "name" in set_data
            assert "release_date" in set_data

    def test_get_home_stats_recent_sets_limited(self, client):
        """Recent sets are limited in number."""
        response = client.get("/api/stats/home")
        data = response.json()

        # Should be a reasonable number like 5-10 most recent
        assert len(data["recent_sets"]) <= 20

    def test_get_home_stats_has_most_expensive_cards(self, client):
        """Response has most expensive cards."""
        response = client.get("/api/stats/home")
        data = response.json()

        assert "most_expensive_cards" in data
        assert isinstance(data["most_expensive_cards"], list)

    def test_get_home_stats_expensive_cards_structure(self, client):
        """Most expensive cards have correct structure."""
        response = client.get("/api/stats/home")
        data = response.json()

        if data["most_expensive_cards"]:
            card = data["most_expensive_cards"][0]
            assert "name" in card
            assert "price" in card
            assert "set_code" in card

    def test_get_home_stats_expensive_cards_limited(self, client):
        """Most expensive cards are limited in number."""
        response = client.get("/api/stats/home")
        data = response.json()

        # Should be a reasonable number like 10-20
        assert len(data["most_expensive_cards"]) <= 50


class TestGetDeckStats:
    """Tests for GET /api/stats/decks endpoint."""

    def test_get_deck_stats_returns_200(self, client):
        """Basic request returns 200."""
        response = client.get("/api/stats/decks")
        assert response.status_code == 200

    def test_get_deck_stats_has_by_format(self, client):
        """Response has decks by format."""
        response = client.get("/api/stats/decks")
        data = response.json()

        assert "by_format" in data
        assert isinstance(data["by_format"], dict)

    def test_get_deck_stats_by_format_structure(self, client):
        """by_format has deck types (not game formats)."""
        response = client.get("/api/stats/decks")
        data = response.json()

        formats = data["by_format"]
        # by_format contains deck types like "Commander Deck", "Secret Lair Drop", etc.
        # Just verify it's a dict with string keys
        for key in formats.keys():
            assert isinstance(key, str)

    def test_get_deck_stats_by_format_values(self, client):
        """by_format values are integers."""
        response = client.get("/api/stats/decks")
        data = response.json()

        for _fmt, count in data["by_format"].items():
            assert isinstance(count, int)
            assert count >= 0

    def test_get_deck_stats_has_by_set(self, client):
        """Response has decks by set."""
        response = client.get("/api/stats/decks")
        data = response.json()

        assert "by_set" in data
        assert isinstance(data["by_set"], dict)

    def test_get_deck_stats_by_set_values(self, client):
        """by_set values are integers."""
        response = client.get("/api/stats/decks")
        data = response.json()

        for _set_code, count in data["by_set"].items():
            assert isinstance(count, int)
            assert count >= 0

    def test_get_deck_stats_has_by_color_combination(self, client):
        """Response has decks by color combination."""
        response = client.get("/api/stats/decks")
        data = response.json()

        assert "by_color_combination" in data
        assert isinstance(data["by_color_combination"], dict)

    def test_get_deck_stats_by_color_combination_values(self, client):
        """by_color_combination values are integers."""
        response = client.get("/api/stats/decks")
        data = response.json()

        for _colors, count in data["by_color_combination"].items():
            assert isinstance(count, int)
            assert count >= 0

    def test_get_deck_stats_has_price_distribution(self, client):
        """Response has price distribution."""
        response = client.get("/api/stats/decks")
        data = response.json()

        assert "price_distribution" in data
        assert isinstance(data["price_distribution"], list)

    def test_get_deck_stats_price_distribution_structure(self, client):
        """Price distribution buckets have correct structure."""
        response = client.get("/api/stats/decks")
        data = response.json()

        if data["price_distribution"]:
            bucket = data["price_distribution"][0]
            assert "range" in bucket
            assert "count" in bucket

    def test_get_deck_stats_has_average_deck_price(self, client):
        """Response has average deck price."""
        response = client.get("/api/stats/decks")
        data = response.json()

        assert "average_deck_price" in data
        if data["average_deck_price"] is not None:
            assert isinstance(data["average_deck_price"], (int, float))

    def test_get_deck_stats_average_deck_price_non_negative(self, client):
        """Average deck price is non-negative."""
        response = client.get("/api/stats/decks")
        data = response.json()

        if data["average_deck_price"] is not None:
            assert data["average_deck_price"] >= 0

    def test_get_deck_stats_has_average_deck_size(self, client):
        """Response has average deck size."""
        response = client.get("/api/stats/decks")
        data = response.json()

        assert "average_deck_size" in data
        if data["average_deck_size"] is not None:
            assert isinstance(data["average_deck_size"], (int, float))

    def test_get_deck_stats_average_deck_size_non_negative(self, client):
        """Average deck size is non-negative."""
        response = client.get("/api/stats/decks")
        data = response.json()

        if data["average_deck_size"] is not None:
            assert data["average_deck_size"] >= 0

    def test_get_deck_stats_average_deck_size_reasonable(self, client):
        """Average deck size is reasonable for MTG decks."""
        response = client.get("/api/stats/decks")
        data = response.json()

        if data["average_deck_size"] is not None and data["average_deck_size"] > 0:
            # Decks are typically 60 or 100 cards
            assert 40 <= data["average_deck_size"] <= 120

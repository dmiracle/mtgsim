"""Tests for price_mode parameter (Issue #27)."""


class TestPriceModeCards:
    """Tests for price_mode on GET /api/cards."""

    def test_price_mode_min_returns_200(self, client):
        """price_mode=min returns 200."""
        response = client.get("/api/cards?unique=true&price_mode=min&sort=price&order=asc&limit=10")
        assert response.status_code == 200

    def test_price_mode_max_returns_200(self, client):
        """price_mode=max returns 200."""
        response = client.get("/api/cards?unique=true&price_mode=max&sort=price&order=asc&limit=10")
        assert response.status_code == 200

    def test_price_mode_invalid_rejected(self, client):
        """Invalid price_mode is rejected."""
        response = client.get("/api/cards?price_mode=invalid")
        assert response.status_code == 422

    def test_price_mode_default_is_min(self, client):
        """Default price_mode behaves like min."""
        default_response = client.get("/api/cards?unique=true&sort=price&order=desc&limit=10")
        min_response = client.get("/api/cards?unique=true&price_mode=min&sort=price&order=desc&limit=10")
        assert default_response.json() == min_response.json()

    def test_price_mode_with_format_filter(self, client):
        """price_mode works with format filter."""
        response = client.get("/api/cards?unique=true&format=modern&price_mode=min&sort=price&order=desc&limit=5")
        assert response.status_code == 200

    def test_price_mode_with_set_filter(self, client, sample_set_code):
        """price_mode works with set filter."""
        response = client.get(
            f"/api/cards?unique=true&set={sample_set_code}&price_mode=max&sort=price&order=desc&limit=5"
        )
        assert response.status_code == 200

    def test_price_mode_min_prices_lte_max(self, client):
        """For same card names, min prices should be <= max prices."""
        min_response = client.get("/api/cards?unique=true&price_mode=min&sort=name&order=asc&limit=20")
        max_response = client.get("/api/cards?unique=true&price_mode=max&sort=name&order=asc&limit=20")

        min_cards = {c["name"]: c["price"] for c in min_response.json()["data"] if c.get("price") is not None}
        max_cards = {c["name"]: c["price"] for c in max_response.json()["data"] if c.get("price") is not None}

        common_names = set(min_cards.keys()) & set(max_cards.keys())
        for name in common_names:
            assert min_cards[name] <= max_cards[name], f"{name}: min={min_cards[name]} > max={max_cards[name]}"

    def test_price_mode_without_unique_returns_200(self, client):
        """price_mode without unique=true still returns 200 (no-op)."""
        response = client.get("/api/cards?price_mode=max&sort=price&order=desc&limit=5")
        assert response.status_code == 200


class TestPriceModeSets:
    """Tests for price_mode on GET /api/sets/{code}."""

    def test_price_mode_min_returns_200(self, client, sample_set_code):
        """price_mode=min on set endpoint returns 200."""
        response = client.get(f"/api/sets/{sample_set_code}?price_mode=min")
        assert response.status_code == 200

    def test_price_mode_max_returns_200(self, client, sample_set_code):
        """price_mode=max on set endpoint returns 200."""
        response = client.get(f"/api/sets/{sample_set_code}?price_mode=max")
        assert response.status_code == 200

    def test_price_mode_invalid_rejected(self, client, sample_set_code):
        """Invalid price_mode is rejected on set endpoint."""
        response = client.get(f"/api/sets/{sample_set_code}?price_mode=invalid")
        assert response.status_code == 422

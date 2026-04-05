"""Tests for batch compact vectors, aggregate, deck features, and grid layout."""


class TestFeatureGridLayout:
    """Tests for GET /api/cards/features/grid-layout."""

    def test_returns_200(self, client):
        response = client.get("/api/cards/features/grid-layout")
        assert response.status_code == 200

    def test_response_structure(self, client):
        data = client.get("/api/cards/features/grid-layout").json()
        assert data["grid_size"] == 8
        assert data["dimensions"] == 64
        assert len(data["layout"]) == 64
        assert "pca_variance_explained" in data

    def test_all_cells_assigned(self, client):
        data = client.get("/api/cards/features/grid-layout").json()
        cells = {(item["row"], item["col"]) for item in data["layout"]}
        expected = {(r, c) for r in range(8) for c in range(8)}
        assert cells == expected

    def test_all_features_present(self, client):
        data = client.get("/api/cards/features/grid-layout").json()
        features = {item["feature"] for item in data["layout"]}
        assert len(features) == 64

    def test_layout_items_have_index(self, client):
        data = client.get("/api/cards/features/grid-layout").json()
        indices = {item["index"] for item in data["layout"]}
        assert indices == set(range(64))


class TestBatchCompactVectors:
    """Tests for GET /api/cards/features/compact."""

    def test_returns_200(self, client):
        response = client.get("/api/cards/features/compact?set=KLD&limit=10")
        assert response.status_code == 200

    def test_response_structure(self, client):
        data = client.get("/api/cards/features/compact?set=KLD&limit=5").json()
        assert "cards" in data
        assert "dimensions" in data
        assert "dimension_names" in data
        assert "total" in data
        assert data["dimensions"] == 64

    def test_cards_have_vectors(self, client):
        data = client.get("/api/cards/features/compact?set=KLD&limit=5").json()
        assert data["total"] > 0
        for card in data["cards"]:
            assert "uuid" in card
            assert "name" in card
            assert "vector" in card
            assert len(card["vector"]) == 64

    def test_limit_parameter(self, client):
        data = client.get("/api/cards/features/compact?set=KLD&limit=3").json()
        assert data["total"] <= 3

    def test_filter_by_rarity(self, client):
        data = client.get("/api/cards/features/compact?set=KLD&rarity=rare&limit=10").json()
        assert data["total"] > 0

    def test_filter_by_colors(self, client):
        response = client.get("/api/cards/features/compact?set=KLD&colors=R&limit=10")
        assert response.status_code == 200


class TestAggregateVectors:
    """Tests for GET /api/cards/features/aggregate."""

    def test_returns_200(self, client):
        response = client.get("/api/cards/features/aggregate?set=KLD")
        assert response.status_code == 200

    def test_response_structure(self, client):
        data = client.get("/api/cards/features/aggregate?set=KLD").json()
        assert "vector" in data
        assert "dimensions" in data
        assert "dimension_names" in data
        assert "card_count" in data
        assert data["dimensions"] == 64
        assert len(data["vector"]) == 64

    def test_vector_is_normalized(self, client):
        import math

        data = client.get("/api/cards/features/aggregate?set=KLD").json()
        magnitude = math.sqrt(sum(v * v for v in data["vector"]))
        assert abs(magnitude - 1.0) < 0.01  # L2 norm ≈ 1.0

    def test_card_count_positive(self, client):
        data = client.get("/api/cards/features/aggregate?set=KLD").json()
        assert data["card_count"] > 0


class TestDeckFeatures:
    """Tests for GET /api/decks/{file}/features."""

    def test_precon_returns_200(self, client, sample_deck_file):
        response = client.get(f"/api/decks/{sample_deck_file}/features")
        assert response.status_code == 200

    def test_response_structure(self, client, sample_deck_file):
        data = client.get(f"/api/decks/{sample_deck_file}/features").json()
        assert "vector" in data
        assert "dimensions" in data
        assert "card_count" in data
        assert data["dimensions"] == 64
        assert len(data["vector"]) == 64

    def test_vector_is_normalized(self, client, sample_deck_file):
        import math

        data = client.get(f"/api/decks/{sample_deck_file}/features").json()
        magnitude = math.sqrt(sum(v * v for v in data["vector"]))
        assert abs(magnitude - 1.0) < 0.01

    def test_nonexistent_returns_404(self, client):
        response = client.get("/api/decks/nonexistent.json/features")
        assert response.status_code == 404

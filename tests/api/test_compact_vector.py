"""Tests for compact card feature vector endpoint."""


class TestCompactVector:
    """Tests for GET /api/cards/{uuid}/features/compact."""

    def test_returns_200(self, client, sample_card_uuid):
        response = client.get(f"/api/cards/{sample_card_uuid}/features/compact")
        assert response.status_code == 200

    def test_response_structure(self, client, sample_card_uuid):
        data = client.get(f"/api/cards/{sample_card_uuid}/features/compact").json()
        assert "uuid" in data
        assert "name" in data
        assert "dimensions" in data
        assert "nonzero" in data
        assert "features" in data
        assert "vector" in data

    def test_compact_dimensions(self, client, sample_card_uuid):
        data = client.get(f"/api/cards/{sample_card_uuid}/features/compact").json()
        assert 50 < data["dimensions"] < 80  # ~60 dims expected

    def test_vector_length_matches_dimensions(self, client, sample_card_uuid):
        data = client.get(f"/api/cards/{sample_card_uuid}/features/compact").json()
        assert len(data["vector"]) == data["dimensions"]

    def test_features_are_sparse(self, client, sample_card_uuid):
        data = client.get(f"/api/cards/{sample_card_uuid}/features/compact").json()
        assert data["nonzero"] > 0
        assert data["nonzero"] < data["dimensions"]

    def test_values_in_range(self, client, sample_card_uuid):
        data = client.get(f"/api/cards/{sample_card_uuid}/features/compact").json()
        for v in data["vector"]:
            assert 0.0 <= v <= 1.0

    def test_has_color_features(self, client, sample_card_uuid):
        data = client.get(f"/api/cards/{sample_card_uuid}/features/compact").json()
        color_feats = [k for k in data["features"] if k.startswith("color_") and k != "color_count"]
        assert len(color_feats) > 0

    def test_has_type_features(self, client, sample_card_uuid):
        data = client.get(f"/api/cards/{sample_card_uuid}/features/compact").json()
        type_feats = [k for k in data["features"] if k.startswith("is_")]
        assert len(type_feats) > 0

    def test_nonexistent_returns_404(self, client):
        response = client.get("/api/cards/nonexistent/features/compact")
        assert response.status_code == 404

    def test_fewer_dims_than_full_features(self, client, sample_card_uuid):
        compact = client.get(f"/api/cards/{sample_card_uuid}/features/compact").json()
        full = client.get(f"/api/cards/{sample_card_uuid}/features").json()
        assert compact["dimensions"] < full["dimensions"]

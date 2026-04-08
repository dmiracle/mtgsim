"""Tests for card feature vector endpoint."""


class TestFeatureVector:
    """Tests for GET /api/cards/{uuid}/features."""

    def test_returns_200(self, client, sample_card_uuid):
        response = client.get(f"/api/cards/{sample_card_uuid}/features")
        assert response.status_code == 200

    def test_response_structure(self, client, sample_card_uuid):
        data = client.get(f"/api/cards/{sample_card_uuid}/features").json()
        assert "uuid" in data
        assert "name" in data
        assert "dimensions" in data
        assert "nonzero" in data
        assert "features" in data

    def test_uuid_matches(self, client, sample_card_uuid):
        data = client.get(f"/api/cards/{sample_card_uuid}/features").json()
        assert data["uuid"] == sample_card_uuid

    def test_dimensions_positive(self, client, sample_card_uuid):
        data = client.get(f"/api/cards/{sample_card_uuid}/features").json()
        assert data["dimensions"] > 0

    def test_features_are_sparse(self, client, sample_card_uuid):
        data = client.get(f"/api/cards/{sample_card_uuid}/features").json()
        assert data["nonzero"] > 0
        assert data["nonzero"] < data["dimensions"]

    def test_features_are_named(self, client, sample_card_uuid):
        data = client.get(f"/api/cards/{sample_card_uuid}/features").json()
        for key in data["features"]:
            assert ":" in key or key.startswith("mv_") or key.startswith("has_")

    def test_all_values_are_floats(self, client, sample_card_uuid):
        data = client.get(f"/api/cards/{sample_card_uuid}/features").json()
        for value in data["features"].values():
            assert isinstance(value, (int, float))
            assert value != 0.0

    def test_nonexistent_card_returns_404(self, client):
        response = client.get("/api/cards/nonexistent-uuid/features")
        assert response.status_code == 404

    def test_has_color_features(self, client, sample_card_uuid):
        data = client.get(f"/api/cards/{sample_card_uuid}/features").json()
        color_features = [k for k in data["features"] if k.startswith("color:")]
        assert len(color_features) > 0

    def test_has_type_features(self, client, sample_card_uuid):
        data = client.get(f"/api/cards/{sample_card_uuid}/features").json()
        type_features = [k for k in data["features"] if k.startswith("type:")]
        assert len(type_features) > 0

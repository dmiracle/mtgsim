"""Tests for card similarity search endpoints."""


class TestListStrategies:
    """Tests for GET /api/cards/similar/strategies."""

    def test_returns_200(self, client):
        response = client.get("/api/cards/similar/strategies")
        assert response.status_code == 200

    def test_returns_list(self, client):
        data = client.get("/api/cards/similar/strategies").json()
        assert isinstance(data, list)
        assert len(data) >= 4

    def test_strategy_has_name_and_description(self, client):
        data = client.get("/api/cards/similar/strategies").json()
        for s in data:
            assert "name" in s
            assert "description" in s

    def test_includes_known_strategies(self, client):
        data = client.get("/api/cards/similar/strategies").json()
        names = {s["name"] for s in data}
        assert "keywords" in names
        assert "tags" in names
        assert "type_match" in names
        assert "mana_curve" in names


class TestSimilarCards:
    """Tests for GET /api/cards/{uuid}/similar."""

    def test_returns_200(self, client, sample_card_uuid):
        response = client.get(f"/api/cards/{sample_card_uuid}/similar")
        assert response.status_code == 200

    def test_response_structure(self, client, sample_card_uuid):
        data = client.get(f"/api/cards/{sample_card_uuid}/similar").json()
        assert "source" in data
        assert "strategies_used" in data
        assert "results" in data
        assert "total" in data

    def test_source_card_is_correct(self, client, sample_card_uuid):
        data = client.get(f"/api/cards/{sample_card_uuid}/similar").json()
        assert data["source"]["uuid"] == sample_card_uuid

    def test_results_have_scores(self, client, sample_card_uuid):
        data = client.get(f"/api/cards/{sample_card_uuid}/similar").json()
        for r in data["results"]:
            assert "card" in r
            assert "score" in r
            assert "strategy_scores" in r
            assert 0 <= r["score"] <= 1

    def test_results_have_card_summary(self, client, sample_card_uuid):
        data = client.get(f"/api/cards/{sample_card_uuid}/similar").json()
        if data["results"]:
            card = data["results"][0]["card"]
            assert "uuid" in card
            assert "name" in card
            assert "image_url" in card

    def test_custom_strategies(self, client, sample_card_uuid):
        data = client.get(f"/api/cards/{sample_card_uuid}/similar?strategies=keywords").json()
        assert data["strategies_used"] == ["keywords"]

    def test_custom_weights(self, client, sample_card_uuid):
        response = client.get(f"/api/cards/{sample_card_uuid}/similar?strategies=keywords,tags&weights=2.0,1.0")
        assert response.status_code == 200

    def test_invalid_strategy_returns_400(self, client, sample_card_uuid):
        response = client.get(f"/api/cards/{sample_card_uuid}/similar?strategies=nonexistent")
        assert response.status_code == 400

    def test_mismatched_weights_returns_400(self, client, sample_card_uuid):
        response = client.get(f"/api/cards/{sample_card_uuid}/similar?strategies=keywords,tags&weights=1.0")
        assert response.status_code == 400

    def test_nonexistent_card_returns_404(self, client):
        response = client.get("/api/cards/nonexistent-uuid/similar")
        assert response.status_code == 404

    def test_limit_parameter(self, client, sample_card_uuid):
        data = client.get(f"/api/cards/{sample_card_uuid}/similar?limit=5").json()
        assert len(data["results"]) <= 5

    def test_mana_curve_strategy(self, client, sample_card_uuid):
        data = client.get(f"/api/cards/{sample_card_uuid}/similar?strategies=mana_curve&limit=5").json()
        assert data["strategies_used"] == ["mana_curve"]

    def test_type_match_strategy(self, client, sample_card_uuid):
        data = client.get(f"/api/cards/{sample_card_uuid}/similar?strategies=type_match&limit=5").json()
        assert data["strategies_used"] == ["type_match"]

    def test_results_sorted_by_score(self, client, sample_card_uuid):
        data = client.get(f"/api/cards/{sample_card_uuid}/similar").json()
        scores = [r["score"] for r in data["results"]]
        assert scores == sorted(scores, reverse=True)

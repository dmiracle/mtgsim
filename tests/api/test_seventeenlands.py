"""Tests for 17Lands API endpoints."""


class TestListDatasets:
    """Tests for GET /api/17lands/datasets endpoint."""

    def test_list_datasets_returns_200(self, client):
        """Basic request returns 200."""
        response = client.get("/api/17lands/datasets")
        assert response.status_code == 200

    def test_list_datasets_response_structure(self, client):
        """Response has correct structure."""
        response = client.get("/api/17lands/datasets")
        data = response.json()
        assert "data" in data
        assert "pagination" in data
        assert isinstance(data["data"], list)

    def test_list_datasets_pagination(self, client):
        """Pagination metadata is present."""
        response = client.get("/api/17lands/datasets?page=1&limit=10")
        data = response.json()
        assert data["pagination"]["page"] == 1
        assert data["pagination"]["limit"] == 10
        assert "total" in data["pagination"]

    def test_list_datasets_filter_by_expansion(self, client):
        """Filter by expansion returns 200."""
        response = client.get("/api/17lands/datasets?expansion=MH3")
        assert response.status_code == 200

    def test_list_datasets_filter_by_format(self, client):
        """Filter by format returns 200."""
        response = client.get("/api/17lands/datasets?format=PremierDraft")
        assert response.status_code == 200

    def test_list_datasets_filter_has_draft(self, client):
        """Filter by has_draft returns 200."""
        response = client.get("/api/17lands/datasets?has_draft=true")
        assert response.status_code == 200

    def test_list_datasets_limit_validation(self, client):
        """Limit cannot exceed 100."""
        response = client.get("/api/17lands/datasets?limit=200")
        assert response.status_code == 422


class TestListExpansions:
    """Tests for GET /api/17lands/expansions endpoint."""

    def test_list_expansions_returns_200(self, client):
        """Basic request returns 200."""
        response = client.get("/api/17lands/expansions")
        assert response.status_code == 200

    def test_list_expansions_returns_list(self, client):
        """Response is a list."""
        response = client.get("/api/17lands/expansions")
        data = response.json()
        assert isinstance(data, list)

    def test_list_expansions_entry_structure(self, client):
        """Expansion entries have correct fields."""
        response = client.get("/api/17lands/expansions")
        data = response.json()
        if data:
            entry = data[0]
            assert "expansion" in entry
            assert "dataset_count" in entry
            assert "formats" in entry
            assert isinstance(entry["formats"], list)


class TestListDraftPicks:
    """Tests for GET /api/17lands/drafts endpoint."""

    def test_list_drafts_returns_200(self, client):
        response = client.get("/api/17lands/drafts")
        assert response.status_code == 200

    def test_list_drafts_response_structure(self, client):
        response = client.get("/api/17lands/drafts")
        data = response.json()
        assert "data" in data
        assert "pagination" in data

    def test_list_drafts_filter_by_expansion(self, client):
        response = client.get("/api/17lands/drafts?expansion=KHM")
        assert response.status_code == 200

    def test_list_drafts_filter_by_card(self, client):
        response = client.get("/api/17lands/drafts?card_name=Lightning+Bolt")
        assert response.status_code == 200

    def test_list_drafts_limit_validation(self, client):
        response = client.get("/api/17lands/drafts?limit=200")
        assert response.status_code == 422


class TestListGames:
    """Tests for GET /api/17lands/games endpoint."""

    def test_list_games_returns_200(self, client):
        response = client.get("/api/17lands/games")
        assert response.status_code == 200

    def test_list_games_response_structure(self, client):
        response = client.get("/api/17lands/games")
        data = response.json()
        assert "data" in data
        assert "pagination" in data

    def test_list_games_filter_by_won(self, client):
        response = client.get("/api/17lands/games?won=true")
        assert response.status_code == 200

    def test_list_games_limit_validation(self, client):
        response = client.get("/api/17lands/games?limit=200")
        assert response.status_code == 422


class TestListReplays:
    """Tests for GET /api/17lands/replays endpoint."""

    def test_list_replays_returns_200(self, client):
        response = client.get("/api/17lands/replays")
        assert response.status_code == 200

    def test_list_replays_response_structure(self, client):
        response = client.get("/api/17lands/replays")
        data = response.json()
        assert "data" in data
        assert "pagination" in data

    def test_list_replays_filter_by_expansion(self, client):
        response = client.get("/api/17lands/replays?expansion=KHM")
        assert response.status_code == 200

    def test_list_replays_limit_validation(self, client):
        response = client.get("/api/17lands/replays?limit=200")
        assert response.status_code == 422


class TestListCardStats:
    """Tests for GET /api/17lands/card_stats endpoint."""

    def test_card_stats_returns_200(self, client):
        response = client.get("/api/17lands/card_stats?expansion=SOS")
        assert response.status_code == 200

    def test_card_stats_response_structure(self, client):
        response = client.get("/api/17lands/card_stats?expansion=SOS")
        data = response.json()
        assert "data" in data
        assert "pagination" in data
        assert "17Lands" in data["attribution"]

    def test_card_stats_row_fields(self, client):
        response = client.get("/api/17lands/card_stats?expansion=SOS&format=PremierDraft")
        rows = response.json()["data"]
        if rows:
            row = rows[0]
            assert {"card_name", "avg_seen", "avg_pick", "win_rate", "ever_drawn_win_rate"} <= row.keys()

    def test_card_stats_requires_expansion(self, client):
        response = client.get("/api/17lands/card_stats")
        assert response.status_code == 422

    def test_card_stats_limit_validation(self, client):
        response = client.get("/api/17lands/card_stats?expansion=SOS&limit=200")
        assert response.status_code == 422

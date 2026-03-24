"""Tests for flashcard API endpoints."""

import uuid

import pytest


@pytest.fixture
def flashcard_user_id():
    return f"test_flashcard_{uuid.uuid4().hex[:8]}"


class TestGenerateFlashcards:
    """Tests for POST /api/flashcards/generate."""

    def test_generate_keywords_returns_200(self, client, flashcard_user_id):
        response = client.post(
            "/api/flashcards/generate",
            json={"user_id": flashcard_user_id, "card_type": "keyword_definition"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "created" in data
        assert "collection" in data
        assert data["created"] > 0

    def test_generate_card_oracle_returns_200(self, client, flashcard_user_id):
        response = client.post(
            "/api/flashcards/generate",
            json={"user_id": flashcard_user_id, "card_type": "card_oracle", "set_code": "KLD"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["created"] > 0
        assert data["collection"] == "card_oracle_KLD"

    def test_generate_card_mana_cost_returns_200(self, client, flashcard_user_id):
        response = client.post(
            "/api/flashcards/generate",
            json={"user_id": flashcard_user_id, "card_type": "card_mana_cost", "set_code": "KLD"},
        )
        assert response.status_code == 200
        assert response.json()["created"] > 0

    def test_generate_card_stats_returns_200(self, client, flashcard_user_id):
        response = client.post(
            "/api/flashcards/generate",
            json={"user_id": flashcard_user_id, "card_type": "card_stats", "set_code": "KLD"},
        )
        assert response.status_code == 200
        assert response.json()["created"] > 0

    def test_generate_card_type_requires_set_code(self, client, flashcard_user_id):
        response = client.post(
            "/api/flashcards/generate",
            json={"user_id": flashcard_user_id, "card_type": "card_oracle"},
        )
        assert response.status_code == 400

    def test_generate_keywords_filtered_by_set(self, client, flashcard_user_id):
        """Keywords with set_code should only include keywords from that set."""
        all_resp = client.post(
            "/api/flashcards/generate",
            json={"user_id": flashcard_user_id, "card_type": "keyword_definition", "collection_name": "all_kw"},
        )
        set_resp = client.post(
            "/api/flashcards/generate",
            json={
                "user_id": flashcard_user_id,
                "card_type": "keyword_definition",
                "set_code": "KLD",
                "collection_name": "kld_kw",
            },
        )
        assert set_resp.json()["created"] < all_resp.json()["created"]
        assert set_resp.json()["created"] > 0

    def test_generate_idempotent(self, client, flashcard_user_id):
        """Second generation of same type should create 0 cards."""
        client.post(
            "/api/flashcards/generate",
            json={"user_id": flashcard_user_id, "card_type": "keyword_definition"},
        )
        response = client.post(
            "/api/flashcards/generate",
            json={"user_id": flashcard_user_id, "card_type": "keyword_definition"},
        )
        assert response.json()["created"] == 0


class TestGetNextFlashcard:
    """Tests for GET /api/flashcards/next."""

    def test_next_returns_200(self, client, flashcard_user_id):
        # Generate some cards first
        client.post(
            "/api/flashcards/generate",
            json={"user_id": flashcard_user_id, "card_type": "keyword_definition"},
        )
        response = client.get(f"/api/flashcards/next?user_id={flashcard_user_id}")
        assert response.status_code == 200
        data = response.json()
        assert "flashcard_id" in data
        assert "question" in data
        assert "answer" in data
        assert data["answer"] is not None
        assert "card_type" in data["question"]

    def test_next_with_collection_filter(self, client, flashcard_user_id):
        client.post(
            "/api/flashcards/generate",
            json={"user_id": flashcard_user_id, "card_type": "keyword_definition"},
        )
        response = client.get(f"/api/flashcards/next?user_id={flashcard_user_id}&collection=keywords_keywordAbilities")
        assert response.status_code == 200

    def test_next_no_cards_returns_null(self, client):
        response = client.get("/api/flashcards/next?user_id=nonexistent_user_xyz")
        assert response.status_code == 200
        assert response.json() is None


class TestRecordReview:
    """Tests for POST /api/flashcards/review."""

    def test_review_returns_200(self, client, flashcard_user_id):
        # Generate and get a card
        client.post(
            "/api/flashcards/generate",
            json={"user_id": flashcard_user_id, "card_type": "keyword_definition"},
        )
        next_resp = client.get(f"/api/flashcards/next?user_id={flashcard_user_id}")
        flashcard_id = next_resp.json()["flashcard_id"]

        response = client.post(
            "/api/flashcards/review",
            json={
                "user_id": flashcard_user_id,
                "flashcard_id": flashcard_id,
                "rating": 4,
                "response_time_ms": 2000,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "interval" in data
        assert "ease_factor" in data
        assert data["interval"] >= 1


class TestListCollections:
    """Tests for GET /api/flashcards/collections."""

    def test_collections_returns_200(self, client, flashcard_user_id):
        client.post(
            "/api/flashcards/generate",
            json={"user_id": flashcard_user_id, "card_type": "keyword_definition"},
        )
        response = client.get(f"/api/flashcards/collections?user_id={flashcard_user_id}")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        assert "name" in data[0]
        assert "card_count" in data[0]


class TestGenerateWithCollectionName:
    """Tests for collection_name parameter on generate."""

    def test_generate_with_custom_collection_name(self, client, flashcard_user_id):
        response = client.post(
            "/api/flashcards/generate",
            json={
                "user_id": flashcard_user_id,
                "card_type": "card_oracle",
                "set_code": "KLD",
                "collection_name": "KLD Study Deck",
            },
        )
        assert response.status_code == 200
        assert response.json()["collection"] == "KLD Study Deck"
        assert response.json()["created"] > 0

    def test_generate_multiple_types_into_same_collection(self, client, flashcard_user_id):
        for card_type in ["card_oracle", "card_mana_cost"]:
            client.post(
                "/api/flashcards/generate",
                json={
                    "user_id": flashcard_user_id,
                    "card_type": card_type,
                    "set_code": "KLD",
                    "collection_name": "KLD Combined",
                },
            )
        collections = client.get(f"/api/flashcards/collections?user_id={flashcard_user_id}").json()
        combined = [c for c in collections if c["name"] == "KLD Combined"]
        assert len(combined) == 1
        assert combined[0]["card_count"] > 0


class TestMergeCollections:
    """Tests for POST /api/flashcards/collections/merge."""

    def test_merge_collections_returns_200(self, client, flashcard_user_id):
        client.post(
            "/api/flashcards/generate",
            json={"user_id": flashcard_user_id, "card_type": "keyword_definition"},
        )
        collections = client.get(f"/api/flashcards/collections?user_id={flashcard_user_id}").json()
        col_ids = [c["id"] for c in collections[:2]]

        response = client.post(
            "/api/flashcards/collections/merge",
            json={"user_id": flashcard_user_id, "collection_ids": col_ids, "name": "Merged Keywords"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["collection"]["name"] == "Merged Keywords"
        assert data["merged_from"] == 2
        assert data["collection"]["card_count"] > 0

    def test_merge_with_delete_originals(self, client, flashcard_user_id):
        client.post(
            "/api/flashcards/generate",
            json={"user_id": flashcard_user_id, "card_type": "keyword_definition"},
        )
        before = client.get(f"/api/flashcards/collections?user_id={flashcard_user_id}").json()
        col_ids = [c["id"] for c in before[:2]]

        client.post(
            "/api/flashcards/collections/merge",
            json={
                "user_id": flashcard_user_id,
                "collection_ids": col_ids,
                "name": "Merged All",
                "delete_originals": True,
            },
        )
        after = client.get(f"/api/flashcards/collections?user_id={flashcard_user_id}").json()
        assert len(after) < len(before)

    def test_merge_not_found(self, client, flashcard_user_id):
        response = client.post(
            "/api/flashcards/collections/merge",
            json={"user_id": flashcard_user_id, "collection_ids": [99999], "name": "Bad Merge"},
        )
        assert response.status_code == 404


class TestDeleteCollection:
    """Tests for DELETE /api/flashcards/collections/{id}."""

    def test_delete_collection_returns_200(self, client, flashcard_user_id):
        client.post(
            "/api/flashcards/generate",
            json={"user_id": flashcard_user_id, "card_type": "keyword_definition"},
        )
        collections = client.get(f"/api/flashcards/collections?user_id={flashcard_user_id}").json()
        col_id = collections[0]["id"]
        card_count = collections[0]["card_count"]

        response = client.delete(f"/api/flashcards/collections/{col_id}?user_id={flashcard_user_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["deleted"] is True
        assert data["cards_removed"] == card_count

    def test_delete_collection_not_found(self, client, flashcard_user_id):
        response = client.delete(f"/api/flashcards/collections/99999?user_id={flashcard_user_id}")
        assert response.status_code == 404

    def test_delete_collection_reduces_count(self, client, flashcard_user_id):
        client.post(
            "/api/flashcards/generate",
            json={"user_id": flashcard_user_id, "card_type": "keyword_definition"},
        )
        before = client.get(f"/api/flashcards/collections?user_id={flashcard_user_id}").json()
        col_id = before[0]["id"]
        client.delete(f"/api/flashcards/collections/{col_id}?user_id={flashcard_user_id}")
        after = client.get(f"/api/flashcards/collections?user_id={flashcard_user_id}").json()
        assert len(after) == len(before) - 1


class TestStudyStats:
    """Tests for GET /api/flashcards/stats."""

    def test_stats_returns_200(self, client, flashcard_user_id):
        client.post(
            "/api/flashcards/generate",
            json={"user_id": flashcard_user_id, "card_type": "keyword_definition"},
        )
        response = client.get(f"/api/flashcards/stats?user_id={flashcard_user_id}")
        assert response.status_code == 200
        data = response.json()
        assert "total_cards" in data
        assert "cards_due" in data
        assert "cards_new" in data
        assert "reviews_today" in data
        assert data["total_cards"] > 0

"""Tests for flashcard analytics endpoints."""

import uuid

import pytest


@pytest.fixture
def analytics_user_id():
    return f"test_analytics_{uuid.uuid4().hex[:8]}"


@pytest.fixture
def user_with_reviews(client, analytics_user_id):
    """Generate cards and do a few reviews."""
    client.post(
        "/api/flashcards/generate",
        json={"user_id": analytics_user_id, "card_type": "keyword_definition"},
    )
    # Do a few reviews
    for _ in range(5):
        resp = client.get(f"/api/flashcards/next?user_id={analytics_user_id}")
        card = resp.json()
        if card:
            client.post(
                "/api/flashcards/review",
                json={
                    "user_id": analytics_user_id,
                    "flashcard_id": card["flashcard_id"],
                    "rating": 4,
                    "response_time_ms": 2000,
                },
            )
    return analytics_user_id


class TestReviewHistory:
    def test_returns_200(self, client, user_with_reviews):
        response = client.get(f"/api/flashcards/analytics/review-history?user_id={user_with_reviews}")
        assert response.status_code == 200
        data = response.json()
        assert "buckets" in data
        assert data["granularity"] == "daily"
        assert len(data["buckets"]) == 30

    def test_today_has_reviews(self, client, user_with_reviews):
        data = client.get(f"/api/flashcards/analytics/review-history?user_id={user_with_reviews}").json()
        today = data["buckets"][-1]
        assert today["reviews"] > 0
        assert today["average_rating"] is not None

    def test_custom_days(self, client, user_with_reviews):
        data = client.get(f"/api/flashcards/analytics/review-history?user_id={user_with_reviews}&days=7").json()
        assert len(data["buckets"]) == 7

    def test_hourly_granularity(self, client, user_with_reviews):
        data = client.get(
            f"/api/flashcards/analytics/review-history?user_id={user_with_reviews}&days=1&granularity=hourly"
        ).json()
        assert data["granularity"] == "hourly"
        assert len(data["buckets"]) == 24
        assert "T" in data["buckets"][0]["date"]

    def test_invalid_granularity_rejected(self, client, user_with_reviews):
        response = client.get(
            f"/api/flashcards/analytics/review-history?user_id={user_with_reviews}&granularity=weekly"
        )
        assert response.status_code == 422


class TestCardDifficulty:
    def test_returns_200(self, client, user_with_reviews):
        response = client.get(f"/api/flashcards/analytics/card-difficulty?user_id={user_with_reviews}")
        assert response.status_code == 200
        data = response.json()
        assert "hardest" in data
        assert "easiest" in data
        assert "most_reviewed" in data

    def test_cards_have_question(self, client, user_with_reviews):
        data = client.get(f"/api/flashcards/analytics/card-difficulty?user_id={user_with_reviews}").json()
        if data["hardest"]:
            card = data["hardest"][0]
            assert "question" in card
            assert "ease_factor" in card


class TestCollectionBreakdown:
    def test_returns_200(self, client, user_with_reviews):
        response = client.get(f"/api/flashcards/analytics/collections?user_id={user_with_reviews}")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

    def test_has_metrics(self, client, user_with_reviews):
        data = client.get(f"/api/flashcards/analytics/collections?user_id={user_with_reviews}").json()
        col = data[0]
        assert "completion_pct" in col
        assert "win_rate" in col
        assert "cards_due" in col


class TestSessionAnalytics:
    def test_returns_200(self, client, user_with_reviews):
        response = client.get(f"/api/flashcards/analytics/sessions?user_id={user_with_reviews}")
        assert response.status_code == 200
        data = response.json()
        assert "total_study_time_ms" in data
        assert "accuracy_by_card_type" in data
        assert data["total_study_time_ms"] > 0

    def test_accuracy_has_keyword_type(self, client, user_with_reviews):
        data = client.get(f"/api/flashcards/analytics/sessions?user_id={user_with_reviews}").json()
        assert "keyword_definition" in data["accuracy_by_card_type"]


class TestRetentionCurve:
    def test_returns_200(self, client, user_with_reviews):
        response = client.get(f"/api/flashcards/analytics/retention?user_id={user_with_reviews}")
        assert response.status_code == 200
        data = response.json()
        assert "buckets" in data
        assert len(data["buckets"]) == 7

    def test_buckets_have_pass_rate(self, client, user_with_reviews):
        data = client.get(f"/api/flashcards/analytics/retention?user_id={user_with_reviews}").json()
        bucket = data["buckets"][0]
        assert "interval_label" in bucket
        assert "pass_rate" in bucket


class TestKeywordInsights:
    def test_returns_200(self, client, user_with_reviews):
        response = client.get(f"/api/flashcards/analytics/keywords?user_id={user_with_reviews}")
        assert response.status_code == 200
        data = response.json()
        assert "hardest" in data
        assert "easiest" in data

    def test_keywords_have_fields(self, client, user_with_reviews):
        data = client.get(f"/api/flashcards/analytics/keywords?user_id={user_with_reviews}").json()
        if data["hardest"]:
            kw = data["hardest"][0]
            assert "keyword" in kw
            assert "ease_factor" in kw
            assert "pass_rate" in kw

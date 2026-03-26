"""Flashcard analytics service — computes study metrics from SRS data."""
# ruff: noqa: E501

import json
import logging
from datetime import UTC, datetime, timedelta

from srs import SRSClient

from mtgsim.api.models.flashcards import (
    CardDifficulty,
    CardDifficultyResponse,
    CollectionBreakdown,
    KeywordInsight,
    KeywordInsightsResponse,
    RetentionBucket,
    RetentionCurveResponse,
    ReviewHistoryResponse,
    SessionAnalytics,
)
from mtgsim.flashcards.generator import _get_or_create_app

logger = logging.getLogger("mtgsim.api.services.flashcard_analytics")


def _get_client() -> SRSClient:
    return SRSClient()


def _parse_question(raw) -> dict:
    if isinstance(raw, dict):
        return raw
    if isinstance(raw, str):
        return json.loads(raw)
    return {}


async def get_review_history(user_id: str, days: int = 30, granularity: str = "daily") -> ReviewHistoryResponse:
    with _get_client() as client:
        now = datetime.now(UTC)

        if granularity == "hourly":
            hours = days * 24
            buckets = _build_buckets(client, user_id, now, hours, timedelta(hours=1), "%Y-%m-%dT%H:00:00")
        else:
            buckets = _build_buckets(client, user_id, now, days, timedelta(days=1), "%Y-%m-%d")

    return ReviewHistoryResponse(buckets=buckets, granularity=granularity, days=days)


def _build_buckets(client, user_id: str, now, count: int, step: timedelta, fmt: str) -> list:
    from mtgsim.api.models.flashcards import ReviewBucket

    buckets = []
    for i in range(count - 1, -1, -1):
        start = now - step * i
        if step >= timedelta(days=1):
            start = start.replace(hour=0, minute=0, second=0, microsecond=0)
        else:
            start = start.replace(minute=0, second=0, microsecond=0)
        end = start + step
        label = start.strftime(fmt)

        rows = client.db.conn.execute(
            "SELECT rating, response_time_ms FROM review_events WHERE user_id = ? AND created_at >= ? AND created_at < ?",
            (user_id, start.isoformat(), end.isoformat()),
        ).fetchall()

        reviews = len(rows)
        if reviews == 0:
            buckets.append(ReviewBucket(date=label, reviews=0))
            continue

        avg_rating = round(sum(r["rating"] for r in rows) / reviews, 2)
        avg_ms = int(sum(r["response_time_ms"] for r in rows) / reviews)

        new_learned = client.db.conn.execute(
            """SELECT COUNT(DISTINCT flashcard_id) FROM review_events
               WHERE user_id = ? AND created_at >= ? AND created_at < ?
               AND flashcard_id NOT IN (
                   SELECT DISTINCT flashcard_id FROM review_events
                   WHERE user_id = ? AND created_at < ?
               )""",
            (user_id, start.isoformat(), end.isoformat(), user_id, start.isoformat()),
        ).fetchone()[0]

        buckets.append(
            ReviewBucket(
                date=label,
                reviews=reviews,
                average_rating=avg_rating,
                average_response_ms=avg_ms,
                new_cards_learned=new_learned,
            )
        )
    return buckets


async def get_card_difficulty(user_id: str, limit: int = 10) -> CardDifficultyResponse:
    with _get_client() as client:
        # Cards with reviews, joined to get question text and review count
        base_query = """
            SELECT s.flashcard_id, f.question, s.ease_factor, s.interval, s.repetitions,
                   (SELECT COUNT(*) FROM review_events re WHERE re.user_id = ? AND re.flashcard_id = s.flashcard_id) as total_reviews
            FROM srs_state s
            JOIN flashcards f ON f.id = s.flashcard_id
            WHERE s.user_id = ? AND s.repetitions > 0
        """

        hardest_rows = client.db.conn.execute(
            base_query + " ORDER BY s.ease_factor ASC LIMIT ?", (user_id, user_id, limit)
        ).fetchall()

        easiest_rows = client.db.conn.execute(
            base_query + " ORDER BY s.ease_factor DESC LIMIT ?", (user_id, user_id, limit)
        ).fetchall()

        most_reviewed_rows = client.db.conn.execute(
            base_query + " ORDER BY total_reviews DESC LIMIT ?", (user_id, user_id, limit)
        ).fetchall()

        def to_card(row):
            return CardDifficulty(
                flashcard_id=row["flashcard_id"],
                question=_parse_question(row["question"]),
                ease_factor=round(row["ease_factor"], 2),
                interval=row["interval"],
                repetitions=row["repetitions"],
                total_reviews=row["total_reviews"],
            )

    return CardDifficultyResponse(
        hardest=[to_card(r) for r in hardest_rows],
        easiest=[to_card(r) for r in easiest_rows],
        most_reviewed=[to_card(r) for r in most_reviewed_rows],
    )


async def get_collection_breakdown(user_id: str) -> list[CollectionBreakdown]:
    with _get_client() as client:
        app = _get_or_create_app(client, user_id)
        now = datetime.now(UTC).isoformat()

        collections = client.db.conn.execute(
            "SELECT id, name FROM collections WHERE user_id = ? AND application_id = ? ORDER BY name",
            (user_id, app.id),
        ).fetchall()

        results = []
        for col in collections:
            cid = col["id"]
            name = col["name"]

            card_count = client.db.conn.execute(
                "SELECT COUNT(*) FROM flashcard_collections WHERE collection_id = ?", (cid,)
            ).fetchone()[0]

            # Cards that have been reviewed at least once
            cards_reviewed = client.db.conn.execute(
                """SELECT COUNT(*) FROM srs_state s
                   JOIN flashcard_collections fc ON fc.flashcard_id = s.flashcard_id
                   WHERE s.user_id = ? AND fc.collection_id = ? AND s.repetitions > 0""",
                (user_id, cid),
            ).fetchone()[0]

            completion_pct = round(100.0 * cards_reviewed / card_count, 1) if card_count > 0 else 0.0

            # Win rate: % of reviews rated 3+ for cards in this collection
            review_stats = client.db.conn.execute(
                """SELECT COUNT(*) as total, SUM(CASE WHEN re.rating >= 3 THEN 1 ELSE 0 END) as passed
                   FROM review_events re
                   JOIN flashcard_collections fc ON fc.flashcard_id = re.flashcard_id
                   WHERE re.user_id = ? AND fc.collection_id = ?""",
                (user_id, cid),
            ).fetchone()
            total_rev = review_stats["total"]
            win_rate = round(100.0 * review_stats["passed"] / total_rev, 1) if total_rev > 0 else None

            # Average ease for reviewed cards
            ease_row = client.db.conn.execute(
                """SELECT AVG(s.ease_factor) FROM srs_state s
                   JOIN flashcard_collections fc ON fc.flashcard_id = s.flashcard_id
                   WHERE s.user_id = ? AND fc.collection_id = ? AND s.repetitions > 0""",
                (user_id, cid),
            ).fetchone()
            avg_ease = round(ease_row[0], 2) if ease_row[0] else None

            # Cards due
            cards_due = client.db.conn.execute(
                """SELECT COUNT(*) FROM srs_state s
                   JOIN flashcard_collections fc ON fc.flashcard_id = s.flashcard_id
                   WHERE s.user_id = ? AND fc.collection_id = ? AND s.next_review_at <= ?""",
                (user_id, cid, now),
            ).fetchone()[0]

            results.append(
                CollectionBreakdown(
                    id=cid,
                    name=name,
                    card_count=card_count,
                    cards_reviewed=cards_reviewed,
                    completion_pct=completion_pct,
                    win_rate=win_rate,
                    average_ease=avg_ease,
                    cards_due=cards_due,
                )
            )

    return results


async def get_session_analytics(user_id: str) -> SessionAnalytics:
    with _get_client() as client:
        # Total study time
        total_ms = client.db.conn.execute(
            "SELECT COALESCE(SUM(response_time_ms), 0) FROM review_events WHERE user_id = ?",
            (user_id,),
        ).fetchone()[0]

        # Total reviews for rate calc
        total_reviews = client.db.conn.execute(
            "SELECT COUNT(*) FROM review_events WHERE user_id = ?", (user_id,)
        ).fetchone()[0]

        avg_cards_per_min = None
        if total_ms > 0 and total_reviews > 0:
            minutes = total_ms / 60000.0
            avg_cards_per_min = round(total_reviews / minutes, 1) if minutes > 0 else None

        # Accuracy by card_type
        rows = client.db.conn.execute(
            """SELECT f.question, re.rating FROM review_events re
               JOIN flashcards f ON f.id = re.flashcard_id
               WHERE re.user_id = ?""",
            (user_id,),
        ).fetchall()

        type_stats: dict[str, dict[str, int]] = {}
        for row in rows:
            q = _parse_question(row["question"])
            card_type = q.get("card_type", "unknown")
            if card_type not in type_stats:
                type_stats[card_type] = {"total": 0, "passed": 0}
            type_stats[card_type]["total"] += 1
            if row["rating"] >= 3:
                type_stats[card_type]["passed"] += 1

        accuracy_by_type = {
            ct: round(100.0 * s["passed"] / s["total"], 1) if s["total"] > 0 else 0.0 for ct, s in type_stats.items()
        }

    return SessionAnalytics(
        total_study_time_ms=total_ms,
        avg_cards_per_minute=avg_cards_per_min,
        accuracy_by_card_type=accuracy_by_type,
    )


async def get_retention_curve(user_id: str) -> RetentionCurveResponse:
    """Pass rate by interval bucket at time of review."""
    with _get_client() as client:
        rows = client.db.conn.execute(
            """SELECT s.interval, re.rating
               FROM review_events re
               JOIN srs_state s ON s.user_id = re.user_id AND s.flashcard_id = re.flashcard_id
               WHERE re.user_id = ?""",
            (user_id,),
        ).fetchall()

    # Bucket by interval
    bucket_defs = [
        ("New (0d)", 0, 0),
        ("1 day", 1, 1),
        ("2-3 days", 2, 3),
        ("4-7 days", 4, 7),
        ("8-14 days", 8, 14),
        ("15-30 days", 15, 30),
        ("31+ days", 31, 999999),
    ]

    buckets = []
    for label, lo, hi in bucket_defs:
        matching = [r for r in rows if lo <= (r["interval"] or 0) <= hi]
        total = len(matching)
        passed = sum(1 for r in matching if r["rating"] >= 3)
        pass_rate = round(100.0 * passed / total, 1) if total > 0 else 0.0
        buckets.append(RetentionBucket(interval_label=label, total_reviews=total, passed=passed, pass_rate=pass_rate))

    return RetentionCurveResponse(buckets=buckets)


async def get_keyword_insights(user_id: str, limit: int = 10) -> KeywordInsightsResponse:
    with _get_client() as client:
        # Get all keyword_definition cards with their SRS state and review history
        rows = client.db.conn.execute(
            """SELECT f.question, s.ease_factor,
                      (SELECT COUNT(*) FROM review_events re WHERE re.user_id = ? AND re.flashcard_id = f.id) as total_reviews,
                      (SELECT COUNT(*) FROM review_events re WHERE re.user_id = ? AND re.flashcard_id = f.id AND re.rating >= 3) as passed
               FROM flashcards f
               JOIN srs_state s ON s.flashcard_id = f.id AND s.user_id = ?
               WHERE f.user_id = ? AND s.repetitions > 0""",
            (user_id, user_id, user_id, user_id),
        ).fetchall()

        keyword_cards = []
        for row in rows:
            q = _parse_question(row["question"])
            if q.get("card_type") != "keyword_definition":
                continue
            total = row["total_reviews"]
            keyword_cards.append(
                KeywordInsight(
                    keyword=q.get("keyword", ""),
                    ease_factor=round(row["ease_factor"], 2),
                    total_reviews=total,
                    pass_rate=round(100.0 * row["passed"] / total, 1) if total > 0 else 0.0,
                )
            )

        hardest = sorted(keyword_cards, key=lambda k: k.ease_factor)[:limit]
        easiest = sorted(keyword_cards, key=lambda k: k.ease_factor, reverse=True)[:limit]

    return KeywordInsightsResponse(hardest=hardest, easiest=easiest)

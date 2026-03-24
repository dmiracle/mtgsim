"""Flashcard service — bridges SRS client with MTG data generation."""

import logging
from datetime import UTC, datetime, timedelta

from srs import SRSClient
from srs.exceptions import NoFlashcardsAvailableError

from mtgsim.api.models.flashcards import (
    CollectionInfo,
    DeleteCollectionResponse,
    FlashcardQuestion,
    GenerateResponse,
    MergeCollectionsResponse,
    ReviewResponse,
    StudyStats,
)
from mtgsim.flashcards.generator import (
    _get_or_create_app,
    _get_or_create_collection,
    generate_card_mana_cost_flashcards,
    generate_card_oracle_flashcards,
    generate_card_stats_flashcards,
    generate_keyword_flashcards,
)

logger = logging.getLogger("mtgsim.api.services.flashcard")

GENERATORS = {
    "keyword_definition": lambda client, user_id, **kw: generate_keyword_flashcards(
        client, user_id, collection_name=kw.get("collection_name"), set_code=kw.get("set_code")
    ),
    "card_oracle": lambda client, user_id, **kw: generate_card_oracle_flashcards(
        client, user_id, kw.get("set_code", ""), kw.get("rarity"), collection_name=kw.get("collection_name")
    ),
    "card_mana_cost": lambda client, user_id, **kw: generate_card_mana_cost_flashcards(
        client, user_id, kw.get("set_code", ""), collection_name=kw.get("collection_name")
    ),
    "card_stats": lambda client, user_id, **kw: generate_card_stats_flashcards(
        client, user_id, kw.get("set_code", ""), collection_name=kw.get("collection_name")
    ),
}

COLLECTION_NAMES = {
    "keyword_definition": lambda **kw: kw.get("collection_name") or "keywords_keywordAbilities",
    "card_oracle": lambda **kw: kw.get("collection_name") or f"card_oracle_{kw.get('set_code', '')}",
    "card_mana_cost": lambda **kw: kw.get("collection_name") or f"card_mana_cost_{kw.get('set_code', '')}",
    "card_stats": lambda **kw: kw.get("collection_name") or f"card_stats_{kw.get('set_code', '')}",
}


class FlashcardService:
    def _get_client(self) -> SRSClient:
        return SRSClient()

    async def generate(
        self,
        user_id: str,
        card_type: str,
        set_code: str | None = None,
        rarity: str | None = None,
        collection_name: str | None = None,
    ) -> GenerateResponse:
        gen_fn = GENERATORS.get(card_type)
        if not gen_fn:
            return GenerateResponse(created=0, collection="unknown")

        col_fn = COLLECTION_NAMES.get(card_type)
        col_name = col_fn(set_code=set_code, collection_name=collection_name) if col_fn else card_type

        with self._get_client() as client:
            created = gen_fn(client, user_id, set_code=set_code, rarity=rarity, collection_name=collection_name)

        return GenerateResponse(created=created, collection=col_name)

    async def get_next(self, user_id: str, collection: str | None = None) -> FlashcardQuestion | None:
        with self._get_client() as client:
            app = _get_or_create_app(client, user_id)

            collection_id = None
            if collection:
                row = client.db.conn.execute(
                    "SELECT id FROM collections WHERE user_id = ? AND name = ? AND application_id = ?",
                    (user_id, collection, app.id),
                ).fetchone()
                if row:
                    collection_id = row[0]

            try:
                card = client.get_next_flashcard(user_id, application_id=app.id, collection_id=collection_id)
            except NoFlashcardsAvailableError:
                return None

            return FlashcardQuestion(
                flashcard_id=card.id,
                question=card.question,
                answer=card.answer,
                collection=collection,
            )

    async def record_review(
        self, user_id: str, flashcard_id: int, rating: int, response_time_ms: int
    ) -> ReviewResponse:
        with self._get_client() as client:
            client.record_review(user_id, flashcard_id, rating=rating, response_time_ms=response_time_ms)
            state = client.get_srs_state(user_id, flashcard_id)

        return ReviewResponse(
            next_review_at=state.next_review_at.isoformat() if state.next_review_at else None,
            interval=state.interval,
            ease_factor=state.ease_factor,
        )

    async def get_collections(self, user_id: str) -> list[CollectionInfo]:
        with self._get_client() as client:
            app = _get_or_create_app(client, user_id)
            rows = client.db.conn.execute(
                """SELECT c.id, c.name, COUNT(fc.flashcard_id) as card_count
                   FROM collections c
                   LEFT JOIN flashcard_collections fc ON c.id = fc.collection_id
                   WHERE c.user_id = ? AND c.application_id = ?
                   GROUP BY c.id, c.name
                   ORDER BY c.name""",
                (user_id, app.id),
            ).fetchall()

        return [CollectionInfo(id=r[0], name=r[1], card_count=r[2]) for r in rows]

    async def get_stats(self, user_id: str) -> StudyStats:
        with self._get_client() as client:
            app = _get_or_create_app(client, user_id)
            now = datetime.now(UTC)

            # Total flashcards for this user/app
            total = client.db.conn.execute(
                """SELECT COUNT(DISTINCT fc.flashcard_id)
                   FROM flashcard_collections fc
                   JOIN collections c ON fc.collection_id = c.id
                   WHERE c.user_id = ? AND c.application_id = ?""",
                (user_id, app.id),
            ).fetchone()[0]

            # Cards due (have been reviewed, next_review_at <= now)
            cards_due = client.db.conn.execute(
                """SELECT COUNT(*) FROM srs_state
                   WHERE user_id = ? AND next_review_at <= ?""",
                (user_id, now.isoformat()),
            ).fetchone()[0]

            # New cards (no srs_state entry yet)
            cards_with_state = client.db.conn.execute(
                "SELECT COUNT(*) FROM srs_state WHERE user_id = ?",
                (user_id,),
            ).fetchone()[0]
            cards_new = total - cards_with_state

            # Reviews today
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            reviews_today = client.db.conn.execute(
                "SELECT COUNT(*) FROM review_events WHERE user_id = ? AND created_at >= ?",
                (user_id, today_start.isoformat()),
            ).fetchone()[0]

            # Mastery distribution (based on interval)
            cards_learning = client.db.conn.execute(
                "SELECT COUNT(*) FROM srs_state WHERE user_id = ? AND repetitions > 0 AND interval < 1",
                (user_id,),
            ).fetchone()[0]
            cards_young = client.db.conn.execute(
                "SELECT COUNT(*) FROM srs_state WHERE user_id = ? AND interval >= 1 AND interval <= 21",
                (user_id,),
            ).fetchone()[0]
            cards_mature = client.db.conn.execute(
                "SELECT COUNT(*) FROM srs_state WHERE user_id = ? AND interval > 21",
                (user_id,),
            ).fetchone()[0]

            # Performance
            ease_row = client.db.conn.execute(
                "SELECT AVG(ease_factor) FROM srs_state WHERE user_id = ? AND repetitions > 0",
                (user_id,),
            ).fetchone()
            average_ease = round(ease_row[0], 2) if ease_row[0] else 2.5

            total_reviews = client.db.conn.execute(
                "SELECT COUNT(*) FROM review_events WHERE user_id = ?",
                (user_id,),
            ).fetchone()[0]

            # Streak: consecutive days with reviews (counting back from today)
            streak_days = 0
            day = today_start
            while True:
                day_end = day + timedelta(days=1)
                has_reviews = client.db.conn.execute(
                    "SELECT COUNT(*) FROM review_events WHERE user_id = ? AND created_at >= ? AND created_at < ?",
                    (user_id, day.isoformat(), day_end.isoformat()),
                ).fetchone()[0]
                if has_reviews == 0:
                    break
                streak_days += 1
                day = day - timedelta(days=1)

            # Forecast
            tomorrow = (now + timedelta(days=1)).isoformat()
            next_week = (now + timedelta(days=7)).isoformat()
            due_tomorrow = client.db.conn.execute(
                "SELECT COUNT(*) FROM srs_state WHERE user_id = ? AND next_review_at <= ?",
                (user_id, tomorrow),
            ).fetchone()[0]
            due_this_week = client.db.conn.execute(
                "SELECT COUNT(*) FROM srs_state WHERE user_id = ? AND next_review_at <= ?",
                (user_id, next_week),
            ).fetchone()[0]

            collections = await self.get_collections(user_id)

        return StudyStats(
            total_cards=total,
            cards_due=cards_due,
            cards_new=cards_new,
            reviews_today=reviews_today,
            collections=collections,
            cards_learning=cards_learning,
            cards_young=cards_young,
            cards_mature=cards_mature,
            average_ease=average_ease,
            total_reviews=total_reviews,
            streak_days=streak_days,
            due_tomorrow=due_tomorrow,
            due_this_week=due_this_week,
        )

    async def merge_collections(
        self, user_id: str, collection_ids: list[int], name: str, delete_originals: bool = False
    ) -> MergeCollectionsResponse | None:
        with self._get_client() as client:
            app = _get_or_create_app(client, user_id)

            # Verify all source collections exist and belong to user
            for cid in collection_ids:
                row = client.db.conn.execute(
                    "SELECT id FROM collections WHERE id = ? AND user_id = ?", (cid, user_id)
                ).fetchone()
                if not row:
                    return None

            # Create target collection
            target = _get_or_create_collection(client, user_id, name, app.id)

            # Copy flashcard links to target collection
            for cid in collection_ids:
                fc_rows = client.db.conn.execute(
                    "SELECT flashcard_id FROM flashcard_collections WHERE collection_id = ?", (cid,)
                ).fetchall()
                for (fid,) in fc_rows:
                    existing = client.db.conn.execute(
                        "SELECT 1 FROM flashcard_collections WHERE flashcard_id = ? AND collection_id = ?",
                        (fid, target.id),
                    ).fetchone()
                    if not existing:
                        client.db.conn.execute(
                            "INSERT INTO flashcard_collections (flashcard_id, collection_id) VALUES (?, ?)",
                            (fid, target.id),
                        )

            # Delete originals if requested
            if delete_originals:
                for cid in collection_ids:
                    if cid != target.id:
                        client.db.conn.execute("DELETE FROM flashcard_collections WHERE collection_id = ?", (cid,))
                        client.db.conn.execute("DELETE FROM collections WHERE id = ?", (cid,))

            client.db.conn.commit()

            # Get final card count
            card_count = client.db.conn.execute(
                "SELECT COUNT(*) FROM flashcard_collections WHERE collection_id = ?", (target.id,)
            ).fetchone()[0]

        return MergeCollectionsResponse(
            collection=CollectionInfo(id=target.id, name=name, card_count=card_count),
            merged_from=len(collection_ids),
            delete_originals=delete_originals,
        )

    async def delete_collection(self, user_id: str, collection_id: int) -> DeleteCollectionResponse | None:
        with self._get_client() as client:
            # Verify collection exists and belongs to user
            row = client.db.conn.execute(
                "SELECT id, name FROM collections WHERE id = ? AND user_id = ?",
                (collection_id, user_id),
            ).fetchone()
            if not row:
                return None

            col_name = row[1]

            # Get flashcard IDs in this collection
            fc_rows = client.db.conn.execute(
                "SELECT flashcard_id FROM flashcard_collections WHERE collection_id = ?",
                (collection_id,),
            ).fetchall()
            flashcard_ids = [r[0] for r in fc_rows]
            cards_removed = len(flashcard_ids)

            # Remove flashcard-collection links
            client.db.conn.execute(
                "DELETE FROM flashcard_collections WHERE collection_id = ?",
                (collection_id,),
            )

            # Delete orphaned flashcards (not in any other collection)
            for fid in flashcard_ids:
                other = client.db.conn.execute(
                    "SELECT COUNT(*) FROM flashcard_collections WHERE flashcard_id = ?",
                    (fid,),
                ).fetchone()[0]
                if other == 0:
                    client.db.conn.execute("DELETE FROM srs_state WHERE flashcard_id = ?", (fid,))
                    client.db.conn.execute("DELETE FROM review_events WHERE flashcard_id = ?", (fid,))
                    client.db.conn.execute("DELETE FROM flashcards WHERE id = ?", (fid,))

            # Delete the collection
            client.db.conn.execute("DELETE FROM collections WHERE id = ?", (collection_id,))
            client.db.conn.commit()

        return DeleteCollectionResponse(deleted=True, collection=col_name, cards_removed=cards_removed)


flashcard_service = FlashcardService()

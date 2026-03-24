"""Flashcard service — bridges SRS client with MTG data generation."""

import logging
from datetime import UTC, datetime

from srs import SRSClient
from srs.exceptions import NoFlashcardsAvailableError

from mtgsim.api.models.flashcards import (
    CollectionInfo,
    DeleteCollectionResponse,
    FlashcardQuestion,
    GenerateResponse,
    ReviewResponse,
    StudyStats,
)
from mtgsim.flashcards.generator import (
    _get_or_create_app,
    generate_card_mana_cost_flashcards,
    generate_card_oracle_flashcards,
    generate_card_stats_flashcards,
    generate_keyword_flashcards,
)

logger = logging.getLogger("mtgsim.api.services.flashcard")

GENERATORS = {
    "keyword_definition": lambda client, user_id, **kw: generate_keyword_flashcards(client, user_id),
    "card_oracle": lambda client, user_id, **kw: generate_card_oracle_flashcards(
        client, user_id, kw.get("set_code", ""), kw.get("rarity")
    ),
    "card_mana_cost": lambda client, user_id, **kw: generate_card_mana_cost_flashcards(
        client, user_id, kw.get("set_code", "")
    ),
    "card_stats": lambda client, user_id, **kw: generate_card_stats_flashcards(client, user_id, kw.get("set_code", "")),
}

COLLECTION_NAMES = {
    "keyword_definition": lambda **kw: "keywords_keywordAbilities",
    "card_oracle": lambda **kw: f"card_oracle_{kw.get('set_code', '')}",
    "card_mana_cost": lambda **kw: f"card_mana_cost_{kw.get('set_code', '')}",
    "card_stats": lambda **kw: f"card_stats_{kw.get('set_code', '')}",
}


class FlashcardService:
    def _get_client(self) -> SRSClient:
        return SRSClient()

    async def generate(
        self, user_id: str, card_type: str, set_code: str | None = None, rarity: str | None = None
    ) -> GenerateResponse:
        gen_fn = GENERATORS.get(card_type)
        if not gen_fn:
            return GenerateResponse(created=0, collection="unknown")

        col_fn = COLLECTION_NAMES.get(card_type)
        col_name = col_fn(set_code=set_code) if col_fn else card_type

        with self._get_client() as client:
            created = gen_fn(client, user_id, set_code=set_code, rarity=rarity)

        return GenerateResponse(created=created, collection=col_name)

    async def get_next(self, user_id: str, collection: str | None = None) -> FlashcardQuestion | None:
        with self._get_client() as client:
            app = _get_or_create_app(client, user_id)

            collection_id = None
            if collection:
                try:
                    row = client.db.conn.execute(
                        "SELECT id FROM collections WHERE user_id = ? AND name = ? AND application_id = ?",
                        (user_id, collection, app.id),
                    ).fetchone()
                    if row:
                        collection_id = row[0]
                except Exception:
                    pass

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

            collections = await self.get_collections(user_id)

        return StudyStats(
            total_cards=total,
            cards_due=cards_due,
            cards_new=cards_new,
            reviews_today=reviews_today,
            collections=collections,
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

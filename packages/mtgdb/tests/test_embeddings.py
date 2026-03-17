"""Tests for the embeddings module."""

import tempfile
from pathlib import Path

import pytest
from mtgdb.embeddings import (
    EMBEDDING_DIMENSIONS,
    embed_text,
    generate_embeddings,
    init_vec_tables,
    prepare_card_text,
    register_sqlite_vec,
    search_similar_cards,
)
from mtgdb.models import MJCard
from mtgdb.session import init_db
from sqlmodel import Session


@pytest.fixture
def temp_db_path():
    """Create a temporary database file path."""
    with tempfile.NamedTemporaryFile(suffix=".sqlite", delete=False) as f:
        yield Path(f.name)


@pytest.fixture
def db_with_cards(temp_db_path):
    """Initialize a database with some test cards and sqlite-vec."""
    engine = init_db(temp_db_path)
    register_sqlite_vec(engine)
    init_vec_tables(engine)

    cards = [
        MJCard(
            uuid="bolt-uuid",
            name="Lightning Bolt",
            set_code="M10",
            type_line="Instant",
            oracle_text="Lightning Bolt deals 3 damage to any target.",
            colors=["R"],
            rarity="common",
        ),
        MJCard(
            uuid="shock-uuid",
            name="Shock",
            set_code="M10",
            type_line="Instant",
            oracle_text="Shock deals 2 damage to any target.",
            colors=["R"],
            rarity="common",
        ),
        MJCard(
            uuid="wrath-uuid",
            name="Wrath of God",
            set_code="M10",
            type_line="Sorcery",
            oracle_text="Destroy all creatures. They can't be regenerated.",
            colors=["W"],
            rarity="rare",
        ),
        MJCard(
            uuid="counterspell-uuid",
            name="Counterspell",
            set_code="M10",
            type_line="Instant",
            oracle_text="Counter target spell.",
            colors=["U"],
            rarity="uncommon",
        ),
        MJCard(
            uuid="island-uuid",
            name="Island",
            set_code="M10",
            type_line="Basic Land - Island",
            oracle_text=None,  # Basic lands have no oracle text
            colors=[],
            rarity="common",
        ),
    ]

    with Session(engine) as session:
        for card in cards:
            session.add(card)
        session.commit()

    yield temp_db_path, engine

    engine.dispose()
    temp_db_path.unlink(missing_ok=True)


class TestPrepareCardText:
    """Tests for prepare_card_text function."""

    def test_oracle_text(self):
        card = MJCard(
            uuid="test",
            name="Test Card",
            set_code="TST",
            type_line="Instant",
            oracle_text="Deal 3 damage.",
        )
        text = prepare_card_text(card, "oracle")
        assert "Card: Test Card" in text
        assert "Type: Instant" in text
        assert "Deal 3 damage." in text

    def test_oracle_text_none_returns_none(self):
        card = MJCard(uuid="test", name="Test Card", set_code="TST")
        text = prepare_card_text(card, "oracle")
        assert text is None

    def test_name_only(self):
        card = MJCard(uuid="test", name="Lightning Bolt", set_code="TST")
        text = prepare_card_text(card, "name_only")
        assert text == "Lightning Bolt"

    def test_flavor_text(self):
        card = MJCard(
            uuid="test",
            name="Test Card",
            set_code="TST",
            flavor_text="The bolt struck true.",
        )
        text = prepare_card_text(card, "flavor")
        assert "Card: Test Card" in text
        assert "The bolt struck true." in text

    def test_combined(self):
        card = MJCard(
            uuid="test",
            name="Test Card",
            set_code="TST",
            type_line="Instant",
            oracle_text="Deal damage.",
            flavor_text="Flavor here.",
        )
        text = prepare_card_text(card, "combined")
        assert "Card: Test Card" in text
        assert "Type: Instant" in text
        assert "Deal damage." in text
        assert "Flavor: Flavor here." in text


class TestEmbedText:
    """Tests for embed_text function."""

    def test_returns_correct_dimensions(self):
        embedding = embed_text("Lightning Bolt")
        assert len(embedding) == EMBEDDING_DIMENSIONS

    def test_returns_floats(self):
        embedding = embed_text("Test text")
        assert all(isinstance(x, float) for x in embedding)

    def test_similar_texts_have_similar_embeddings(self):
        import numpy as np

        emb1 = np.array(embed_text("Lightning Bolt deals 3 damage"))
        emb2 = np.array(embed_text("Shock deals 2 damage"))
        emb3 = np.array(embed_text("Counter target spell"))

        # Cosine similarity
        sim_12 = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
        sim_13 = np.dot(emb1, emb3) / (np.linalg.norm(emb1) * np.linalg.norm(emb3))

        # Damage spells should be more similar to each other than to counter
        assert sim_12 > sim_13


class TestVecTables:
    """Tests for sqlite-vec table initialization."""

    def test_init_vec_tables(self, temp_db_path):
        engine = init_db(temp_db_path)
        register_sqlite_vec(engine)
        init_vec_tables(engine)

        # Check table exists via raw connection
        conn = engine.raw_connection()
        try:
            result = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='vec_card_embeddings'"
            ).fetchone()
            assert result is not None
        finally:
            conn.close()

        engine.dispose()

    def test_init_vec_tables_idempotent(self, temp_db_path):
        engine = init_db(temp_db_path)
        register_sqlite_vec(engine)

        # Should not raise on multiple calls
        init_vec_tables(engine)
        init_vec_tables(engine)

        engine.dispose()


class TestGenerateEmbeddings:
    """Tests for embedding generation."""

    def test_generate_oracle_embeddings(self, db_with_cards):
        db_path, engine = db_with_cards

        with Session(engine) as session:
            count = generate_embeddings(session, field_source="oracle")

        # 4 cards have oracle text (Island doesn't)
        assert count == 4

        # Check vectors were inserted
        conn = engine.raw_connection()
        try:
            result = conn.execute("SELECT COUNT(*) FROM vec_card_embeddings WHERE field_source = 'oracle'").fetchone()
            assert result[0] == 4
        finally:
            conn.close()

    def test_generate_name_embeddings(self, db_with_cards):
        db_path, engine = db_with_cards

        with Session(engine) as session:
            count = generate_embeddings(session, field_source="name_only")

        # All 5 cards have names
        assert count == 5

    def test_incremental_generation(self, db_with_cards):
        db_path, engine = db_with_cards

        with Session(engine) as session:
            # First run
            count1 = generate_embeddings(session, field_source="oracle")

        with Session(engine) as session:
            # Second run should skip existing
            count2 = generate_embeddings(session, field_source="oracle")

        assert count1 == 4
        assert count2 == 0

    def test_force_regeneration(self, db_with_cards):
        db_path, engine = db_with_cards

        with Session(engine) as session:
            count1 = generate_embeddings(session, field_source="oracle")

        with Session(engine) as session:
            count2 = generate_embeddings(session, field_source="oracle", force=True)

        assert count1 == 4
        assert count2 == 4


class TestSearchSimilarCards:
    """Tests for similarity search."""

    def test_search_finds_similar_cards(self, db_with_cards):
        db_path, engine = db_with_cards

        with Session(engine) as session:
            generate_embeddings(session, field_source="oracle")

            # Search for damage spells
            results = search_similar_cards(
                session,
                query="deal damage to target",
                field_source="oracle",
                limit=3,
            )

        assert len(results) > 0
        # Lightning Bolt and Shock should be top results
        names = [card.name for card, _ in results[:2]]
        assert "Lightning Bolt" in names or "Shock" in names

    def test_search_by_embedding(self, db_with_cards):
        db_path, engine = db_with_cards

        with Session(engine) as session:
            generate_embeddings(session, field_source="oracle")

            # Get embedding for query
            query_embedding = embed_text("destroy creatures")

            results = search_similar_cards(
                session,
                embedding=query_embedding,
                field_source="oracle",
                limit=3,
            )

        assert len(results) > 0
        # Wrath of God should be in results
        names = [card.name for card, _ in results]
        assert "Wrath of God" in names

    def test_search_returns_distances(self, db_with_cards):
        db_path, engine = db_with_cards

        with Session(engine) as session:
            generate_embeddings(session, field_source="oracle")

            results = search_similar_cards(
                session,
                query="damage spell",
                field_source="oracle",
                limit=3,
            )

        # All results should have distances
        for card, distance in results:
            assert isinstance(distance, float)
            assert distance >= 0

    def test_search_name_only(self, db_with_cards):
        db_path, engine = db_with_cards

        with Session(engine) as session:
            generate_embeddings(session, field_source="name_only")

            # Typo in name (simulating OCR error)
            results = search_similar_cards(
                session,
                query="Ligthning Bolt",  # typo
                field_source="name_only",
                limit=3,
            )

        assert len(results) > 0
        # Should still find Lightning Bolt despite typo
        names = [card.name for card, _ in results]
        assert "Lightning Bolt" in names

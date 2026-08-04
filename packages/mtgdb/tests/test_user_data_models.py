"""Tests for name-keyed user data models and the user_card_interaction migration."""

import pytest
from mtgdb.models import (
    MJCard,
    UserCardInteraction,
    UserCardNote,
    UserCardTag,
    UserTagDefinition,
    UserTierList,
    UserTierListEntry,
)
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select


class TestUserCardTag:
    def test_unique_per_card_and_tag(self, initialized_db):
        _, engine = initialized_db
        with Session(engine) as session:
            session.add(UserCardTag(card_name="Lightning Bolt", tag="burn"))
            session.commit()
            session.add(UserCardTag(card_name="Lightning Bolt", tag="burn"))
            with pytest.raises(IntegrityError):
                session.commit()
            session.rollback()
            session.add(UserCardTag(card_name="Lightning Bolt", tag="removal"))
            session.commit()

    def test_definition_unique_per_tag(self, initialized_db):
        _, engine = initialized_db
        with Session(engine) as session:
            session.add(UserTagDefinition(tag="burn", description="Direct damage"))
            session.commit()
            session.add(UserTagDefinition(tag="burn", description="dup"))
            with pytest.raises(IntegrityError):
                session.commit()


class TestUserTierList:
    def test_entry_unique_per_list_and_card(self, initialized_db):
        _, engine = initialized_db
        with Session(engine) as session:
            tier_list = UserTierList(name="SOS Draft", set_code="SOS", format="PremierDraft")
            session.add(tier_list)
            session.commit()
            session.add(UserTierListEntry(tier_list_id=tier_list.id, card_name="Bolt", tier="S"))
            session.commit()
            session.add(UserTierListEntry(tier_list_id=tier_list.id, card_name="Bolt", tier="A"))
            with pytest.raises(IntegrityError):
                session.commit()

    def test_same_card_in_different_lists(self, initialized_db):
        _, engine = initialized_db
        with Session(engine) as session:
            a = UserTierList(name="A")
            b = UserTierList(name="B")
            session.add(a)
            session.add(b)
            session.commit()
            session.add(UserTierListEntry(tier_list_id=a.id, card_name="Bolt", tier="S"))
            session.add(UserTierListEntry(tier_list_id=b.id, card_name="Bolt", tier="C", position=2))
            session.commit()
            entries = session.exec(select(UserTierListEntry).where(UserTierListEntry.card_name == "Bolt")).all()
            assert {e.tier for e in entries} == {"S", "C"}


class TestUserCardNote:
    def test_multiple_notes_per_card(self, initialized_db):
        _, engine = initialized_db
        with Session(engine) as session:
            session.add(UserCardNote(card_name="Bolt", body="great"))
            session.add(UserCardNote(card_name="Bolt", kind="strategy", title="vs aggro", body="hold it"))
            session.commit()
            notes = session.exec(select(UserCardNote).where(UserCardNote.card_name == "Bolt")).all()
            assert len(notes) == 2
            assert notes[0].kind == "note"


class TestInteractionDefaults:
    def test_new_columns_have_defaults(self, initialized_db):
        _, engine = initialized_db
        with Session(engine) as session:
            session.add(MJCard(uuid="u1", name="A", set_code="TST"))
            session.add(MJCard(uuid="u2", name="B", set_code="TST"))
            session.add(
                UserCardInteraction(source_card_uuid="u1", target_card_uuid="u2", interaction_type="synergy")
            )
            session.commit()
            row = session.exec(select(UserCardInteraction)).one()
            assert row.detected_by == "manual"
            assert row.confidence == 1.0
            assert row.source_card_name is None


class TestInteractionMigration:
    """Old-shape user_card_interaction: init_db must add columns, indexes, and backfill names."""

    def test_migrates_and_backfills(self, temp_db_path):
        import sqlite3

        from mtgdb.session import close_db, init_db

        conn = sqlite3.connect(temp_db_path)
        conn.executescript("""
            CREATE TABLE mj_card (
                uuid VARCHAR PRIMARY KEY, name VARCHAR, set_code VARCHAR,
                printed_name VARCHAR, type_line VARCHAR, oracle_text VARCHAR
            );
            INSERT INTO mj_card (uuid, name, set_code) VALUES
                ('u1', 'Splinter Twin', 'ROE'), ('u2', 'Deceiver Exarch', 'NPH');
            CREATE TABLE user_card_interaction (
                id INTEGER PRIMARY KEY,
                source_card_uuid VARCHAR NOT NULL,
                target_card_uuid VARCHAR NOT NULL,
                interaction_type VARCHAR NOT NULL,
                is_bidirectional BOOLEAN NOT NULL,
                description VARCHAR,
                strength INTEGER,
                extra JSON NOT NULL,
                created_at DATETIME NOT NULL,
                updated_at DATETIME NOT NULL
            );
            INSERT INTO user_card_interaction
                (source_card_uuid, target_card_uuid, interaction_type, is_bidirectional, extra, created_at, updated_at)
            VALUES ('u1', 'u2', 'combo', 1, '{}', '2026-01-01', '2026-01-01');
        """)
        conn.commit()
        conn.close()

        close_db()
        engine = init_db(temp_db_path)

        with Session(engine) as session:
            row = session.exec(select(UserCardInteraction)).one()
            assert row.source_card_name == "Splinter Twin"
            assert row.target_card_name == "Deceiver Exarch"
            assert row.detected_by == "manual"
            assert row.confidence == 1.0

        import sqlite3 as s

        conn = s.connect(temp_db_path)
        indexes = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='index'")}
        conn.close()
        assert "ix_user_card_interaction_source_card_name" in indexes
        assert "ix_user_card_interaction_target_card_name" in indexes

        # idempotent: second init_db is a no-op
        close_db()
        init_db(temp_db_path)
        close_db()

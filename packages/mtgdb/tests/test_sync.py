"""Tests for mtgdb sync functionality."""

import json
import sqlite3
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
from mtgdb.models import MJDeck, MJDeckCard, MJKeyword, MJSet
from mtgdb.sync.download import extract_xz
from mtgdb.sync.tables import _parse_json_array, sync_decks, sync_keywords, sync_sets
from sqlmodel import Session, select


class TestParseJsonArray:
    """Tests for _parse_json_array helper."""

    def test_parse_none(self):
        """Test parsing None."""
        assert _parse_json_array(None) == []

    def test_parse_list(self):
        """Test parsing an existing list."""
        assert _parse_json_array(["a", "b"]) == ["a", "b"]

    def test_parse_json_string(self):
        """Test parsing a JSON string."""
        assert _parse_json_array('["R", "G"]') == ["R", "G"]

    def test_parse_invalid_json(self):
        """Test parsing non-JSON strings falls back to comma-splitting."""
        assert _parse_json_array("R,G") == ["R", "G"]

    def test_parse_other_type(self):
        """Test parsing non-string/list returns empty list."""
        assert _parse_json_array(123) == []


class TestSyncSets:
    """Tests for sync_sets function."""

    @pytest.fixture
    def source_db(self):
        """Create a source database with set data."""
        with tempfile.NamedTemporaryFile(suffix=".sqlite", delete=False) as f:
            source_path = Path(f.name)

        conn = sqlite3.connect(source_path)
        conn.execute("""
            CREATE TABLE sets (
                code TEXT PRIMARY KEY,
                name TEXT,
                type TEXT,
                releaseDate TEXT,
                baseSetSize INTEGER,
                totalSetSize INTEGER,
                block TEXT,
                parentCode TEXT,
                keyruneCode TEXT,
                isFoilOnly INTEGER,
                isOnlineOnly INTEGER,
                isPartialPreview INTEGER
            )
        """)
        conn.execute("""
            INSERT INTO sets VALUES
            ('TST', 'Test Set', 'expansion', '2024-01-01', 100, 120, 'Test Block', NULL, 'TST', 0, 0, 0),
            ('TST2', 'Test Set 2', 'core', '2024-06-01', 200, 250, NULL, 'TST', 'TST2', 1, 0, 0)
        """)
        conn.commit()
        conn.close()

        yield source_path
        source_path.unlink(missing_ok=True)

    def test_sync_sets(self, initialized_db, source_db):
        """Test syncing sets from source database."""
        db_path, engine = initialized_db

        with patch("mtgdb.sync.tables.get_engine", return_value=engine):
            sync_sets(source_db)

        with Session(engine) as session:
            sets = session.exec(select(MJSet)).all()
            assert len(sets) == 2

            tst = session.exec(select(MJSet).where(MJSet.code == "TST")).first()
            assert tst.name == "Test Set"
            assert tst.base_set_size == 100


class TestSyncKeywords:
    """Tests for sync_keywords function."""

    @pytest.fixture
    def keywords_file(self):
        """Create a keywords JSON file."""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as f:
            json.dump(
                {
                    "data": {
                        "keywordAbilities": ["Flying", "Haste", "Trample"],
                        "keywordActions": ["Destroy", "Exile", "Sacrifice"],
                        "abilityWords": ["Landfall", "Revolt"],
                    }
                },
                f,
            )
            keywords_path = Path(f.name)

        yield keywords_path
        keywords_path.unlink(missing_ok=True)

    def test_sync_keywords(self, initialized_db, keywords_file):
        """Test syncing keywords from JSON file."""
        db_path, engine = initialized_db

        with patch("mtgdb.sync.tables.get_engine", return_value=engine):
            sync_keywords(keywords_file)

        with Session(engine) as session:
            keywords = session.exec(select(MJKeyword)).all()
            assert len(keywords) == 8

            flying = session.exec(select(MJKeyword).where(MJKeyword.name == "Flying")).first()
            assert flying.type == "keywordAbilities"

    def test_sync_keywords_missing_file(self, initialized_db):
        """Test syncing with missing file."""
        db_path, engine = initialized_db
        missing_path = Path("/nonexistent/keywords.json")

        with patch("mtgdb.sync.tables.get_engine", return_value=engine):
            # Should not raise, just log warning
            sync_keywords(missing_path)


class TestSyncDecks:
    """Tests for sync_decks function."""

    @pytest.fixture
    def deck_dir(self):
        """Create a directory with deck JSON files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            deck_path = Path(tmpdir)

            # Create deck files
            deck1 = {
                "data": {
                    "name": "Test Deck 1",
                    "code": "TST",
                    "type": "precon",
                    "releaseDate": "2024-01-01",
                    "mainBoard": [
                        {"name": "Lightning Bolt", "count": 4, "uuid": "bolt-uuid", "manaCost": "{R}"},
                        {"name": "Mountain", "count": 20},
                    ],
                    "sideBoard": [
                        {"name": "Shock", "count": 2},
                    ],
                    "commander": [],
                }
            }

            with open(deck_path / "TestDeck1_TST.json", "w") as f:
                json.dump(deck1, f)

            yield deck_path

    def test_sync_decks(self, initialized_db, deck_dir):
        """Test syncing decks from directory."""
        db_path, engine = initialized_db

        with patch("mtgdb.sync.tables.get_engine", return_value=engine):
            sync_decks(deck_dir)

        with Session(engine) as session:
            decks = session.exec(select(MJDeck)).all()
            assert len(decks) == 1

            deck = decks[0]
            assert deck.name == "Test Deck 1"
            assert deck.main_board_count == 24
            assert deck.side_board_count == 2

            cards = session.exec(select(MJDeckCard).where(MJDeckCard.deck_uuid == deck.uuid)).all()
            assert len(cards) == 3

    def test_sync_decks_missing_dir(self, initialized_db):
        """Test syncing with missing directory."""
        db_path, engine = initialized_db
        missing_path = Path("/nonexistent/decks")

        with patch("mtgdb.sync.tables.get_engine", return_value=engine):
            # Should not raise, just log warning
            sync_decks(missing_path)


class TestDownloadFunctions:
    """Tests for download utility functions."""

    def test_extract_xz_invalid_file(self):
        """Test extracting invalid xz file."""
        with tempfile.NamedTemporaryFile(suffix=".xz", delete=False) as src:
            src.write(b"not valid xz data")
            src_path = Path(src.name)

        with tempfile.NamedTemporaryFile(suffix=".sqlite", delete=False) as dest:
            dest_path = Path(dest.name)

        result = extract_xz(src_path, dest_path)
        assert result is False

        src_path.unlink(missing_ok=True)
        dest_path.unlink(missing_ok=True)

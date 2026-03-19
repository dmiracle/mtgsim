"""Tests for Scryfall oracle tag sync."""

import json
import tempfile
from pathlib import Path

import pytest
from mtgdb.models import MJCardTag
from mtgdb.sync.scryfall import sync_tags
from sqlmodel import Session, SQLModel, create_engine, select


@pytest.fixture
def tmp_engine(tmp_path):
    """Create a temporary SQLite database for testing."""
    db_path = tmp_path / "test.sqlite"
    engine = create_engine(f"sqlite:///{db_path}", echo=False)
    SQLModel.metadata.create_all(engine)
    return engine


@pytest.fixture
def sample_tags_file():
    """Create a temporary tags JSON file for testing."""
    data = {
        "mana-dork": ["Llanowar Elves", "Birds of Paradise", "Elvish Mystic"],
        "ramp": ["Llanowar Elves", "Cultivate", "Kodama's Reach"],
        "removal": ["Lightning Bolt", "Swords to Plowshares"],
    }
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(data, f)
        return Path(f.name)


class TestSyncTags:
    """Tests for sync_tags function."""

    def test_sync_tags_populates_table(self, sample_tags_file, tmp_engine, monkeypatch):
        """sync_tags inserts rows into mj_card_tag."""
        monkeypatch.setattr("mtgdb.sync.scryfall.get_engine", lambda: tmp_engine)
        sync_tags(sample_tags_file)

        with Session(tmp_engine) as session:
            results = session.exec(select(MJCardTag)).all()
            assert len(results) == 8  # 3 + 3 + 2

    def test_sync_tags_correct_data(self, sample_tags_file, tmp_engine, monkeypatch):
        """sync_tags stores correct card_name and tag pairs."""
        monkeypatch.setattr("mtgdb.sync.scryfall.get_engine", lambda: tmp_engine)
        sync_tags(sample_tags_file)

        with Session(tmp_engine) as session:
            dorks = session.exec(select(MJCardTag).where(MJCardTag.tag == "mana-dork")).all()
            names = {t.card_name for t in dorks}
            assert names == {"Llanowar Elves", "Birds of Paradise", "Elvish Mystic"}

    def test_sync_tags_clears_old_data(self, sample_tags_file, tmp_engine, monkeypatch):
        """sync_tags replaces existing data on re-sync."""
        monkeypatch.setattr("mtgdb.sync.scryfall.get_engine", lambda: tmp_engine)
        sync_tags(sample_tags_file)
        sync_tags(sample_tags_file)

        with Session(tmp_engine) as session:
            results = session.exec(select(MJCardTag)).all()
            assert len(results) == 8

    def test_sync_tags_missing_file(self, tmp_engine, monkeypatch):
        """sync_tags handles missing file gracefully."""
        monkeypatch.setattr("mtgdb.sync.scryfall.get_engine", lambda: tmp_engine)
        sync_tags(Path("/nonexistent/file.json"))

    def test_sync_tags_card_in_multiple_tags(self, sample_tags_file, tmp_engine, monkeypatch):
        """A card can appear in multiple tags."""
        monkeypatch.setattr("mtgdb.sync.scryfall.get_engine", lambda: tmp_engine)
        sync_tags(sample_tags_file)

        with Session(tmp_engine) as session:
            llanowar = session.exec(select(MJCardTag).where(MJCardTag.card_name == "Llanowar Elves")).all()
            tags = {t.tag for t in llanowar}
            assert tags == {"mana-dork", "ramp"}

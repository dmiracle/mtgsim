"""Tests for 17Lands CSV ingestion idempotency and card stat computation."""

import csv
import gzip
from pathlib import Path

import mtgdb.session
import pytest
from mtgdb.models import MJCard
from mtgdb.sync.seventeenlands import ingest_draft_csv, ingest_game_csv
from mtgdb.sync.seventeenlands_stats import compute_card_stats, store_card_ratings
from sqlalchemy import text
from sqlmodel import Session

CARDS = ["Ash Zealot", "Boros Elite", "Cloudfin Raptor"]

DRAFT_HEADER = (
    ["expansion", "event_type", "draft_id", "pack_number", "pick_number", "pick"]
    + [f"pack_card_{c}" for c in CARDS]
    + [f"pool_{c}" for c in CARDS]
)

# (draft_id, pack, pick_number, pick, pack contents A/B/C, pool A/B/C)
DRAFT_ROWS = [
    ("d1", 0, 0, "Ash Zealot", 1, 1, 0, 0, 0, 0),
    ("d1", 0, 1, "Boros Elite", 0, 1, 0, 1, 0, 0),
    ("d2", 0, 0, "Cloudfin Raptor", 1, 0, 1, 0, 0, 0),
]

GAME_HEADER = (
    ["expansion", "event_type", "draft_id", "build_index", "game_number", "won"]
    + [f"opening_hand_{c}" for c in CARDS]
    + [f"deck_{c}" for c in CARDS]
    + [f"drawn_{c}" for c in CARDS]
    + [f"sideboard_{c}" for c in CARDS]
)

# (draft_id, build, game, won, oh A/B/C, deck A/B/C, drawn A/B/C, sideboard A/B/C)
GAME_ROWS = [
    ("d1", 0, 1, "True", 1, 0, 0, 2, 1, 0, 0, 1, 0, 0, 0, 1),
    ("d1", 0, 2, "False", 0, 1, 0, 2, 1, 0, 0, 0, 0, 0, 0, 1),
    ("d2", 0, 1, "True", 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0),
]


def _write_csv_gz(path: Path, header: list[str], rows: list[tuple]) -> Path:
    with gzip.open(path, "wt", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        for row in rows:
            writer.writerow(["TST", "PremierDraft", *row])
    return path


@pytest.fixture
def seventeenlands_db(initialized_db, monkeypatch, tmp_path):
    """Temp DB wired into get_session, plus draft/game fixture CSVs."""
    _, engine = initialized_db
    monkeypatch.setattr(mtgdb.session, "_engine", engine)

    with Session(engine) as session:
        session.add(MJCard(uuid="u1", name="Ash Zealot", set_code="TST", colors=["R"], rarity="rare"))
        session.commit()

    draft_csv = _write_csv_gz(tmp_path / "draft.csv.gz", DRAFT_HEADER, DRAFT_ROWS)
    game_csv = _write_csv_gz(tmp_path / "game.csv.gz", GAME_HEADER, GAME_ROWS)
    return engine, draft_csv, game_csv


def _counts(engine, table: str) -> int:
    with engine.connect() as conn:
        return conn.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()


class TestIngestIdempotency:
    def test_draft_reingest_does_not_duplicate(self, seventeenlands_db):
        engine, draft_csv, _ = seventeenlands_db
        assert ingest_draft_csv(draft_csv) == 3
        assert ingest_draft_csv(draft_csv) == 3
        assert _counts(engine, "mj_17l_draft_pick") == 3
        assert _counts(engine, "mj_17l_draft_card") == 6

    def test_game_reingest_does_not_duplicate(self, seventeenlands_db):
        engine, _, game_csv = seventeenlands_db
        assert ingest_game_csv(game_csv) == 3
        assert ingest_game_csv(game_csv) == 3
        assert _counts(engine, "mj_17l_game") == 3
        assert _counts(engine, "mj_17l_game_card") == 7


class TestComputeCardStats:
    @pytest.fixture
    def stats(self, seventeenlands_db):
        engine, draft_csv, game_csv = seventeenlands_db
        ingest_draft_csv(draft_csv)
        ingest_game_csv(game_csv)
        assert compute_card_stats("TST", "PremierDraft") == 3
        with engine.connect() as conn:
            rows = conn.execute(text("SELECT * FROM mj_17l_card_stat")).mappings().all()
        return {r["card_name"]: r for r in rows}

    def test_draft_metrics(self, stats):
        a, b, c = stats["Ash Zealot"], stats["Boros Elite"], stats["Cloudfin Raptor"]
        assert (a["pick_count"], a["avg_pick"]) == (1, 1.0)
        assert (b["pick_count"], b["avg_pick"]) == (1, 2.0)
        assert (c["pick_count"], c["avg_pick"]) == (1, 1.0)
        # B was seen at picks 0 and 1 of the same pack: one sighting, last seen at 2
        assert (a["seen_count"], a["avg_seen"]) == (2, 1.0)
        assert (b["seen_count"], b["avg_seen"]) == (1, 2.0)
        assert (c["seen_count"], c["avg_seen"]) == (1, 1.0)

    def test_game_metrics(self, stats):
        a = stats["Ash Zealot"]
        assert (a["pool_count"], a["game_count"], a["win_rate"], a["play_rate"]) == (2, 2, 0.5, 1.0)
        assert (a["opening_hand_game_count"], a["opening_hand_win_rate"]) == (1, 1.0)
        assert (a["drawn_game_count"], a["drawn_win_rate"]) == (0, None)
        assert (a["ever_drawn_game_count"], a["ever_drawn_win_rate"]) == (1, 1.0)
        assert (a["never_drawn_game_count"], a["never_drawn_win_rate"]) == (1, 0.0)
        assert a["drawn_improvement_win_rate"] == 1.0

        b = stats["Boros Elite"]
        assert (b["game_count"], b["win_rate"]) == (2, 0.5)
        assert (b["drawn_game_count"], b["drawn_win_rate"]) == (1, 1.0)
        assert (b["ever_drawn_game_count"], b["ever_drawn_win_rate"]) == (2, 0.5)
        assert (b["never_drawn_game_count"], b["never_drawn_win_rate"]) == (0, None)
        assert b["drawn_improvement_win_rate"] is None

        c = stats["Cloudfin Raptor"]
        assert (c["pool_count"], c["game_count"], c["win_rate"]) == (3, 1, 1.0)
        assert c["play_rate"] == pytest.approx(1 / 3)

    def test_identity_enrichment(self, stats):
        assert (stats["Ash Zealot"]["color"], stats["Ash Zealot"]["rarity"]) == ("R", "rare")
        assert stats["Boros Elite"]["color"] is None

    def test_recompute_replaces_rows(self, seventeenlands_db):
        engine, draft_csv, game_csv = seventeenlands_db
        ingest_draft_csv(draft_csv)
        ingest_game_csv(game_csv)
        compute_card_stats("TST", "PremierDraft")
        compute_card_stats("TST", "PremierDraft")
        assert _counts(engine, "mj_17l_card_stat") == 3


RATINGS_PAYLOAD = [
    {
        "name": "Ash Zealot",
        "mtga_id": 12345,
        "color": "R",
        "rarity": "rare",
        "seen_count": 1000,
        "avg_seen": 4.2,
        "pick_count": 400,
        "avg_pick": 3.8,
        "game_count": 900,
        "pool_count": 1100,
        "play_rate": 0.818,
        "win_rate": 0.57,
        "opening_hand_game_count": 150,
        "opening_hand_win_rate": 0.6,
        "drawn_game_count": 200,
        "drawn_win_rate": 0.58,
        "ever_drawn_game_count": 350,
        "ever_drawn_win_rate": 0.59,
        "never_drawn_game_count": 550,
        "never_drawn_win_rate": 0.55,
        "drawn_improvement_win_rate": 0.04,
        "url": "https://cards.scryfall.io/large/x.jpg",
        "types": ["Creature - Human Warrior"],
    },
    {
        "name": "Summon: Bahamut",
        "mtga_id": 95853,
        "color": "",
        "rarity": "mythic",
        "seen_count": 0,
        "avg_seen": None,
        "pick_count": 0,
        "avg_pick": None,
        "game_count": 0,
        "pool_count": 0,
        "play_rate": None,
        "win_rate": None,
        "opening_hand_game_count": 0,
        "opening_hand_win_rate": None,
        "drawn_game_count": 0,
        "drawn_win_rate": None,
        "ever_drawn_game_count": 0,
        "ever_drawn_win_rate": None,
        "never_drawn_game_count": 0,
        "never_drawn_win_rate": None,
        "drawn_improvement_win_rate": None,
    },
]


class TestStoreCardRatings:
    def test_store_and_restore_idempotent(self, seventeenlands_db):
        engine, _, _ = seventeenlands_db
        assert store_card_ratings(RATINGS_PAYLOAD, "TST", "PremierDraft", "2026-07-21") == 2
        assert store_card_ratings(RATINGS_PAYLOAD, "TST", "PremierDraft", "2026-07-21") == 2
        assert _counts(engine, "mj_17l_card_stat") == 2

    def test_stored_values(self, seventeenlands_db):
        engine, _, _ = seventeenlands_db
        store_card_ratings(RATINGS_PAYLOAD, "TST", "PremierDraft", "2026-07-21")
        with engine.connect() as conn:
            rows = conn.execute(text("SELECT * FROM mj_17l_card_stat ORDER BY card_name")).mappings().all()
        a, b = rows
        assert (a["card_name"], a["source"], a["mtga_id"]) == ("Ash Zealot", "17lands", 12345)
        assert (a["avg_seen"], a["ever_drawn_win_rate"], a["dataset_last_updated"]) == (4.2, 0.59, "2026-07-21")
        assert (b["card_name"], b["game_count"], b["win_rate"]) == ("Summon: Bahamut", 0, None)

    def test_sources_coexist(self, seventeenlands_db):
        engine, draft_csv, game_csv = seventeenlands_db
        ingest_draft_csv(draft_csv)
        ingest_game_csv(game_csv)
        compute_card_stats("TST", "PremierDraft")
        store_card_ratings(RATINGS_PAYLOAD, "TST", "PremierDraft", "2026-07-21")
        compute_card_stats("TST", "PremierDraft")
        with engine.connect() as conn:
            by_source = dict(
                conn.execute(text("SELECT source, COUNT(*) FROM mj_17l_card_stat GROUP BY source")).fetchall()
            )
        assert by_source == {"public_dataset": 3, "17lands": 2}

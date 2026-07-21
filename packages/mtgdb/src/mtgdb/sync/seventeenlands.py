"""17Lands public dataset sync: fetch index from Prismic, download CSV files, ingest CSVs."""

import csv
import gzip
import logging
import tarfile
import time
from datetime import UTC, datetime
from io import TextIOWrapper
from itertools import chain
from pathlib import Path

import requests
from sqlalchemy import text
from sqlmodel import select

from mtgdb.config import PRISMIC_API_URL, SEVENTEENLANDS_DIR
from mtgdb.models import (
    MJ17LDataset,
    MJ17LDraftCard,
    MJ17LDraftPick,
    MJ17LGame,
    MJ17LGameCard,
    MJ17LReplay,
    MJ17LReplayTurn,
)
from mtgdb.session import get_session
from mtgdb.sync.download import download

logger = logging.getLogger(__name__)

# Pause between consecutive S3 downloads; 17Lands rate-limits bulk downloaders.
DOWNLOAD_DELAY = 3.0


def _extract_url(rich_text_field: list[dict]) -> str | None:
    """Extract hyperlink URL from Prismic rich text field."""
    if not rich_text_field:
        return None
    for block in rich_text_field:
        for span in block.get("spans", []):
            if span.get("type") == "hyperlink":
                return span["data"]["url"]
    return None


def _extract_text(rich_text_field: list[dict]) -> str | None:
    """Extract plain text from Prismic rich text field."""
    if not rich_text_field:
        return None
    return rich_text_field[0].get("text")


def fetch_dataset_index() -> list[dict]:
    """Fetch the 17Lands public dataset index from Prismic CMS.

    Returns list of dicts with keys: expansion, format, last_updated,
    draft_data_url, game_data_url, replay_data_url.
    """
    logger.info("Fetching 17Lands dataset index from Prismic...")

    # Get master ref
    api_resp = requests.get(PRISMIC_API_URL, timeout=30)
    api_resp.raise_for_status()
    api_data = api_resp.json()
    master_ref = next(r["ref"] for r in api_data["refs"] if r["isMasterRef"])

    # Query public-data document
    query_url = (
        f'{PRISMIC_API_URL}/documents/search?ref={master_ref}&q=[[at(document.type,"public-data")]]&pageSize=100'
    )
    resp = requests.get(query_url, timeout=30)
    resp.raise_for_status()
    results = resp.json()["results"]

    if not results:
        logger.warning("No public-data document found in Prismic")
        return []

    raw_datasets = results[0]["data"]["datasets"]
    datasets = []
    for ds in raw_datasets:
        datasets.append(
            {
                "expansion": _extract_text(ds.get("expansion", [])),
                "format": _extract_text(ds.get("format", [])),
                "last_updated": _extract_text(ds.get("last_updated", [])),
                "draft_data_url": _extract_url(ds.get("draft_data", [])),
                "game_data_url": _extract_url(ds.get("game_data", [])),
                "replay_data_url": _extract_url(ds.get("replay_data", [])),
            }
        )

    logger.info(f"Found {len(datasets)} datasets in 17Lands index")
    return datasets


def sync_dataset_metadata(datasets: list[dict] | None = None) -> int:
    """Upsert 17Lands dataset metadata into the database.

    Returns count of datasets synced.
    """
    if datasets is None:
        datasets = fetch_dataset_index()

    now = datetime.now(UTC).isoformat()

    with get_session() as session:
        for ds in datasets:
            exp = ds["expansion"]
            fmt = ds["format"]
            if not exp or not fmt:
                continue

            existing = session.exec(
                select(MJ17LDataset).where((MJ17LDataset.expansion == exp) & (MJ17LDataset.format == fmt))
            ).first()

            if existing:
                existing.last_updated = ds["last_updated"]
                existing.draft_data_url = ds["draft_data_url"]
                existing.game_data_url = ds["game_data_url"]
                existing.replay_data_url = ds["replay_data_url"]
                existing.synced_at = now
                session.add(existing)
            else:
                record = MJ17LDataset(
                    expansion=exp,
                    format=fmt,
                    last_updated=ds["last_updated"],
                    draft_data_url=ds["draft_data_url"],
                    game_data_url=ds["game_data_url"],
                    replay_data_url=ds["replay_data_url"],
                    synced_at=now,
                )
                session.add(record)

        session.commit()

    logger.info(f"Synced {len(datasets)} dataset metadata records")
    return len(datasets)


def _url_to_local_path(url: str) -> Path:
    """Convert an S3 URL to a local file path under SEVENTEENLANDS_DIR."""
    # URL: https://17lands-public.s3.amazonaws.com/analysis_data/draft_data/draft_data_public.STX.PremierDraft.csv.gz
    # Path: ~/.mtgsim/reference/17lands/draft_data/draft_data_public.STX.PremierDraft.csv.gz
    parts = url.split("/analysis_data/")
    if len(parts) != 2:
        return SEVENTEENLANDS_DIR / url.split("/")[-1]
    return SEVENTEENLANDS_DIR / parts[1]


def download_dataset_files(
    expansion: str | None = None,
    format: str | None = None,
    force: bool = False,
    data_types: list[str] | None = None,
) -> int:
    """Download 17Lands CSV files for matching datasets.

    Returns count of files downloaded.
    """
    if data_types is None:
        data_types = ["draft", "game", "replay"]
    downloaded = 0

    with get_session() as session:
        query = select(MJ17LDataset)
        if expansion:
            query = query.where(MJ17LDataset.expansion == expansion)
        if format:
            query = query.where(MJ17LDataset.format == format)

        datasets = session.exec(query).all()

        for ds in datasets:
            for data_type, url_attr, flag_attr in [
                ("draft_data", "draft_data_url", "draft_data_downloaded"),
                ("game_data", "game_data_url", "game_data_downloaded"),
                ("replay_data", "replay_data_url", "replay_data_downloaded"),
            ]:
                if data_type.removesuffix("_data") not in data_types:
                    continue
                url = getattr(ds, url_attr)
                if not url:
                    continue

                version_attr = f"{data_type}_downloaded_version"
                already_downloaded = getattr(ds, flag_attr)
                if already_downloaded and not force:
                    if ds.last_updated and getattr(ds, version_attr) != ds.last_updated:
                        logger.warning(
                            f"{ds.expansion}/{ds.format} {data_type} is stale "
                            f"(downloaded {getattr(ds, version_attr)}, index has {ds.last_updated}); "
                            "use --force to re-download"
                        )
                    continue

                dest = _url_to_local_path(url)
                if dest.exists() and not force:
                    setattr(ds, flag_attr, True)
                    session.add(ds)
                    continue

                if downloaded:
                    time.sleep(DOWNLOAD_DELAY)
                logger.info(f"Downloading {ds.expansion}/{ds.format} {data_type}...")
                if download(url, dest):
                    setattr(ds, flag_attr, True)
                    setattr(ds, version_attr, ds.last_updated)
                    session.add(ds)
                    downloaded += 1

        session.commit()

    logger.info(f"Downloaded {downloaded} files")
    return downloaded


# =============================================================================
# CSV Ingestion
# =============================================================================

BATCH_SIZE = 1000


def _open_csv(path: Path):
    """Open a .csv.gz file (handles both plain gzip and tar-wrapped gzip)."""
    # Check if the gzip contains a tar archive by reading raw bytes
    with gzip.open(path, "rb") as f:
        header = f.read(262)

    is_tar = len(header) >= 262 and header[257:262] == b"ustar"

    if is_tar:
        tf = tarfile.open(path, "r:gz")
        members = tf.getmembers()
        csv_member = next((m for m in members if m.name.endswith(".csv")), members[0])
        f = tf.extractfile(csv_member)
        return TextIOWrapper(f, encoding="utf-8")
    else:
        return gzip.open(path, "rt", encoding="utf-8")


def _safe_int(val: str) -> int | None:
    if not val or val == "":
        return None
    try:
        return int(float(val))
    except (ValueError, TypeError):
        return None


def _safe_float(val: str) -> float | None:
    if not val or val == "":
        return None
    try:
        return float(val)
    except (ValueError, TypeError):
        return None


def _safe_bool(val: str) -> bool | None:
    if not val or val == "":
        return None
    return val.lower() in ("true", "1", "yes")


def _clear_rows(session, child_sql: str, parent_sql: str, expansion: str, event_type: str) -> None:
    """Delete previously ingested rows for one dataset so re-ingestion is idempotent."""
    params = {"expansion": expansion, "event_type": event_type}
    conn = session.connection()
    child_deleted = conn.execute(text(child_sql), params).rowcount
    parent_deleted = conn.execute(text(parent_sql), params).rowcount
    session.commit()
    if parent_deleted:
        logger.info(f"Cleared {parent_deleted:,} existing rows (+{child_deleted:,} card/turn rows) before re-ingest")


def _clear_draft_rows(session, expansion: str, event_type: str) -> None:
    _clear_rows(
        session,
        "DELETE FROM mj_17l_draft_card WHERE draft_id IN "
        "(SELECT draft_id FROM mj_17l_draft_pick WHERE expansion = :expansion AND event_type = :event_type)",
        "DELETE FROM mj_17l_draft_pick WHERE expansion = :expansion AND event_type = :event_type",
        expansion,
        event_type,
    )


def _clear_game_rows(session, expansion: str, event_type: str) -> None:
    _clear_rows(
        session,
        "DELETE FROM mj_17l_game_card WHERE draft_id IN "
        "(SELECT draft_id FROM mj_17l_game WHERE expansion = :expansion AND event_type = :event_type)",
        "DELETE FROM mj_17l_game WHERE expansion = :expansion AND event_type = :event_type",
        expansion,
        event_type,
    )


def _clear_replay_rows(session, expansion: str, format: str) -> None:
    _clear_rows(
        session,
        "DELETE FROM mj_17l_replay_turn WHERE draft_id IN "
        "(SELECT draft_id FROM mj_17l_replay WHERE expansion = :expansion AND format = :event_type)",
        "DELETE FROM mj_17l_replay WHERE expansion = :expansion AND format = :event_type",
        expansion,
        format,
    )


def ingest_draft_csv(path: Path) -> int:
    """Ingest a draft data CSV into mj_17l_draft_pick and mj_17l_draft_card tables."""
    logger.info(f"Ingesting draft data from {path.name}...")
    row_count = 0

    f = _open_csv(path)
    reader = csv.DictReader(f)

    pack_card_cols = [h for h in reader.fieldnames if h.startswith("pack_card_")]
    pool_cols = [h for h in reader.fieldnames if h.startswith("pool_")]
    card_names = [h.removeprefix("pack_card_") for h in pack_card_cols]

    pick_batch = []
    card_batch = []

    with get_session() as session:
        first_row = next(reader, None)
        if first_row is None:
            f.close()
            return 0
        _clear_draft_rows(session, first_row["expansion"], first_row["event_type"])

        for row in chain([first_row], reader):
            draft_id = row["draft_id"]
            pack_number = _safe_int(row["pack_number"])
            pick_number = _safe_int(row["pick_number"])

            pick = MJ17LDraftPick(
                expansion=row["expansion"],
                event_type=row["event_type"],
                draft_id=draft_id,
                draft_time=row.get("draft_time"),
                user_win_rate_bucket=_safe_float(row.get("user_match_win_rate_bucket")),
                user_n_matches_bucket=_safe_int(row.get("user_n_matches_bucket")),
                event_match_wins=_safe_int(row.get("event_match_wins")),
                event_match_losses=_safe_int(row.get("event_match_losses")),
                pack_number=pack_number,
                pick_number=pick_number,
                pick=row.get("pick"),
                pick_maindeck_rate=_safe_float(row.get("pick_maindeck_rate")),
                pick_sideboard_in_rate=_safe_float(row.get("pick_sideboard_in_rate")),
            )
            pick_batch.append(pick)

            for card_name, pack_col, pool_col in zip(card_names, pack_card_cols, pool_cols, strict=True):
                in_pack_val = _safe_int(row.get(pack_col))
                pool_val = _safe_int(row.get(pool_col))
                if in_pack_val or pool_val:
                    card_batch.append(
                        MJ17LDraftCard(
                            draft_id=draft_id,
                            pack_number=pack_number,
                            pick_number=pick_number,
                            card_name=card_name,
                            in_pack=bool(in_pack_val),
                            pool_count=pool_val or 0,
                        )
                    )

            row_count += 1
            if row_count % BATCH_SIZE == 0:
                session.add_all(pick_batch)
                session.add_all(card_batch)
                session.commit()
                pick_batch.clear()
                card_batch.clear()
                if row_count % 10000 == 0:
                    logger.info(f"  draft: {row_count:,} rows ingested...")

        if pick_batch:
            session.add_all(pick_batch)
            session.add_all(card_batch)
            session.commit()

    f.close()
    logger.info(f"Draft ingestion complete: {row_count:,} picks")
    return row_count


def ingest_game_csv(path: Path) -> int:
    """Ingest a game data CSV into mj_17l_game and mj_17l_game_card tables."""
    logger.info(f"Ingesting game data from {path.name}...")
    row_count = 0

    f = _open_csv(path)
    reader = csv.DictReader(f)

    oh_cols = [h for h in reader.fieldnames if h.startswith("opening_hand_")]
    deck_cols = [h for h in reader.fieldnames if h.startswith("deck_")]
    drawn_cols = [h for h in reader.fieldnames if h.startswith("drawn_")]
    sb_cols = [h for h in reader.fieldnames if h.startswith("sideboard_")]
    card_names = [h.removeprefix("opening_hand_") for h in oh_cols]

    card_batch = []

    game_batch = []

    with get_session() as session:
        first_row = next(reader, None)
        if first_row is None:
            f.close()
            return 0
        _clear_game_rows(session, first_row["expansion"], first_row["event_type"])

        for row in chain([first_row], reader):
            draft_id = row["draft_id"]
            build_index = _safe_int(row.get("build_index"))
            game_number = _safe_int(row.get("game_number"))

            game_batch.append(
                MJ17LGame(
                    expansion=row["expansion"],
                    event_type=row["event_type"],
                    draft_id=draft_id,
                    build_index=build_index,
                    draft_time=row.get("draft_time"),
                    game_number=game_number,
                    rank=row.get("rank"),
                    user_win_rate_bucket=_safe_float(row.get("user_win_rate_bucket")),
                    user_n_games_bucket=_safe_int(row.get("user_n_games_bucket")),
                    on_play=_safe_bool(row.get("on_play")),
                    num_mulligans=_safe_int(row.get("num_mulligans")),
                    opp_num_mulligans=_safe_int(row.get("opp_num_mulligans")),
                    opp_colors=row.get("opp_colors"),
                    num_turns=_safe_int(row.get("num_turns")),
                    won=_safe_bool(row.get("won")),
                )
            )

            for i, card_name in enumerate(card_names):
                oh = _safe_int(row.get(oh_cols[i]))
                dk = _safe_int(row.get(deck_cols[i]))
                dr = _safe_int(row.get(drawn_cols[i]))
                sb = _safe_int(row.get(sb_cols[i]))
                if oh or dk or dr or sb:
                    card_batch.append(
                        MJ17LGameCard(
                            draft_id=draft_id,
                            build_index=build_index,
                            game_number=game_number,
                            card_name=card_name,
                            in_opening_hand=oh or 0,
                            in_deck=dk or 0,
                            drawn=dr or 0,
                            sideboarded=sb or 0,
                        )
                    )

            row_count += 1
            if row_count % BATCH_SIZE == 0:
                session.add_all(game_batch)
                session.add_all(card_batch)
                session.commit()
                game_batch.clear()
                card_batch.clear()
                if row_count % 10000 == 0:
                    logger.info(f"  game: {row_count:,} rows ingested...")

        if game_batch:
            session.add_all(game_batch)
            session.add_all(card_batch)
            session.commit()

    f.close()
    logger.info(f"Game ingestion complete: {row_count:,} games")
    return row_count


_REPLAY_TURN_METRICS = [
    "cards_drawn",
    "cards_discarded",
    "lands_played",
    "cards_foretold",
    "creatures_cast",
    "non_creatures_cast",
    "user_instants_sorceries_cast",
    "oppo_instants_sorceries_cast",
    "user_abilities",
    "oppo_abilities",
    "user_cards_learned",
    "oppo_cards_learned",
    "creatures_attacked",
    "creatures_blocked",
    "creatures_unblocked",
    "creatures_blocking",
    "player_combat_damage_dealt",
    "user_creatures_killed_combat",
    "oppo_creatures_killed_combat",
    "user_creatures_killed_non_combat",
    "oppo_creatures_killed_non_combat",
    "user_mana_spent",
    "oppo_mana_spent",
    "eot_user_cards_in_hand",
    "eot_oppo_cards_in_hand",
    "eot_user_lands_in_play",
    "eot_oppo_lands_in_play",
    "eot_user_creatures_in_play",
    "eot_oppo_creatures_in_play",
    "eot_user_non_creatures_in_play",
    "eot_oppo_non_creatures_in_play",
    "eot_user_life",
    "eot_oppo_life",
]

_INT_METRICS = {
    "player_combat_damage_dealt",
    "user_mana_spent",
    "oppo_mana_spent",
    "eot_user_life",
    "eot_oppo_life",
}


def ingest_replay_csv(path: Path) -> int:
    """Ingest a replay data CSV into mj_17l_replay and mj_17l_replay_turn tables."""
    logger.info(f"Ingesting replay data from {path.name}...")
    row_count = 0

    f = _open_csv(path)
    reader = csv.DictReader(f)

    replay_batch = []
    turn_batch = []

    with get_session() as session:
        first_row = next(reader, None)
        if first_row is None:
            f.close()
            return 0
        if first_row.get("expansion") and first_row.get("format"):
            _clear_replay_rows(session, first_row["expansion"], first_row["format"])

        for row in chain([first_row], reader):
            replay = MJ17LReplay(
                expansion=row.get("expansion"),
                format=row.get("format"),
                draft_id=row.get("draft_id"),
                history_id=row.get("history_id"),
                time=row.get("time"),
                game_index=_safe_int(row.get("game_index")),
                user_rank=row.get("user_rank"),
                oppo_rank=row.get("oppo_rank"),
                user_deck_colors=row.get("user_deck_colors"),
                oppo_deck_colors=row.get("oppo_deck_colors"),
                user_mulligans=_safe_int(row.get("user_mulligans")),
                oppo_mulligans=_safe_int(row.get("oppo_mulligans")),
                on_play=_safe_bool(row.get("on_play")),
                turns=_safe_int(row.get("turns")),
                won=_safe_bool(row.get("won")),
                missing_diffs=row.get("missing_diffs"),
                user_total_cards_drawn=_safe_int(row.get("user_total_cards_drawn")),
                user_total_cards_discarded=_safe_int(row.get("user_total_cards_discarded")),
                user_total_lands_played=_safe_int(row.get("user_total_lands_played")),
                user_total_cards_foretold=_safe_int(row.get("user_total_cards_foretold")),
                user_total_creatures_cast=_safe_int(row.get("user_total_creatures_cast")),
                user_total_non_creatures_cast=_safe_int(row.get("user_total_non_creatures_cast")),
                user_total_instants_sorceries_cast=_safe_int(row.get("user_total_instants_sorceries_cast")),
                user_total_cards_learned=_safe_int(row.get("user_total_cards_learned")),
                user_total_mana_spent=_safe_int(row.get("user_total_mana_spent")),
                oppo_total_cards_drawn=_safe_int(row.get("oppo_total_cards_drawn")),
                oppo_total_cards_discarded=_safe_int(row.get("oppo_total_cards_discarded")),
                oppo_total_lands_played=_safe_int(row.get("oppo_total_lands_played")),
                oppo_total_cards_foretold=_safe_int(row.get("oppo_total_cards_foretold")),
                oppo_total_creatures_cast=_safe_int(row.get("oppo_total_creatures_cast")),
                oppo_total_non_creatures_cast=_safe_int(row.get("oppo_total_non_creatures_cast")),
                oppo_total_instants_sorceries_cast=_safe_int(row.get("oppo_total_instants_sorceries_cast")),
                oppo_total_cards_learned=_safe_int(row.get("oppo_total_cards_learned")),
                oppo_total_mana_spent=_safe_int(row.get("oppo_total_mana_spent")),
            )
            replay_batch.append(replay)

            draft_id = row.get("draft_id")
            game_index = _safe_int(row.get("game_index"))
            max_turns = _safe_int(row.get("turns")) or 0
            for turn_num in range(1, min(max_turns + 1, 31)):
                for player in ("user", "oppo"):
                    prefix = f"{player}_turn_{turn_num}_"
                    has_data = any(row.get(prefix + m) for m in _REPLAY_TURN_METRICS)
                    if not has_data:
                        continue
                    turn_data = {
                        "draft_id": draft_id,
                        "game_index": game_index,
                        "turn_number": turn_num,
                        "player": player,
                    }
                    for metric in _REPLAY_TURN_METRICS:
                        val = row.get(prefix + metric, "")
                        if metric in _INT_METRICS:
                            turn_data[metric] = _safe_int(val)
                        else:
                            turn_data[metric] = val if val else None
                    turn_batch.append(MJ17LReplayTurn(**turn_data))

            row_count += 1
            if row_count % BATCH_SIZE == 0:
                session.add_all(replay_batch)
                session.add_all(turn_batch)
                session.commit()
                replay_batch.clear()
                turn_batch.clear()
                if row_count % 10000 == 0:
                    logger.info(f"  replay: {row_count:,} rows ingested...")

        if replay_batch:
            session.add_all(replay_batch)
            session.add_all(turn_batch)
            session.commit()

    f.close()
    logger.info(f"Replay ingestion complete: {row_count:,} replays")
    return row_count


def ingest_datasets(
    expansion: str | None = None,
    format: str | None = None,
    data_types: list[str] | None = None,
) -> dict[str, int]:
    """Ingest downloaded CSV files into normalized tables.

    Returns dict of {data_type: rows_ingested}.
    """
    if data_types is None:
        data_types = ["draft", "game", "replay"]

    results = {}

    with get_session() as session:
        query = select(MJ17LDataset)
        if expansion:
            query = query.where(MJ17LDataset.expansion == expansion)
        if format:
            query = query.where(MJ17LDataset.format == format)
        datasets = session.exec(query).all()

    for ds in datasets:
        for dtype, url_attr, flag_attr, ingested_attr, ingest_fn in [
            ("draft", "draft_data_url", "draft_data_downloaded", "draft_data_ingested_at", ingest_draft_csv),
            ("game", "game_data_url", "game_data_downloaded", "game_data_ingested_at", ingest_game_csv),
            ("replay", "replay_data_url", "replay_data_downloaded", "replay_data_ingested_at", ingest_replay_csv),
        ]:
            if dtype not in data_types:
                continue
            url = getattr(ds, url_attr)
            if not url or not getattr(ds, flag_attr):
                continue

            path = _url_to_local_path(url)
            if not path.exists():
                logger.warning(f"File not found: {path}")
                continue

            key = f"{ds.expansion}.{ds.format}.{dtype}"
            rows = ingest_fn(path)
            results[key] = rows

            with get_session() as session:
                record = session.get(MJ17LDataset, ds.id)
                setattr(record, ingested_attr, datetime.now(UTC).isoformat())
                session.add(record)
                session.commit()

    return results

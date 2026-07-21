"""Compute 17Lands-style per-card statistics from ingested public dataset tables.

Metric semantics follow https://www.17lands.com/metrics_definitions:
    ALSA    average pick number (1-based) at which a card was last seen in a pack
    ATA     average pick number (1-based) at which a card was taken
    GP WR   win rate of games with the card in the maindeck
    OH WR   win rate of games with the card in the opening hand
    GD WR   win rate of games where the card was drawn after the opening hand
    GIH WR  win rate of games where the card was in hand at any point (OH or drawn)
    GNS WR  win rate of games with the card in the maindeck but never in hand
    IWD     GIH WR - GNS WR
"""

import logging
from datetime import UTC, datetime

import requests
from sqlalchemy import text
from sqlmodel import select

from mtgdb.models import MJ17LCardStat, MJ17LDataset, MJCard
from mtgdb.session import get_session

logger = logging.getLogger(__name__)

CARD_RATINGS_URL = "https://www.17lands.com/card_ratings/data"
USER_AGENT = "mtgsim/0.1 (github.com/dmiracle/mtgsim; occasional single-set fetches)"

# card_ratings/data response fields that map 1:1 onto MJ17LCardStat columns
_RATING_FIELDS = [
    "mtga_id",
    "rarity",
    "seen_count",
    "avg_seen",
    "pick_count",
    "avg_pick",
    "pool_count",
    "play_rate",
    "game_count",
    "win_rate",
    "opening_hand_game_count",
    "opening_hand_win_rate",
    "drawn_game_count",
    "drawn_win_rate",
    "ever_drawn_game_count",
    "ever_drawn_win_rate",
    "never_drawn_game_count",
    "never_drawn_win_rate",
    "drawn_improvement_win_rate",
]

_DRAFT_PICK_SQL = """
SELECT pick AS card_name, COUNT(*) AS pick_count, AVG(pick_number + 1) AS avg_pick
FROM mj_17l_draft_pick
WHERE expansion = :expansion AND event_type = :format AND pick IS NOT NULL
GROUP BY pick
"""

# Last-seen-at per (draft, pack, card): a card wheeling back in the same pack counts
# once, at its latest sighting.
_DRAFT_SEEN_SQL = """
SELECT card_name, COUNT(*) AS seen_count, AVG(last_seen) AS avg_seen
FROM (
    SELECT dc.card_name, MAX(dc.pick_number) + 1 AS last_seen
    FROM mj_17l_draft_card dc
    JOIN (
        SELECT DISTINCT draft_id FROM mj_17l_draft_pick
        WHERE expansion = :expansion AND event_type = :format
    ) d ON d.draft_id = dc.draft_id
    WHERE dc.in_pack
    GROUP BY dc.draft_id, dc.pack_number, dc.card_name
)
GROUP BY card_name
"""

_GAME_SQL = """
SELECT
    gc.card_name,
    COUNT(*) FILTER (WHERE gc.in_deck > 0 OR gc.sideboarded > 0) AS pool_count,
    COUNT(*) FILTER (WHERE gc.in_deck > 0) AS game_count,
    COUNT(*) FILTER (WHERE gc.in_deck > 0 AND g.won) AS game_wins,
    COUNT(*) FILTER (WHERE gc.in_opening_hand > 0) AS oh_count,
    COUNT(*) FILTER (WHERE gc.in_opening_hand > 0 AND g.won) AS oh_wins,
    COUNT(*) FILTER (WHERE gc.drawn > 0) AS drawn_count,
    COUNT(*) FILTER (WHERE gc.drawn > 0 AND g.won) AS drawn_wins,
    COUNT(*) FILTER (WHERE gc.in_opening_hand > 0 OR gc.drawn > 0) AS gih_count,
    COUNT(*) FILTER (WHERE (gc.in_opening_hand > 0 OR gc.drawn > 0) AND g.won) AS gih_wins,
    COUNT(*) FILTER (WHERE gc.in_deck > 0 AND gc.in_opening_hand = 0 AND gc.drawn = 0) AS gns_count,
    COUNT(*) FILTER (WHERE gc.in_deck > 0 AND gc.in_opening_hand = 0 AND gc.drawn = 0 AND g.won) AS gns_wins
FROM mj_17l_game_card gc
JOIN mj_17l_game g
    ON g.draft_id = gc.draft_id
    AND g.build_index IS gc.build_index
    AND g.game_number IS gc.game_number
WHERE g.expansion = :expansion AND g.event_type = :format
GROUP BY gc.card_name
"""


def _rate(wins: int, count: int) -> float | None:
    return wins / count if count else None


def _card_identity(session, expansion: str) -> dict[str, tuple[str, str | None]]:
    """Map card name -> (color, rarity) from mj_card for one set."""
    cards = session.exec(select(MJCard).where(MJCard.set_code == expansion)).all()
    return {c.name: ("".join(c.colors), c.rarity) for c in cards}


def compute_card_stats(expansion: str, format: str) -> int:
    """Compute per-card stats for one expansion/format and replace mj_17l_card_stat rows.

    Returns the number of card rows written.
    """
    logger.info(f"Computing card stats for {expansion}/{format}...")
    params = {"expansion": expansion, "format": format}
    stats: dict[str, dict] = {}

    with get_session() as session:
        conn = session.connection()

        for row in conn.execute(text(_DRAFT_PICK_SQL), params).mappings():
            stats.setdefault(row["card_name"], {}).update(pick_count=row["pick_count"], avg_pick=row["avg_pick"])

        for row in conn.execute(text(_DRAFT_SEEN_SQL), params).mappings():
            stats.setdefault(row["card_name"], {}).update(seen_count=row["seen_count"], avg_seen=row["avg_seen"])

        for row in conn.execute(text(_GAME_SQL), params).mappings():
            stats.setdefault(row["card_name"], {}).update(
                pool_count=row["pool_count"],
                play_rate=_rate(row["game_count"], row["pool_count"]),
                game_count=row["game_count"],
                win_rate=_rate(row["game_wins"], row["game_count"]),
                opening_hand_game_count=row["oh_count"],
                opening_hand_win_rate=_rate(row["oh_wins"], row["oh_count"]),
                drawn_game_count=row["drawn_count"],
                drawn_win_rate=_rate(row["drawn_wins"], row["drawn_count"]),
                ever_drawn_game_count=row["gih_count"],
                ever_drawn_win_rate=_rate(row["gih_wins"], row["gih_count"]),
                never_drawn_game_count=row["gns_count"],
                never_drawn_win_rate=_rate(row["gns_wins"], row["gns_count"]),
            )

        identity = _card_identity(session, expansion)
        dataset = session.exec(
            select(MJ17LDataset).where((MJ17LDataset.expansion == expansion) & (MJ17LDataset.format == format))
        ).first()
        computed_at = datetime.now(UTC).isoformat()

        conn.execute(
            text(
                "DELETE FROM mj_17l_card_stat "
                "WHERE expansion = :expansion AND format = :format AND source = 'public_dataset'"
            ),
            params,
        )

        for card_name, values in stats.items():
            gih_wr = values.get("ever_drawn_win_rate")
            gns_wr = values.get("never_drawn_win_rate")
            if gih_wr is not None and gns_wr is not None:
                values["drawn_improvement_win_rate"] = gih_wr - gns_wr
            color, rarity = identity.get(card_name, (None, None))
            session.add(
                MJ17LCardStat(
                    expansion=expansion,
                    format=format,
                    card_name=card_name,
                    dataset_last_updated=dataset.last_updated if dataset else None,
                    computed_at=computed_at,
                    color=color,
                    rarity=rarity,
                    **values,
                )
            )

        session.commit()

    logger.info(f"Card stats complete: {len(stats):,} cards for {expansion}/{format}")
    return len(stats)


def store_card_ratings(cards: list[dict], expansion: str, format: str, end_date: str) -> int:
    """Replace mj_17l_card_stat rows (source='17lands') with site-calculated ratings."""
    computed_at = datetime.now(UTC).isoformat()

    with get_session() as session:
        session.connection().execute(
            text("DELETE FROM mj_17l_card_stat WHERE expansion = :expansion AND format = :format AND source = :src"),
            {"expansion": expansion, "format": format, "src": "17lands"},
        )
        for card in cards:
            values = {k: card.get(k) for k in _RATING_FIELDS}
            for count_field in (f for f in _RATING_FIELDS if f.endswith("_count")):
                values[count_field] = values[count_field] or 0
            session.add(
                MJ17LCardStat(
                    expansion=expansion,
                    format=format,
                    card_name=card["name"],
                    source="17lands",
                    dataset_last_updated=end_date,
                    computed_at=computed_at,
                    color=card.get("color"),
                    **values,
                )
            )
        session.commit()

    return len(cards)


def fetch_card_ratings(
    expansion: str,
    format: str,
    start_date: str = "2019-01-01",
    end_date: str | None = None,
) -> int:
    """Fetch 17Lands-calculated card ratings (the Card Data page) for one expansion/format.

    One request per call. This is curated data under the 17Lands usage guidelines
    (https://www.17lands.com/usage_guidelines): cite as "17Lands", and observe the
    12-day embargo on new expansions in anything user-facing.
    """
    end_date = end_date or datetime.now(UTC).date().isoformat()
    logger.info(f"Fetching 17Lands card ratings for {expansion}/{format} ({start_date}..{end_date})...")

    resp = requests.get(
        CARD_RATINGS_URL,
        params={"expansion": expansion, "format": format, "start_date": start_date, "end_date": end_date},
        headers={"User-Agent": USER_AGENT},
        timeout=60,
    )
    resp.raise_for_status()
    cards = resp.json()

    count = store_card_ratings(cards, expansion, format, end_date)
    logger.info(f"Card ratings stored: {count:,} cards for {expansion}/{format}")
    return count

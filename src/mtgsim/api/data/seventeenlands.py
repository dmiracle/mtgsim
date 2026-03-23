"""17Lands data access layer."""

import logging

from mtgdb.models import MJ17LDataset, MJ17LDraftPick, MJ17LGame, MJ17LReplay
from mtgdb.session import get_session
from sqlmodel import func, select

logger = logging.getLogger("mtgsim.api.data.seventeenlands")


class SeventeenLandsData:
    """Data access for 17Lands datasets."""

    def list_datasets(
        self,
        expansion: str | None = None,
        format: str | None = None,
        has_draft: bool | None = None,
        has_game: bool | None = None,
        has_replay: bool | None = None,
        page: int = 1,
        limit: int = 50,
    ) -> tuple[list[dict], int]:
        with get_session() as session:
            query = select(MJ17LDataset)

            if expansion:
                query = query.where(MJ17LDataset.expansion == expansion)
            if format:
                query = query.where(MJ17LDataset.format == format)
            if has_draft is True:
                query = query.where(MJ17LDataset.draft_data_url.is_not(None))
            if has_game is True:
                query = query.where(MJ17LDataset.game_data_url.is_not(None))
            if has_replay is True:
                query = query.where(MJ17LDataset.replay_data_url.is_not(None))

            count_query = select(func.count()).select_from(query.subquery())
            total = session.exec(count_query).one()

            query = query.order_by(MJ17LDataset.last_updated.desc(), MJ17LDataset.expansion)
            offset = (page - 1) * limit
            query = query.offset(offset).limit(limit)

            results = session.exec(query).all()
            datasets = []
            for ds in results:
                datasets.append(
                    {
                        "id": ds.id,
                        "expansion": ds.expansion,
                        "format": ds.format,
                        "last_updated": ds.last_updated,
                        "has_draft_data": ds.draft_data_url is not None,
                        "has_game_data": ds.game_data_url is not None,
                        "has_replay_data": ds.replay_data_url is not None,
                        "draft_data_downloaded": ds.draft_data_downloaded,
                        "game_data_downloaded": ds.game_data_downloaded,
                        "replay_data_downloaded": ds.replay_data_downloaded,
                    }
                )
            return datasets, total

    def list_expansions(self) -> list[dict]:
        with get_session() as session:
            query = (
                select(
                    MJ17LDataset.expansion,
                    func.count().label("dataset_count"),
                )
                .group_by(MJ17LDataset.expansion)
                .order_by(MJ17LDataset.expansion)
            )
            rows = session.exec(query).all()

            expansions = []
            for expansion, count in rows:
                # Get formats and data availability for this expansion
                detail_query = select(MJ17LDataset).where(MJ17LDataset.expansion == expansion)
                details = session.exec(detail_query).all()
                formats = sorted({d.format for d in details})
                has_draft = any(d.draft_data_url for d in details)
                has_game = any(d.game_data_url for d in details)
                has_replay = any(d.replay_data_url for d in details)

                expansions.append(
                    {
                        "expansion": expansion,
                        "dataset_count": count,
                        "formats": formats,
                        "has_draft_data": has_draft,
                        "has_game_data": has_game,
                        "has_replay_data": has_replay,
                    }
                )
            return expansions

    def list_draft_picks(
        self,
        expansion: str | None = None,
        event_type: str | None = None,
        card_name: str | None = None,
        page: int = 1,
        limit: int = 50,
    ) -> tuple[list[dict], int]:
        with get_session() as session:
            query = select(MJ17LDraftPick)
            if expansion:
                query = query.where(MJ17LDraftPick.expansion == expansion)
            if event_type:
                query = query.where(MJ17LDraftPick.event_type == event_type)
            if card_name:
                query = query.where(MJ17LDraftPick.pick == card_name)

            total = session.exec(select(func.count()).select_from(query.subquery())).one()
            query = query.order_by(MJ17LDraftPick.draft_time.desc())
            query = query.offset((page - 1) * limit).limit(limit)
            results = session.exec(query).all()

            return [
                {
                    "id": r.id,
                    "expansion": r.expansion,
                    "event_type": r.event_type,
                    "draft_id": r.draft_id,
                    "draft_time": r.draft_time,
                    "pack_number": r.pack_number,
                    "pick_number": r.pick_number,
                    "pick": r.pick,
                    "event_match_wins": r.event_match_wins,
                    "event_match_losses": r.event_match_losses,
                }
                for r in results
            ], total

    def list_games(
        self,
        expansion: str | None = None,
        event_type: str | None = None,
        won: bool | None = None,
        page: int = 1,
        limit: int = 50,
    ) -> tuple[list[dict], int]:
        with get_session() as session:
            query = select(MJ17LGame)
            if expansion:
                query = query.where(MJ17LGame.expansion == expansion)
            if event_type:
                query = query.where(MJ17LGame.event_type == event_type)
            if won is not None:
                query = query.where(MJ17LGame.won == won)

            total = session.exec(select(func.count()).select_from(query.subquery())).one()
            query = query.order_by(MJ17LGame.draft_time.desc())
            query = query.offset((page - 1) * limit).limit(limit)
            results = session.exec(query).all()

            return [
                {
                    "id": r.id,
                    "expansion": r.expansion,
                    "event_type": r.event_type,
                    "draft_id": r.draft_id,
                    "game_number": r.game_number,
                    "on_play": r.on_play,
                    "num_turns": r.num_turns,
                    "won": r.won,
                    "opp_colors": r.opp_colors,
                    "rank": r.rank,
                }
                for r in results
            ], total

    def list_replays(
        self,
        expansion: str | None = None,
        format: str | None = None,
        won: bool | None = None,
        page: int = 1,
        limit: int = 50,
    ) -> tuple[list[dict], int]:
        with get_session() as session:
            query = select(MJ17LReplay)
            if expansion:
                query = query.where(MJ17LReplay.expansion == expansion)
            if format:
                query = query.where(MJ17LReplay.format == format)
            if won is not None:
                query = query.where(MJ17LReplay.won == won)

            total = session.exec(select(func.count()).select_from(query.subquery())).one()
            query = query.order_by(MJ17LReplay.time.desc())
            query = query.offset((page - 1) * limit).limit(limit)
            results = session.exec(query).all()

            return [
                {
                    "id": r.id,
                    "expansion": r.expansion,
                    "format": r.format,
                    "draft_id": r.draft_id,
                    "game_index": r.game_index,
                    "turns": r.turns,
                    "won": r.won,
                    "user_deck_colors": r.user_deck_colors,
                    "oppo_deck_colors": r.oppo_deck_colors,
                }
                for r in results
            ], total


seventeenlands_data = SeventeenLandsData()

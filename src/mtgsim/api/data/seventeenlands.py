"""17Lands data access layer."""

import logging

from mtgdb.models import MJ17LDataset
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


seventeenlands_data = SeventeenLandsData()

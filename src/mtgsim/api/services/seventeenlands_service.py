"""17Lands service layer."""

import logging

from mtgsim.api.data.seventeenlands import seventeenlands_data
from mtgsim.api.models.common import Pagination
from mtgsim.api.models.seventeenlands import (
    DatasetListResponse,
    DatasetSummary,
    ExpansionSummary,
)

logger = logging.getLogger("mtgsim.api.services.seventeenlands")


class SeventeenLandsService:
    async def list_datasets(
        self,
        expansion: str | None = None,
        format: str | None = None,
        has_draft: bool | None = None,
        has_game: bool | None = None,
        has_replay: bool | None = None,
        page: int = 1,
        limit: int = 50,
    ) -> DatasetListResponse:
        datasets, total = seventeenlands_data.list_datasets(
            expansion=expansion,
            format=format,
            has_draft=has_draft,
            has_game=has_game,
            has_replay=has_replay,
            page=page,
            limit=limit,
        )
        pages = (total + limit - 1) // limit if limit > 0 else 1
        return DatasetListResponse(
            data=[DatasetSummary(**d) for d in datasets],
            pagination=Pagination(page=page, limit=limit, total=total, pages=pages),
        )

    async def list_expansions(self) -> list[ExpansionSummary]:
        expansions = seventeenlands_data.list_expansions()
        return [ExpansionSummary(**e) for e in expansions]


seventeenlands_service = SeventeenLandsService()

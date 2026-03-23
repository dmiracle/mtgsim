"""17Lands service layer."""

import logging

from mtgsim.api.data.seventeenlands import seventeenlands_data
from mtgsim.api.models.common import Pagination
from mtgsim.api.models.seventeenlands import (
    DatasetListResponse,
    DatasetSummary,
    DraftPickListResponse,
    DraftPickSummary,
    ExpansionSummary,
    GameListResponse,
    GameSummary,
    ReplayListResponse,
    ReplaySummary,
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

    async def list_draft_picks(
        self,
        expansion: str | None = None,
        event_type: str | None = None,
        card_name: str | None = None,
        page: int = 1,
        limit: int = 50,
    ) -> DraftPickListResponse:
        data, total = seventeenlands_data.list_draft_picks(
            expansion=expansion,
            event_type=event_type,
            card_name=card_name,
            page=page,
            limit=limit,
        )
        pages = (total + limit - 1) // limit if limit > 0 else 1
        return DraftPickListResponse(
            data=[DraftPickSummary(**d) for d in data],
            pagination=Pagination(page=page, limit=limit, total=total, pages=pages),
        )

    async def list_games(
        self,
        expansion: str | None = None,
        event_type: str | None = None,
        won: bool | None = None,
        page: int = 1,
        limit: int = 50,
    ) -> GameListResponse:
        data, total = seventeenlands_data.list_games(
            expansion=expansion,
            event_type=event_type,
            won=won,
            page=page,
            limit=limit,
        )
        pages = (total + limit - 1) // limit if limit > 0 else 1
        return GameListResponse(
            data=[GameSummary(**d) for d in data],
            pagination=Pagination(page=page, limit=limit, total=total, pages=pages),
        )

    async def list_replays(
        self,
        expansion: str | None = None,
        format: str | None = None,
        won: bool | None = None,
        page: int = 1,
        limit: int = 50,
    ) -> ReplayListResponse:
        data, total = seventeenlands_data.list_replays(
            expansion=expansion,
            format=format,
            won=won,
            page=page,
            limit=limit,
        )
        pages = (total + limit - 1) // limit if limit > 0 else 1
        return ReplayListResponse(
            data=[ReplaySummary(**d) for d in data],
            pagination=Pagination(page=page, limit=limit, total=total, pages=pages),
        )


seventeenlands_service = SeventeenLandsService()

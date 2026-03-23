"""17Lands Pydantic response models."""

from pydantic import BaseModel

from mtgsim.api.models.common import Pagination


class DatasetSummary(BaseModel):
    """Summary of a 17Lands public dataset."""

    id: int
    expansion: str
    format: str
    last_updated: str | None = None
    has_draft_data: bool = False
    has_game_data: bool = False
    has_replay_data: bool = False
    draft_data_downloaded: bool = False
    game_data_downloaded: bool = False
    replay_data_downloaded: bool = False


class DatasetListResponse(BaseModel):
    """Response for dataset list endpoint."""

    data: list[DatasetSummary]
    pagination: Pagination


class ExpansionSummary(BaseModel):
    """Summary of datasets available for an expansion."""

    expansion: str
    dataset_count: int
    formats: list[str]
    has_draft_data: bool = False
    has_game_data: bool = False
    has_replay_data: bool = False


class DraftPickSummary(BaseModel):
    """Summary of a draft pick."""

    id: int
    expansion: str
    event_type: str
    draft_id: str
    draft_time: str | None = None
    pack_number: int | None = None
    pick_number: int | None = None
    pick: str | None = None
    event_match_wins: int | None = None
    event_match_losses: int | None = None


class DraftPickListResponse(BaseModel):
    data: list[DraftPickSummary]
    pagination: Pagination


class GameSummary(BaseModel):
    """Summary of a game."""

    id: int
    expansion: str
    event_type: str
    draft_id: str
    game_number: int | None = None
    on_play: bool | None = None
    num_turns: int | None = None
    won: bool | None = None
    opp_colors: str | None = None
    rank: str | None = None


class GameListResponse(BaseModel):
    data: list[GameSummary]
    pagination: Pagination


class ReplaySummary(BaseModel):
    """Summary of a game replay."""

    id: int
    expansion: str
    format: str
    draft_id: str
    game_index: int | None = None
    turns: int | None = None
    won: bool | None = None
    user_deck_colors: str | None = None
    oppo_deck_colors: str | None = None


class ReplayListResponse(BaseModel):
    data: list[ReplaySummary]
    pagination: Pagination

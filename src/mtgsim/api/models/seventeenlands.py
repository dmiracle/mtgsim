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

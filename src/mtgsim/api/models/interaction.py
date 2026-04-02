"""API models for card interactions."""

from pydantic import BaseModel, Field

from mtgsim.api.models.common import Pagination


class InteractionCard(BaseModel):
    """Minimal card info embedded in interaction responses."""

    uuid: str
    name: str
    type_line: str | None = None
    mana_cost: str | None = None
    image_url: str | None = None


class InteractionCreateRequest(BaseModel):
    """Request to create a card interaction."""

    source_card_uuid: str
    target_card_uuid: str
    interaction_type: str
    is_bidirectional: bool = True
    description: str | None = None
    strength: int | None = Field(default=None, ge=1, le=5)
    extra: dict = Field(default_factory=dict)


class InteractionUpdateRequest(BaseModel):
    """Request to update an interaction."""

    interaction_type: str | None = None
    is_bidirectional: bool | None = None
    description: str | None = None
    strength: int | None = Field(default=None, ge=1, le=5)
    extra: dict | None = None


class InteractionDetail(BaseModel):
    """Full interaction detail."""

    id: int
    source_card: InteractionCard
    target_card: InteractionCard
    interaction_type: str
    is_bidirectional: bool
    description: str | None = None
    strength: int | None = None
    extra: dict = Field(default_factory=dict)
    created_at: str
    updated_at: str


class InteractionListResponse(BaseModel):
    """Paginated list of interactions."""

    data: list[InteractionDetail]
    pagination: Pagination


class InteractionGraphNode(BaseModel):
    """A card node in the interaction graph with its edges."""

    card: InteractionCard
    interactions: list[InteractionDetail]


class InteractionGraphResponse(BaseModel):
    """Graph traversal result from a starting card."""

    root_card: InteractionCard
    depth: int
    nodes: list[InteractionGraphNode]
    total_interactions: int

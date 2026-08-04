"""API models for card interactions."""

from pydantic import BaseModel, Field, model_validator

from mtgsim.api.models.common import Pagination

# Interaction taxonomy (docs/interaction-model-v2.md). Enforced on create/update
# only — reads never reject legacy free-string rows. "payoff" is the reverse
# presentation of a directed "enables" edge (source enabler -> target payoff).
DIRECTED_TYPES = {"enables", "counters"}
BIDIRECTIONAL_TYPES = {"combo", "synergy", "anti_synergy"}
INTERACTION_TYPES = DIRECTED_TYPES | BIDIRECTIONAL_TYPES


def _validate_type(interaction_type: str) -> str:
    if interaction_type not in INTERACTION_TYPES:
        allowed = ", ".join(sorted(INTERACTION_TYPES))
        raise ValueError(f"interaction_type must be one of: {allowed}")
    return interaction_type


def _force_directionality(interaction_type: str) -> bool:
    return interaction_type not in DIRECTED_TYPES


class InteractionCard(BaseModel):
    """Minimal card info embedded in interaction responses."""

    uuid: str
    name: str
    type_line: str | None = None
    mana_cost: str | None = None
    image_url: str | None = None


class InteractionCreateRequest(BaseModel):
    """Create an interaction, addressed by a uuid pair or a card-name pair."""

    source_card_uuid: str | None = None
    target_card_uuid: str | None = None
    source_card_name: str | None = None
    target_card_name: str | None = None
    interaction_type: str
    is_bidirectional: bool = True
    description: str | None = None
    strength: int | None = Field(default=None, ge=1, le=5)
    interaction_subtype: str | None = Field(default=None, max_length=60)
    detected_by: str = Field(default="manual", max_length=40)
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    extra: dict = Field(default_factory=dict)

    @model_validator(mode="after")
    def _check(self) -> "InteractionCreateRequest":
        by_uuid = bool(self.source_card_uuid and self.target_card_uuid)
        by_name = bool(self.source_card_name and self.target_card_name)
        if by_uuid == by_name:
            raise ValueError("provide either both card uuids or both card names")
        _validate_type(self.interaction_type)
        self.is_bidirectional = _force_directionality(self.interaction_type)
        return self


class InteractionUpdateRequest(BaseModel):
    """Request to update an interaction."""

    interaction_type: str | None = None
    is_bidirectional: bool | None = None
    description: str | None = None
    strength: int | None = Field(default=None, ge=1, le=5)
    interaction_subtype: str | None = Field(default=None, max_length=60)
    detected_by: str | None = Field(default=None, max_length=40)
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    extra: dict | None = None

    @model_validator(mode="after")
    def _check(self) -> "InteractionUpdateRequest":
        if self.interaction_type is not None:
            _validate_type(self.interaction_type)
            self.is_bidirectional = _force_directionality(self.interaction_type)
        return self


class InteractionDetail(BaseModel):
    """Full interaction detail."""

    id: int
    source_card: InteractionCard
    target_card: InteractionCard
    source_card_name: str | None = None
    target_card_name: str | None = None
    interaction_type: str
    interaction_subtype: str | None = None
    is_bidirectional: bool
    description: str | None = None
    strength: int | None = None
    detected_by: str = "manual"
    confidence: float = 1.0
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

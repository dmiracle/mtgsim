"""Service layer for card interactions."""

import logging
import math

from mtgsim.api.data.interactions import interactions_data
from mtgsim.api.models.common import Pagination
from mtgsim.api.models.interaction import (
    InteractionCard,
    InteractionCreateRequest,
    InteractionDetail,
    InteractionGraphNode,
    InteractionGraphResponse,
    InteractionListResponse,
    InteractionUpdateRequest,
)

logger = logging.getLogger(__name__)


def _to_interaction_card(d: dict) -> InteractionCard:
    return InteractionCard(
        uuid=d.get("uuid", ""),
        name=d.get("name", ""),
        type_line=d.get("type_line"),
        mana_cost=d.get("mana_cost"),
        image_url=d.get("image_url"),
    )


def _to_detail(d: dict) -> InteractionDetail:
    return InteractionDetail(
        id=d["id"],
        source_card=_to_interaction_card(d["source_card"]),
        target_card=_to_interaction_card(d["target_card"]),
        source_card_name=d.get("source_card_name"),
        target_card_name=d.get("target_card_name"),
        interaction_type=d["interaction_type"],
        interaction_subtype=d.get("interaction_subtype"),
        is_bidirectional=d["is_bidirectional"],
        description=d.get("description"),
        strength=d.get("strength"),
        detected_by=d.get("detected_by", "manual"),
        confidence=d.get("confidence", 1.0),
        extra=d.get("extra", {}),
        created_at=d.get("created_at", ""),
        updated_at=d.get("updated_at", ""),
    )


class InteractionService:
    async def create_interaction(self, req: InteractionCreateRequest) -> InteractionDetail | None:
        result = interactions_data.create_interaction(
            interaction_type=req.interaction_type,
            source_card_uuid=req.source_card_uuid,
            target_card_uuid=req.target_card_uuid,
            source_card_name=req.source_card_name,
            target_card_name=req.target_card_name,
            is_bidirectional=req.is_bidirectional,
            description=req.description,
            strength=req.strength,
            interaction_subtype=req.interaction_subtype,
            detected_by=req.detected_by,
            confidence=req.confidence,
            extra=req.extra,
        )
        if not result:
            return None
        return _to_detail(result)

    async def get_interaction(self, interaction_id: int) -> InteractionDetail | None:
        result = interactions_data.get_interaction(interaction_id)
        if not result:
            return None
        return _to_detail(result)

    async def update_interaction(self, interaction_id: int, req: InteractionUpdateRequest) -> InteractionDetail | None:
        fields = req.model_dump(exclude_unset=True)
        if not fields:
            return await self.get_interaction(interaction_id)
        result = interactions_data.update_interaction(interaction_id, **fields)
        if not result:
            return None
        return _to_detail(result)

    async def delete_interaction(self, interaction_id: int) -> bool:
        return interactions_data.delete_interaction(interaction_id)

    async def list_interactions(
        self,
        card_uuid: str | None = None,
        card_name: str | None = None,
        interaction_type: str | None = None,
        page: int = 1,
        limit: int = 50,
    ) -> InteractionListResponse:
        results, total = interactions_data.list_interactions(
            card_uuid=card_uuid,
            card_name=card_name,
            interaction_type=interaction_type,
            page=page,
            limit=limit,
        )
        pages = math.ceil(total / limit) if total > 0 else 0
        return InteractionListResponse(
            data=[_to_detail(r) for r in results],
            pagination=Pagination(page=page, limit=limit, total=total, pages=pages),
        )

    async def get_interaction_graph(
        self, card_uuid: str | None = None, card_name: str | None = None, depth: int = 1
    ) -> InteractionGraphResponse | None:
        if card_name:
            result = interactions_data.get_interaction_graph_by_name(card_name, depth)
        else:
            result = interactions_data.get_interaction_graph(card_uuid, depth)
        if not result:
            return None
        return InteractionGraphResponse(
            root_card=_to_interaction_card(result["root_card"]),
            depth=result["depth"],
            nodes=[
                InteractionGraphNode(
                    card=_to_interaction_card(n["card"]),
                    interactions=[_to_detail(i) for i in n["interactions"]],
                )
                for n in result["nodes"]
            ],
            total_interactions=result["total_interactions"],
        )


interaction_service = InteractionService()

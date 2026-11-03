"""API router for situational card evaluations (developing / parity / behind / ahead)."""

from fastapi import APIRouter, HTTPException

from mtgsim.api.data.evaluations import evaluations_data
from mtgsim.api.models.evaluation import (
    CardEvaluation,
    EvaluationSetCreateRequest,
    EvaluationSetDetail,
    EvaluationSetSummary,
)

router = APIRouter(prefix="/evaluation-sets", tags=["evaluations"])


@router.post("", response_model=EvaluationSetSummary, status_code=201)
async def create_set(req: EvaluationSetCreateRequest) -> EvaluationSetSummary:
    return EvaluationSetSummary(**evaluations_data.create_set(req.name, req.set_code))


@router.get("", response_model=list[EvaluationSetSummary])
async def list_sets() -> list[EvaluationSetSummary]:
    return [EvaluationSetSummary(**s) for s in evaluations_data.list_sets()]


@router.get("/{set_id}", response_model=EvaluationSetDetail)
async def get_set(set_id: int) -> EvaluationSetDetail:
    result = evaluations_data.get_set(set_id)
    if result is None:
        raise HTTPException(status_code=404, detail=f"Evaluation set not found: {set_id}")
    return EvaluationSetDetail(**result)


@router.put("/{set_id}/entries", response_model=CardEvaluation)
async def put_evaluation(set_id: int, req: CardEvaluation) -> CardEvaluation:
    """Replace a card's scores; sending every situation as null removes the card from the set."""
    result = evaluations_data.put_evaluation(set_id, req.card_name, req.model_dump(exclude={"card_name"}))
    if result is None:
        raise HTTPException(status_code=404, detail=f"Evaluation set or card not found: {set_id}, {req.card_name}")
    return CardEvaluation(**result)


@router.delete("/{set_id}", status_code=204)
async def delete_set(set_id: int) -> None:
    if not evaluations_data.delete_set(set_id):
        raise HTTPException(status_code=404, detail=f"Evaluation set not found: {set_id}")

"""Keywords/Glossary API endpoints."""

from fastapi import APIRouter
from pydantic import BaseModel

from mtgsim.api.data import keywords_data


class KeywordDefinition(BaseModel):
    """Single keyword definition."""

    term: str
    definition: str


class KeywordsResponse(BaseModel):
    """Response containing all keyword categories."""

    ability_words: list[KeywordDefinition]
    keyword_abilities: list[KeywordDefinition]
    keyword_actions: list[KeywordDefinition]


class FormatsResponse(BaseModel):
    """Response containing format information."""

    formats: list[dict]


router = APIRouter(prefix="/keywords", tags=["reference"])


@router.get("", response_model=KeywordsResponse)
async def get_keywords() -> KeywordsResponse:
    """
    Get MTG keywords for glossary.

    Returns all keyword categories:
    - **ability_words**: Words that have no rules meaning but group cards thematically
    - **keyword_abilities**: Keywords with specific rules meaning (flying, trample, etc.)
    - **keyword_actions**: Keywords that represent game actions (destroy, exile, etc.)
    """
    all_keywords = keywords_data.get_all_keywords()

    return KeywordsResponse(
        ability_words=[KeywordDefinition(term=kw, definition="") for kw in all_keywords["ability_words"]],
        keyword_abilities=[KeywordDefinition(term=kw, definition="") for kw in all_keywords["keyword_abilities"]],
        keyword_actions=[KeywordDefinition(term=kw, definition="") for kw in all_keywords["keyword_actions"]],
    )


@router.get("/formats", response_model=FormatsResponse)
async def get_formats() -> FormatsResponse:
    """
    Get available format information.

    Returns list of supported formats with descriptions and deck counts.
    """
    return FormatsResponse(
        formats=[
            {
                "id": "standard",
                "name": "Standard",
                "description": "Uses cards from recent sets",
                "deck_count": 0,
            },
            {
                "id": "pioneer",
                "name": "Pioneer",
                "description": "Uses cards from Return to Ravnica forward",
                "deck_count": 0,
            },
            {
                "id": "modern",
                "name": "Modern",
                "description": "Uses cards from 8th Edition forward",
                "deck_count": 0,
            },
            {
                "id": "legacy",
                "name": "Legacy",
                "description": "Uses cards from all sets with a ban list",
                "deck_count": 0,
            },
            {
                "id": "vintage",
                "name": "Vintage",
                "description": "Uses cards from all sets with restrictions",
                "deck_count": 0,
            },
            {
                "id": "commander",
                "name": "Commander",
                "description": "100-card singleton format with a commander",
                "deck_count": 0,
            },
        ]
    )

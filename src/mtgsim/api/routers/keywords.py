"""Keywords/Glossary API endpoints."""

from fastapi import APIRouter
from pydantic import BaseModel


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

    TODO: Load from Keywords.json
    """
    # Stub data - should load from Keywords.json
    return KeywordsResponse(
        ability_words=[
            KeywordDefinition(
                term="Battalion",
                definition="Whenever this creature and at least two other creatures attack...",
            ),
            KeywordDefinition(
                term="Landfall",
                definition="Whenever a land enters the battlefield under your control...",
            ),
        ],
        keyword_abilities=[
            KeywordDefinition(
                term="Flying",
                definition="This creature can't be blocked except by creatures with flying or reach.",
            ),
            KeywordDefinition(
                term="Trample",
                definition="This creature can deal excess combat damage to the player or planeswalker it's attacking.",
            ),
            KeywordDefinition(
                term="Haste",
                definition="This creature can attack and tap as soon as it comes under your control.",
            ),
        ],
        keyword_actions=[
            KeywordDefinition(
                term="Destroy",
                definition="Move a permanent from the battlefield to its owner's graveyard.",
            ),
            KeywordDefinition(
                term="Exile",
                definition="Move a card to the exile zone.",
            ),
            KeywordDefinition(
                term="Sacrifice",
                definition="Move a permanent you control to its owner's graveyard.",
            ),
        ],
    )


@router.get("/formats", response_model=FormatsResponse)
async def get_formats() -> FormatsResponse:
    """
    Get available format information.

    Returns list of supported formats with descriptions and deck counts.
    """
    # Stub data
    return FormatsResponse(
        formats=[
            {
                "id": "standard",
                "name": "Standard",
                "description": "Uses cards from recent sets",
                "deck_count": 150,
            },
            {
                "id": "pioneer",
                "name": "Pioneer",
                "description": "Uses cards from Return to Ravnica forward",
                "deck_count": 300,
            },
            {
                "id": "modern",
                "name": "Modern",
                "description": "Uses cards from 8th Edition forward",
                "deck_count": 800,
            },
            {
                "id": "legacy",
                "name": "Legacy",
                "description": "Uses cards from all sets with a ban list",
                "deck_count": 500,
            },
            {
                "id": "vintage",
                "name": "Vintage",
                "description": "Uses cards from all sets with restrictions",
                "deck_count": 400,
            },
            {
                "id": "commander",
                "name": "Commander",
                "description": "100-card singleton format with a commander",
                "deck_count": 898,
            },
        ]
    )

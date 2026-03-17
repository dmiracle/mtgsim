"""Booster pack data models."""

from pydantic import BaseModel


class BoosterCard(BaseModel):
    uuid: str
    name: str
    set_code: str
    number: str | None = None
    rarity: str
    slot: str  # "common", "uncommon", "rare_mythic", "land", "wildcard", "foil_wildcard"
    is_foil: bool = False
    image_url: str | None = None
    mana_cost: str | None = None
    mana_value: float | None = None
    type_line: str | None = None
    colors: list[str] = []


class BoosterPack(BaseModel):
    set_code: str
    set_name: str
    booster_type: str  # "play", "draft", "set"
    cards: list[BoosterCard]

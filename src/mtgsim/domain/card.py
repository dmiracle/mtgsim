from enum import Enum

from pydantic import BaseModel


class Color(str, Enum):
    WHITE = "W"
    BLUE = "U"
    BLACK = "B"
    RED = "R"
    GREEN = "G"
    COLORLESS = "C"


class CardType(str, Enum):
    CREATURE = "Creature"
    INSTANT = "Instant"
    SORCERY = "Sorcery"
    ENCHANTMENT = "Enchantment"
    ARTIFACT = "Artifact"
    LAND = "Land"
    PLANESWALKER = "Planeswalker"
    BATTLE = "Battle"


class Supertype(str, Enum):
    BASIC = "Basic"
    LEGENDARY = "Legendary"
    SNOW = "Snow"
    WORLD = "World"


class Rarity(str, Enum):
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    MYTHIC = "mythic"


class ManaCost(BaseModel):
    """Domain model for mana cost - focuses on business logic and validation."""
    white: int = 0
    blue: int = 0
    black: int = 0
    red: int = 0
    green: int = 0
    colorless: int = 0
    generic: int = 0

    @property
    def cmc(self) -> int:
        """Converted mana cost - total mana required."""
        return self.white + self.blue + self.black + self.red + self.green + self.colorless + self.generic


class Card(BaseModel):
    """Domain model for cards - focuses on business logic and validation."""
    name: str
    mana_cost: ManaCost | None = None
    card_types: list[CardType] = []
    supertypes: list[Supertype] = []
    subtypes: list[str] = []
    oracle_text: str = ""
    flavor_text: str = ""
    text_box: str = ""
    raw_text: str = ""
    image_url: str | None = None
    power: int | None = None
    toughness: int | None = None
    loyalty: int | None = None
    defense: int | None = None
    color_identity: list[Color] = []
    rarity: Rarity = Rarity.COMMON

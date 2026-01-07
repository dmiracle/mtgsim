from dataclasses import dataclass, field
from enum import Enum


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


@dataclass
class ManaCost:
    """Domain model for mana cost - pure business logic without API dependencies."""
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


@dataclass
class Card:
    """Domain model for cards - pure business logic without API dependencies."""
    name: str
    mana_cost: ManaCost | None = None
    card_types: list[CardType] = field(default_factory=list)
    supertypes: list[Supertype] = field(default_factory=list)
    subtypes: list[str] = field(default_factory=list)
    oracle_text: str = ""
    flavor_text: str = ""
    text_box: str = ""
    raw_text: str = ""
    image_url: str | None = None
    power: int | None = None
    toughness: int | None = None
    loyalty: int | None = None
    defense: int | None = None
    color_identity: list[Color] = field(default_factory=list)
    rarity: Rarity = Rarity.COMMON

import base64
import os
from abc import ABC, abstractmethod
from pathlib import Path

from openai import OpenAI

from .card import Card, CardType, ManaCost, Rarity, Supertype

SYSTEM_PROMPT = """You are an expert Magic: The Gathering card scanner.
Analyze the provided card image and extract the data strictly adhering to the schema.

For Mana Cost, count specific symbols:
- {2}{W}{W} means generic=2, white=2
- {G} means green=1
- {C} means colorless=1 (diamond symbol)

Separate the type line into:
- supertypes: Legendary, Basic, Snow, World
- card_types: Creature, Instant, Sorcery, Enchantment, Artifact, Land, Planeswalker, Battle
- subtypes: Elf, Warrior, Forest, Aura, etc.

Distinguish between Oracle text (rules text) and Flavor text (italicized text).
Identify the rarity from the set symbol color (black=common, silver=uncommon, gold=rare, orange-red=mythic).
For creatures, extract power and toughness. For planeswalkers, extract starting loyalty.
For battles, extract defense."""


class ExtractionPipeline(ABC):
    """Abstract base class for card image extraction pipelines."""

    @abstractmethod
    def extract(self, image_path: Path) -> Card:
        """Extract card data from an image file."""
        pass


class OpenAIExtractionPipeline(ExtractionPipeline):
    """Extraction pipeline using OpenAI's vision API."""

    def __init__(self, api_key: str | None = None, model: str = "gpt-4o"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key required. Set OPENAI_API_KEY env var or pass api_key.")
        self.client = OpenAI(api_key=self.api_key)
        self.model = model

    def _encode_image(self, image_path: Path) -> str:
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")

    def _get_mime_type(self, image_path: Path) -> str:
        suffix = image_path.suffix.lower()
        mime_types = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".gif": "image/gif",
            ".webp": "image/webp",
        }
        return mime_types.get(suffix, "image/jpeg")

    def extract(self, image_path: Path) -> Card:
        base64_image = self._encode_image(image_path)
        mime_type = self._get_mime_type(image_path)

        completion = self.client.beta.chat.completions.parse(
            model=self.model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:{mime_type};base64,{base64_image}"},
                        }
                    ],
                },
            ],
            response_format=Card,
        )

        card = completion.choices[0].message.parsed
        card.image_url = str(image_path)
        return card


class MockExtractionPipeline(ExtractionPipeline):
    """Mock pipeline that returns sample card data for testing."""

    def extract(self, image_path: Path) -> Card:
        filename = image_path.stem.lower()

        if "land" in filename or "forest" in filename or "island" in filename:
            return Card(
                name="Tropical Island",
                card_types=[CardType.LAND],
                subtypes=["Forest", "Island"],
                oracle_text="{T}: Add {G} or {U}.",
                rarity=Rarity.RARE,
                image_url=str(image_path),
                raw_text="(T: Add G or U.)",
            )
        elif "creature" in filename or "dragon" in filename:
            return Card(
                name="Shivan Dragon",
                mana_cost=ManaCost(red=2, generic=4),
                card_types=[CardType.CREATURE],
                subtypes=["Dragon"],
                oracle_text="Flying\n{R}: Shivan Dragon gets +1/+0 until end of turn.",
                power=5,
                toughness=5,
                rarity=Rarity.RARE,
                image_url=str(image_path),
                raw_text="Flying\nR: Shivan Dragon gets +1/+0 until end of turn.",
            )
        elif "planeswalker" in filename or "jace" in filename:
            return Card(
                name="Jace, the Mind Sculptor",
                mana_cost=ManaCost(blue=2, generic=2),
                card_types=[CardType.PLANESWALKER],
                supertypes=[Supertype.LEGENDARY],
                subtypes=["Jace"],
                oracle_text=(
                    "+2: Look at the top card of target player's library.\n"
                    "-1: Return target creature to its owner's hand.\n"
                    "-12: Exile all cards from target player's library."
                ),
                loyalty=3,
                rarity=Rarity.MYTHIC,
                image_url=str(image_path),
                raw_text=(
                    "+2: Look at the top card of target player's library. "
                    "-1: Return target creature to owner's hand. "
                    "-12: Exile all cards from target player's library."
                ),
            )
        else:
            return Card(
                name="Lightning Bolt",
                mana_cost=ManaCost(red=1),
                card_types=[CardType.INSTANT],
                oracle_text="Lightning Bolt deals 3 damage to any target.",
                rarity=Rarity.COMMON,
                image_url=str(image_path),
                raw_text="Lightning Bolt deals 3 damage to any target.",
            )


def get_pipeline(pipeline_name: str = "mock", **kwargs) -> ExtractionPipeline:
    """Factory function to get an extraction pipeline by name."""
    pipelines = {
        "mock": MockExtractionPipeline,
        "openai": OpenAIExtractionPipeline,
    }

    if pipeline_name not in pipelines:
        raise ValueError(f"Unknown pipeline: {pipeline_name}. Available: {list(pipelines.keys())}")

    return pipelines[pipeline_name](**kwargs)

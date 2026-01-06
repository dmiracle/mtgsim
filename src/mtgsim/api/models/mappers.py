"""Centralized data transfer object mapping."""

import json
import sqlite3
from typing import Any

from mtgsim.api.models.card import CardSummary
from mtgsim.api.models.deck import DeckLegality, DeckSummary
from mtgsim.api.models.set import SetSummary


class DTOMapper:
    """Centralized data transfer object mapping."""

    @staticmethod
    def map_card_summary(row: sqlite3.Row, price: float | None = None) -> CardSummary:
        """Map database row to CardSummary model.

        Args:
            row: Database row containing card data
            price: Optional price to include in the summary

        Returns:
            CardSummary model instance
        """
        # Handle JSON fields safely
        color_identity = DTOMapper._decode_json_field(row.get("colorIdentity", "[]"))
        if not isinstance(color_identity, list):
            color_identity = []

        return CardSummary(
            uuid=row["uuid"],
            name=row["name"],
            type=row.get("type"),
            mana_cost=row.get("manaCost"),
            mana_value=row.get("manaValue", 0),
            rarity=row.get("rarity"),
            set_code=row.get("setCode"),
            color_identity=color_identity,
            text=row.get("text"),
            price=price,
            image_url=row.get("image_url"),
        )

    @staticmethod
    def map_deck_summary(row: sqlite3.Row, stats: dict | None = None) -> DeckSummary:
        """Map database row to DeckSummary model.

        Args:
            row: Database row containing deck data
            stats: Optional stats dictionary containing additional deck information

        Returns:
            DeckSummary model instance
        """
        # Handle JSON fields safely
        colors = DTOMapper._decode_json_field(row.get("colors", "[]"))
        if not isinstance(colors, list):
            colors = []

        # Extract legality information if available
        legalities = DTOMapper._decode_json_field(row.get("legalities", "{}"))
        if not isinstance(legalities, dict):
            legalities = {}

        legality = DeckLegality(
            standard=legalities.get("standard", False),
            pioneer=legalities.get("pioneer", False),
            modern=legalities.get("modern", False),
            legacy=legalities.get("legacy", False),
            vintage=legalities.get("vintage", False),
            commander=legalities.get("commander", False),
            brawl=legalities.get("brawl", False),
            historic=legalities.get("historic", False),
            pauper=legalities.get("pauper", False),
        )

        return DeckSummary(
            file=row["file"],
            name=row["name"],
            code=row["code"],
            card_count=row.get("card_count", 0),
            colors=colors,
            price=row.get("price"),
            release_date=row.get("releaseDate"),
            legality=legality,
        )

    @staticmethod
    def map_set_summary(row: sqlite3.Row) -> SetSummary:
        """Map database row to SetSummary model.

        Args:
            row: Database row containing set data

        Returns:
            SetSummary model instance
        """
        # Handle keyrune_code with proper fallback
        keyrune_code = row.get("keyruneCode")
        if keyrune_code is None:
            keyrune_code = row["code"]

        return SetSummary(
            code=row["code"],
            name=row["name"],
            type=row["type"],
            release_date=row.get("releaseDate"),
            base_set_size=row.get("baseSetSize", 0),
            total_set_size=row.get("totalSetSize", 0),
            block=row.get("block"),
            keyrune_code=keyrune_code,
        )

    @staticmethod
    def _decode_json_field(value: str | None) -> Any:
        """Safely decode JSON field from database.

        Args:
            value: JSON string from database field

        Returns:
            Decoded JSON value or None if invalid
        """
        if not value:
            return None

        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return None

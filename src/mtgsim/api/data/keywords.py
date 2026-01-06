"""Keywords data access layer."""

import json
from pathlib import Path


class KeywordsData:
    """Data access for MTG keywords."""

    def __init__(self):
        self._keywords: dict | None = None

    def _load_keywords(self):
        """Load keywords from JSON file."""
        if self._keywords is not None:
            return

        # Find Keywords.json in resources
        import mtgsim

        package_dir = Path(mtgsim.__file__).parent.parent.parent
        keywords_path = package_dir / "resources" / "Keywords.json"

        if keywords_path.exists():
            with open(keywords_path) as f:
                data = json.load(f)
                self._keywords = data.get("data", {})
        else:
            self._keywords = {}

    def get_ability_words(self) -> list[str]:
        """Get all ability words."""
        self._load_keywords()
        return self._keywords.get("abilityWords", [])

    def get_keyword_abilities(self) -> list[str]:
        """Get all keyword abilities."""
        self._load_keywords()
        return self._keywords.get("keywordAbilities", [])

    def get_keyword_actions(self) -> list[str]:
        """Get all keyword actions."""
        self._load_keywords()
        return self._keywords.get("keywordActions", [])

    def get_all_keywords(self) -> dict:
        """Get all keyword categories."""
        self._load_keywords()
        return {
            "ability_words": self.get_ability_words(),
            "keyword_abilities": self.get_keyword_abilities(),
            "keyword_actions": self.get_keyword_actions(),
        }


# Singleton instance
keywords_data = KeywordsData()

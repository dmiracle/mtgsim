"""Keywords data access layer."""

from mtgsim.reference import ref_db


class KeywordsData:
    """Data access for MTG keywords from database."""

    def _get_keywords_by_type(self, keyword_type: str) -> list[str]:
        """Get keywords of a specific type from database."""
        if not ref_db.is_initialized():
            return []

        cursor = ref_db.conn.execute(
            "SELECT keyword FROM keyword WHERE type = ? ORDER BY keyword",
            [keyword_type],
        )
        return [row["keyword"] for row in cursor.fetchall()]

    def get_ability_words(self) -> list[str]:
        """Get all ability words."""
        return self._get_keywords_by_type("abilityWords")

    def get_keyword_abilities(self) -> list[str]:
        """Get all keyword abilities."""
        return self._get_keywords_by_type("keywordAbilities")

    def get_keyword_actions(self) -> list[str]:
        """Get all keyword actions."""
        return self._get_keywords_by_type("keywordActions")

    def get_all_keywords(self) -> dict:
        """Get all keyword categories."""
        return {
            "ability_words": self.get_ability_words(),
            "keyword_abilities": self.get_keyword_abilities(),
            "keyword_actions": self.get_keyword_actions(),
        }

    def search_keywords(self, query: str) -> list[dict]:
        """Search keywords by partial match."""
        if not ref_db.is_initialized():
            return []

        cursor = ref_db.conn.execute(
            "SELECT keyword, type FROM keyword WHERE keyword LIKE ? ORDER BY keyword",
            [f"%{query}%"],
        )
        return [{"keyword": row["keyword"], "type": row["type"]} for row in cursor.fetchall()]

    def get_keyword_count(self) -> dict[str, int]:
        """Get count of keywords by type."""
        if not ref_db.is_initialized():
            return {}

        cursor = ref_db.conn.execute("SELECT type, COUNT(*) as count FROM keyword GROUP BY type")
        return {row["type"]: row["count"] for row in cursor.fetchall()}


# Singleton instance
keywords_data = KeywordsData()

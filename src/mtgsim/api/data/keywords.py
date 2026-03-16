"""Keywords data access layer."""

from mtgdb.models import MJKeyword
from mtgdb.session import get_session
from sqlmodel import func, select


class KeywordsData:
    """Data access for MTG keywords from database."""

    def _get_keywords_by_type(self, keyword_type: str) -> list[str]:
        """Get keywords of a specific type from database."""
        with get_session() as session:
            query = select(MJKeyword.name).where(MJKeyword.type == keyword_type).order_by(MJKeyword.name)
            return list(session.exec(query).all())

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
        with get_session() as session:
            q = select(MJKeyword.name, MJKeyword.type).where(MJKeyword.name.contains(query)).order_by(MJKeyword.name)
            results = session.exec(q).all()
            return [{"keyword": name, "type": kw_type} for name, kw_type in results]

    def get_keyword_count(self) -> dict[str, int]:
        """Get count of keywords by type."""
        with get_session() as session:
            query = select(MJKeyword.type, func.count()).group_by(MJKeyword.type)
            results = session.exec(query).all()
            return dict(results)

    def categorize_keyword_freq(self, keyword_freq: dict[str, int]) -> dict:
        """Categorize keyword frequencies into ability_words, keyword_abilities, keyword_actions."""
        if not keyword_freq:
            return {"ability_words": {}, "keyword_abilities": {}, "keyword_actions": {}}

        with get_session() as session:
            query = select(MJKeyword.name, MJKeyword.type).where(MJKeyword.name.in_(list(keyword_freq.keys())))
            type_map = dict(session.exec(query).all())

        result = {"ability_words": {}, "keyword_abilities": {}, "keyword_actions": {}}
        category_map = {
            "abilityWords": "ability_words",
            "keywordAbilities": "keyword_abilities",
            "keywordActions": "keyword_actions",
        }
        for kw, count in keyword_freq.items():
            kw_type = type_map.get(kw)
            category = category_map.get(kw_type, "keyword_abilities")
            result[category][kw] = count

        return result


# Singleton instance
keywords_data = KeywordsData()

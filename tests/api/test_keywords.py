"""Tests for keywords/glossary API endpoints."""


class TestGetKeywords:
    """Tests for GET /api/keywords endpoint."""

    def test_get_keywords_returns_200(self, client):
        """Basic request returns 200."""
        response = client.get("/api/keywords")
        assert response.status_code == 200

    def test_get_keywords_has_ability_words(self, client):
        """Response has ability words."""
        response = client.get("/api/keywords")
        data = response.json()

        assert "ability_words" in data
        assert isinstance(data["ability_words"], list)

    def test_get_keywords_has_keyword_abilities(self, client):
        """Response has keyword abilities."""
        response = client.get("/api/keywords")
        data = response.json()

        assert "keyword_abilities" in data
        assert isinstance(data["keyword_abilities"], list)

    def test_get_keywords_has_keyword_actions(self, client):
        """Response has keyword actions."""
        response = client.get("/api/keywords")
        data = response.json()

        assert "keyword_actions" in data
        assert isinstance(data["keyword_actions"], list)

    def test_get_keywords_ability_word_structure(self, client):
        """Ability words have correct structure."""
        response = client.get("/api/keywords")
        data = response.json()

        if data["ability_words"]:
            word = data["ability_words"][0]
            assert "term" in word
            assert "definition" in word

    def test_get_keywords_ability_word_term_is_string(self, client):
        """Ability word term is a string."""
        response = client.get("/api/keywords")
        data = response.json()

        if data["ability_words"]:
            word = data["ability_words"][0]
            assert isinstance(word["term"], str)
            assert len(word["term"]) > 0

    def test_get_keywords_ability_word_definition_is_string(self, client):
        """Ability word definition is a string."""
        response = client.get("/api/keywords")
        data = response.json()

        if data["ability_words"]:
            word = data["ability_words"][0]
            assert isinstance(word["definition"], str)
            # Definition may be empty since MTGJSON only provides terms

    def test_get_keywords_keyword_ability_structure(self, client):
        """Keyword abilities have correct structure."""
        response = client.get("/api/keywords")
        data = response.json()

        if data["keyword_abilities"]:
            keyword = data["keyword_abilities"][0]
            assert "term" in keyword
            assert "definition" in keyword

    def test_get_keywords_keyword_ability_term_is_string(self, client):
        """Keyword ability term is a string."""
        response = client.get("/api/keywords")
        data = response.json()

        if data["keyword_abilities"]:
            keyword = data["keyword_abilities"][0]
            assert isinstance(keyword["term"], str)
            assert len(keyword["term"]) > 0

    def test_get_keywords_keyword_ability_definition_is_string(self, client):
        """Keyword ability definition is a string."""
        response = client.get("/api/keywords")
        data = response.json()

        if data["keyword_abilities"]:
            keyword = data["keyword_abilities"][0]
            assert isinstance(keyword["definition"], str)
            # Definition may be empty since MTGJSON only provides terms

    def test_get_keywords_keyword_action_structure(self, client):
        """Keyword actions have correct structure."""
        response = client.get("/api/keywords")
        data = response.json()

        if data["keyword_actions"]:
            action = data["keyword_actions"][0]
            assert "term" in action
            assert "definition" in action

    def test_get_keywords_keyword_action_term_is_string(self, client):
        """Keyword action term is a string."""
        response = client.get("/api/keywords")
        data = response.json()

        if data["keyword_actions"]:
            action = data["keyword_actions"][0]
            assert isinstance(action["term"], str)
            assert len(action["term"]) > 0

    def test_get_keywords_keyword_action_definition_is_string(self, client):
        """Keyword action definition is a string."""
        response = client.get("/api/keywords")
        data = response.json()

        if data["keyword_actions"]:
            action = data["keyword_actions"][0]
            assert isinstance(action["definition"], str)
            # Definition may be empty since MTGJSON only provides terms

    def test_get_keywords_contains_common_abilities(self, client):
        """Response contains common keyword abilities."""
        response = client.get("/api/keywords")
        data = response.json()

        ability_terms = [k["term"].lower() for k in data["keyword_abilities"]]
        # Should have common abilities like flying, trample, etc.
        common_abilities = ["flying", "trample", "haste"]
        for ability in common_abilities:
            assert ability in ability_terms, f"Missing common ability: {ability}"

    def test_get_keywords_contains_common_actions(self, client):
        """Response contains common keyword actions."""
        response = client.get("/api/keywords")
        data = response.json()

        action_terms = [k["term"].lower() for k in data["keyword_actions"]]
        # Should have common actions like destroy, exile, etc.
        common_actions = ["destroy", "exile", "sacrifice"]
        for action in common_actions:
            assert action in action_terms, f"Missing common action: {action}"


class TestGetFormats:
    """Tests for GET /api/keywords/formats endpoint."""

    def test_get_formats_returns_200(self, client):
        """Basic request returns 200."""
        response = client.get("/api/keywords/formats")
        assert response.status_code == 200

    def test_get_formats_has_formats_list(self, client):
        """Response has formats list."""
        response = client.get("/api/keywords/formats")
        data = response.json()

        assert "formats" in data
        assert isinstance(data["formats"], list)

    def test_get_formats_not_empty(self, client):
        """Formats list is not empty."""
        response = client.get("/api/keywords/formats")
        data = response.json()

        assert len(data["formats"]) > 0

    def test_get_formats_format_has_id(self, client):
        """Each format has an id."""
        response = client.get("/api/keywords/formats")
        data = response.json()

        for fmt in data["formats"]:
            assert "id" in fmt
            assert isinstance(fmt["id"], str)

    def test_get_formats_format_has_name(self, client):
        """Each format has a name."""
        response = client.get("/api/keywords/formats")
        data = response.json()

        for fmt in data["formats"]:
            assert "name" in fmt
            assert isinstance(fmt["name"], str)

    def test_get_formats_format_has_description(self, client):
        """Each format has a description."""
        response = client.get("/api/keywords/formats")
        data = response.json()

        for fmt in data["formats"]:
            assert "description" in fmt
            assert isinstance(fmt["description"], str)

    def test_get_formats_format_has_deck_count(self, client):
        """Each format has a deck count."""
        response = client.get("/api/keywords/formats")
        data = response.json()

        for fmt in data["formats"]:
            assert "deck_count" in fmt
            assert isinstance(fmt["deck_count"], int)
            assert fmt["deck_count"] >= 0

    def test_get_formats_contains_standard(self, client):
        """Formats includes Standard."""
        response = client.get("/api/keywords/formats")
        data = response.json()

        format_ids = [f["id"] for f in data["formats"]]
        assert "standard" in format_ids

    def test_get_formats_contains_pioneer(self, client):
        """Formats includes Pioneer."""
        response = client.get("/api/keywords/formats")
        data = response.json()

        format_ids = [f["id"] for f in data["formats"]]
        assert "pioneer" in format_ids

    def test_get_formats_contains_modern(self, client):
        """Formats includes Modern."""
        response = client.get("/api/keywords/formats")
        data = response.json()

        format_ids = [f["id"] for f in data["formats"]]
        assert "modern" in format_ids

    def test_get_formats_contains_legacy(self, client):
        """Formats includes Legacy."""
        response = client.get("/api/keywords/formats")
        data = response.json()

        format_ids = [f["id"] for f in data["formats"]]
        assert "legacy" in format_ids

    def test_get_formats_contains_vintage(self, client):
        """Formats includes Vintage."""
        response = client.get("/api/keywords/formats")
        data = response.json()

        format_ids = [f["id"] for f in data["formats"]]
        assert "vintage" in format_ids

    def test_get_formats_contains_commander(self, client):
        """Formats includes Commander."""
        response = client.get("/api/keywords/formats")
        data = response.json()

        format_ids = [f["id"] for f in data["formats"]]
        assert "commander" in format_ids

    def test_get_formats_unique_ids(self, client):
        """Format ids are unique."""
        response = client.get("/api/keywords/formats")
        data = response.json()

        format_ids = [f["id"] for f in data["formats"]]
        assert len(format_ids) == len(set(format_ids))

"""Tests for card API endpoints."""


class TestSearchCards:
    """Tests for GET /api/cards endpoint."""

    def test_search_cards_returns_200(self, client):
        """Basic request returns 200."""
        response = client.get("/api/cards")
        assert response.status_code == 200

    def test_search_cards_returns_paginated_response(self, client):
        """Response has correct structure."""
        response = client.get("/api/cards")
        data = response.json()

        assert "data" in data
        assert "pagination" in data
        assert isinstance(data["data"], list)

    def test_search_cards_pagination_metadata(self, client):
        """Pagination metadata is correct."""
        response = client.get("/api/cards?page=1&limit=10")
        data = response.json()

        assert data["pagination"]["page"] == 1
        assert data["pagination"]["limit"] == 10
        assert "total" in data["pagination"]
        assert "pages" in data["pagination"]

    def test_search_cards_by_name(self, client, sample_search_query):
        """Search by card name works."""
        response = client.get(f"/api/cards?q={sample_search_query}")
        assert response.status_code == 200

    def test_search_cards_by_partial_name(self, client):
        """Partial name search works."""
        response = client.get("/api/cards?q=bolt")
        assert response.status_code == 200

    def test_search_cards_filter_by_set(self, client, sample_set_code):
        """Filter by set code works."""
        response = client.get(f"/api/cards?set={sample_set_code}")
        assert response.status_code == 200

    def test_search_cards_filter_by_rarity_common(self, client):
        """Filter by common rarity works."""
        response = client.get("/api/cards?rarity=common")
        assert response.status_code == 200

    def test_search_cards_filter_by_rarity_uncommon(self, client):
        """Filter by uncommon rarity works."""
        response = client.get("/api/cards?rarity=uncommon")
        assert response.status_code == 200

    def test_search_cards_filter_by_rarity_rare(self, client):
        """Filter by rare rarity works."""
        response = client.get("/api/cards?rarity=rare")
        assert response.status_code == 200

    def test_search_cards_filter_by_rarity_mythic(self, client):
        """Filter by mythic rarity works."""
        response = client.get("/api/cards?rarity=mythic")
        assert response.status_code == 200

    def test_search_cards_filter_by_type_creature(self, client):
        """Filter by creature type works."""
        response = client.get("/api/cards?type=Creature")
        assert response.status_code == 200

    def test_search_cards_filter_by_type_instant(self, client):
        """Filter by instant type works."""
        response = client.get("/api/cards?type=Instant")
        assert response.status_code == 200

    def test_search_cards_filter_by_type_sorcery(self, client):
        """Filter by sorcery type works."""
        response = client.get("/api/cards?type=Sorcery")
        assert response.status_code == 200

    def test_search_cards_filter_by_type_land(self, client):
        """Filter by land type works."""
        response = client.get("/api/cards?type=Land")
        assert response.status_code == 200

    def test_search_cards_filter_by_multiple_types_is_union(self, client):
        """type=Creature,Instant unions to (Creature OR Instant), not intersect."""
        creature = client.get("/api/cards?type=Creature&limit=1").json()
        instant = client.get("/api/cards?type=Instant&limit=1").json()
        both = client.get("/api/cards?type=Creature,Instant&limit=1").json()
        c_total = creature["pagination"]["total"]
        i_total = instant["pagination"]["total"]
        both_total = both["pagination"]["total"]
        assert both_total >= max(c_total, i_total)
        assert both_total <= c_total + i_total

    def test_search_cards_filter_by_colors_single(self, client):
        """Filter by single color works."""
        response = client.get("/api/cards?colors=W")
        assert response.status_code == 200

    def test_search_cards_filter_by_colors_multiple(self, client):
        """Filter by multiple colors works."""
        response = client.get("/api/cards?colors=WU")
        assert response.status_code == 200

    def test_search_cards_filter_by_price_range(self, client):
        """Filter by price range works."""
        response = client.get("/api/cards?price_min=1&price_max=10")
        assert response.status_code == 200

    def test_search_cards_filter_by_price_min_only(self, client):
        """Filter by minimum price only works."""
        response = client.get("/api/cards?price_min=5")
        assert response.status_code == 200

    def test_search_cards_filter_by_price_max_only(self, client):
        """Filter by maximum price only works."""
        response = client.get("/api/cards?price_max=10")
        assert response.status_code == 200

    def test_search_cards_sort_by_name_asc(self, client):
        """Sort by name ascending works."""
        response = client.get("/api/cards?sort=name&order=asc")
        assert response.status_code == 200

    def test_search_cards_sort_by_name_desc(self, client):
        """Sort by name descending works."""
        response = client.get("/api/cards?sort=name&order=desc")
        assert response.status_code == 200

    def test_search_cards_sort_by_price(self, client):
        """Sort by price works."""
        response = client.get("/api/cards?sort=price&order=desc")
        assert response.status_code == 200

    def test_search_cards_sort_by_mana_value(self, client):
        """Sort by mana value works."""
        response = client.get("/api/cards?sort=mana_value&order=asc")
        assert response.status_code == 200

    def test_search_cards_combined_filters(self, client):
        """Multiple filters combined work."""
        response = client.get("/api/cards?q=dragon&rarity=rare&colors=R&sort=price&order=desc")
        assert response.status_code == 200

    def test_search_cards_pagination_page_2(self, client):
        """Page 2 pagination works."""
        response = client.get("/api/cards?page=2&limit=20")
        assert response.status_code == 200

    def test_search_cards_limit_validation(self, client):
        """Limit cannot exceed 100."""
        response = client.get("/api/cards?limit=200")
        assert response.status_code == 422

    def test_search_cards_invalid_order(self, client):
        """Invalid order value is rejected."""
        response = client.get("/api/cards?order=invalid")
        assert response.status_code == 422

    def test_search_cards_card_summary_structure(self, client):
        """Card summary has correct fields."""
        response = client.get("/api/cards")
        data = response.json()

        if data["data"]:
            card = data["data"][0]
            assert "uuid" in card
            assert "name" in card
            assert "type" in card
            assert "mana_cost" in card
            assert "rarity" in card
            assert "set_code" in card
            assert "color_identity" in card

    def test_search_cards_filter_by_tags(self, client):
        """Filter by oracle tags works."""
        response = client.get("/api/cards?tags=mana-dork")
        assert response.status_code == 200

    def test_search_cards_filter_by_multiple_tags(self, client):
        """Filter by multiple oracle tags works."""
        response = client.get("/api/cards?tags=mana-dork,ramp")
        assert response.status_code == 200

    def test_search_cards_card_summary_has_tags(self, client):
        """Card summary includes tags field."""
        response = client.get("/api/cards")
        data = response.json()

        if data["data"]:
            card = data["data"][0]
            assert "tags" in card
            assert isinstance(card["tags"], list)


class TestCardStats:
    """Tests for GET /api/cards/stats endpoint."""

    def test_stats_returns_200(self, client):
        response = client.get("/api/cards/stats")
        assert response.status_code == 200

    def test_stats_response_structure(self, client):
        data = client.get("/api/cards/stats").json()
        assert "total" in data
        assert "mana_curve" in data
        assert "type_distribution" in data
        assert "rarity_distribution" in data
        assert "color_distribution" in data
        assert "price_stats" in data
        assert data["total"] > 0

    def test_stats_with_set_filter(self, client, sample_set_code):
        data = client.get(f"/api/cards/stats?set={sample_set_code}").json()
        assert data["total"] > 0
        assert len(data["mana_curve"]) > 0

    def test_stats_with_rarity_filter(self, client):
        data = client.get("/api/cards/stats?rarity=mythic").json()
        assert data["total"] > 0
        assert data["rarity_distribution"].get("mythic", 0) == data["total"]

    def test_stats_mana_curve_is_dict(self, client, sample_set_code):
        data = client.get(f"/api/cards/stats?set={sample_set_code}").json()
        curve = data["mana_curve"]
        assert isinstance(curve, dict)
        for key in curve:
            assert key.isdigit()

    def test_stats_price_stats_fields(self, client, sample_set_code):
        data = client.get(f"/api/cards/stats?set={sample_set_code}").json()
        ps = data["price_stats"]
        assert "total" in ps
        assert "average" in ps
        assert "median" in ps

    def test_stats_with_type_filter(self, client, sample_set_code):
        data = client.get(f"/api/cards/stats?set={sample_set_code}&type=Creature").json()
        assert data["total"] > 0
        assert "Creature" in data["type_distribution"]

    def test_stats_unique_dedup(self, client, sample_set_code):
        all_data = client.get(f"/api/cards/stats?set={sample_set_code}").json()
        unique_data = client.get(f"/api/cards/stats?set={sample_set_code}&unique=true").json()
        assert unique_data["total"] <= all_data["total"]

    def test_stats_text_filter_applies(self, client):
        """Stats endpoint honors the text filter (was silently dropped)."""
        bare = client.get("/api/cards/stats?rarity=mythic&unique=true").json()
        with_text = client.get("/api/cards/stats?rarity=mythic&unique=true&text=enchantment").json()
        assert with_text["total"] < bare["total"]

    def test_stats_total_matches_cards_listing(self, client):
        """Filtered total from /cards/stats must equal /cards pagination.total under the same filters."""
        qs = "type=Creature&rarity=mythic&format=standard&unique=true&text=enchantment"
        cards = client.get(f"/api/cards?{qs}&limit=1").json()
        stats = client.get(f"/api/cards/stats?{qs}").json()
        assert stats["total"] == cards["pagination"]["total"]


class TestUniqueCanonicalPick:
    """Regression: unique=true must pick a canonical printing that respects every filter."""

    def test_unique_does_not_drop_cards_with_cheaper_offrarity_reprints(self, client):
        """Cards whose cheapest standard printing is rare but also have a mythic
        printing must still appear when filtering rarity=mythic with unique=true.

        Concrete case: Enduring Courage in DSK ships as both rare ($2.32 normal)
        and mythic. Before fix, the unique row-number picked the cheapest printing
        (rare) and the main query's rarity=mythic filter then dropped the card.
        """
        qs = "type=Creature&rarity=mythic&format=standard&unique=true&text=enchantment"
        data = client.get(f"/api/cards?{qs}&limit=100").json()
        names = [c["name"] for c in data["data"]]
        assert "Enduring Courage" in names


class TestFtsBooleanSearch:
    """The text= filter passes FTS5 boolean syntax through (AND / OR / NOT / parens / phrase)."""

    def test_escape_emits_quoted_tokens(self):
        from mtgsim.api.data.helpers import _escape_fts_query

        assert _escape_fts_query("flying lifelink") == '"flying" "lifelink"'
        assert _escape_fts_query("flying AND lifelink") == '"flying" AND "lifelink"'
        assert _escape_fts_query("flying OR lifelink") == '"flying" OR "lifelink"'
        assert _escape_fts_query("flying NOT vigilance") == '"flying" NOT "vigilance"'
        assert _escape_fts_query("flying and lifelink") == '"flying" AND "lifelink"'  # case-insensitive ops
        assert _escape_fts_query("enchant*") == '"enchant"*'
        assert _escape_fts_query('"trigger an ability"') == '"trigger an ability"'
        assert _escape_fts_query("(flying OR reach) AND lifelink") == '( "flying" OR "reach" ) AND "lifelink"'
        assert _escape_fts_query("") == ""
        assert _escape_fts_query("flying-lifelink") == '"flying-lifelink"'  # hyphens stay literal

    def test_and_narrows_results(self, client):
        flying = client.get("/api/cards?text=flying&limit=1").json()["pagination"]["total"]
        lifelink = client.get("/api/cards?text=lifelink&limit=1").json()["pagination"]["total"]
        both = client.get("/api/cards?text=flying+AND+lifelink&limit=1").json()["pagination"]["total"]
        assert both < flying
        assert both < lifelink

    def test_or_broadens_results(self, client):
        flying = client.get("/api/cards?text=flying&limit=1").json()["pagination"]["total"]
        either = client.get("/api/cards?text=flying+OR+lifelink&limit=1").json()["pagination"]["total"]
        assert either >= flying

    def test_not_excludes_results(self, client):
        flying = client.get("/api/cards?text=flying&limit=1").json()["pagination"]["total"]
        without = client.get("/api/cards?text=flying+NOT+vigilance&limit=1").json()["pagination"]["total"]
        assert without < flying

    def test_parens_group_correctly(self, client):
        grouped = client.get("/api/cards", params={"text": "(flying OR reach) AND lifelink", "limit": 1}).json()
        assert grouped["pagination"]["total"] > 0


class TestGetTags:
    """Tests for GET /api/cards/tags endpoint."""

    def test_get_tags_returns_200(self, client):
        """Tags endpoint returns 200."""
        response = client.get("/api/cards/tags")
        assert response.status_code == 200

    def test_get_tags_returns_list(self, client):
        """Tags endpoint returns a list."""
        response = client.get("/api/cards/tags")
        data = response.json()
        assert isinstance(data, list)

    def test_get_tags_entry_structure(self, client):
        """Tag entries have tag and count fields."""
        response = client.get("/api/cards/tags")
        data = response.json()
        if data:
            assert "tag" in data[0]
            assert "count" in data[0]


class TestGetCard:
    """Tests for GET /api/cards/{uuid} endpoint."""

    def test_get_card_returns_200(self, client, sample_card_uuid):
        """Valid card UUID returns 200."""
        response = client.get(f"/api/cards/{sample_card_uuid}")
        assert response.status_code == 200

    def test_get_card_returns_detail_structure(self, client, sample_card_uuid):
        """Response has correct structure."""
        response = client.get(f"/api/cards/{sample_card_uuid}")
        data = response.json()

        assert "uuid" in data
        assert "name" in data
        assert "all_prices" in data
        assert "legalities" in data

    def test_get_card_basic_fields(self, client, sample_card_uuid):
        """Card has basic fields."""
        response = client.get(f"/api/cards/{sample_card_uuid}")
        data = response.json()

        assert "uuid" in data
        assert "name" in data
        assert "mana_cost" in data
        assert "mana_value" in data
        assert "type" in data
        assert "types" in data
        assert "rarity" in data
        assert "set_code" in data

    def test_get_card_text_fields(self, client, sample_card_uuid):
        """Card has text fields."""
        response = client.get(f"/api/cards/{sample_card_uuid}")
        data = response.json()

        assert "text" in data
        assert "flavor_text" in data

    def test_get_card_color_fields(self, client, sample_card_uuid):
        """Card has color fields."""
        response = client.get(f"/api/cards/{sample_card_uuid}")
        data = response.json()

        assert "color_identity" in data
        assert "colors" in data
        assert isinstance(data["color_identity"], list)
        assert isinstance(data["colors"], list)

    def test_get_card_creature_fields(self, client, sample_card_uuid):
        """Card has power/toughness fields."""
        response = client.get(f"/api/cards/{sample_card_uuid}")
        data = response.json()

        assert "power" in data
        assert "toughness" in data

    def test_get_card_prices_structure(self, client, sample_card_uuid):
        """Card prices have correct structure."""
        response = client.get(f"/api/cards/{sample_card_uuid}")
        data = response.json()

        all_prices = data["all_prices"]
        assert isinstance(all_prices, list)
        if all_prices:
            assert "provider" in all_prices[0]
            assert "price" in all_prices[0]

    def test_get_card_legalities_structure(self, client, sample_card_uuid):
        """Card legalities have correct structure."""
        response = client.get(f"/api/cards/{sample_card_uuid}")
        data = response.json()

        legalities = data["legalities"]
        assert "standard" in legalities
        assert "pioneer" in legalities
        assert "modern" in legalities
        assert "legacy" in legalities
        assert "vintage" in legalities
        assert "commander" in legalities

    def test_get_card_deck_appearances(self, client, sample_card_uuid):
        """Card has deck appearances list."""
        response = client.get(f"/api/cards/{sample_card_uuid}")
        data = response.json()

        assert "appears_in_decks" in data
        assert isinstance(data["appears_in_decks"], list)

    def test_get_card_deck_appearance_structure(self, client, sample_card_uuid):
        """Deck appearance has correct structure."""
        response = client.get(f"/api/cards/{sample_card_uuid}")
        data = response.json()

        if data["appears_in_decks"]:
            appearance = data["appears_in_decks"][0]
            assert "file" in appearance
            assert "name" in appearance
            assert "count" in appearance

    def test_get_card_other_printings(self, client, sample_card_uuid):
        """Card has other printings list."""
        response = client.get(f"/api/cards/{sample_card_uuid}")
        data = response.json()

        assert "other_printings" in data
        assert isinstance(data["other_printings"], list)

    def test_get_card_other_printing_structure(self, client, sample_card_uuid):
        """Other printing has correct structure."""
        response = client.get(f"/api/cards/{sample_card_uuid}")
        data = response.json()

        if data["other_printings"]:
            printing = data["other_printings"][0]
            assert "set_code" in printing
            assert "set_name" in printing
            assert "uuid" in printing

    def test_get_card_has_tags(self, client, sample_card_uuid):
        """Card detail includes tags field."""
        response = client.get(f"/api/cards/{sample_card_uuid}")
        data = response.json()

        assert "tags" in data
        assert isinstance(data["tags"], list)

    def test_get_card_image_url(self, client, sample_card_uuid):
        """Card has image URL."""
        response = client.get(f"/api/cards/{sample_card_uuid}")
        data = response.json()

        assert "image_url" in data

    def test_get_card_not_found(self, client):
        """Non-existent card returns 404."""
        response = client.get("/api/cards/not-a-real-uuid")
        assert response.status_code == 404

    def test_get_card_not_found_error_format(self, client):
        """404 error has correct format."""
        response = client.get("/api/cards/not-a-real-uuid")
        data = response.json()

        assert "error" in data
        assert "code" in data["error"]
        assert "message" in data["error"]

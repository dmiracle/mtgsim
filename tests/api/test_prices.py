"""Tests for price API endpoints."""


class TestSearchPrices:
    """Tests for GET /api/prices endpoint."""

    def test_search_prices_returns_200(self, client):
        """Basic request returns 200."""
        response = client.get("/api/prices")
        assert response.status_code == 200

    def test_search_prices_returns_paginated_response(self, client):
        """Response has correct structure."""
        response = client.get("/api/prices")
        data = response.json()

        assert "data" in data
        assert "pagination" in data
        assert isinstance(data["data"], list)

    def test_search_prices_has_meta(self, client):
        """Response has meta field."""
        response = client.get("/api/prices")
        data = response.json()

        assert "meta" in data
        assert "total_cards_with_prices" in data["meta"]

    def test_search_prices_pagination_metadata(self, client):
        """Pagination metadata is correct."""
        response = client.get("/api/prices?page=1&limit=10")
        data = response.json()

        assert data["pagination"]["page"] == 1
        assert data["pagination"]["limit"] == 10
        assert "total" in data["pagination"]
        assert "pages" in data["pagination"]

    def test_search_prices_by_name(self, client, sample_search_query):
        """Search by card name works."""
        response = client.get(f"/api/prices?q={sample_search_query}")
        assert response.status_code == 200

    def test_search_prices_filter_by_set(self, client, sample_set_code):
        """Filter by set code works."""
        response = client.get(f"/api/prices?set={sample_set_code}")
        assert response.status_code == 200

    def test_search_prices_filter_by_rarity_common(self, client):
        """Filter by common rarity works."""
        response = client.get("/api/prices?rarity=common")
        assert response.status_code == 200

    def test_search_prices_filter_by_rarity_rare(self, client):
        """Filter by rare rarity works."""
        response = client.get("/api/prices?rarity=rare")
        assert response.status_code == 200

    def test_search_prices_filter_by_rarity_mythic(self, client):
        """Filter by mythic rarity works."""
        response = client.get("/api/prices?rarity=mythic")
        assert response.status_code == 200

    def test_search_prices_filter_by_price_range(self, client):
        """Filter by price range works."""
        response = client.get("/api/prices?price_min=1&price_max=10")
        assert response.status_code == 200

    def test_search_prices_filter_by_price_min_only(self, client):
        """Filter by minimum price only works."""
        response = client.get("/api/prices?price_min=5")
        assert response.status_code == 200

    def test_search_prices_filter_by_price_max_only(self, client):
        """Filter by maximum price only works."""
        response = client.get("/api/prices?price_max=10")
        assert response.status_code == 200

    def test_search_prices_sort_by_average_usd_desc(self, client):
        """Sort by average USD price descending (default) works."""
        response = client.get("/api/prices?sort=average_usd&order=desc")
        assert response.status_code == 200

    def test_search_prices_sort_by_average_usd_asc(self, client):
        """Sort by average USD price ascending works."""
        response = client.get("/api/prices?sort=average_usd&order=asc")
        assert response.status_code == 200

    def test_search_prices_sort_by_tcgplayer(self, client):
        """Sort by TCGplayer price works."""
        response = client.get("/api/prices?sort=tcgplayer&order=desc")
        assert response.status_code == 200

    def test_search_prices_sort_by_cardkingdom(self, client):
        """Sort by Card Kingdom price works."""
        response = client.get("/api/prices?sort=cardkingdom&order=desc")
        assert response.status_code == 200

    def test_search_prices_combined_filters(self, client, sample_set_code):
        """Multiple filters combined work."""
        response = client.get(f"/api/prices?set={sample_set_code}&rarity=rare&price_min=1&sort=average_usd&order=desc")
        assert response.status_code == 200

    def test_search_prices_pagination_page_2(self, client):
        """Page 2 pagination works."""
        response = client.get("/api/prices?page=2&limit=20")
        assert response.status_code == 200

    def test_search_prices_limit_validation(self, client):
        """Limit cannot exceed 100."""
        response = client.get("/api/prices?limit=200")
        assert response.status_code == 422

    def test_search_prices_invalid_order(self, client):
        """Invalid order value is rejected."""
        response = client.get("/api/prices?order=invalid")
        assert response.status_code == 422

    def test_search_prices_price_summary_structure(self, client):
        """Price summary has correct fields."""
        response = client.get("/api/prices")
        data = response.json()

        if data["data"]:
            price = data["data"][0]
            assert "uuid" in price
            assert "name" in price
            assert "set_code" in price
            assert "rarity" in price
            assert "prices" in price
            assert "average_usd" in price

    def test_search_prices_has_source_prices(self, client):
        """Price summary includes source prices in prices object."""
        response = client.get("/api/prices")
        data = response.json()

        if data["data"]:
            price = data["data"][0]
            # Prices are nested under "prices" object
            prices = price.get("prices", {})
            # Should have at least one price source
            has_prices = any(
                prices.get(source) is not None
                for source in ["tcgplayer", "cardkingdom", "cardsphere", "cardmarket", "mtgo"]
            )
            assert has_prices or price.get("average_usd") is not None


class TestGetPrice:
    """Tests for GET /api/prices/{uuid} endpoint."""

    def test_get_price_returns_200(self, client, sample_card_uuid):
        """Valid card UUID returns 200."""
        response = client.get(f"/api/prices/{sample_card_uuid}")
        assert response.status_code == 200

    def test_get_price_returns_detail_structure(self, client, sample_card_uuid):
        """Response has correct structure."""
        response = client.get(f"/api/prices/{sample_card_uuid}")
        data = response.json()

        assert "uuid" in data
        assert "name" in data
        assert "set_code" in data
        assert "paper" in data
        assert "mtgo" in data

    def test_get_price_card_identification(self, client, sample_card_uuid):
        """Price detail identifies the card."""
        response = client.get(f"/api/prices/{sample_card_uuid}")
        data = response.json()

        assert "uuid" in data
        assert "name" in data
        assert "set_code" in data

    def test_get_price_paper_structure(self, client, sample_card_uuid):
        """Paper prices have correct structure."""
        response = client.get(f"/api/prices/{sample_card_uuid}")
        data = response.json()

        paper = data.get("paper")
        if paper:
            # Paper should be a dict with expected provider keys
            assert isinstance(paper, dict)
            for source in ["tcgplayer", "cardkingdom", "cardsphere", "cardmarket"]:
                assert source in paper

    def test_get_price_tcgplayer_structure(self, client, sample_card_uuid):
        """TCGplayer prices structure."""
        response = client.get(f"/api/prices/{sample_card_uuid}")
        data = response.json()

        if data.get("paper") and data["paper"].get("tcgplayer"):
            tcg = data["paper"]["tcgplayer"]
            # Should have retail and/or buylist
            assert "retail" in tcg or "buylist" in tcg

    def test_get_price_tcgplayer_retail(self, client, sample_card_uuid):
        """TCGplayer retail prices structure."""
        response = client.get(f"/api/prices/{sample_card_uuid}")
        data = response.json()

        if data.get("paper") and data["paper"].get("tcgplayer"):
            tcg = data["paper"]["tcgplayer"]
            if tcg.get("retail"):
                # Retail should have normal and/or foil
                assert "normal" in tcg["retail"] or "foil" in tcg["retail"]

    def test_get_price_tcgplayer_buylist(self, client, sample_card_uuid):
        """TCGplayer buylist prices structure."""
        response = client.get(f"/api/prices/{sample_card_uuid}")
        data = response.json()

        if data.get("paper") and data["paper"].get("tcgplayer"):
            tcg = data["paper"]["tcgplayer"]
            if tcg.get("buylist"):
                # Buylist should have normal and/or foil
                assert "normal" in tcg["buylist"] or "foil" in tcg["buylist"]

    def test_get_price_cardkingdom_structure(self, client, sample_card_uuid):
        """Card Kingdom prices structure."""
        response = client.get(f"/api/prices/{sample_card_uuid}")
        data = response.json()

        if data.get("paper") and data["paper"].get("cardkingdom"):
            ck = data["paper"]["cardkingdom"]
            # Should have retail and/or buylist
            assert "retail" in ck or "buylist" in ck

    def test_get_price_cardkingdom_retail(self, client, sample_card_uuid):
        """Card Kingdom retail prices."""
        response = client.get(f"/api/prices/{sample_card_uuid}")
        data = response.json()

        if data.get("paper") and data["paper"].get("cardkingdom"):
            ck = data["paper"]["cardkingdom"]
            if ck.get("retail"):
                # Retail should have normal/foil
                assert "normal" in ck["retail"] or "foil" in ck["retail"]

    def test_get_price_cardkingdom_buylist(self, client, sample_card_uuid):
        """Card Kingdom buylist prices."""
        response = client.get(f"/api/prices/{sample_card_uuid}")
        data = response.json()

        if data.get("paper") and data["paper"].get("cardkingdom"):
            ck = data["paper"]["cardkingdom"]
            if ck.get("buylist"):
                # Buylist should have normal/foil
                assert "normal" in ck["buylist"] or "foil" in ck["buylist"]

    def test_get_price_cardsphere_structure(self, client, sample_card_uuid):
        """Cardsphere prices structure."""
        response = client.get(f"/api/prices/{sample_card_uuid}")
        data = response.json()

        if data.get("paper") and data["paper"].get("cardsphere"):
            cs = data["paper"]["cardsphere"]
            # Should have retail
            assert "retail" in cs

    def test_get_price_cardmarket_structure(self, client, sample_card_uuid):
        """Cardmarket prices structure (EUR)."""
        response = client.get(f"/api/prices/{sample_card_uuid}")
        data = response.json()

        if data.get("paper") and data["paper"].get("cardmarket"):
            cm = data["paper"]["cardmarket"]
            # Should have retail pricing
            assert "retail" in cm

    def test_get_price_mtgo_structure(self, client, sample_card_uuid):
        """MTGO prices structure."""
        response = client.get(f"/api/prices/{sample_card_uuid}")
        data = response.json()

        mtgo = data.get("mtgo")
        # MTGO should have cardhoarder or be empty dict/None
        assert mtgo is None or isinstance(mtgo, dict)

    def test_get_price_mtgo_cardhoarder(self, client, sample_card_uuid):
        """MTGO Cardhoarder prices."""
        response = client.get(f"/api/prices/{sample_card_uuid}")
        data = response.json()

        if data.get("mtgo") and data["mtgo"].get("cardhoarder"):
            ch = data["mtgo"]["cardhoarder"]
            # Should have retail
            assert "retail" in ch

    def test_get_price_history_structure(self, client, sample_card_uuid):
        """Price history structure (if available)."""
        response = client.get(f"/api/prices/{sample_card_uuid}")
        data = response.json()

        # History may or may not be present
        if "price_history" in data and data["price_history"]:
            assert isinstance(data["price_history"], list)
            if data["price_history"]:
                entry = data["price_history"][0]
                assert "date" in entry

    def test_get_price_not_found(self, client):
        """Non-existent card returns 404."""
        response = client.get("/api/prices/not-a-real-uuid")
        assert response.status_code == 404

    def test_get_price_not_found_error_format(self, client):
        """404 error has correct format."""
        response = client.get("/api/prices/not-a-real-uuid")
        data = response.json()

        assert "error" in data
        assert "code" in data["error"]
        assert "message" in data["error"]

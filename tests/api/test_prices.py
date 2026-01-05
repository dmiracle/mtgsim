"""Tests for price API endpoints."""

import pytest


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
            assert "average_usd" in price

    def test_search_prices_has_source_prices(self, client):
        """Price summary includes source prices."""
        response = client.get("/api/prices")
        data = response.json()

        if data["data"]:
            price = data["data"][0]
            # Should have at least one price source
            assert "tcgplayer" in price or "cardkingdom" in price or "cardsphere" in price


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
        assert "set_name" in data
        assert "rarity" in data

    def test_get_price_paper_structure(self, client, sample_card_uuid):
        """Paper prices have correct structure."""
        response = client.get(f"/api/prices/{sample_card_uuid}")
        data = response.json()

        paper = data["paper"]
        # Should have TCGplayer prices
        if "tcgplayer" in paper:
            tcg = paper["tcgplayer"]
            assert "normal" in tcg or "retail" in tcg

    def test_get_price_tcgplayer_normal(self, client, sample_card_uuid):
        """TCGplayer normal prices structure."""
        response = client.get(f"/api/prices/{sample_card_uuid}")
        data = response.json()

        if "tcgplayer" in data["paper"]:
            tcg = data["paper"]["tcgplayer"]
            if "normal" in tcg and tcg["normal"]:
                # Price should be a number or None
                assert tcg["normal"] is None or isinstance(tcg["normal"], (int, float))

    def test_get_price_tcgplayer_foil(self, client, sample_card_uuid):
        """TCGplayer foil prices structure."""
        response = client.get(f"/api/prices/{sample_card_uuid}")
        data = response.json()

        if "tcgplayer" in data["paper"]:
            tcg = data["paper"]["tcgplayer"]
            if "foil" in tcg:
                assert tcg["foil"] is None or isinstance(tcg["foil"], (int, float))

    def test_get_price_cardkingdom_structure(self, client, sample_card_uuid):
        """Card Kingdom prices structure."""
        response = client.get(f"/api/prices/{sample_card_uuid}")
        data = response.json()

        if "cardkingdom" in data["paper"]:
            ck = data["paper"]["cardkingdom"]
            # Should have retail and/or buylist
            assert "retail" in ck or "buylist" in ck

    def test_get_price_cardkingdom_retail(self, client, sample_card_uuid):
        """Card Kingdom retail prices."""
        response = client.get(f"/api/prices/{sample_card_uuid}")
        data = response.json()

        if "cardkingdom" in data["paper"]:
            ck = data["paper"]["cardkingdom"]
            if "retail" in ck and ck["retail"]:
                # Retail should have normal/foil
                assert "normal" in ck["retail"] or "foil" in ck["retail"]

    def test_get_price_cardkingdom_buylist(self, client, sample_card_uuid):
        """Card Kingdom buylist prices."""
        response = client.get(f"/api/prices/{sample_card_uuid}")
        data = response.json()

        if "cardkingdom" in data["paper"]:
            ck = data["paper"]["cardkingdom"]
            if "buylist" in ck and ck["buylist"]:
                # Buylist should have normal/foil
                assert "normal" in ck["buylist"] or "foil" in ck["buylist"]

    def test_get_price_cardsphere_structure(self, client, sample_card_uuid):
        """Cardsphere prices structure."""
        response = client.get(f"/api/prices/{sample_card_uuid}")
        data = response.json()

        if "cardsphere" in data["paper"]:
            cs = data["paper"]["cardsphere"]
            # Should have normal/foil
            assert "normal" in cs or "foil" in cs

    def test_get_price_cardmarket_structure(self, client, sample_card_uuid):
        """Cardmarket prices structure (EUR)."""
        response = client.get(f"/api/prices/{sample_card_uuid}")
        data = response.json()

        if "cardmarket" in data["paper"]:
            cm = data["paper"]["cardmarket"]
            # Should have retail pricing
            assert "retail" in cm

    def test_get_price_mtgo_structure(self, client, sample_card_uuid):
        """MTGO prices structure."""
        response = client.get(f"/api/prices/{sample_card_uuid}")
        data = response.json()

        mtgo = data["mtgo"]
        # MTGO should have cardhoarder or be empty dict
        assert isinstance(mtgo, dict)

    def test_get_price_mtgo_cardhoarder(self, client, sample_card_uuid):
        """MTGO Cardhoarder prices."""
        response = client.get(f"/api/prices/{sample_card_uuid}")
        data = response.json()

        if "cardhoarder" in data["mtgo"]:
            ch = data["mtgo"]["cardhoarder"]
            # Should have normal/foil
            assert "normal" in ch or "foil" in ch

    def test_get_price_average_calculated(self, client, sample_card_uuid):
        """Average USD is calculated."""
        response = client.get(f"/api/prices/{sample_card_uuid}")
        data = response.json()

        assert "average_usd" in data
        if data["average_usd"] is not None:
            assert isinstance(data["average_usd"], (int, float))

    def test_get_price_history_structure(self, client, sample_card_uuid):
        """Price history structure (if available)."""
        response = client.get(f"/api/prices/{sample_card_uuid}")
        data = response.json()

        # History may or may not be present
        if "history" in data and data["history"]:
            assert isinstance(data["history"], list)
            if data["history"]:
                entry = data["history"][0]
                assert "date" in entry
                assert "price" in entry

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

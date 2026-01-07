"""Property-based tests for domain to API model conversion.

**Feature: domain-api-consolidation, Property 6: Domain to API Model Conversion**
**Validates: Requirements 3.4, 4.3**

Tests that domain models can be consistently converted to valid API model responses
with all required fields and proper data types.
"""

from datetime import datetime

from hypothesis import given
from hypothesis import strategies as st

from mtgsim.api.data.converters import (
    create_readonly_domain_card,
    domain_card_to_api_dict,
    domain_set_to_api_dict,
    reference_card_to_api_dict,
    reference_card_to_domain,
)
from mtgsim.db.domain_models import DomainCard, DomainSet
from mtgsim.db.reference_models import MTGJsonCard


class TestDomainToApiModelConversion:
    """Test that domain models convert correctly to API response formats."""

    @given(
        uuid=st.text(min_size=36, max_size=36),  # UUID format
        name=st.text(min_size=1, max_size=100),
        mana_cost=st.one_of(st.none(), st.text(min_size=1, max_size=20)),
        mana_value=st.one_of(st.none(), st.floats(min_value=0, max_value=20)),
        type_line=st.one_of(st.none(), st.text(min_size=1, max_size=100)),
        rarity=st.sampled_from(["common", "uncommon", "rare", "mythic"]),
        set_code=st.one_of(st.none(), st.text(min_size=3, max_size=5)),
        price=st.one_of(st.none(), st.floats(min_value=0, max_value=1000)),
    )
    def test_domain_card_to_api_conversion_completeness(
        self, uuid, name, mana_cost, mana_value, type_line, rarity, set_code, price
    ):
        """
        Property 6: Domain to API Model Conversion

        For any valid domain card, converting it to API format should produce
        a dictionary with all required fields and proper data types.

        **Validates: Requirements 3.4, 4.3**
        """
        # Create a domain card with the generated data
        domain_card = DomainCard(
            uuid=uuid,
            name=name,
            mana_cost=mana_cost,
            mana_value=mana_value,
            type_line=type_line,
            rarity=rarity,
            set_code=set_code,
            tcgplayer_price_usd=price,
            added_at=datetime.utcnow(),
        )

        # Convert to API format
        api_dict = domain_card_to_api_dict(domain_card)

        # Verify result is a dictionary
        assert isinstance(api_dict, dict), "API conversion should return a dictionary"

        # Verify all required fields are present
        required_fields = [
            "uuid",
            "name",
            "mana_cost",
            "mana_value",
            "type",
            "rarity",
            "set_code",
            "color_identity",
            "colors",
            "power",
            "toughness",
            "text",
            "legalities",
            "price",
            "in_collection",
        ]

        for field in required_fields:
            assert field in api_dict, f"API dict should contain {field} field"

        # Verify data types and values
        assert isinstance(api_dict["uuid"], str), "UUID should be string"
        assert api_dict["uuid"] == uuid, "UUID should match original"

        assert isinstance(api_dict["name"], str), "Name should be string"
        assert api_dict["name"] == name, "Name should match original"

        assert api_dict["mana_cost"] == mana_cost, "Mana cost should match original"
        assert api_dict["mana_value"] == mana_value, "Mana value should match original"

        assert isinstance(api_dict["rarity"], str), "Rarity should be string"
        assert api_dict["rarity"] == rarity, "Rarity should match original"

        assert isinstance(api_dict["color_identity"], list), "Color identity should be list"
        assert isinstance(api_dict["colors"], list), "Colors should be list"
        assert isinstance(api_dict["legalities"], dict), "Legalities should be dict"

        assert isinstance(api_dict["in_collection"], bool), "in_collection should be boolean"
        assert api_dict["in_collection"] is True, "Domain cards should be in collection"

        assert api_dict["price"] == price, "Price should match original"

        # Domain-specific fields should be present
        assert "is_owned" in api_dict, "Should have is_owned field"
        assert "quantity_owned" in api_dict, "Should have quantity_owned field"
        assert "is_wanted" in api_dict, "Should have is_wanted field"
        assert "added_at" in api_dict, "Should have added_at field"

    @given(
        uuid=st.text(min_size=36, max_size=36),
        name=st.text(min_size=1, max_size=100),
        mana_cost=st.one_of(st.none(), st.text(min_size=1, max_size=20)),
        rarity=st.sampled_from(["common", "uncommon", "rare", "mythic"]),
        set_code=st.one_of(st.none(), st.text(min_size=3, max_size=5)),
    )
    def test_reference_card_to_api_conversion_completeness(self, uuid, name, mana_cost, rarity, set_code):
        """
        Property 6: Domain to API Model Conversion

        For any valid reference card, converting it to API format should produce
        a dictionary with all required fields and proper data types.

        **Validates: Requirements 3.4, 4.3**
        """
        # Create a reference card with the generated data
        ref_card = MTGJsonCard(
            uuid=uuid,
            name=name,
            mana_cost=mana_cost,
            rarity=rarity,
            set_code=set_code,
        )

        # Convert to API format
        api_dict = reference_card_to_api_dict(ref_card)

        # Verify result is a dictionary
        assert isinstance(api_dict, dict), "API conversion should return a dictionary"

        # Verify all required fields are present
        required_fields = [
            "uuid",
            "name",
            "mana_cost",
            "type",
            "rarity",
            "set_code",
            "color_identity",
            "colors",
            "legalities",
            "price",
            "in_collection",
        ]

        for field in required_fields:
            assert field in api_dict, f"API dict should contain {field} field"

        # Verify data types and values
        assert isinstance(api_dict["uuid"], str), "UUID should be string"
        assert api_dict["uuid"] == uuid, "UUID should match original"

        assert isinstance(api_dict["name"], str), "Name should be string"
        assert api_dict["name"] == name, "Name should match original"

        assert api_dict["mana_cost"] == mana_cost, "Mana cost should match original"
        assert api_dict["rarity"] == rarity, "Rarity should match original"

        assert isinstance(api_dict["color_identity"], list), "Color identity should be list"
        assert isinstance(api_dict["colors"], list), "Colors should be list"
        assert isinstance(api_dict["legalities"], dict), "Legalities should be dict"

        assert isinstance(api_dict["in_collection"], bool), "in_collection should be boolean"
        assert api_dict["in_collection"] is False, "Reference cards should not be in collection"

        assert api_dict["price"] is None, "Reference cards should not have pricing"

        # Reference-specific fields should be present
        assert "edhrec_rank" in api_dict, "Should have edhrec_rank field"
        assert "edhrec_saltiness" in api_dict, "Should have edhrec_saltiness field"

    @given(
        code=st.text(min_size=3, max_size=5),
        name=st.text(min_size=1, max_size=100),
        set_type=st.sampled_from(["core", "expansion", "masters", "draft_innovation"]),
        base_set_size=st.integers(min_value=0, max_value=500),
        total_set_size=st.integers(min_value=0, max_value=500),
    )
    def test_domain_set_to_api_conversion_completeness(self, code, name, set_type, base_set_size, total_set_size):
        """
        Property 6: Domain to API Model Conversion

        For any valid domain set, converting it to API format should produce
        a dictionary with all required fields and proper data types.

        **Validates: Requirements 3.4, 4.3**
        """
        # Ensure total_set_size >= base_set_size
        if total_set_size < base_set_size:
            total_set_size = base_set_size

        # Create a domain set with the generated data
        domain_set = DomainSet(
            code=code,
            name=name,
            type=set_type,
            base_set_size=base_set_size,
            total_set_size=total_set_size,
            added_at=datetime.utcnow(),
        )

        # Convert to API format
        api_dict = domain_set_to_api_dict(domain_set)

        # Verify result is a dictionary
        assert isinstance(api_dict, dict), "API conversion should return a dictionary"

        # Verify all required fields are present
        required_fields = [
            "code",
            "name",
            "type",
            "base_set_size",
            "total_set_size",
            "languages",
            "translations",
            "in_collection",
        ]

        for field in required_fields:
            assert field in api_dict, f"API dict should contain {field} field"

        # Verify data types and values
        assert isinstance(api_dict["code"], str), "Code should be string"
        assert api_dict["code"] == code, "Code should match original"

        assert isinstance(api_dict["name"], str), "Name should be string"
        assert api_dict["name"] == name, "Name should match original"

        assert isinstance(api_dict["type"], str), "Type should be string"
        assert api_dict["type"] == set_type, "Type should match original"

        assert isinstance(api_dict["base_set_size"], int), "Base set size should be integer"
        assert api_dict["base_set_size"] == base_set_size, "Base set size should match original"

        assert isinstance(api_dict["total_set_size"], int), "Total set size should be integer"
        assert api_dict["total_set_size"] == total_set_size, "Total set size should match original"

        assert isinstance(api_dict["languages"], list), "Languages should be list"
        assert isinstance(api_dict["translations"], dict), "Translations should be dict"

        assert isinstance(api_dict["in_collection"], bool), "in_collection should be boolean"
        assert api_dict["in_collection"] is True, "Domain sets should be in collection"

        # Domain-specific aggregated fields should be present
        assert "total_price" in api_dict, "Should have total_price field"
        assert "average_price" in api_dict, "Should have average_price field"
        assert "card_count_by_rarity" in api_dict, "Should have card_count_by_rarity field"
        assert "color_distribution" in api_dict, "Should have color_distribution field"
        assert "added_at" in api_dict, "Should have added_at field"

    def test_reference_to_domain_conversion_preserves_data(self):
        """
        Property 6: Domain to API Model Conversion

        Converting a reference model to domain model and then to API format
        should preserve all the original data fields.

        **Validates: Requirements 3.4, 4.3**
        """
        # Create a reference card with known data
        ref_card = MTGJsonCard(
            uuid="12345678-1234-1234-1234-123456789012",
            name="Test Card",
            mana_cost="{2}{U}",
            mana_value=3.0,
            type="Creature — Human Wizard",
            rarity="rare",
            set_code="TST",
            power="2",
            toughness="3",
            color_identity=["U"],
            colors=["U"],
            legalities={"standard": "Legal", "modern": "Legal"},
        )

        # Convert to domain model
        domain_card = reference_card_to_domain(ref_card)

        # Verify domain model preserves reference data
        assert domain_card.uuid == ref_card.uuid, "UUID should be preserved"
        assert domain_card.name == ref_card.name, "Name should be preserved"
        assert domain_card.mana_cost == ref_card.mana_cost, "Mana cost should be preserved"
        assert domain_card.mana_value == ref_card.mana_value, "Mana value should be preserved"
        assert domain_card.type_line == ref_card.type, "Type should be preserved"
        assert domain_card.rarity == ref_card.rarity, "Rarity should be preserved"
        assert domain_card.set_code == ref_card.set_code, "Set code should be preserved"
        assert domain_card.power == ref_card.power, "Power should be preserved"
        assert domain_card.toughness == ref_card.toughness, "Toughness should be preserved"
        assert domain_card.legalities == ref_card.legalities, "Legalities should be preserved"

        # Convert domain model to API format
        api_dict = domain_card_to_api_dict(domain_card)

        # Verify API format preserves original reference data
        assert api_dict["uuid"] == ref_card.uuid, "API UUID should match reference"
        assert api_dict["name"] == ref_card.name, "API name should match reference"
        assert api_dict["mana_cost"] == ref_card.mana_cost, "API mana cost should match reference"
        assert api_dict["mana_value"] == ref_card.mana_value, "API mana value should match reference"
        assert api_dict["type"] == ref_card.type, "API type should match reference"
        assert api_dict["rarity"] == ref_card.rarity, "API rarity should match reference"
        assert api_dict["set_code"] == ref_card.set_code, "API set code should match reference"
        assert api_dict["power"] == ref_card.power, "API power should match reference"
        assert api_dict["toughness"] == ref_card.toughness, "API toughness should match reference"
        assert api_dict["legalities"] == ref_card.legalities, "API legalities should match reference"

    def test_readonly_domain_card_conversion(self):
        """
        Property 6: Domain to API Model Conversion

        Creating a read-only domain card from a reference card should produce
        a valid API format with domain-like structure but marked as not in collection.

        **Validates: Requirements 3.4, 4.3**
        """
        # Create a reference card
        ref_card = MTGJsonCard(
            uuid="12345678-1234-1234-1234-123456789012",
            name="Test Card",
            mana_cost="{1}{R}",
            rarity="common",
            set_code="TST",
        )

        # Convert to read-only domain format
        readonly_dict = create_readonly_domain_card(ref_card)

        # Verify it has the structure of a domain card API response
        assert isinstance(readonly_dict, dict), "Should return a dictionary"
        assert readonly_dict["in_collection"] is False, "Should not be in collection"

        # Should have domain-like fields with default values
        assert "is_owned" in readonly_dict, "Should have is_owned field"
        assert readonly_dict["is_owned"] is False, "Should not be owned"

        assert "quantity_owned" in readonly_dict, "Should have quantity_owned field"
        assert readonly_dict["quantity_owned"] == 0, "Should have zero quantity"

        assert "is_wanted" in readonly_dict, "Should have is_wanted field"
        assert readonly_dict["is_wanted"] is False, "Should not be wanted"

        assert "added_at" in readonly_dict, "Should have added_at field"
        assert readonly_dict["added_at"] is None, "Should have null added_at"

        # Should preserve reference card data
        assert readonly_dict["uuid"] == ref_card.uuid, "Should preserve UUID"
        assert readonly_dict["name"] == ref_card.name, "Should preserve name"
        assert readonly_dict["mana_cost"] == ref_card.mana_cost, "Should preserve mana cost"
        assert readonly_dict["rarity"] == ref_card.rarity, "Should preserve rarity"

    @given(
        field_name=st.sampled_from(["uuid", "name", "type_line", "rarity", "set_code"]),
        field_value=st.one_of(st.none(), st.text(min_size=1, max_size=50)),
    )
    def test_api_conversion_handles_optional_fields(self, field_name, field_value):
        """
        Property 6: Domain to API Model Conversion

        API conversion should handle optional/nullable fields gracefully,
        preserving None values and not causing errors.

        **Validates: Requirements 3.4, 4.3**
        """
        # Create a minimal domain card
        domain_card = DomainCard(
            uuid="12345678-1234-1234-1234-123456789012",
            name="Test Card",
        )

        # Set the specific field to the generated value
        setattr(domain_card, field_name, field_value)

        # Convert to API format (should not raise exceptions)
        api_dict = domain_card_to_api_dict(domain_card)

        # Verify conversion succeeded
        assert isinstance(api_dict, dict), "Conversion should succeed"

        # Verify the field value is preserved (even if None)
        if field_name == "type_line":
            # type_line maps to "type" in API
            assert "type" in api_dict, "Type field should be present in API"
            assert api_dict["type"] == field_value, "Type field should preserve value"
        else:
            assert field_name in api_dict, f"Field {field_name} should be present"
            assert api_dict[field_name] == field_value, f"Field {field_name} should preserve value"

    def test_conversion_consistency_across_model_types(self):
        """
        Property 6: Domain to API Model Conversion

        Converting the same logical entity through different model types
        (reference vs domain) should produce consistent API representations.

        **Validates: Requirements 3.4, 4.3**
        """
        # Create a reference card
        ref_card = MTGJsonCard(
            uuid="12345678-1234-1234-1234-123456789012",
            name="Lightning Bolt",
            mana_cost="{R}",
            mana_value=1.0,
            type="Instant",
            rarity="common",
            set_code="LEA",
            color_identity=["R"],
            colors=["R"],
        )

        # Convert reference card directly to API
        ref_api = reference_card_to_api_dict(ref_card)

        # Convert reference to domain, then to API
        domain_card = reference_card_to_domain(ref_card)
        domain_api = domain_card_to_api_dict(domain_card)

        # Core fields should be consistent between both API representations
        core_fields = ["uuid", "name", "mana_cost", "mana_value", "type", "rarity", "set_code"]

        for field in core_fields:
            ref_value = ref_api.get(field)
            domain_value = domain_api.get(field)

            assert ref_value == domain_value, (
                f"Field {field} should be consistent: ref={ref_value}, domain={domain_value}"
            )

        # Collection status should differ appropriately
        assert ref_api["in_collection"] is False, "Reference card should not be in collection"
        assert domain_api["in_collection"] is True, "Domain card should be in collection"

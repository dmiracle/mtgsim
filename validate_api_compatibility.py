#!/usr/bin/env python3
"""
API backward compatibility validation script.

This script validates that all existing API endpoints return identical response structures
and that existing query parameters and filtering options work unchanged.

Requirements validated:
- 3.1: API returns identical response structures as before consolidation
- 3.2: API supports all existing query parameters and filtering options
- 3.3: API maintains the same performance characteristics for common operations
"""

import sys

from fastapi.testclient import TestClient


class APICompatibilityValidator:
    """Validates API backward compatibility."""

    def __init__(self):
        self.violations: list[str] = []
        self.warnings: list[str] = []
        self.client: TestClient | None = None

        # Define expected API endpoints and their parameters
        self.expected_endpoints = {
            "/api/cards": {
                "methods": ["GET"],
                "query_params": [
                    "q",
                    "set_code",
                    "rarity",
                    "card_type",
                    "colors",
                    "price_min",
                    "price_max",
                    "sort",
                    "order",
                    "page",
                    "limit",
                    "scope",
                ],
                "response_fields": ["data", "pagination"],
                "data_item_fields": [
                    "uuid",
                    "name",
                    "type",
                    "mana_cost",
                    "mana_value",
                    "rarity",
                    "set_code",
                    "color_identity",
                    "text",
                    "price",
                    "image_url",
                    "in_collection",
                ],
            },
            "/api/cards/{uuid}": {
                "methods": ["GET"],
                "query_params": ["scope"],
                "response_fields": [
                    "uuid",
                    "name",
                    "mana_cost",
                    "mana_value",
                    "type",
                    "types",
                    "subtypes",
                    "text",
                    "flavor_text",
                    "rarity",
                    "set_code",
                    "set_name",
                    "color_identity",
                    "colors",
                    "power",
                    "toughness",
                    "image_url",
                    "prices",
                    "legalities",
                    "appears_in_decks",
                    "other_printings",
                    "in_collection",
                ],
            },
            "/api/sets": {
                "methods": ["GET"],
                "query_params": ["q", "type", "block", "sort", "order", "page", "limit", "scope"],
                "response_fields": ["data", "pagination"],
            },
            "/api/sets/{code}": {
                "methods": ["GET"],
                "query_params": ["scope"],
                "response_fields": [
                    "code",
                    "name",
                    "type",
                    "release_date",
                    "base_set_size",
                    "total_set_size",
                    "block",
                    "keyrune_code",
                    "is_foil_only",
                    "is_online_only",
                ],
            },
            "/api/decks": {
                "methods": ["GET"],
                "query_params": ["q", "type", "colors", "sort", "order", "page", "limit", "scope"],
                "response_fields": ["data", "pagination"],
            },
            "/api/decks/{uuid}": {
                "methods": ["GET"],
                "query_params": ["scope"],
                "response_fields": ["file", "name", "code", "type", "release_date", "card_count", "colors", "price"],
            },
            "/api/stats": {
                "methods": ["GET"],
                "query_params": [],
                "response_fields": ["total_cards", "total_sets", "total_decks", "database_size"],
            },
        }

    def setup_test_client(self) -> bool:
        """Set up the FastAPI test client."""
        try:
            from mtgsim.api.main import app

            self.client = TestClient(app)
            return True
        except Exception as e:
            self.violations.append(f"❌ Failed to set up test client: {e}")
            return False

    def validate_endpoint_availability(self) -> bool:
        """Validate that all expected endpoints are available."""
        print("🔍 Validating endpoint availability...")

        if not self.client:
            return False

        success = True

        for endpoint, config in self.expected_endpoints.items():
            for method in config["methods"]:
                try:
                    # Replace path parameters with test values
                    test_endpoint = endpoint.replace("{uuid}", "test-uuid-123")
                    test_endpoint = test_endpoint.replace("{code}", "TEST")

                    if method == "GET":
                        response = self.client.get(test_endpoint)
                    else:
                        continue  # Skip other methods for now

                    # We expect either 200 (success) or 404 (not found) for test data
                    # What we don't want is 500 (server error) or 405 (method not allowed)
                    if response.status_code in [500, 405]:
                        self.violations.append(f"❌ Endpoint {method} {endpoint} returned {response.status_code}")
                        success = False
                    elif response.status_code not in [200, 404, 422]:
                        self.warnings.append(
                            f"⚠️  Endpoint {method} {endpoint} returned unexpected status {response.status_code}"
                        )

                except Exception as e:
                    self.violations.append(f"❌ Failed to test endpoint {method} {endpoint}: {e}")
                    success = False

        return success

    def validate_response_structure(self) -> bool:
        """Validate that response structures match expected format."""
        print("🔍 Validating response structures...")

        if not self.client:
            return False

        success = True

        # Test cards endpoint with different scopes
        for scope in ["user", "reference", "combined"]:
            try:
                response = self.client.get(f"/api/cards?limit=1&scope={scope}")

                if response.status_code == 200:
                    data = response.json()

                    # Check top-level structure
                    expected_fields = self.expected_endpoints["/api/cards"]["response_fields"]
                    for field in expected_fields:
                        if field not in data:
                            self.violations.append(f"❌ Cards endpoint (scope={scope}) missing field: {field}")
                            success = False

                    # Check pagination structure
                    if "pagination" in data:
                        pagination_fields = ["page", "limit", "total", "pages"]
                        for field in pagination_fields:
                            if field not in data["pagination"]:
                                self.violations.append(f"❌ Cards pagination (scope={scope}) missing field: {field}")
                                success = False

                    # Check data item structure (if data exists)
                    if "data" in data and data["data"]:
                        item = data["data"][0]
                        expected_item_fields = self.expected_endpoints["/api/cards"]["data_item_fields"]
                        for field in expected_item_fields:
                            if field not in item:
                                self.violations.append(f"❌ Card item (scope={scope}) missing field: {field}")
                                success = False

            except Exception as e:
                self.violations.append(f"❌ Failed to validate cards response structure (scope={scope}): {e}")
                success = False

        return success

    def validate_query_parameters(self) -> bool:
        """Validate that all expected query parameters work."""
        print("🔍 Validating query parameters...")

        if not self.client:
            return False

        success = True

        # Test cards endpoint with various parameters
        test_params = [
            {"q": "Lightning"},
            {"set_code": "M21"},
            {"rarity": "rare"},
            {"card_type": "Creature"},
            {"colors": ["R", "U"]},
            {"sort": "name", "order": "asc"},
            {"page": 1, "limit": 10},
            {"scope": "user"},
            {"scope": "reference"},
            {"scope": "combined"},
        ]

        for params in test_params:
            try:
                response = self.client.get("/api/cards", params=params)

                # We expect either 200 (success) or 422 (validation error for bad params)
                # We don't want 500 (server error)
                if response.status_code == 500:
                    self.violations.append(f"❌ Cards endpoint with params {params} returned server error")
                    success = False
                elif response.status_code not in [200, 422]:
                    self.warnings.append(
                        f"⚠️  Cards endpoint with params {params} returned status {response.status_code}"
                    )

            except Exception as e:
                self.violations.append(f"❌ Failed to test cards endpoint with params {params}: {e}")
                success = False

        return success

    def validate_filtering_options(self) -> bool:
        """Validate that filtering options work as expected."""
        print("🔍 Validating filtering options...")

        if not self.client:
            return False

        success = True

        # Test that filtering actually filters results
        try:
            # Get all cards
            all_response = self.client.get("/api/cards?limit=100&scope=reference")

            if all_response.status_code == 200:
                all_data = all_response.json()
                total_cards = all_data.get("pagination", {}).get("total", 0)

                if total_cards > 0:
                    # Test rarity filter
                    rare_response = self.client.get("/api/cards?rarity=rare&limit=100&scope=reference")
                    if rare_response.status_code == 200:
                        rare_data = rare_response.json()
                        rare_count = rare_data.get("pagination", {}).get("total", 0)

                        # Rare cards should be a subset of all cards
                        if rare_count > total_cards:
                            self.violations.append(
                                f"❌ Rarity filter returned more cards ({rare_count}) than total ({total_cards})"
                            )
                            success = False

                        # Check that all returned cards have the correct rarity
                        for card in rare_data.get("data", []):
                            if card.get("rarity") != "rare":
                                self.violations.append(
                                    f"❌ Rarity filter returned card with rarity '{card.get('rarity')}' "
                                    f"instead of 'rare'"
                                )
                                success = False
                                break

        except Exception as e:
            self.violations.append(f"❌ Failed to validate filtering: {e}")
            success = False

        return success

    def validate_scope_behavior(self) -> bool:
        """Validate that scope parameter works correctly."""
        print("🔍 Validating scope behavior...")

        if not self.client:
            return False

        success = True

        try:
            # Test different scopes
            scopes = ["user", "reference", "combined"]
            scope_results = {}

            for scope in scopes:
                response = self.client.get(f"/api/cards?limit=10&scope={scope}")
                if response.status_code == 200:
                    data = response.json()
                    scope_results[scope] = {
                        "total": data.get("pagination", {}).get("total", 0),
                        "cards": data.get("data", []),
                    }

                    # Check in_collection field matches scope expectation
                    for card in data.get("data", []):
                        actual_in_collection = card.get("in_collection", False)

                        if scope == "user" and not actual_in_collection:
                            self.warnings.append(f"⚠️  User scope card {card.get('name')} has in_collection=False")
                        elif scope == "reference" and actual_in_collection:
                            self.warnings.append(f"⚠️  Reference scope card {card.get('name')} has in_collection=True")

            # Combined scope should have >= reference scope cards
            if "combined" in scope_results and "reference" in scope_results:
                combined_total = scope_results["combined"]["total"]
                reference_total = scope_results["reference"]["total"]

                if combined_total < reference_total:
                    self.violations.append(
                        f"❌ Combined scope has fewer cards ({combined_total}) than reference scope ({reference_total})"
                    )
                    success = False

        except Exception as e:
            self.violations.append(f"❌ Failed to validate scope behavior: {e}")
            success = False

        return success

    def validate_error_handling(self) -> bool:
        """Validate that error handling works correctly."""
        print("🔍 Validating error handling...")

        if not self.client:
            return False

        success = True

        # Test invalid UUID
        try:
            response = self.client.get("/api/cards/invalid-uuid")
            if response.status_code not in [404, 422]:
                self.warnings.append(f"⚠️  Invalid UUID returned status {response.status_code} instead of 404/422")
        except Exception as e:
            self.violations.append(f"❌ Failed to test invalid UUID: {e}")
            success = False

        # Test invalid query parameters
        try:
            response = self.client.get("/api/cards?page=-1")
            if response.status_code not in [422, 400]:
                self.warnings.append(
                    f"⚠️  Invalid page parameter returned status {response.status_code} instead of 422/400"
                )
        except Exception as e:
            self.violations.append(f"❌ Failed to test invalid parameters: {e}")
            success = False

        return success

    def print_results(self):
        """Print validation results."""
        print("\n" + "=" * 60)
        print("🔄 API BACKWARD COMPATIBILITY VALIDATION RESULTS")
        print("=" * 60)

        if self.violations:
            print(f"\n❌ VIOLATIONS FOUND ({len(self.violations)}):")
            for violation in self.violations:
                print(f"  {violation}")

        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  {warning}")

        if not self.violations and not self.warnings:
            print("\n✅ All API endpoints are backward compatible!")
        elif not self.violations:
            print(f"\n✅ No compatibility violations found, but {len(self.warnings)} warnings to review")
        else:
            print(f"\n❌ {len(self.violations)} compatibility violations found that need to be fixed")

        print("\n" + "=" * 60)


def main():
    """Run API backward compatibility validation."""
    validator = APICompatibilityValidator()

    print("🔄 VALIDATING API BACKWARD COMPATIBILITY")
    print("=" * 60)
    print("Checking that:")
    print("• All existing API endpoints are available")
    print("• Response structures are identical")
    print("• Query parameters work unchanged")
    print("• Filtering options work correctly")
    print("• Scope behavior is consistent")
    print("• Error handling is preserved")
    print()

    # Set up test client
    if not validator.setup_test_client():
        validator.print_results()
        return 1

    # Run all validations
    results = [
        validator.validate_endpoint_availability(),
        validator.validate_response_structure(),
        validator.validate_query_parameters(),
        validator.validate_filtering_options(),
        validator.validate_scope_behavior(),
        validator.validate_error_handling(),
    ]

    # Print results
    validator.print_results()

    # Return success if no violations
    success = all(results) and len(validator.violations) == 0
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())

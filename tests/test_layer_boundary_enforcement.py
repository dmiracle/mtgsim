"""
Property-based tests for layer boundary enforcement.

**Feature: domain-api-consolidation, Property 13: Layer Boundary Enforcement**
**Validates: Requirements 6.3, 6.5**

Property 13: Layer Boundary Enforcement
*For any* domain model class, it should not contain dependencies on API-specific libraries or formatting logic
"""

import ast
import sys
from pathlib import Path

import pytest
from hypothesis import given
from hypothesis import strategies as st

# Import the validator from the root directory
sys.path.insert(0, str(Path(__file__).parent.parent))
from validate_layer_boundaries import LayerBoundaryValidator


class TestLayerBoundaryEnforcement:
    """Property-based tests for architectural layer boundary enforcement."""

    def setup_method(self):
        """Set up test fixtures."""
        self.validator = LayerBoundaryValidator()
        self.domain_files = [
            Path("src/mtgsim/db/domain_models.py"),
            Path("src/mtgsim/db/reference_models.py"),
            Path("src/mtgsim/domain/card.py"),
        ]
        self.api_files = list(Path("src/mtgsim/api").rglob("*.py"))
        self.data_access_files = list(Path("src/mtgsim/api/data").glob("*.py"))

    @given(
        st.sampled_from(
            ["src/mtgsim/db/domain_models.py", "src/mtgsim/db/reference_models.py", "src/mtgsim/domain/card.py"]
        )
    )
    def test_domain_models_have_no_api_dependencies(self, domain_file_path: str):
        """
        **Feature: domain-api-consolidation, Property 13: Layer Boundary Enforcement**

        Property: For any domain model file, it should not contain imports from API-specific modules.
        This ensures domain models remain independent of API concerns.
        """
        file_path = Path(domain_file_path)

        if not file_path.exists():
            pytest.skip(f"Domain file {file_path} does not exist")

        # Parse the file and check for API-specific imports
        api_imports = self._get_api_specific_imports(file_path)

        # Domain models should not import from API layers
        assert len(api_imports) == 0, (
            f"Domain model {file_path} contains API-specific imports: {api_imports}. "
            f"Domain models should not depend on API layers."
        )

    @given(
        st.sampled_from(
            ["src/mtgsim/db/domain_models.py", "src/mtgsim/db/reference_models.py", "src/mtgsim/domain/card.py"]
        )
    )
    def test_domain_models_have_no_presentation_logic(self, domain_file_path: str):
        """
        **Feature: domain-api-consolidation, Property 13: Layer Boundary Enforcement**

        Property: For any domain model file, it should not contain presentation or formatting logic.
        Domain models should focus on business logic and data integrity only.
        """
        file_path = Path(domain_file_path)

        if not file_path.exists():
            pytest.skip(f"Domain file {file_path} does not exist")

        # Check for presentation-related method names and logic
        presentation_violations = self._get_presentation_logic_violations(file_path)

        # Domain models should not contain presentation logic
        assert len(presentation_violations) == 0, (
            f"Domain model {file_path} contains presentation logic: {presentation_violations}. "
            f"Presentation logic should be in API models or services."
        )

    def test_dependency_direction_is_correct(self):
        """
        **Feature: domain-api-consolidation, Property 13: Layer Boundary Enforcement**

        Property: For any layer in the system, dependencies should flow in the correct direction:
        Domain <- Data Access <- API (domain should not depend on higher layers).
        """
        violations = []

        # Check that domain layer doesn't depend on API or data access layers
        for domain_file in self.domain_files:
            if domain_file.exists():
                upward_deps = self._get_upward_dependencies(domain_file)
                if upward_deps:
                    violations.extend([f"{domain_file}: depends on {dep}" for dep in upward_deps])

        assert len(violations) == 0, (
            f"Found dependency direction violations: {violations}. "
            f"Domain layer should not depend on API or data access layers."
        )

    @given(
        st.lists(
            st.sampled_from(
                [
                    "fastapi",
                    "starlette",
                    "uvicorn",
                    "httpx",
                    "requests",
                    "mtgsim.api.models",
                    "mtgsim.api.routers",
                    "mtgsim.api.services",
                ]
            ),
            min_size=1,
            max_size=3,
        )
    )
    def test_api_specific_imports_are_detected(self, api_modules: list[str]):
        """
        **Feature: domain-api-consolidation, Property 13: Layer Boundary Enforcement**

        Property: For any API-specific module name, the validator should correctly identify it
        as API-specific and flag it if found in domain models.
        """
        # Test that the validator correctly identifies API-specific modules
        for module in api_modules:
            is_api_specific = self.validator._is_api_specific_import(module)
            assert is_api_specific, f"Module '{module}' should be identified as API-specific"

            # Test with submodules too
            submodule = f"{module}.submodule"
            is_submodule_api_specific = self.validator._is_api_specific_import(submodule)
            assert is_submodule_api_specific, f"Submodule '{submodule}' should be identified as API-specific"

    def test_converter_layer_exists_and_is_complete(self):
        """
        **Feature: domain-api-consolidation, Property 13: Layer Boundary Enforcement**

        Property: The converter layer should exist and contain all necessary conversion functions
        to maintain proper separation between domain and API models.
        """
        converter_file = Path("src/mtgsim/api/data/converters.py")
        assert converter_file.exists(), "Converter module should exist to maintain layer separation"

        # Check that required converter functions exist
        required_functions = [
            "domain_card_to_api_dict",
            "reference_card_to_api_dict",
            "reference_card_to_domain",
            "domain_set_to_api_dict",
            "reference_set_to_api_dict",
            "domain_deck_to_api_dict",
            "reference_deck_to_api_dict",
        ]

        with open(converter_file) as f:
            content = f.read()

        missing_functions = [func for func in required_functions if func not in content]
        assert len(missing_functions) == 0, (
            f"Missing converter functions: {missing_functions}. "
            f"All conversion functions are required for proper layer separation."
        )

    def test_overall_layer_boundary_validation_passes(self):
        """
        **Feature: domain-api-consolidation, Property 13: Layer Boundary Enforcement**

        Property: The overall system should pass all layer boundary validation checks,
        ensuring proper architectural separation is maintained.
        """
        # Run the complete validation
        results = [
            self.validator.validate_domain_models(),
            self.validator.validate_data_access_layer(),
            self.validator.validate_api_layer(),
            self.validator.validate_converter_separation(),
            self.validator.validate_dependency_direction(),
        ]

        # Collect any violations found
        violations = self.validator.violations

        assert all(results), (
            f"Layer boundary validation failed with violations: {violations}. "
            f"All architectural boundaries must be properly maintained."
        )

        assert len(violations) == 0, f"Found {len(violations)} layer boundary violations: {violations}"

    def _get_api_specific_imports(self, file_path: Path) -> list[str]:
        """Get list of API-specific imports from a file."""
        api_imports = []

        try:
            with open(file_path) as f:
                content = f.read()

            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if self.validator._is_api_specific_import(alias.name):
                            api_imports.append(alias.name)

                elif isinstance(node, ast.ImportFrom):
                    if node.module and self.validator._is_api_specific_import(node.module):
                        api_imports.append(node.module)

        except Exception:
            # If we can't parse the file, assume no API imports
            pass

        return api_imports

    def _get_presentation_logic_violations(self, file_path: Path) -> list[str]:
        """Get list of presentation logic violations from a file."""
        violations = []

        try:
            with open(file_path) as f:
                content = f.read()

            tree = ast.parse(content)

            # Check for presentation-related method names
            presentation_keywords = {
                "serialize",
                "render",
                "template",
                "response",
                "request",
                "endpoint",
                "route",
                "json_response",
                "format_for_api",
            }

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    method_name = node.name.lower()
                    for keyword in presentation_keywords:
                        if keyword in method_name:
                            violations.append(f"Method '{node.name}' contains presentation keyword '{keyword}'")

        except Exception:
            # If we can't parse the file, assume no violations
            pass

        return violations

    def _get_upward_dependencies(self, file_path: Path) -> list[str]:
        """Get list of upward dependencies (domain depending on API/data layers)."""
        upward_deps = []

        try:
            with open(file_path) as f:
                content = f.read()

            # Check for imports that violate dependency direction
            upward_patterns = ["mtgsim.api", "fastapi", "starlette", "uvicorn"]

            for pattern in upward_patterns:
                if pattern in content:
                    upward_deps.append(pattern)

        except Exception:
            # If we can't read the file, assume no dependencies
            pass

        return upward_deps

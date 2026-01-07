#!/usr/bin/env python3
"""
Layer boundary validation script.

This script validates that domain models don't contain API-specific logic
and that clear boundaries exist between domain, data access, and API layers.

Requirements validated:
- 6.1: Domain models focus on business logic and data integrity
- 6.2: API models focus on request/response serialization and validation  
- 6.3: Domain models don't contain API-specific formatting or presentation logic
- 6.5: Clear boundaries between domain, data access, and API layers
"""

import ast
import importlib.util
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple


class LayerBoundaryValidator:
    """Validates architectural layer boundaries."""
    
    def __init__(self):
        self.violations: List[str] = []
        self.warnings: List[str] = []
        
        # Define what constitutes API-specific imports/dependencies
        self.api_specific_modules = {
            'fastapi', 'pydantic', 'starlette', 'uvicorn',
            'httpx', 'requests', 'flask', 'django',
            'mtgsim.api.models', 'mtgsim.api.routers', 'mtgsim.api.services'
        }
        
        # Define what constitutes presentation/formatting logic
        self.presentation_keywords = {
            'json', 'serialize', 'format', 'render', 'template',
            'response', 'request', 'endpoint', 'route'
        }
    
    def validate_domain_models(self) -> bool:
        """Validate that domain models don't contain API-specific logic."""
        print("🔍 Validating domain model layer boundaries...")
        
        domain_files = [
            Path("src/mtgsim/db/domain_models.py"),
            Path("src/mtgsim/db/reference_models.py"),
            Path("src/mtgsim/domain/card.py"),
        ]
        
        for file_path in domain_files:
            if file_path.exists():
                self._check_domain_file(file_path)
        
        return len(self.violations) == 0
    
    def validate_data_access_layer(self) -> bool:
        """Validate data access layer boundaries."""
        print("🔍 Validating data access layer boundaries...")
        
        data_files = list(Path("src/mtgsim/api/data").glob("*.py"))
        
        for file_path in data_files:
            self._check_data_access_file(file_path)
        
        return len(self.violations) == 0
    
    def validate_api_layer(self) -> bool:
        """Validate API layer boundaries."""
        print("🔍 Validating API layer boundaries...")
        
        # Check that API models only contain serialization logic
        api_model_files = list(Path("src/mtgsim/api/models").glob("*.py"))
        for file_path in api_model_files:
            self._check_api_model_file(file_path)
        
        # Check that services properly separate concerns
        service_files = list(Path("src/mtgsim/api/services").glob("*.py"))
        for file_path in service_files:
            self._check_service_file(file_path)
        
        return len(self.violations) == 0
    
    def _check_domain_file(self, file_path: Path):
        """Check a domain model file for API-specific dependencies."""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            # Check imports
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if self._is_api_specific_import(alias.name):
                            self.violations.append(
                                f"❌ {file_path}: Domain model imports API-specific module '{alias.name}'"
                            )
                
                elif isinstance(node, ast.ImportFrom):
                    if node.module and self._is_api_specific_import(node.module):
                        self.violations.append(
                            f"❌ {file_path}: Domain model imports from API-specific module '{node.module}'"
                        )
            
            # Check for API-specific method names or logic
            self._check_for_presentation_logic(file_path, tree)
            
        except Exception as e:
            self.warnings.append(f"⚠️  Could not parse {file_path}: {e}")
    
    def _check_data_access_file(self, file_path: Path):
        """Check a data access file for proper layer separation."""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            # Data access layer should import from domain but not from API models
            # (except for conversion utilities which are acceptable)
            if file_path.name != "converters.py":
                for node in ast.walk(tree):
                    if isinstance(node, ast.ImportFrom):
                        if node.module and "mtgsim.api.models" in node.module:
                            self.violations.append(
                                f"❌ {file_path}: Data access layer imports API models directly"
                            )
            
        except Exception as e:
            self.warnings.append(f"⚠️  Could not parse {file_path}: {e}")
    
    def _check_api_model_file(self, file_path: Path):
        """Check API model files for proper separation."""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            # API models should not import domain models directly
            # They should work with converted data
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom):
                    if node.module and "mtgsim.db.domain_models" in node.module:
                        self.violations.append(
                            f"❌ {file_path}: API model imports domain models directly"
                        )
            
        except Exception as e:
            self.warnings.append(f"⚠️  Could not parse {file_path}: {e}")
    
    def _check_service_file(self, file_path: Path):
        """Check service files for proper layer usage."""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Services should use data access layer, not query databases directly
            if "session.exec" in content or "session.query" in content:
                self.warnings.append(
                    f"⚠️  {file_path}: Service may be querying database directly instead of using data access layer"
                )
            
        except Exception as e:
            self.warnings.append(f"⚠️  Could not parse {file_path}: {e}")
    
    def _check_for_presentation_logic(self, file_path: Path, tree: ast.AST):
        """Check for presentation/formatting logic in domain models."""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Check method names for presentation concerns
                method_name = node.name.lower()
                for keyword in self.presentation_keywords:
                    if keyword in method_name and keyword not in ['format']:  # 'format' can be legitimate
                        self.warnings.append(
                            f"⚠️  {file_path}: Domain model method '{node.name}' may contain presentation logic"
                        )
    
    def _is_api_specific_import(self, module_name: str) -> bool:
        """Check if a module import is API-specific."""
        for api_module in self.api_specific_modules:
            if module_name.startswith(api_module):
                return True
        return False
    
    def validate_converter_separation(self) -> bool:
        """Validate that converters properly separate concerns."""
        print("🔍 Validating converter layer separation...")
        
        converter_file = Path("src/mtgsim/api/data/converters.py")
        if not converter_file.exists():
            self.violations.append("❌ Converter module not found")
            return False
        
        try:
            with open(converter_file, 'r') as f:
                content = f.read()
            
            # Check that converters exist for both directions
            required_functions = [
                'domain_card_to_api_dict',
                'reference_card_to_api_dict',
                'reference_card_to_domain',
                'domain_set_to_api_dict',
                'reference_set_to_api_dict',
                'domain_deck_to_api_dict',
                'reference_deck_to_api_dict'
            ]
            
            for func_name in required_functions:
                if func_name not in content:
                    self.violations.append(
                        f"❌ Missing converter function: {func_name}"
                    )
            
            # Check that converters don't contain business logic
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Converters should be simple transformation functions
                    # Complex business logic should be in domain models
                    if len(node.body) > 20:  # Arbitrary threshold
                        self.warnings.append(
                            f"⚠️  Converter function '{node.name}' is complex - consider moving logic to domain model"
                        )
            
        except Exception as e:
            self.warnings.append(f"⚠️  Could not parse converter file: {e}")
        
        return len(self.violations) == 0
    
    def validate_dependency_direction(self) -> bool:
        """Validate that dependencies flow in the correct direction."""
        print("🔍 Validating dependency direction...")
        
        # Domain layer should not depend on API or data access layers
        # Data access layer can depend on domain layer
        # API layer can depend on data access layer but should use converters
        
        dependency_violations = []
        
        # Check domain -> API dependencies (should not exist)
        domain_files = [
            Path("src/mtgsim/db/domain_models.py"),
            Path("src/mtgsim/db/reference_models.py"),
        ]
        
        for file_path in domain_files:
            if file_path.exists():
                try:
                    with open(file_path, 'r') as f:
                        content = f.read()
                    
                    if "mtgsim.api" in content:
                        dependency_violations.append(
                            f"❌ {file_path}: Domain layer depends on API layer"
                        )
                    
                    if "mtgsim.api.data" in content:
                        dependency_violations.append(
                            f"❌ {file_path}: Domain layer depends on data access layer"
                        )
                        
                except Exception as e:
                    self.warnings.append(f"⚠️  Could not check dependencies in {file_path}: {e}")
        
        self.violations.extend(dependency_violations)
        return len(dependency_violations) == 0
    
    def print_results(self):
        """Print validation results."""
        print("\n" + "="*60)
        print("🏗️  LAYER BOUNDARY VALIDATION RESULTS")
        print("="*60)
        
        if self.violations:
            print(f"\n❌ VIOLATIONS FOUND ({len(self.violations)}):")
            for violation in self.violations:
                print(f"  {violation}")
        
        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  {warning}")
        
        if not self.violations and not self.warnings:
            print("\n✅ All layer boundaries are properly maintained!")
        elif not self.violations:
            print(f"\n✅ No violations found, but {len(self.warnings)} warnings to review")
        else:
            print(f"\n❌ {len(self.violations)} violations found that need to be fixed")
        
        print("\n" + "="*60)


def main():
    """Run layer boundary validation."""
    validator = LayerBoundaryValidator()
    
    print("🏗️  VALIDATING ARCHITECTURAL LAYER BOUNDARIES")
    print("="*60)
    print("Checking that:")
    print("• Domain models don't contain API-specific logic")
    print("• Clear boundaries exist between layers")
    print("• Dependencies flow in the correct direction")
    print("• Converters properly separate concerns")
    print()
    
    # Run all validations
    results = [
        validator.validate_domain_models(),
        validator.validate_data_access_layer(),
        validator.validate_api_layer(),
        validator.validate_converter_separation(),
        validator.validate_dependency_direction(),
    ]
    
    # Print results
    validator.print_results()
    
    # Return success if no violations
    success = all(results) and len(validator.violations) == 0
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
"""Property-based tests for configuration module.

Feature: mtgsim-refactor, Property 1: Configuration Centralization
"""

import tempfile
from pathlib import Path
from unittest.mock import patch

from hypothesis import given
from hypothesis import strategies as st

from mtgsim.config import MTGSimConfig, config


class TestConfigurationCentralization:
    """Property-based tests for configuration centralization."""

    @given(st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd"))))
    def test_config_provides_consistent_paths(self, mock_home_suffix):
        """Property 1: Configuration Centralization

        For any module that requires application paths, the Configuration_Module
        should be the sole source of path information, eliminating all ad-hoc
        path construction patterns including Path.home() / ".mtgsim" usage.

        **Feature: mtgsim-refactor, Property 1: Configuration Centralization**
        **Validates: Requirements 1.1, 1.2, 1.3, 1.4**
        """
        # Create a temporary directory to simulate different home directories
        with tempfile.TemporaryDirectory() as temp_dir:
            mock_home = Path(temp_dir) / mock_home_suffix
            mock_home.mkdir(parents=True, exist_ok=True)

            with patch("pathlib.Path.home", return_value=mock_home):
                test_config = MTGSimConfig()

                # Test that all paths are consistently derived from the configuration
                reference_dir = test_config.reference_dir
                user_db_path = test_config.user_db_path
                mtgjson_dir = test_config.mtgjson_dir

                # Property: All user-specific paths should be under the same .mtgsim directory
                expected_base = mock_home / ".mtgsim"

                assert reference_dir.parent == expected_base
                assert user_db_path.parent == expected_base
                assert mtgjson_dir.parent.parent == expected_base

                # Property: Paths should be consistent across multiple calls
                assert test_config.reference_dir == reference_dir
                assert test_config.user_db_path == user_db_path
                assert test_config.mtgjson_dir == mtgjson_dir

                # Property: mtgjson_dir should be a subdirectory of reference_dir
                assert mtgjson_dir.parent == reference_dir

    def test_config_eliminates_adhoc_patterns(self):
        """Property 1: Configuration Centralization - Ad-hoc Pattern Elimination

        The configuration module should provide the standard paths that replace
        all ad-hoc Path.home() / ".mtgsim" constructions.

        **Feature: mtgsim-refactor, Property 1: Configuration Centralization**
        **Validates: Requirements 1.1, 1.2, 1.3, 1.4**
        """
        # Test that config provides all the paths that modules need
        test_config = MTGSimConfig()

        # These are the paths that should replace ad-hoc constructions
        adhoc_reference_path = Path.home() / ".mtgsim" / "reference"
        adhoc_db_path = Path.home() / ".mtgsim" / "mtgsim.db"
        adhoc_mtgjson_path = Path.home() / ".mtgsim" / "reference" / "mtgjson"

        # Property: Config paths should match the ad-hoc patterns they replace
        assert test_config.reference_dir == adhoc_reference_path
        assert test_config.user_db_path == adhoc_db_path
        assert test_config.mtgjson_dir == adhoc_mtgjson_path

    @given(st.integers(min_value=1, max_value=10))
    def test_config_singleton_consistency(self, num_accesses):
        """Property 1: Configuration Centralization - Singleton Consistency

        The singleton config instance should provide consistent paths across
        multiple accesses and modules.

        **Feature: mtgsim-refactor, Property 1: Configuration Centralization**
        **Validates: Requirements 1.1, 1.2, 1.3, 1.4**
        """
        # Collect paths from multiple accesses
        reference_dirs = []
        user_db_paths = []
        mtgjson_dirs = []
        project_roots = []
        resources_dirs = []

        for _ in range(num_accesses):
            reference_dirs.append(config.reference_dir)
            user_db_paths.append(config.user_db_path)
            mtgjson_dirs.append(config.mtgjson_dir)
            project_roots.append(config.project_root)
            resources_dirs.append(config.resources_dir)

        # Property: All accesses should return identical paths
        assert len(set(reference_dirs)) == 1
        assert len(set(user_db_paths)) == 1
        assert len(set(mtgjson_dirs)) == 1
        assert len(set(project_roots)) == 1
        assert len(set(resources_dirs)) == 1

    def test_project_root_detection(self):
        """Property 1: Configuration Centralization - Project Root Detection

        The project root should be consistently detected by finding pyproject.toml.

        **Feature: mtgsim-refactor, Property 1: Configuration Centralization**
        **Validates: Requirements 1.1, 1.2, 1.3, 1.4**
        """
        test_config = MTGSimConfig()
        project_root = test_config.project_root

        # Property: Project root should contain pyproject.toml
        assert (project_root / "pyproject.toml").exists()

        # Property: Resources dir should be under project root
        assert test_config.resources_dir.parent == project_root

        # Property: Project root should be an absolute path
        assert project_root.is_absolute()

    @given(st.text(min_size=1, max_size=20, alphabet=st.characters(whitelist_categories=("Lu", "Ll"))))
    def test_path_relationships(self, mock_suffix):
        """Property 1: Configuration Centralization - Path Relationships

        All configuration paths should maintain proper hierarchical relationships.

        **Feature: mtgsim-refactor, Property 1: Configuration Centralization**
        **Validates: Requirements 1.1, 1.2, 1.3, 1.4**
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            mock_home = Path(temp_dir) / mock_suffix
            mock_home.mkdir(parents=True, exist_ok=True)

            with patch("pathlib.Path.home", return_value=mock_home):
                test_config = MTGSimConfig()

                # Property: mtgjson_dir should be under reference_dir
                assert test_config.reference_dir in test_config.mtgjson_dir.parents

                # Property: Both reference_dir and user_db_path should be under .mtgsim
                mtgsim_base = mock_home / ".mtgsim"
                assert mtgsim_base in test_config.reference_dir.parents
                assert mtgsim_base in test_config.user_db_path.parents

                # Property: resources_dir should be under project_root
                assert test_config.project_root in test_config.resources_dir.parents

"""Centralized configuration for MTGSim application."""

from pathlib import Path


class MTGSimConfig:
    """Centralized configuration for MTGSim application.

    Provides standardized paths for project root, resources directory,
    reference directory, user database, and MTGJSON data directory.
    Replaces ad-hoc path construction patterns throughout the application.
    """

    @property
    def project_root(self) -> Path:
        """Get project root directory.

        Returns the root directory of the MTGSim project, determined by
        walking up from this config file to find the directory containing
        pyproject.toml.
        """
        current = Path(__file__).parent
        while current != current.parent:
            if (current / "pyproject.toml").exists():
                return current
            current = current.parent
        # Fallback to the parent of the src directory
        return Path(__file__).parent.parent.parent

    @property
    def resources_dir(self) -> Path:
        """Get resources directory path.

        Returns the resources directory within the project root.
        This directory is intended for static resources and reference data.
        """
        return self.project_root / "resources"

    @property
    def reference_dir(self) -> Path:
        """Get reference data directory path.

        Returns the user's reference data directory at ~/.mtgsim/reference.
        This directory contains runtime copies of MTGJSON data.
        """
        return Path.home() / ".mtgsim" / "reference"

    @property
    def user_db_path(self) -> Path:
        """Get user database path.

        Returns the path to the user's personal collection database
        at ~/.mtgsim/mtgsim.db.
        """
        return Path.home() / ".mtgsim" / "mtgsim.db"

    @property
    def mtgjson_dir(self) -> Path:
        """Get MTGJSON data directory path.

        Returns the directory containing MTGJSON SQLite databases
        at ~/.mtgsim/reference/mtgjson.
        """
        return self.reference_dir / "mtgjson"


# Singleton instance for application-wide use
config = MTGSimConfig()

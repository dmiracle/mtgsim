"""Property-based tests for CLI command registration."""

import pytest
from hypothesis import given, strategies as st
from typer.testing import CliRunner

from mtgsim.cli import app
from mtgsim.cli.card_commands import card_app
from mtgsim.cli.db_commands import db_app
from mtgsim.cli.mtgjson_commands import mtgjson_app


class TestCLICommandRegistration:
    """Test CLI command registration consistency."""

    def test_main_app_has_subcommands(self):
        """Main app should have all expected subcommands registered."""
        runner = CliRunner()
        result = runner.invoke(app, ["--help"])
        
        assert result.exit_code == 0
        help_output = result.output
        
        # Check that all expected subcommands are present
        assert "card" in help_output
        assert "db" in help_output
        assert "mtgjson" in help_output

    def test_card_app_commands_discoverable(self):
        """Card app commands should be discoverable through help."""
        runner = CliRunner()
        result = runner.invoke(app, ["card", "--help"])
        
        assert result.exit_code == 0
        help_output = result.output
        
        # Check that card subcommands are present
        assert "card" in help_output
        assert "extract" in help_output

    def test_db_app_commands_discoverable(self):
        """DB app commands should be discoverable through help."""
        runner = CliRunner()
        result = runner.invoke(app, ["db", "--help"])
        
        assert result.exit_code == 0
        help_output = result.output
        
        # Check that db subcommands are present
        assert "init" in help_output
        assert "sync" in help_output

    def test_mtgjson_app_commands_discoverable(self):
        """MTGJSON app commands should be discoverable through help."""
        runner = CliRunner()
        result = runner.invoke(app, ["mtgjson", "--help"])
        
        assert result.exit_code == 0
        help_output = result.output
        
        # Check that mtgjson subcommands are present
        assert "info" in help_output
        assert "stats" in help_output

    @given(st.sampled_from(["card", "db", "mtgjson"]))
    def test_subcommand_help_consistency(self, subcommand):
        """For any valid subcommand, help should be accessible and consistent.
        
        **Feature: mtgsim-refactor, Property 6: CLI Command Registration**
        **Validates: Requirements 6.1, 6.2, 6.3, 6.4**
        """
        runner = CliRunner()
        result = runner.invoke(app, [subcommand, "--help"])
        
        # All subcommands should have accessible help
        assert result.exit_code == 0
        
        # Help output should contain the subcommand name
        assert subcommand in result.output.lower()
        
        # Help should contain usage information
        assert "usage:" in result.output.lower()
        
        # Help should contain options section
        assert "options" in result.output.lower()

    def test_app_instances_used_consistently(self):
        """All CLI modules should use their declared app instances consistently."""
        # Verify that card_app is properly defined and has registered commands
        assert hasattr(card_app, 'registered_commands')
        assert len(card_app.registered_commands) > 0
        
        # Verify that db_app is properly defined and has registered commands
        assert hasattr(db_app, 'registered_commands')
        assert len(db_app.registered_commands) > 0
        
        # Verify that mtgjson_app is properly defined and has registered commands
        assert hasattr(mtgjson_app, 'registered_commands')
        assert len(mtgjson_app.registered_commands) > 0

    @given(st.sampled_from(["card card", "card extract"]))
    def test_card_commands_registration(self, command_path):
        """For any card command, it should be properly registered and discoverable.
        
        **Feature: mtgsim-refactor, Property 6: CLI Command Registration**
        **Validates: Requirements 6.1, 6.2, 6.3, 6.4**
        """
        runner = CliRunner()
        command_parts = command_path.split()
        help_command = command_parts + ["--help"]
        
        result = runner.invoke(app, help_command)
        
        # Command should be discoverable and have help
        assert result.exit_code == 0
        
        # Help should contain usage information
        assert "usage:" in result.output.lower()

    def test_no_brittle_registration_patterns(self):
        """Verify that no commands use brittle @typer.Typer().command() pattern."""
        import inspect
        from mtgsim.cli import card_commands
        
        # Get the source code of the card_commands module
        source = inspect.getsource(card_commands)
        
        # Should not contain the brittle pattern
        assert "@typer.Typer().command()" not in source
        
        # Should contain the correct pattern
        assert "@card_app.command()" in source
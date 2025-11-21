"""
Tests for check_workflow_tasks module.

Test from the root directory with:
    pytest -vv -rx ./for_gh_runner/tests/test_check_workflow_tasks.py
"""
import sys
from pathlib import Path

# Add parent directory to path to import the module
sys.path.insert(0, str(Path(__file__).parent.parent))

from check_workflow_tasks import main


def test_import():
    """Test that check_workflow_tasks module can be imported."""
    # Simply importing the module should work
    assert main is not None


def test_main_function_exists():
    """Test that main function is callable."""
    # The main function should be callable
    assert callable(main)


def test_main_returns_int():
    """Test that main function returns an integer exit code."""
    # Note: This will fail because the actual log path doesn't exist
    # but we're testing that it returns the correct type
    exit_code = main()
    assert isinstance(exit_code, int)
    # Should return 2 (error) because the log path doesn't exist
    assert exit_code == 2

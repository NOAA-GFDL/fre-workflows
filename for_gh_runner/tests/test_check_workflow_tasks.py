"""
Tests for check_workflow_tasks module.

Test from the root directory with:
    pytest -vv -rx ./for_gh_runner/tests/test_check_workflow_tasks.py
"""
import sys
import tempfile
from pathlib import Path

# Add parent directory to path to import the module
sys.path.insert(0, str(Path(__file__).parent.parent))

from check_workflow_tasks import main, print_workflow_summary


def test_import():
    """Test that check_workflow_tasks module can be imported."""
    # Simply importing the module should work
    assert main is not None
    assert print_workflow_summary is not None


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


def test_print_workflow_summary_missing_path():
    """Test print_workflow_summary returns 1 when path doesn't exist."""
    exit_code = print_workflow_summary("/nonexistent/path")
    assert exit_code == 1


def test_print_workflow_summary_with_valid_path():
    """Test print_workflow_summary with a valid directory structure."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create minimal directory structure
        log_path = Path(tmpdir) / "log"
        log_path.mkdir()

        # Create a job directory
        job_dir = log_path / "job" / "19800101" / "pp-starter" / "NN"
        job_dir.mkdir(parents=True)
        job_file = job_dir / "job"
        job_file.write_text("#!/bin/bash\necho test\n")

        # Create config directory
        config_dir = log_path / "config"
        config_dir.mkdir()
        config_file = config_dir / "01-rose-suite.conf"
        config_file.write_text("[jinja2:suite.rc]\nTEST=value\n")

        # Run the summary function
        exit_code = print_workflow_summary(tmpdir)
        assert exit_code == 0


def test_print_workflow_summary_function_exists():
    """Test that print_workflow_summary function is callable."""
    assert callable(print_workflow_summary)

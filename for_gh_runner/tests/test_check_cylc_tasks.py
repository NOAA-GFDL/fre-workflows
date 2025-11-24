"""
Tests for check_cylc_tasks module.

Test from the root directory with:
    pytest -vv -rx ./for_gh_runner/tests/test_check_cylc_tasks.py
"""
import os
import sys
import tempfile
import logging
from pathlib import Path

# Add parent directory to path to import the module
sys.path.insert(0, str(Path(__file__).parent.parent))

from check_cylc_tasks import (
    configure_logging,
    check_task_status,
    check_multiple_tasks
)


def test_configure_logging_default():
    """Test that configure_logging sets up logging with default INFO level."""
    # Reset logging configuration
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    configure_logging(verbose=False, quiet=False)
    logger = logging.getLogger()
    assert logger.level == logging.INFO


def test_configure_logging_verbose():
    """Test that configure_logging sets DEBUG level when verbose=True."""
    # Reset logging configuration
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    configure_logging(verbose=True, quiet=False)
    logger = logging.getLogger()
    assert logger.level == logging.DEBUG


def test_configure_logging_quiet():
    """Test that configure_logging sets WARNING level when quiet=True."""
    # Reset logging configuration
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    configure_logging(verbose=False, quiet=True)
    logger = logging.getLogger()
    assert logger.level == logging.WARNING


def test_check_task_status_with_success():
    """Test check_task_status returns 0 when task succeeds."""
    # Create a temporary directory structure
    with tempfile.TemporaryDirectory() as tmpdir:
        log_base_path = tmpdir
        task_dir = Path(tmpdir) / "log" / "job" / "1980" / "pp-starter" / "01"
        task_dir.mkdir(parents=True)

        # Create a job.status file with success
        status_file = task_dir / "job.status"
        status_file.write_text("CYLC_JOB_EXIT=SUCCEEDED\n")

        # Configure logging to suppress output during test
        configure_logging(quiet=True)

        # Check task status
        exit_code = check_task_status(
            log_base_path=log_base_path,
            task_pattern="pp-starter",
            attempt_range="01"
        )

        assert exit_code == 0


def test_check_task_status_with_failure():
    """Test check_task_status returns 1 when task fails."""
    # Create a temporary directory structure
    with tempfile.TemporaryDirectory() as tmpdir:
        log_base_path = tmpdir
        task_dir = Path(tmpdir) / "log" / "job" / "1980" / "stage-history" / "01"
        task_dir.mkdir(parents=True)

        # Create a job.status file with failure
        status_file = task_dir / "job.status"
        status_file.write_text("CYLC_JOB_EXIT=ERR\n")

        # Configure logging to suppress output during test
        configure_logging(quiet=True)

        # Check task status
        exit_code = check_task_status(
            log_base_path=log_base_path,
            task_pattern="stage-history",
            attempt_range="01"
        )

        assert exit_code == 1


def test_check_task_status_with_failure_continue_on_error():
    """Test check_task_status returns 0 when continue_on_error=True."""
    # Create a temporary directory structure
    with tempfile.TemporaryDirectory() as tmpdir:
        log_base_path = tmpdir
        task_dir = Path(tmpdir) / "log" / "job" / "1980" / "regrid-xy-ocean" / "01"
        task_dir.mkdir(parents=True)

        # Create a job.status file with failure
        status_file = task_dir / "job.status"
        status_file.write_text("CYLC_JOB_EXIT=ERR\n")

        # Configure logging to suppress output during test
        configure_logging(quiet=True)

        # Check task status with continue_on_error
        exit_code = check_task_status(
            log_base_path=log_base_path,
            task_pattern="regrid-xy*",
            attempt_range="01",
            continue_on_error=True
        )

        assert exit_code == 0


def test_check_task_status_no_files_found():
    """Test check_task_status returns 0 when no job.status files found."""
    # Create a temporary directory structure with no job.status files
    with tempfile.TemporaryDirectory() as tmpdir:
        log_base_path = tmpdir

        # Configure logging to suppress output during test
        configure_logging(quiet=True)

        # Check task status for non-existent task
        exit_code = check_task_status(
            log_base_path=log_base_path,
            task_pattern="nonexistent-task",
            attempt_range="01"
        )

        assert exit_code == 0


def test_check_task_status_with_wildcard():
    """Test check_task_status works with wildcard patterns."""
    # Create a temporary directory structure
    with tempfile.TemporaryDirectory() as tmpdir:
        log_base_path = tmpdir

        # Create multiple tasks matching wildcard
        for task_name in ["regrid-xy-ocean", "regrid-xy-atmos"]:
            task_dir = Path(tmpdir) / "log" / "job" / "1980" / task_name / "01"
            task_dir.mkdir(parents=True)
            status_file = task_dir / "job.status"
            status_file.write_text("CYLC_JOB_EXIT=SUCCEEDED\n")

        # Configure logging to suppress output during test
        configure_logging(quiet=True)

        # Check task status with wildcard
        exit_code = check_task_status(
            log_base_path=log_base_path,
            task_pattern="regrid-xy*",
            attempt_range="01"
        )

        assert exit_code == 0


def test_check_multiple_tasks_all_success():
    """Test check_multiple_tasks returns 0 when all tasks succeed."""
    # Create a temporary directory structure
    with tempfile.TemporaryDirectory() as tmpdir:
        log_base_path = tmpdir

        # Create multiple successful tasks
        for task_name in ["pp-starter", "stage-history"]:
            task_dir = Path(tmpdir) / "log" / "job" / "1980" / task_name / "01"
            task_dir.mkdir(parents=True)
            status_file = task_dir / "job.status"
            status_file.write_text("CYLC_JOB_EXIT=SUCCEEDED\n")

        # Configure logging to suppress output during test
        configure_logging(quiet=True)

        # Define task configuration
        tasks_config = [
            {'name': 'pp-starter'},
            {'name': 'stage-history'},
        ]

        # Check multiple tasks
        exit_code = check_multiple_tasks(
            log_base_path=log_base_path,
            tasks_config=tasks_config,
            attempt_range="01"
        )

        assert exit_code == 0


def test_check_multiple_tasks_with_failure():
    """Test check_multiple_tasks returns 1 when a task fails."""
    # Create a temporary directory structure
    with tempfile.TemporaryDirectory() as tmpdir:
        log_base_path = tmpdir

        # Create one successful and one failed task
        task_dir1 = Path(tmpdir) / "log" / "job" / "1980" / "pp-starter" / "01"
        task_dir1.mkdir(parents=True)
        status_file1 = task_dir1 / "job.status"
        status_file1.write_text("CYLC_JOB_EXIT=SUCCEEDED\n")

        task_dir2 = Path(tmpdir) / "log" / "job" / "1980" / "stage-history" / "01"
        task_dir2.mkdir(parents=True)
        status_file2 = task_dir2 / "job.status"
        status_file2.write_text("CYLC_JOB_EXIT=ERR\n")

        # Configure logging to suppress output during test
        configure_logging(quiet=True)

        # Define task configuration
        tasks_config = [
            {'name': 'pp-starter'},
            {'name': 'stage-history'},
        ]

        # Check multiple tasks
        exit_code = check_multiple_tasks(
            log_base_path=log_base_path,
            tasks_config=tasks_config,
            attempt_range="01"
        )

        assert exit_code == 1


def test_check_multiple_tasks_with_continue_on_error():
    """Test check_multiple_tasks continues when continue_on_error is set."""
    # Create a temporary directory structure
    with tempfile.TemporaryDirectory() as tmpdir:
        log_base_path = tmpdir

        # Create tasks with one failure that should be ignored
        task_dir1 = Path(tmpdir) / "log" / "job" / "1980" / "pp-starter" / "01"
        task_dir1.mkdir(parents=True)
        status_file1 = task_dir1 / "job.status"
        status_file1.write_text("CYLC_JOB_EXIT=SUCCEEDED\n")

        task_dir2 = Path(tmpdir) / "log" / "job" / "1980" / "regrid-xy-ocean" / "01"
        task_dir2.mkdir(parents=True)
        status_file2 = task_dir2 / "job.status"
        status_file2.write_text("CYLC_JOB_EXIT=ERR\n")

        task_dir3 = Path(tmpdir) / "log" / "job" / "1980" / "clean-01" / "01"
        task_dir3.mkdir(parents=True)
        status_file3 = task_dir3 / "job.status"
        status_file3.write_text("CYLC_JOB_EXIT=SUCCEEDED\n")

        # Configure logging to suppress output during test
        configure_logging(quiet=True)

        # Define task configuration with continue_on_error
        tasks_config = [
            {'name': 'pp-starter'},
            {'name': 'regrid-xy*', 'continue_on_error': True},
            {'name': 'clean*'},
        ]

        # Check multiple tasks - should continue past regrid-xy failure
        exit_code = check_multiple_tasks(
            log_base_path=log_base_path,
            tasks_config=tasks_config,
            attempt_range="01"
        )

        assert exit_code == 0


def test_check_multiple_tasks_missing_log_path():
    """Test check_multiple_tasks raises FileNotFoundError for missing path."""
    # Configure logging to suppress output during test
    configure_logging(quiet=True)

    # Define task configuration
    tasks_config = [
        {'name': 'pp-starter'},
    ]

    # Check multiple tasks with non-existent path
    try:
        check_multiple_tasks(
            log_base_path="/nonexistent/path",
            tasks_config=tasks_config,
            attempt_range="01"
        )
        # Should not reach here
        assert False, "Expected FileNotFoundError"
    except FileNotFoundError:
        # Expected exception
        assert True

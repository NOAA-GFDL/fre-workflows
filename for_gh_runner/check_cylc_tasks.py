#!/usr/bin/env python3
"""
Utility module for checking Cylc workflow task statuses.

This module provides functions to check the success or failure status of Cylc
workflow tasks by examining job.status files in the Cylc log directory.
It uses Python's logging module for structured output suitable for CI/CD environments.

Example usage:
    python check_cylc_tasks.py --log-base-path /path/to/cylc-run/workflow \\
                                --task-pattern pp-starter \\
                                --attempt-range "0[1-3]"
"""

import argparse
import glob
import logging
import subprocess
import sys
from pathlib import Path
from typing import List, Dict, Any


def configure_logging(verbose: bool = False, quiet: bool = False) -> None:
    """
    Configure logging for the application.

    Sets up the logging format and level appropriate for CI/CD environments,
    with timestamps and structured output suitable for GitHub Actions.

    Args:
        verbose: If True, set logging level to DEBUG
        quiet: If True, set logging level to WARNING

    Returns:
        None
    """
    log_format = '%(asctime)s - %(levelname)s - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'

    if verbose:
        level = logging.DEBUG
    elif quiet:
        level = logging.WARNING
    else:
        level = logging.INFO

    logging.basicConfig(
        level=level,
        format=log_format,
        datefmt=date_format,
        stream=sys.stdout
    )


def check_task_status(
    log_base_path: str,
    task_pattern: str,
    attempt_range: str = "0[1-3]",
    continue_on_error: bool = False
) -> int:
    """
    Check the success or failure status of a Cylc workflow task.

    Searches for CYLC_JOB_EXIT=SUCCEEDED or CYLC_JOB_EXIT=ERR in job.status
    files matching the given task pattern and attempt range.

    Args:
        log_base_path: Base path to the Cylc workflow log directory
        task_pattern: Task name pattern (e.g., 'pp-starter', 'regrid-xy*')
        attempt_range: Pattern for attempt numbers (default: '0[1-3]')
        continue_on_error: If True, log errors but return 0 (default: False)

    Returns:
        Exit code:
            0: Success (all tasks succeeded or continue_on_error=True)
            1: Task failures found
            2: Grep/execution errors occurred

    Raises:
        FileNotFoundError: If the log_base_path does not exist
    """
    logger = logging.getLogger(__name__)
    logger.info("Checking task: %s", task_pattern)

    # Construct the path pattern for job.status files
    status_file_pattern = (
        f"{log_base_path}/log/job/*/{task_pattern}/{attempt_range}/job.status"
    )
    logger.debug("Looking for files matching: %s", status_file_pattern)

    # Find matching files
    matching_files = glob.glob(status_file_pattern)
    if not matching_files:
        logger.warning("No job.status files found matching pattern: %s", status_file_pattern)

    # Check for successes
    try:
        success_result = subprocess.run(
            ["grep", "-E", "CYLC_JOB_EXIT=SUCCEEDED"] + matching_files,
            capture_output=True,
            text=True,
            check=False
        )
        success_exit_code = success_result.returncode

        if success_exit_code == 0:
            # Found successes
            # grep outputs one match per line when searching multiple files
            # Split by newlines (equivalent to original shell script's sed 's/ /\n/g')
            success_lines = success_result.stdout.strip().split('\n')
            for line in success_lines:
                if line:
                    logger.info(line)
        elif success_exit_code == 1:
            # No successes found
            logger.warning("No succeeded tasks found for pattern: %s", task_pattern)
        else:
            # Grep error
            logger.error("WARNING: error with grep execution (success check)")
            if not continue_on_error:
                return 2

    except FileNotFoundError:
        logger.error("grep command not found")
        if not continue_on_error:
            return 2
    except Exception as ex:
        logger.error("Error checking successes: %s", str(ex))
        if not continue_on_error:
            return 2

    # Check for failures
    try:
        failure_result = subprocess.run(
            ["grep", "-E", "CYLC_JOB_EXIT=ERR"] + matching_files,
            capture_output=True,
            text=True,
            check=False
        )
        failure_exit_code = failure_result.returncode

        if failure_exit_code == 0:
            # Found failures
            logger.error("Failures found for pattern: %s", task_pattern)
            # grep outputs one match per line when searching multiple files
            # Split by newlines (equivalent to original shell script's sed 's/ /\n/g')
            failure_lines = failure_result.stdout.strip().split('\n')
            for line in failure_lines:
                if line:
                    logger.error(line)
            if not continue_on_error:
                return 1
        elif failure_exit_code == 1:
            # No failures found
            logger.info("No task failures found for pattern: %s", task_pattern)
        else:
            # Grep error
            logger.error("WARNING: error with grep execution (failure check)")
            if not continue_on_error:
                return 2

    except FileNotFoundError:
        logger.error("grep command not found")
        if not continue_on_error:
            return 2
    except Exception as ex:
        logger.error("Error checking failures: %s", str(ex))
        if not continue_on_error:
            return 2

    return 0


def check_multiple_tasks(
    log_base_path: str,
    tasks_config: List[Dict[str, Any]],
    attempt_range: str = "0[1-3]"
) -> int:
    """
    Check the status of multiple Cylc workflow tasks.

    Processes a list of task configurations and checks the status of each task.
    Stops at the first task that fails (unless continue_on_error is set for that task).

    Args:
        log_base_path: Base path to the Cylc workflow log directory
        tasks_config: List of task configuration dictionaries with keys:
            - 'name': Task name pattern (required)
            - 'continue_on_error': Whether to continue on task failure (optional)
        attempt_range: Default pattern for attempt numbers (default: '0[1-3]')

    Returns:
        Exit code:
            0: Success (all tasks succeeded)
            1: At least one task failed
            2: Grep/execution errors occurred

    Raises:
        FileNotFoundError: If the log_base_path does not exist
    """
    logger = logging.getLogger(__name__)

    # Validate log base path exists
    log_path = Path(log_base_path)
    if not log_path.exists():
        logger.error("Log base path does not exist: %s", log_base_path)
        raise FileNotFoundError(f"Log base path not found: {log_base_path}")

    overall_exit_code = 0

    for task_config in tasks_config:
        task_name = task_config.get('name')
        if not task_name:
            logger.error("Task configuration missing 'name' field: %s", task_config)
            continue

        task_continue_on_error = task_config.get('continue_on_error', False)
        task_attempt_range = task_config.get('attempt_range', attempt_range)

        exit_code = check_task_status(
            log_base_path=log_base_path,
            task_pattern=task_name,
            attempt_range=task_attempt_range,
            continue_on_error=task_continue_on_error
        )

        # Track the worst exit code seen
        if exit_code > overall_exit_code and not task_continue_on_error:
            overall_exit_code = exit_code

        # Stop processing if we hit a fatal error (exit code 2)
        # or a task failure (exit code 1) without continue_on_error
        if exit_code != 0 and not task_continue_on_error:
            logger.error("Task check failed for: %s (exit code: %d)", task_name, exit_code)
            break

    return overall_exit_code


def main() -> int:
    """
    Main entry point for the CLI interface.

    Parses command-line arguments and checks the status of Cylc workflow tasks.

    Returns:
        Exit code (0=success, 1=task failures, 2=execution errors)
    """
    parser = argparse.ArgumentParser(
        description='Check Cylc workflow task statuses by examining job.status files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Check a single task
  %(prog)s --log-base-path /path/to/cylc-run/workflow --task-pattern pp-starter

  # Check a task with wildcards
  %(prog)s --log-base-path /path/to/cylc-run/workflow --task-pattern "regrid-xy*"

  # Continue on error for specific task
  %(prog)s --log-base-path /path/to/cylc-run/workflow --task-pattern "regrid-xy*" --continue-on-error

  # Enable verbose logging
  %(prog)s --log-base-path /path/to/cylc-run/workflow --task-pattern pp-starter --verbose
        """
    )

    parser.add_argument(
        '--log-base-path',
        required=True,
        help='Base path to the Cylc workflow log directory'
    )
    parser.add_argument(
        '--task-pattern',
        required=True,
        help='Task name pattern (e.g., pp-starter, regrid-xy*)'
    )
    parser.add_argument(
        '--attempt-range',
        default='0[1-3]',
        help='Pattern for attempt numbers (default: 0[1-3])'
    )
    parser.add_argument(
        '--continue-on-error',
        action='store_true',
        help='Continue execution even if task failures are found'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose (DEBUG level) logging'
    )
    parser.add_argument(
        '--quiet',
        action='store_true',
        help='Enable quiet mode (WARNING level and above only)'
    )

    args = parser.parse_args()

    # Configure logging
    configure_logging(verbose=args.verbose, quiet=args.quiet)

    # Check task status
    try:
        exit_code = check_task_status(
            log_base_path=args.log_base_path,
            task_pattern=args.task_pattern,
            attempt_range=args.attempt_range,
            continue_on_error=args.continue_on_error
        )
        return exit_code
    except FileNotFoundError as ex:
        logging.error("File not found: %s", str(ex))
        return 2
    except Exception as ex:
        logging.error("Unexpected error: %s", str(ex))
        return 2


if __name__ == '__main__':
    sys.exit(main())

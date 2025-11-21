#!/usr/bin/env python3
"""
Wrapper script for checking all PPP workflow tasks.

This script uses the check_cylc_tasks module to check the status of all tasks
in the PPP (Portable Post-Processing) workflow. It defines the task configuration
and validates that the log path exists before processing.

Usage:
    python check_workflow_tasks.py
"""

import sys
import logging
from pathlib import Path

# Add current directory to sys.path to support execution from any directory
sys.path.insert(0, str(Path(__file__).parent))

# Import the check_cylc_tasks module
from check_cylc_tasks import configure_logging, check_multiple_tasks  # pylint: disable=wrong-import-position


def main() -> int:
    """
    Check all tasks in the PPP workflow.

    Configures logging and checks the status of all PPP workflow tasks
    in the specified order with appropriate error handling for each task.

    Returns:
        Exit code:
            0: Success (all tasks succeeded)
            1: Task failures found
            2: Execution errors occurred
    """
    # Configure logging for GitHub Actions
    configure_logging(verbose=False, quiet=False)
    logger = logging.getLogger(__name__)

    # Define the log base path for the PPP workflow
    log_base_path = "/contrib/container-test/ppp-setup/cylc-run/test_pp__ptest__ttest"

    # Validate that the log path exists
    log_path = Path(log_base_path)
    if not log_path.exists():
        logger.error("Log base path does not exist: %s", log_base_path)
        logger.error("Please ensure the workflow has been executed before checking task statuses")
        return 2

    logger.info("Checking PPP workflow tasks in: %s", log_base_path)

    # Define the task checking configuration for the PPP workflow
    # Tasks are checked in the order they appear in the workflow
    tasks_config = [
        {'name': 'pp-starter'},
        {'name': 'stage-history'},
        {'name': 'regrid-xy*', 'continue_on_error': True},
        {'name': 'mask-atmos-plevel*'},
        {'name': 'remap-pp-components*'},
        {'name': 'make-timeavgs*'},
        {'name': 'rename-split-to-pp*'},
        {'name': 'split-netcdf*'},
        {'name': 'combine-timeavgs*'},
        {'name': 'clean*'},
    ]

    # Check all tasks
    try:
        exit_code = check_multiple_tasks(
            log_base_path=log_base_path,
            tasks_config=tasks_config,
            attempt_range="0[1-3]"
        )

        if exit_code == 0:
            logger.info("All workflow tasks completed successfully")
        elif exit_code == 1:
            logger.error("Workflow completed with task failures")
        else:
            logger.error("Workflow check completed with errors")

        return exit_code

    except FileNotFoundError as ex:
        logger.error("File not found: %s", str(ex))
        return 2
    except Exception as ex:
        logger.error("Unexpected error: %s", str(ex))
        return 2


if __name__ == '__main__':
    sys.exit(main())

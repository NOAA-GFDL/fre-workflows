#!/usr/bin/env python3
"""
Wrapper script for checking all PPP workflow tasks.

This script uses the check_cylc_tasks module to check the status of all tasks
in the PPP (Portable Post-Processing) workflow. It defines the task configuration
and validates that the log path exists before processing.

Usage:
    python check_workflow_tasks.py
    python check_workflow_tasks.py --summary  # Print workflow summary only
"""

import sys
import logging
import glob
import argparse
from pathlib import Path

# Add current directory to sys.path to support execution from any directory
sys.path.insert(0, str(Path(__file__).parent))

# Import the check_cylc_tasks module
from check_cylc_tasks import configure_logging, check_multiple_tasks  # pylint: disable=wrong-import-position


def print_workflow_summary(log_base_path: str) -> int:
    """
    Print summary information about the workflow run.

    This function prints:
    - Number of tasks launched
    - Job directories with job scripts
    - Job scripts for 1980 only
    - Rose-suite configuration

    Args:
        log_base_path: Base path to the Cylc workflow log directory

    Returns:
        Exit code:
            0: Success (summary printed)
            1: Errors occurred while printing summary
    """
    logger = logging.getLogger(__name__)

    # Validate that the log path exists
    log_path = Path(log_base_path)
    if not log_path.exists():
        logger.error("Log base path does not exist: %s", log_base_path)
        return 1

    try:
        # Count number of tasks launched
        job_pattern = f"{log_base_path}/log/job/????*/*/NN/job"
        job_files = glob.glob(job_pattern)
        num_tasks = len(job_files)
        print(f"number of tasks launched: {num_tasks}")
        print()

        # List all job directories with job scripts
        if job_files:
            print("here's all the job directories with job scripts:")
            for job_file in sorted(job_files):
                # Get file stats to match ls -l output
                job_path = Path(job_file)
                stat = job_path.stat()
                print(f"{stat.st_mode:o} {stat.st_nlink} {stat.st_size} {job_file}")
            print()

        # List job scripts for 1980 only
        job_1980_pattern = f"{log_base_path}/log/job/1980*/*/NN/job"
        job_1980_files = glob.glob(job_1980_pattern)
        if job_1980_files:
            print("here's all the job scripts for 1980 only:")
            for job_file in sorted(job_1980_files):
                job_path = Path(job_file)
                stat = job_path.stat()
                print(f"{stat.st_mode:o} {stat.st_nlink} {stat.st_size} {job_file}")
            print()

        # Print rose-suite configuration
        config_pattern = f"{log_base_path}/log/config/*rose-suite.conf"
        config_files = glob.glob(config_pattern)
        if config_files:
            print("rose-suite conf for workflow:")
            for config_file in sorted(config_files):
                with open(config_file, 'r', encoding='utf-8') as f:
                    print(f.read())
            print()

        return 0

    except Exception as ex:
        logger.error("Error printing workflow summary: %s", str(ex))
        return 1


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
    parser = argparse.ArgumentParser(
        description='Check PPP workflow task statuses or print workflow summary'
    )
    parser.add_argument(
        '--summary',
        action='store_true',
        help='Print workflow summary only (do not check task statuses)'
    )
    args = parser.parse_args()

    # Configure logging
    configure_logging(verbose=False, quiet=False)

    # Define the log base path for the PPP workflow
    log_base_path = "/contrib/container-test/ppp-setup/cylc-run/test_pp__ptest__ttest"

    if args.summary:
        # Just print the summary
        sys.exit(print_workflow_summary(log_base_path))
    else:
        # Run the main task checking
        sys.exit(main())

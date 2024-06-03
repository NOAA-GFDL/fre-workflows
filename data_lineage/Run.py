import sys
from data_lineage.dag.FetchData import main as fetch_main
from data_lineage.dag.SerialDag import main as generate_serial_dag
from data_lineage.verification.Validate import main as validate
from data_lineage.dag.Visualize import draw


def main(fingerprint):
    """
    Controls the entire data lineage tool.
        1. Fetches jobs from EPMT
        2. Creates the serial dag
        3. Verifies with configuration dag
        4. Draws the serial dag

    Args:
        fingerprint: String
            The CYLC_WORKFLOW_UUID generated from a cylc workflow.
    """
    jobs, run_dir = fetch_main(fingerprint)

    serial_dag = generate_serial_dag(jobs, run_dir)

    validate(serial_dag, run_dir)
    draw(serial_dag)

    print("Successfully finished running, ending program.")

if __name__ == "__main__":
    # If not passing in a fingerprint to Run.py, use the provided fingerprint instead.
    if len(sys.argv) == 1:
        fingerprint = '21bc35b4-f6bf-40c7-9bbb-027dfcd436f0'
    elif len(sys.argv) == 2:
        fingerprint = sys.argv[1]
    else:
        print('ERROR: Incorrect args. Please either specificy a fingerprint, or '
              'pass in 0 args to use the fingerprint provided in Run.py.')
        sys.exit(1)

    main(fingerprint)

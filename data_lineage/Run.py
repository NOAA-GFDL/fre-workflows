import sys
from data_lineage.dag.FetchData import main as fetch_main
from data_lineage.dag.ioDag import main as generate_io_dag
from data_lineage.verification.Validate import main as validate
from data_lineage.dag.Visualize import draw


def main(fingerprint):
    """
    Controls the entire data lineage tool.
        1. Fetches jobs from EPMT
        2. Creates the io dag
        3. Verifies with configuration dag
        4. Draws the io dag

    Args:
        fingerprint: String
            The CYLC_WORKFLOW_UUID generated from a cylc workflow.
    """
    jobs, run_dir = fetch_main(fingerprint)

    io_dag = generate_io_dag(jobs, run_dir)

    validate(io_dag, run_dir)
    draw(io_dag)

    print("Successfully finished running, ending program.")

if __name__ == "__main__":
    # If not passing in a fingerprint to Run.py, use the provided fingerprint instead.
    if len(sys.argv) == 1:
        fingerprint = 'eb6642d6-871b-42c8-98bf-2dcbb0e98525'
    elif len(sys.argv) == 2:
        fingerprint = sys.argv[1]
    else:
        print('ERROR: Incorrect args. Please either specificy a fingerprint, or '
              'pass in 0 args to use the fingerprint provided in Run.py.')
        sys.exit(1)

    main(fingerprint)

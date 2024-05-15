from data_lineage.dag.FetchData import main as fetch_main
from data_lineage.dag.SerialDag import main as generate_serial_dag
from data_lineage.verification.Validate import main as validate
from data_lineage.dag.Visualize import draw


def main():
    fp = '21bc35b4-f6bf-40c7-9bbb-027dfcd436f0'
    jobs, run_dir = fetch_main(fp)

    serial_dag = generate_serial_dag(jobs, run_dir)

    validate(serial_dag, run_dir)
    draw(serial_dag)

    print("Successfully finished running, ending program.")

if __name__ == "__main__":
    main()

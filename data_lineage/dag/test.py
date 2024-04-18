import Dag
import logging  # Not working properly
from Visualize import draw
from FetchFromFingerprint import main as fp_main
from data_lineage.verification import Parse
from data_lineage.verification import Validate


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# run54/log/job/19810101T0000Z/remap-pp-components-ts-P2Y_atmos_scalar/01/job.err

# mainly for debugging purposes, triggers dag_print
def status(dag):
    dag.dag_print()


def main():
    fp = '342164be-ebb1-4d24-827c-210fdd48ec62'  # Put your $CYLC_WORKFLOW_UUID here to run
    jobs, run_dir = fp_main(fp)

    print('----Constructing DAG----')
    dag = Dag.DAG()
    dag.set_run_dir(run_dir)
    node_count, edge_count = 0, 0

    # add all the nodes in job_dict
    print('Adding nodes...')
    for job in jobs.items():
        job_name = job[0]
        input_files = job[1]['input']
        output_files = job[1]['output']
        dag.add_node(job_name, input_files, output_files)
        node_count += 1
    print(f'Created {node_count} nodes')

    print('Adding edges...')
    for node in dag.get_nodes():
        name = node.get_name()
        output = node.get_output()
        for next_node in reversed(dag.get_nodes()):
            next_name = next_node.get_name()
            next_input = next_node.get_input()
            if name == next_name:  # skip if same node
                continue
            # iterate over the i/o files in the two nodes
            for output_file, output_file_hash in output.items():
                for input_file, input_file_hash in next_input.items():
                    # if the output file matches the input file
                    if output_file == input_file and output_file_hash == input_file_hash:
                        # check if the edge exists, if it does, then add the file name to the existing edge's contents
                        existing_edge = dag.find_edge(node, next_node)
                        if existing_edge:
                            # if filename is not in the edge's contents, add it
                            if output_file not in existing_edge.get_contents():
                                existing_edge.add_content(output_file)
                        else:
                            dag.add_edge(node, next_node, output_file)
                            edge_count += 1
                    if output_file == input_file and output_file_hash != input_file_hash:
                        dag.decrement_fidelity()
    print(f'Created {edge_count} edges')

    status(dag)

    # Uncomment for dag debugging
    # dag.find_job('rename-split-to-pp-regrid_land_daily_cmip.1980')
    # dag.find_file("input", 'land_daily_cmip.geolat_t.nc')

    # draw(dag)

    print("finished")


if __name__ == "__main__":
    main()

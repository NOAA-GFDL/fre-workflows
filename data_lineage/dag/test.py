import Dag
import logging  # Not working properly
from Visualize import draw
from FetchFromFingerprint import main as fp_main
from data_lineage.verification.Validate import main as validate


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    fp = '3afb50cb-0061-4740-9c35-d09a1749e313'  # Put your $CYLC_WORKFLOW_UUID here to run
    jobs, run_dir = fp_main(fp)

    print('----Constructing DAG----')
    dag = Dag.DAG()
    dag.set_run_dir(run_dir)
    node_count, edge_count = 0, 0

    # add all the nodes in job_dict
    print('Adding nodes...')
    for job in jobs.items():
        job_name = job[0]
        job_name = job_name.split('0101')[0]
        job_name, job_date = job_name.split('.')
        formatted_name = job_date + '_' + job_name
        input_files = job[1]['input']
        output_files = job[1]['output']
        dag.add_node(formatted_name, input_files, output_files)
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

    dag.dag_print()
    draw(dag)

    # Uncomment for dag debugging
    # dag.find_job('1981_remap-pp-components-ts-P2Y_land')
    # dag.find_file("output", 'land_month_cmip.198001-198112.cLand.nc')


    validate(dag, run_dir)
    print("finished")


if __name__ == "__main__":
    main()

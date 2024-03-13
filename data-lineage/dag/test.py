import Edge
import Node
import Dag
from Fetch import main as fetch


# mainly for debugging purposes, triggers dag_print
def status(dag):
    dag.dag_print()


def main():
    job_dict = fetch()
    print('----Constructing DAG----')

    dag = Dag.DAG()
    node_count, edge_count = 0, 0

    # add all the nodes in job_dict
    print('Adding nodes...')
    for job in job_dict.items():
        job_name = job[0]
        input_files = job[1]['input_files']
        output_files = job[1]['output_files']
        job_node = Node.Node(job_name, input_files, output_files)
        dag.add_node(job_node)
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
            for output_file in output:  # iterate over the i/o files in the two nodes
                for input_file in next_input:
                    # if the output file matches the input file
                    if output_file[0] == input_file[0] and output_file[1] == input_file[1]:
                        # check if the edge exists, if it does, then add the file name to
                        # the existing edge's contents
                        existing_edge = dag.find_edge(node, next_node)
                        if existing_edge:
                            # if filename is not in the edge's contents, add it
                            if output_file[0] not in existing_edge.get_contents():
                                existing_edge.add_content(output_file[0])
                        else:
                            new_edge = Edge.Edge(node, next_node)
                            new_edge.add_content(output_file[0])
                            dag.add_edge(new_edge)
                            edge_count += 1
                    if output_file[0] == input_file[0] and output_file[1] != input_file[1]:
                        dag.decrement_fidelity()
    print(f'Created {edge_count} edges')

    status(dag)


if __name__ == "__main__":
    main()

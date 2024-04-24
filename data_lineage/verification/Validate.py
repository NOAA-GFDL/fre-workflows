from data_lineage.verification.Parse import read_from_file
from data_lineage.verification.Construct import process_graph


def load_dag_from_config(run_dir):
    data = read_from_file(run_dir)
    config_dag = process_graph(data)
    return config_dag


def compare_dags(serialized_dag, config_dag):
    serial_nodes = serialized_dag.get_nodes()

    for node in serial_nodes:

        if node.get_inbound_edges() != 0:
            continue

        neighbors = serialized_dag.find_neighbors(node)

        for neighbor in neighbors:
            shared_edge = config_dag.find_edge(node, neighbor)

            if not shared_edge:
                print(f'there is a broken edge')


def main(serialized_dag, run_dir):
    config_dag = load_dag_from_config(run_dir)

    compare_dags(serialized_dag, config_dag)

    print('finished validating')
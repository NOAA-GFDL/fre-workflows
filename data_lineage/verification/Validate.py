from data_lineage.verification.Parse import read_from_file
from data_lineage.verification.Construct import process_graph


def load_dag_from_config(run_dir):
    data = read_from_file(run_dir)
    config_dag = process_graph(data)
    return config_dag


def check_node_is_present(node, config_dag):
    name = node.get_name()
    for config_node in config_dag.get_nodes():
        if name == config_node.get_name():
            return True
    return False

def check_edge_is_present(node, serial_dag, config_dag):

    neighbors = serial_dag.find_neighbors(node)

    for neighbor in neighbors:
        shared_edge = config_dag.find_edge(node, neighbor)

        if not shared_edge:
            # What should be done when a serialized edge exists in but is not in config?
            print(f'there is a broken edge.')

def is_subgraph(serial_dag, config_dag):

    serial_nodes = serial_dag.get_nodes()
    config_nodes = config_dag.get_nodes()
    root_nodes = []

    for node in serial_nodes:
        if node.get_inbound_edges() == 0:
            root_nodes.append(node)

    def dfs(serial_node, config_node):

        if serial_node not in serial_nodes:
            return True
        if config_node not in config_nodes:
            return False
        if serial_node.get_name() != config_node.get_name():
            return False

        for neighbor in serial_dag.find_neighbors(serial_node):
            if not dfs(neighbor, config_node):
                return False

        return True

    for config_node in config_nodes:
        for root_node in root_nodes:
            if dfs(root_node, config_node):
                return False

    return True


def compare_dags(serial_dag, config_dag):
    serial_nodes = serial_dag.get_nodes()

    for node in serial_nodes:

        if not check_node_is_present(node, config_dag):
            print(f'{node.get_name()} not found in config dag')

        # fix
        if node.get_inbound_edges() == 0:
            check_edge_is_present(node, serial_dag, config_dag)

    if not is_subgraph(serial_dag, config_dag):
        print("something went wrong")


def main(serial_dag, run_dir):
    config_dag = load_dag_from_config(run_dir)

    compare_dags(serial_dag, config_dag)

    print('finished validating')
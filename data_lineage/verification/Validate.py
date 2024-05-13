from data_lineage.verification.Parse import read_from_file
from data_lineage.verification.Construct import process_graph


def load_dag_from_config(run_dir):
    """
    Calls the primary functions within Parse.py and Construct.py to create a config_dag object.

    The docstrings for the two functions contains more information about their purposes.

    Args:
        run_dir: String
            Scraped from the initial EPMT query, contains the location of the cylc-run. Used to
            locate the configuration file.

    Returns:
        config_dag: Dag
            A complete DAG constructed from a cylc-run's 01-start-01.cylc file.
    """
    data = read_from_file(run_dir)
    config_dag = process_graph(data)
    return config_dag


def check_node_is_present(node, config_dag):
    """
    Checks if the node passed in exists in the config_dag. Comparison checks if
    the names are equal.

    Args:
        node: Node
            A node from the serial_dag
        config_dag: Dag
            Constructed with 01-start-01.cylc

    Returns:
        Boolean whether node exists in config_dag
    """
    name = node.get_name()
    for config_node in config_dag.get_nodes():
        if name == config_node.get_name():
            return True
    return False

def check_edge_is_present(node, serial_dag, config_dag):
    """
    Checks if every outbound edge a node from the serial_dag has exists in
    the config_dag. Comparison checks if the edge object exists

    Args:
        node: Node
            A node from the serial_dag
        serial_dag: Dag
            Constructed with EPMT annotations
        config_dag: Dag
            Constructed with 01-start-01.cylc

    Returns:
        Boolean whether every outbound edge from node exists in config_dag
    """
    neighbors = serial_dag.find_neighbors(node)

    for neighbor in neighbors:
        shared_edge = config_dag.find_edge(node, neighbor)

        if not shared_edge:
            # What should be done when a serialized edge exists in but is not in config?
            print(f'ERROR: There is a broken edge between {node} and {neighbor}.')

def is_subgraph(serial_dag, config_dag):
    """
    Traverses the serial_dag to determine if it is a subgraph of config_dag. Uses the
    depth-first search algorithm to validate.

    Args:
        serial_dag: Dag
            Constructed with EPMT annotations
        config_dag: Dag
            Constructed with 01-start-01.cylc

    Returns:
        Boolean whether serial_dag is a subgraph of config_dag
    """
    serial_nodes = serial_dag.get_nodes()
    config_nodes = config_dag.get_nodes()
    root_nodes = []

    for node in serial_nodes:
        if node.get_inbound_edges() == 0:
            root_nodes.append(node)

    def dfs(serial_node, config_node):

        if serial_node not in serial_nodes:
            print(f'ERROR: Serial node {serial_node} not found in the serial DAG.')
            return True
        if config_node not in config_nodes:
            print(f'ERROR: Config node {config_node} not found in the config DAG.')
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
    """
    Calls the three functions to compare serial_dag and config_dag.

    Args:
        serial_dag: Dag
            Constructed with EPMT annotations
        config_dag: Dag
            Constructed with 01-start-01.cylc
    """
    serial_nodes = serial_dag.get_nodes()

    for node in serial_nodes:

        if not check_node_is_present(node, config_dag):
            print(f'ERROR: {node.get_name()} not found in config DAG.')

        if node.get_inbound_edges() == 0:
            check_edge_is_present(node, serial_dag, config_dag)

    if not is_subgraph(serial_dag, config_dag):
        print("ERROR: There was a problem verifying the DAG.")
    else:
        print('Subgraph comparison complete, no errors were encountered.')


def main(serial_dag, run_dir):
    """
    Verifies serial_dag's legitimacy by comparing it to a DAG constructed from
    the 01-start-01.cylc configuration file of a cylc-run.

    A serial_dag is valid if there are no breakages in the graph, and it's
    structure is reflective of the structure of the configuration DAG.

    Args:
        serial_dag: Dag
            Constructed with EPMT annotations
        run_dir: String
            Absolute path of the cylc-run directory
    """
    print('\nGenerating DAG from log/config/01-start-01.cylc...')

    config_dag = load_dag_from_config(run_dir)

    print('\n----Starting Validation----')
    compare_dags(serial_dag, config_dag)
    print('----Finished Validation----\n')

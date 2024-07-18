import re
import pytest
from data_lineage.dag.Node import Node
from data_lineage.dag.Edge import Edge
from data_lineage.dag.Dag import DAG
from data_lineage.dag.FetchData import format_jobs
from data_lineage.tests.dag.MockEPMTQuery import mock_call, mock_job_names, mock_input, mock_output

MOCK_JOB_NAMES = mock_job_names()
MOCK_INPUT = mock_input()
MOCK_OUTPUT = mock_output()

def mock_formatted_jobs():
    epmt_query = mock_call()
    formatted_jobs = format_jobs(epmt_query)
    return formatted_jobs

def node_array():
    nodes = []
    jobs = mock_formatted_jobs()

    for job in jobs:
        new_node = Node(job_name=job, _input=jobs[job]['input'], _output=jobs[job]['output'])
        nodes.append(new_node)

    return nodes

@pytest.fixture
def dag():
    new_dag = DAG()
    nodes = node_array()

    for node in nodes:
        new_dag.add_node(node)

    new_dag.create_edge(nodes[0], nodes[1])
    new_dag.create_edge(nodes[1], nodes[2])
    new_dag.create_edge(nodes[1], nodes[3])
    new_dag.create_edge(nodes[2], nodes[4])
    new_dag.create_edge(nodes[3], nodes[4])
    new_dag.create_edge(nodes[4], nodes[5])

    for edge in new_dag.get_edges():
        start_node = edge.get_start()
        end_node = edge.get_end()

        for file in start_node.get_output():
            if file in end_node.get_input():
                edge.add_content(file)

    return new_dag

def test_dag_creation(dag):
    """
    Tests if the DAG was created successfully.
    """
    nodes = node_array()

    assert len(dag.get_nodes()) == len(nodes)
    assert len(dag.get_edges()) == 6

def test_dag_add_node(dag):
    """
    Tests the add_node function of a DAG by asserting a node with the name 'testing' exists,
    and the number of nodes in the dag is increased by 1 after the addition of the new node.
    """
    old_node_count = len(dag.get_nodes())

    node = Node(job_name='testing')
    dag.add_node(node)

    new_node_count = len(dag.get_nodes())

    assert new_node_count == old_node_count + 1
    assert dag.find_node('testing') is not None

def test_dag_add_node_exceptions(dag):
    old_node_count = len(dag.get_nodes())

    node_already_present = Node(job_name=MOCK_JOB_NAMES[1]) # STAGE-HISTORY node
    node_wrong_type = 123

    with pytest.raises(ValueError, match=f'ERROR: Node "STAGE-HISTORY" already exists in this DAG'):
        dag.add_node(node_already_present)

    with pytest.raises(TypeError, match=re.escape('ERROR: arg must be a Node object. If a node'
                                                  ' is not created already, use the function'
                                                  ' create_node() instead')):
        dag.add_node(node_wrong_type)

    assert len(dag.get_nodes()) == old_node_count

def test_dag_add_edge(dag):
    old_edge_count = len(dag.get_edges())

    start_node = dag.find_node(MOCK_JOB_NAMES[1])
    end_node = dag.find_node(MOCK_JOB_NAMES[4])

    edge = Edge(start_node, end_node)
    dag.add_edge(edge)

    new_edge_count = len(dag.get_edges())

    assert new_edge_count == old_edge_count + 1
    assert dag.find_edge(start_node, end_node) is not None

def test_dag_add_edge_exceptions(dag):
    old_edge_count = len(dag.get_edges())

    edge_already_exists = Edge(dag.find_node(MOCK_JOB_NAMES[1]),
                               dag.find_node(MOCK_JOB_NAMES[2]))

    new_node = Node(job_name='node_not_in_dag')
    edge_start_node_does_not_exist = Edge(new_node,
                                          dag.find_node(MOCK_JOB_NAMES[2]))
    edge_wrong_type = 123

    with pytest.raises(ValueError, match=f'ERROR: "{edge_already_exists}" '
                                         f'already exists in this DAG'):
        dag.add_edge(edge_already_exists)

    with pytest.raises(ValueError, match='ERROR: Start node "node_not_in_dag"'
                                                   ' does not exist in this DAG'):
        dag.add_edge(edge_start_node_does_not_exist)

    with pytest.raises(TypeError, match=re.escape('ERROR: arg must be an Edge object.'
                                                  ' If a edge is not created already, '
                                                  'use the function create_edge() '
                                                  'instead')):
        dag.add_edge(edge_wrong_type)

    assert len(dag.get_edges()) == old_edge_count

def test_dag_cyclic(dag):
    assert dag.check_acyclic() == True



import pytest
from data_lineage.dag.Node import Node
from data_lineage.dag.Edge import Edge
from data_lineage.dag.FetchData import format_jobs
from data_lineage.tests.dag.MockEPMTQuery import mock_call, mock_job_names, mock_input, mock_output

MOCK_JOB_NAMES = mock_job_names()
MOCK_INPUT = mock_input()
MOCK_OUTPUT = mock_output()

def mock_formatted_jobs():
    epmt_query = mock_call()
    formatted_jobs = format_jobs(epmt_query)
    return formatted_jobs

@pytest.fixture
def node_array():
    nodes = []
    jobs = mock_formatted_jobs()

    for job in jobs:
        new_node = Node(job_name=job, _input=jobs[job]['input'], _output=jobs[job]['output'])
        nodes.append(new_node)

    return nodes

def test_create_nodes(node_array):
    """
    Tests if every node was created successfully.
    """
    for node in node_array:
        assert node.get_name() in MOCK_JOB_NAMES

def test_create_node_with_no_name():
    """
    Tests a node can not be created without being passed a job_name.
    """
    with pytest.raises(TypeError, match=".*missing 1 required positional argument: 'job_name'.*"):
        nameless_node = Node()

def test_find_neighbors(node_array):
    """
    Tests the Node's find_neighbors() function works and returns a list
    of all other nodes where the current node is the starting node in
    the edge and the other node is the ending node.
    """
    edge1 = Edge(node_array[0], node_array[1])
    edge2 = Edge(node_array[1], node_array[2])
    edge2_1 = Edge(node_array[1], node_array[3])
    edge3 = Edge(node_array[2], node_array[4])
    edge3_1 = Edge(node_array[3], node_array[4])
    edge4 = Edge(node_array[4], node_array[5])

    edges = [edge1, edge2, edge2_1, edge3, edge3_1, edge4]

    assert node_array[0].find_neighbors(edges) == [node_array[1]]
    assert node_array[1].find_neighbors(edges) == [node_array[2], node_array[3]]
    assert node_array[2].find_neighbors(edges) == [node_array[4]]
    assert node_array[3].find_neighbors(edges) == [node_array[4]]
    assert node_array[4].find_neighbors(edges) == [node_array[5]]

def test_input(node_array):
    """
    Test if all the input files are added correctly.
    """
    for node in node_array:
        if node.get_input():
            MOCK_INPUT_array = MOCK_INPUT[node.get_name()].split(',')
            # Make sure the node contains the same amount of input files as
            # specified in MOCK_INPUT
            assert len(MOCK_INPUT_array) == len(node.get_input())

            for mock_file in MOCK_INPUT_array:
                file_name, file_hash = mock_file.split(' ')

                assert file_name in node.get_input()
                assert file_hash == node.get_input()[file_name]

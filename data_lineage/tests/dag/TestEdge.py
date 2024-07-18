import pytest
from data_lineage.dag.Node import Node
from data_lineage.dag.Edge import Edge
from data_lineage.dag.FetchData import format_jobs
from data_lineage.tests.dag.MockEPMTQuery import mock_call, mock_job_names, mock_input, mock_output

MOCK_JOB_NAMES = mock_job_names()
MOCK_INPUT = mock_input()
MOCK_OUTPUT = mock_output()

incorrect_content = [123, 12.3, ['test', 'test123'], {'a': 'bc'}]

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


def edge_array():
    nodes = node_array()

    edge1 = Edge(nodes[0], nodes[1])
    edge2 = Edge(nodes[1], nodes[2])
    edge2_1 = Edge(nodes[1], nodes[3])
    edge3 = Edge(nodes[2], nodes[4])
    edge3_1 = Edge(nodes[3], nodes[4])
    edge4 = Edge(nodes[4], nodes[5])

    edges = [edge1, edge2, edge2_1, edge3, edge3_1, edge4]

    return edges

@pytest.mark.parametrize('edge', edge_array())
def test_add_content(edge):
    start_node = edge.get_start()
    end_node = edge.get_end()

    start_files = start_node.get_output()
    end_files = end_node.get_input()

    for file in start_files:
        if file in end_files:
            edge.add_content(file)

    assert edge.get_contents() is not None

@pytest.mark.parametrize('incorrect_content_type', incorrect_content)
def test_add_content_not_string(incorrect_content_type):
    edges = edge_array()
    edge = edges[0]

    with pytest.raises(TypeError, match="ERROR: Content is not a string"):
        edge.add_content(incorrect_content_type)

def test_add_content_already_exists():
    edges = edge_array()
    edge = edges[0]

    edge.add_content('test')
    assert 'test' in  edge.get_contents()

    with pytest.raises(ValueError, match=f'ERROR: test already exists in {edge}'):
        edge.add_content('test')


import pytest
from ...dag import Node as NodeClass
from ...dag import Edge as EdgeClass


@pytest.fixture
def nodes():
    empty_node = NodeClass.Node(job_name='testing')
    dummy_node1 = NodeClass.Node(job_name='Node1', _output='test.txt')
    dummy_node2 = NodeClass.Node(job_name='Node2', _input='test.txt', _output='result.txt')
    dummy_node2_1 = NodeClass.Node(job_name='Node2_1', _output='result.txt')
    dummy_node3 = NodeClass.Node(job_name='Node3', _input='result.txt')

    return [empty_node, dummy_node1, dummy_node2, dummy_node2_1, dummy_node3]


def test_create(nodes):
    for node in nodes:
        assert node is not None


def test_create_with_no_name():
    # Checks a node can not be created without being passed a job_name
    with pytest.raises(TypeError, match=".*missing 1 required positional argument: 'job_name'.*"):
        nameless_node = NodeClass.Node()


def test_get_input(nodes):
    # Tests when there is no input files found
    no_input_nodes = [nodes[0], nodes[1], nodes[3]]
    for node in no_input_nodes:
        with pytest.raises(AttributeError, match='ERROR: No input files found'):
            node.get_input()

    assert nodes[2].get_input() == 'test.txt'
    assert nodes[4].get_input() == 'result.txt'


def test_get_output(nodes):
    # Tests when there is no input files found
    no_input_nodes = [nodes[0], nodes[4]]
    for node in no_input_nodes:
        with pytest.raises(AttributeError, match='ERROR: No output files found'):
            node.get_output()

    assert nodes[1].get_output() == 'test.txt'
    assert nodes[2].get_output() == 'result.txt'
    assert nodes[3].get_output() == 'result.txt'


def test_get_name(nodes):
    names = ['testing', 'Node1', 'Node2', 'Node2_1', 'Node3']
    for i, node in enumerate(nodes):
        assert node.get_name() == names[i]


def test_find_neighbors(nodes):
    edge1 = EdgeClass.Edge(nodes[1], nodes[2])
    edge2 = EdgeClass.Edge(nodes[2], nodes[4])
    edge3 = EdgeClass.Edge(nodes[3], nodes[4])
    edges = [edge1, edge2, edge3]

    assert nodes[0].find_neighbors(edges) == []
    assert nodes[1].find_neighbors(edges) == [nodes[2]]
    assert nodes[2].find_neighbors(edges) == [nodes[4]]
    assert nodes[3].find_neighbors(edges) == [nodes[4]]
    assert nodes[4].find_neighbors(edges) == []


if __name__ == '__main__':
    pytest.main()

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


@pytest.fixture
def edges(nodes):
    edge1 = EdgeClass.Edge(nodes[1], nodes[2])
    edge2 = EdgeClass.Edge(nodes[2], nodes[4])
    edge3 = EdgeClass.Edge(nodes[3], nodes[4])

    return [edge1, edge2, edge3]


def test_create_edge(nodes):
    # Mimic the same behavior as the edges fixture to assert they were created successfully
    edge1 = EdgeClass.Edge(nodes[1], nodes[2])
    edge2 = EdgeClass.Edge(nodes[2], nodes[4])
    edge3 = EdgeClass.Edge(nodes[3], nodes[4])

    edges = [edge1, edge2, edge3]

    for edge in edges:
        assert edge is not None


def test_create_edge_with_missing_param(nodes):
    with pytest.raises(TypeError, match=".*missing 2 required positional arguments: 'start' and 'end.*"):
        no_start_edge = EdgeClass.Edge()
    with pytest.raises(TypeError, match=".*missing 1 required positional argument: 'start'.*"):
        no_start_edge = EdgeClass.Edge(end=nodes[2])
    with pytest.raises(TypeError, match=".*missing 1 required positional argument: 'end'.*"):
        no_start_edge = EdgeClass.Edge(start=nodes[1])


def test_get_start(nodes, edges):
    assert edges[0].get_start() == nodes[1]
    assert edges[1].get_start() == nodes[2]
    assert edges[2].get_start() == nodes[3]


def test_get_end(nodes, edges):
    assert edges[0].get_end() == nodes[2]
    assert edges[1].get_end() == nodes[4]
    assert edges[2].get_end() == nodes[4]


def test_add_content(edges):
    edge = edges[0]
    assert edge.contents == []
    edge.add_content('io_file.nc')
    assert edge.contents == ['io_file.nc']
    edge.add_content('file2.nc')
    assert edge.contents == ['io_file.nc', 'file2.nc']


def test_get_contents(edges):
    edge = edges[0]
    edge.add_content('io_file.nc')
    assert edge.get_contents() == ['io_file.nc']
    edge.add_content('file2.nc')
    assert edge.get_contents() == ['io_file.nc', 'file2.nc']


def test_add_content_type_error(edges):
    edge = edges[0]
    with pytest.raises(TypeError, match=f"ERROR: Content is not a string"):
        edge.add_content(123)
    assert edge.get_contents() == []


def test_add_content_value_error(edges):
    edge = edges[0]
    edge.add_content('io_file.nc')
    with pytest.raises(ValueError, match=f"ERROR: io_file.nc already exists in {edge}"):
        edge.add_content('io_file.nc')
    assert edge.get_contents() == ['io_file.nc']


if __name__ == '__main__':
    pytest.main()

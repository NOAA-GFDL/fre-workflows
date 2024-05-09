import pytest

from ...dag import Node as NodeClass
from ...dag import Edge as EdgeClass
from ...dag import Dag as DagClass


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


@pytest.fixture
def blank_dag():
    return DagClass.DAG()


@pytest.fixture
def dag(nodes, edges):
    dag = DagClass.DAG()
    build_dag(nodes, edges, dag)
    return dag


def build_dag(nodes, edges, dag):
    """
                        _____
                       | DAG |
                        ‾‾‾‾‾
        dummy_node1                      empty_node
                    \
                        dummy_node2
                                    \
                                      dummy_node3
                                    /
                        dummy_node2_1
    """
    for node in nodes:
        dag.add_node(node)
    for edge in edges:
        dag.add_edge(edge)
    return dag


def test_get_nodes(blank_dag, dag, nodes):
    assert blank_dag.get_nodes() == []

    # dag.add_nodes(node for node in nodes) in the build_dag helper function
    assert dag.get_nodes() == nodes

    node = nodes[0]

    assert node not in blank_dag.get_nodes()
    assert node in dag.get_nodes()


def test_add_node(blank_dag):
    assert len(blank_dag.get_nodes()) == 0

    new_node = NodeClass.Node('test node')
    blank_dag.add_node(new_node)

    assert len(blank_dag.get_nodes()) == 1
    assert new_node in blank_dag.get_nodes()


def test_add_existing_node_error(blank_dag):
    node = NodeClass.Node('test node')
    blank_dag.add_node(node)
    assert blank_dag.get_nodes() == [node]

    with pytest.raises(ValueError, match=f"ERROR: Node '{node.name}' already exists in this DAG"):
        blank_dag.add_node(node)

    assert blank_dag.get_nodes() == [node]


def test_get_edges(blank_dag, dag, edges):
    assert blank_dag.get_edges() == []
    # dag.add_nodes(node for node in nodes) in the build_dag helper function
    assert dag.get_edges() == edges

    edge = edges[0]

    assert edge not in blank_dag.get_edges()
    assert edge in dag.get_edges()


def test_add_edge(blank_dag):
    nodes = [
        NodeClass.Node(job_name='Node1',
                       _output="[('test.txt', '60d0a1f8')]"),
        NodeClass.Node(job_name='Node2',
                       _input="[('test.txt', '60d0a1f8')]",
                       _output="[('result.txt',  '10f3dff5')]")
    ]

    for node in nodes:
        blank_dag.add_node(node)

    edge = EdgeClass.Edge(nodes[0], nodes[1])

    assert blank_dag.get_edges() == []
    blank_dag.add_edge(edge)
    assert blank_dag.get_edges() == [edge]


def test_add_edge_already_exist(dag, nodes, edges):
    edge = edges[0]
    with pytest.raises(ValueError, match=f"ERROR: {edge} already exists in this DAG"):
        dag.add_edge(edge)


def test_find_node(dag, nodes):
    assert dag.find_node('Node1') == nodes[1]

    new_node = NodeClass.Node('test_find_node')
    dag.add_node(new_node)
    assert dag.find_node('test_find_node') == new_node


def test_find_node_does_not_exist(dag):
    assert dag.find_node('new_node') is None
    # Existing Node1 has a capital N, testing for lowercase here
    assert dag.find_node('node1') is None
    assert dag.find_node('') is None


def test_find_edge(dag, nodes, edges):
    """
    edges[0] = nodes[1] -> nodes[2]
    edges[1] = nodes[2] -> nodes[4]
    edges[2] = nodes[3] -> nodes[4]
    """

    expected_edges = {
        (nodes[1], nodes[2]): edges[0],
        (nodes[2], nodes[4]): edges[1],
        (nodes[3], nodes[4]): edges[2],
        (nodes[1], nodes[4]): None  # A fake edge that shouldn't exist
    }

    for edge_nodes, expected_edge in expected_edges.items():
        edge = dag.find_edge(*edge_nodes)
        assert edge == expected_edge


def test_find_neighbors(dag, nodes, edges):
    new_edge = EdgeClass.Edge(nodes[1], nodes[3])
    dag.add_edge(new_edge)
    neighbors = {
        nodes[0]: [],
        nodes[1]: [nodes[2], nodes[3]],  # Added an extra neighbor
        nodes[2]: [nodes[4]],
        nodes[3]: [nodes[4]],
    }

    for start, end in neighbors.items():
        assert dag.find_neighbors(start) == end


def test_acyclic(dag, nodes, edges):
    assert not dag.check_cyclic()

    cyclic_edge = EdgeClass.Edge(nodes[4], nodes[1])
    dag.add_edge(cyclic_edge)
    assert dag.check_cyclic()


if __name__ == '__main__':
    pytest.main()

import unittest

from ...dag import Node as NodeClass
from ...dag import Edge as EdgeClass
from ...dag import Dag as DagClass


class TestDag(unittest.TestCase):

    def setUp(self):
        self.dag = DagClass.DAG()

    def buildDag(self):
        """
            DummyNode1
                       \
                         DummyNode2
                                      \
                                        DummyNode3
                                      /
                         DummyNode2_1
        """
        self.DummyNode1 = NodeClass.Node(job_name='Node1',
                                         _output="[('test.txt', '60d0a1f8')]")
        self.DummyNode2 = NodeClass.Node(job_name='Node2',
                                         _input="[('test.txt', '60d0a1f8')]",
                                         _output="[('result.txt',  '10f3dff5')]")
        self.DummyNode2_1 = NodeClass.Node(job_name='Node2_1',
                                           _output="[('result.txt',  '10f3dff5')]")
        self.DummyNode3 = NodeClass.Node(job_name='Node3',
                                         _input="[('result.txt',  '10f3dff5')]")
        self.edge1 = EdgeClass.Edge(self.DummyNode1, self.DummyNode2)
        self.edge2 = EdgeClass.Edge(self.DummyNode2, self.DummyNode3)
        self.edge3 = EdgeClass.Edge(self.DummyNode2_1, self.DummyNode3)

        nodes = [self.DummyNode1, self.DummyNode2, self.DummyNode2_1, self.DummyNode3]
        edges = [self.edge1, self.edge2, self.edge3]

        for node in nodes:
            self.dag.add_node(node)

        for edge in edges:
            self.dag.add_edge(edge)

    def test_add_node(self):
        old_node_count = len(self.dag.nodes)
        new_node = NodeClass.Node(job_name='Node1')
        self.dag.add_node(new_node)
        new_node_count = len(self.dag.nodes)
        self.assertNotEqual(old_node_count, new_node_count)
        self.assertEqual(len(self.dag.nodes), 1)
        self.assertEqual(self.dag.nodes, [new_node])

    def test_add_node_error(self):
        existing_node = NodeClass.Node(job_name='Node1')
        self.dag.add_node(existing_node)

        # Define error nodes with duplicate names
        error_nodes = [
            existing_node,
            NodeClass.Node(job_name='Node1', _output="[('error.txt', '68a74b1f')]")
        ]
        for node in error_nodes:
            with self.assertRaises(ValueError) as context:
                self.dag.add_node(node)
            self.assertEqual(str(context.exception), f"ERROR: Node '{node.name}' already exists in this DAG")
        self.assertEqual(len(self.dag.nodes), 1)

    def test_add_edge(self):
        nodes = [
            NodeClass.Node(job_name='Node1',
                           _output="[('test.txt', '60d0a1f8')]"),
            NodeClass.Node(job_name='Node2',
                           _input="[('test.txt', '60d0a1f8')]",
                           _output="[('result.txt',  '10f3dff5')]")
        ]

        for node in nodes:
            self.dag.add_node(node)

        new_edge = EdgeClass.Edge(nodes[0], nodes[1])

        self.dag.add_edge(new_edge)

    def test_find_node(self):
        pass

    def test_find_edge(self):
        pass

    def test_find_neighbors(self):
        pass

    def test_find_nodes(self):
        pass

    def test_find_edges(self):
        pass

    def test_fidelity(self):
        pass

    def test_acyclic(self):
        pass

import unittest
from ...dag import Node as NodeClass
from ...dag import Edge as EdgeClass


class TestNode(unittest.TestCase):

    def setUp(self):
        self.EmptyNode = NodeClass.Node(job_name='testing')
        self.DummyNode1 = NodeClass.Node(job_name='Node1', _output='test.txt')
        self.DummyNode2 = NodeClass.Node(job_name='Node2', _input='test.txt', _output='result.txt')
        self.DummyNode2_1 = NodeClass.Node(job_name='Node2', _output='result.txt')
        self.DummyNode3 = NodeClass.Node(job_name='Node3', _input='result.txt')

    def test_create(self):
        self.assertIsNotNone(self.EmptyNode)
        self.assertIsNotNone(self.DummyNode1)
        self.assertIsNotNone(self.DummyNode2)
        self.assertIsNotNone(self.DummyNode2_1)
        self.assertIsNotNone(self.DummyNode3)

    def test_get_input(self):
        # Tests when there is no input files found
        no_input = [self.EmptyNode, self.DummyNode1, self.DummyNode2_1]
        for node in no_input:
            with self.assertRaises(AttributeError) as context:
                node.get_input()
            self.assertEqual(str(context.exception), 'ERROR: No input files found')

        self.assertEqual(self.DummyNode2.get_input(), 'test.txt')
        self.assertEqual(self.DummyNode3.get_input(), 'result.txt')

    def test_get_output(self):
        # Tests when there is no output files found
        no_output = [self.EmptyNode, self.DummyNode3]
        with self.assertRaises(AttributeError) as context:
            self.EmptyNode.get_output()
        self.assertEqual(str(context.exception), 'ERROR: No output files found')

        self.assertEqual(self.DummyNode1.get_output(), 'test.txt')
        self.assertEqual(self.DummyNode2.get_output(), 'result.txt')
        self.assertEqual(self.DummyNode2_1.get_output(), 'result.txt')

    def test_find_neighbors(self):
        edge1 = EdgeClass.Edge(self.DummyNode1, self.DummyNode2)
        edge2 = EdgeClass.Edge(self.DummyNode2, self.DummyNode3)
        edge3 = EdgeClass.Edge(self.DummyNode2_1, self.DummyNode3)
        edges = [edge1, edge2, edge3]

        self.assertEqual(self.EmptyNode.find_neighbors(edges), [])
        self.assertEqual(self.DummyNode1.find_neighbors(edges), [self.DummyNode2])
        self.assertEqual(self.DummyNode2.find_neighbors(edges), [self.DummyNode3])
        self.assertEqual(self.DummyNode2_1.find_neighbors(edges), [self.DummyNode3])


if __name__ == '__main__':
    unittest.main(verbosity=0)

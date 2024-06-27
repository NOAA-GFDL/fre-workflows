import unittest
from ...dag import Node as NodeClass
from ...dag import Edge as EdgeClass


class TestEdge(unittest.TestCase):

    def setUp(self):
        self.DummyNode1 = NodeClass.Node(job_name='Node1', _output='test.txt')
        self.DummyNode2 = NodeClass.Node(job_name='Node2', _input='test.txt', _output='result.txt')
        self.DummyNode2_1 = NodeClass.Node(job_name='Node2', _output='result.txt')
        self.DummyNode3 = NodeClass.Node(job_name='Node3', _input='result.txt')

        self.edge1 = EdgeClass.Edge(self.DummyNode1, self.DummyNode2)
        self.edge2 = EdgeClass.Edge(self.DummyNode2, self.DummyNode3)
        self.edge3 = EdgeClass.Edge(self.DummyNode2_1, self.DummyNode3)

    def test_get_start(self):
        self.assertEqual(self.edge1.get_start(), self.DummyNode1)
        self.assertEqual(self.edge2.get_start(), self.DummyNode2)
        self.assertEqual(self.edge3.get_start(), self.DummyNode2_1)

    def test_get_end(self):
        self.assertEqual(self.edge1.get_end(), self.DummyNode2)
        self.assertEqual(self.edge2.get_end(), self.DummyNode3)
        self.assertEqual(self.edge2.get_end(), self.DummyNode3)

    def test_add_content(self):
        # add 'intermediate.txt' to edge1.contents
        self.assertEqual(len(self.edge1.contents), 0)
        self.edge1.add_content('intermediate.txt')
        self.assertEqual(self.edge1.contents, ['intermediate.txt'])

        # check if edge1.contents still only has 1 item inside, then add middle.txt
        self.assertEqual(len(self.edge1.contents), 1)
        self.edge1.add_content('middle.txt')
        self.assertEqual(len(self.edge1.contents), 2)
        self.assertEqual(self.edge1.contents, ['intermediate.txt', 'middle.txt'])

    def test_add_content_type_error(self):
        # try to add 123 to edge1.contents, but it produces a TypeError
        with self.assertRaises(TypeError) as context:
            self.edge1.add_content(123)
        self.assertEqual(str(context.exception), 'ERROR: Content is not a string')
        self.assertEqual(len(self.edge1.contents), 0)

    def test_add_content_value_error(self):
        # add 'intermediate.txt' to edge1.contents
        self.assertEqual(len(self.edge1.contents), 0)
        self.edge1.add_content('intermediate.txt')
        self.assertEqual(self.edge1.contents, ['intermediate.txt'])

        # try to add 'intermediate.txt' again, but it produces a ValueError
        with self.assertRaises(ValueError) as context:
            self.edge1.add_content('intermediate.txt')
        self.assertEqual(str(context.exception), 'ERROR: intermediate.txt already exists in Edge from Node1 to Node2')
        self.assertEqual(len(self.edge1.contents), 1)

    def test_get_contents(self):
        self.assertEqual(self.edge1.get_contents(), [])
        self.edge1.add_content('intermediate.txt')
        self.assertEqual(len(self.edge1.contents), 1)
        self.assertEqual(len(self.edge1.get_contents()), 1)
        self.assertEqual(self.edge1.get_contents(), ['intermediate.txt'])
        self.edge1.add_content('temporary.txt')
        self.assertEqual(len(self.edge1.contents), 2)
        self.assertEqual(len(self.edge1.get_contents()), 2)
        self.assertEqual(self.edge1.get_contents(), ['intermediate.txt', 'temporary.txt'])


if __name__ == '__main__':
    unittest.main(verbosity=2)

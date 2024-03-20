from collections import defaultdict


class DAG:
    def __init__(self):
        self.nodes = []
        self.edges = []
        self.fidelity = 100
        self.graph = defaultdict(list)

    def __str__(self):
        return f'Directed Acyclic Graph with {len(self.nodes)} nodes and {len(self.edges)} edges'

    def __repr__(self):
        return f'Directed Acyclic Graph with {len(self.nodes)} nodes and {len(self.edges)} edges'

    def add_node(self, node):
        if node.name in self.nodes:
            raise ValueError(f"Node '{node.name}' already exists in this DAG")
        self.nodes.append(node)

    def add_edge(self, edge):
        start_name = self.find_node(edge.start.get_name())
        end_name = self.find_node(edge.end.get_name())
        if start_name not in self.nodes:
            raise ValueError(f"Start node '{edge.start}' does not exist in this DAG")
        if end_name not in self.nodes:
            raise ValueError(f"End node '{edge.end.name}' does not exist in this DAG")
        self.edges.append(edge)

    def find_node(self, name):
        for node in self.nodes:
            if node.get_name() == name:
                return node
        return None

    def find_edge(self, start_node, end_node):
        for edge in self.edges:
            if edge.get_start() == start_node and edge.get_end() == end_node:
                return edge
        return None

    def find_neighbors(self, node):
        neighbors = []
        for edge in self.edges:
            if edge.get_start() is node:
                neighbors.append(edge.get_end())
        return neighbors

    def get_nodes(self):
        return self.nodes

    def get_edges(self):
        return self.edges

    def get_fidelity(self):
        return self.fidelity

    def decrement_fidelity(self):
        self.fidelity -= 1
        return

    def check_cyclic_util(self, node, visited, parent):

        idx = self.nodes.index(node)
        visited[idx] = True
        neighbors = self.find_neighbors(node)

        for neighbor in neighbors:
            neighbor_idx = self.nodes.index(neighbor)
            if not visited[neighbor_idx]:
                if self.check_cyclic_util(neighbor, visited, node):
                    return True
            elif parent != neighbor and parent is not None:
                # If the neighbor is visited, and it's not the parent node
                return True

        return False

    def check_cyclic(self):
        visited = [False] * len(self.nodes)

        for node in self.nodes:
            if not visited[self.nodes.index(node)]:
                if self.check_cyclic_util(node, visited, None):
                    return True
        return False

    def dag_print(self):
        print(f'----DAG Statistics----')
        print(f'Nodes    : {len(self.nodes)}')
        print(f'Edges    : {len(self.edges)}')
        print(f'Acyclic  : {self.check_cyclic()}')
        print(f'Fidelity : {self.fidelity}/100')
        return

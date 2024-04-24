class Node:
    def __init__(self, job_name, _input=None, _output=None):
        self.name = job_name

        if _input:
            self.input = _input
        else:
            self.input = {}

        if _output:
            self.output = _output
        else:
            self.output = {}

        self.inbound_edges = 0

    def __str__(self):
        return f'{{{self.name}, {self.input}, {self.output}}}'

    def __repr__(self):
        return f'{self.name}'

    def find_neighbors(self, edges):
        neighbors = []
        for edge in edges:
            if edge.get_start() == self and edge.get_end not in neighbors:
                neighbors.append(edge.get_end())
        return neighbors

    def get_name(self):
        return self.name

    def get_input(self):
        if not hasattr(self, 'input'):
            raise AttributeError(f'ERROR: No input files found')
        return self.input

    def get_output(self):
        if not hasattr(self, 'output'):
            raise AttributeError(f'ERROR: No output files found')
        return self.output

    def get_inbound_edges(self):
        return self.inbound_edges

    def increment_inbound_edeges(self):
        self.inbound_edges += 1
        return

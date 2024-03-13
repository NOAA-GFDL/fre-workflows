class Node:
    def __init__(self, job_name, _input, _output):
        self.name = job_name
        self.input = _input
        self.output = _output

    def __str__(self):
        return f'{{{self.name}, {self.input}, {self.output}}}'

    def __repr__(self):
        return f'{self.name}'

    def find_edges(self):
        pass

    def find_neighbors(self, edges):
        pass

    def get_name(self):
        return self.name

    def get_input(self):
        return self.input

    def get_output(self):
        return self.output

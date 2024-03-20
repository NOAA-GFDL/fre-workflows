class Node:
    def __init__(self, job_name, _input=None, _output=None):
        self.name = job_name
        if _input:
            self.input = _input
        if _output:
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
        if not hasattr(self, 'input'):
            raise AttributeError("No input files found")
        return self.input

    def get_output(self):
        if not hasattr(self, 'output'):
            raise AttributeError("No output files found")
        return self.output

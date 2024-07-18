from data_lineage.dag.Node import Node


class Edge:
    def __init__(self, start: Node, end: Node, contents=None):
        self.start = start
        self.end = end
        self.contents = []

    def __str__(self):
        return f'Edge from {self.start.get_name()} to {self.end.get_name()}'

    def __repr__(self):
        return f'{{{self.start.get_name()}, {self.end.get_name()}}}'

    def add_content(self, content):
        if type(content) != str:
            raise TypeError('ERROR: Content is not a string')
        if content in self.get_contents():
            raise ValueError(f'ERROR: {content} already exists in {self}')
        self.contents.append(str(content))

    def get_start(self):
        return self.start

    def get_end(self):
        return self.end

    def get_contents(self):
        return self.contents

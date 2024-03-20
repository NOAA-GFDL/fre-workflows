import Node


class Edge:
    def __init__(self, u: Node, v: Node):
        self.start = u
        self.end = v
        self.contents = []

    def __str__(self):
        return f'Edge from {self.start.get_name()} to {self.end.get_name()}'

    def __repr__(self):
        return f'{{{self.start.get_name()}, {self.end.get_name()}}}'

    def add_content(self, content):
        if content in self.get_contents():
            raise ValueError(f'{content} already exists in {self}')
        self.contents.append(content)

    def get_start(self):
        return self.start

    def get_end(self):
        end = self.end
        return end

    def get_contents(self):
        return self.contents

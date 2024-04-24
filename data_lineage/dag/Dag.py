import subprocess
import Node
import Edge


class DAG:
    def __init__(self):
        # TODO : refactor as a dictionary to speed up lookup time for nodes and edges
        self.nodes = []
        self.edges = []
        self.fidelity = 100
        self.run_dir = ''

    def __str__(self):
        return f'Directed Acyclic Graph with {len(self.nodes)} nodes and {len(self.edges)} edges'

    def __repr__(self):
        return f'Directed Acyclic Graph with {len(self.nodes)} nodes and {len(self.edges)} edges'

    def add_node(self, job_name, _input = None, _output = None):

        for existing_node in self.get_nodes():
            if job_name == existing_node.get_name():
                raise ValueError(f"ERROR: Node '{node.name}' already exists in this DAG")

        node = Node.Node(job_name, _input, _output)
        self.nodes.append(node)

    def add_edge(self, node, next_node, content=None):

        start_name = self.find_node(node.get_name())
        end_name = self.find_node(next_node.get_name())

        if start_name not in self.nodes:
            raise ValueError(f"Start node '{edge.start}' does not exist in this DAG")
        if end_name not in self.nodes:
            raise ValueError(f"End node '{edge.end.name}' does not exist in this DAG")

        edge = Edge.Edge(node, next_node, contents=[content])
        next_node.increment_inbound_edeges()

        if edge in self.edges:
            raise ValueError(f"ERROR: {edge} already exists in this DAG")

        self.edges.append(edge)

    def find_node(self, name):
        for node in self.nodes:
            if node.get_name() == name:
                return node
        return None

    def find_edge(self, start_node, end_node):
        for edge in self.edges:
            if edge.get_start().get_name() == start_node.get_name() and edge.get_end().get_name() == end_node.get_name():
                return edge
        return None

    def find_neighbors(self, node):
        neighbors = []
        for edge in self.edges:
            if edge.get_start() is node and edge.get_end() not in neighbors:
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

    def set_run_dir(self, directory):
        self.run_dir = directory
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

    def find_job(self, name):
        """
        For debugging
        """
        for node in self.nodes:
            if name in node.name:
                print(f'Found {node.name}')
                print(f'   input')
                for i in node.input:
                    print(i)
                print(f'   output')
                for o in node.output:
                    print(o)
                print(f'\n')

    def find_file(self, io_type, file):
        """
        For debugging
        """
        # converts io_type to a mapping for lookup
        io_files = {
            'input': lambda node1: node.input,
            'output': lambda node1: node.output
        }

        for node in self.nodes:
            files_list = io_files[io_type](node)
            for node_file in files_list:
                if file in node_file:
                    print(f'{node.name} has {node_file} in its {io_type} list')

    def find_total_job_count(self):
        """
        Counts the number of directories in cylc-run/runN/log/job/*/*
        """
        total_jobs = []
        job_dir = f'{self.run_dir}/log/job/'
        cmd = f'ls -ldt {job_dir}*/*/'
        jobs = subprocess.run(cmd, capture_output=True, shell=True, text=True)
        jobs_split = jobs.stdout.split('\n')

        for line in jobs_split:
            # skip jobs that contain these keywords, there should not be any analysis, but just to make sure
            job_ignore = ['clean', 'pp-starter', 'stage-history', 'analysis']
            if any(keyword in line for keyword in job_ignore):
                continue
            total_jobs.append(line)

        # `.` is counted as a dir in the job_dir, subtract one entry from total_jobs
        return len(total_jobs) - 1

    def dag_print(self):
        print(f'----DAG Statistics----')
        print(f'Nodes    : {len(self.nodes)}')
        print(f'Omitted  : {self.find_total_job_count() - len(self.nodes)}')
        print(f'Edges    : {len(self.edges)}')
        print(f'Acyclic  : {self.check_cyclic()}')
        print(f'Fidelity : {self.fidelity}/100')
        return

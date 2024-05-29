import subprocess
from data_lineage.dag.Node import Node
from data_lineage.dag.Edge import Edge


class DAG:
    def __init__(self):
        # TODO : refactor as a dictionary to speed up lookup time for
        #  nodes and edges
        self.nodes = []
        self.edges = []
        self.fidelity = 100
        self.run_dir = ''

    def __str__(self):
        return (f'Directed Acyclic Graph with {len(self.nodes)} nodes '
                f'and {len(self.edges)} edges')

    def __repr__(self):
        return (f'Directed Acyclic Graph with {len(self.nodes)} nodes '
                f'and {len(self.edges)} edges')

    def add_node(self, node):
        """
            Adds an node object that already exists to the DAG.

            If the node is created in another function, use this to add it to the DAG. Otherwise,
            use create_node().
            """
        if not isinstance(node, Node):
            raise TypeError(f'{node} must be a Node object. If a node is not created already,'
                            f'use the function create_node() instead.')
        self.nodes.append(node)

    def add_edge(self, edge):
        """
        Adds an edge object that already exists to the DAG.

        If the edge is created in another function, use this to add it to the DAG. Otherwise,
        use create_edge().
        """
        if not isinstance(edge, Edge):
            raise TypeError(f'{edge} must be an Edge object. If a edge is not created already,'
                            f'use the function create_edge() instead.')
        self.edges.append(edge)

    def create_node(self, job_name, _input = None, _output = None):
        """
        Creates a new node and adds it to the DAG.

        Args:
            job_name: String
                This will be the name of the node created.
            _input: List
                The input file names for the job.
            _output: List
                The output file names for the job.
        """
        for existing_node in self.get_nodes():
            if job_name == existing_node.get_name():
                raise ValueError(f'ERROR: Node "{node.name}" already '
                                 f'exists in this DAG')

        node = Node(job_name, _input, _output)
        self.nodes.append(node)

    def create_edge(self, node, next_node, content=None):
        """
        Creates a new edge and adds it to the DAG.

        Args:
            node: Node
                The starting (outbound) node of the edge.
            next_node: Node
                The ending (inbound) node of the edge.
            content: String
                The file that is shared between the nodes. The file is
                represented as the absolute path.
        """
        start_name = self.find_node(node.get_name())
        end_name = self.find_node(next_node.get_name())

        if start_name not in self.nodes:
            raise ValueError(f'Start node "{edge.start}" does not exist in this DAG')
        if end_name not in self.nodes:
            raise ValueError(f'End node "{edge.end.name}" does not exist in this DAG')

        edge = Edge(node, next_node, contents=[content])
        next_node.increment_inbound_edeges()

        if edge in self.edges:
            raise ValueError(f'ERROR: {edge} already exists in this DAG')

        self.edges.append(edge)

    def find_node(self, name):
        for node in self.nodes:
            if node.get_name() == name:
                return node
        return None

    def find_edge(self, start_node, end_node):
        """
        Check if an edge exists between two nodes.

        Args:
            start_node: Node
            end_node: Node
        Returns:
            The edge if it exists, otherwise return None.
        """
        for edge in self.edges:
            if (edge.get_start().get_name() == start_node.get_name()
                    and edge.get_end().get_name() == end_node.get_name()):
                return edge
        return None

    def find_neighbors(self, node):
        """
        Iterates through the list of edges and returns all that have `node` as the start node.

        Args:
            node: Node
                The starting node in the edge
        Returns:
            neighbors: List
                The nodes that share an edge with `node`. The neighbors are always
                the end of the edge.
        """
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
        """
        The run directory is important for find_total_job_count(). The directory
        path is saved within the DAG when it is created.
        """
        self.run_dir = directory
        return

    def check_cyclic_helper(self, node, visited, parent):
        """
        Recursive DFS.
        """
        idx = self.nodes.index(node)
        visited[idx] = True
        neighbors = self.find_neighbors(node)

        for neighbor in neighbors:
            neighbor_idx = self.nodes.index(neighbor)
            if not visited[neighbor_idx]:
                if self.check_cyclic_helper(neighbor, visited, node):
                    return True
            elif parent != neighbor and parent is not None:
                # If the neighbor is visited, and it's not the parent node
                return True

        return False

    def check_cyclic(self):
        """
        Performs Depth-First-Search (DFS) on the DAG.

        Returns:
            True if DFS visits all nodes within the DAG. False otherwise.
        """
        visited = [False] * len(self.nodes)

        for node in self.nodes:
            if not visited[self.nodes.index(node)]:
                if self.check_cyclic_helper(node, visited, None):
                    return True
        return False

    def find_job(self, name_substring):
        """
        For debugging. Prints all jobs that contain `name_substring`
        in its job name.

`       Args:
            name_substring: String
                Substring that jobs need in order to be printed.
        """
        for node in self.nodes:
            if name_substring in node.name:
                print(f'Found {node.name}')
                print(f'   input')
                for i in node.input:
                    print(i)
                print(f'   output')
                for o in node.output:
                    print(o)
                print(f'\n')

    def find_file(self, io_type, file_name_substring):
        """
        For debugging. Prints all nodes that contain `file_name_substring`
        in its `io_type`.

        Args:
            io_type: String
                Should be either 'input' or 'output'.
            file_name_substring: String
                Substring that file's need in their name in order to be printed.
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
        Counts the number of directories in cylc-run/runN/log/job/*/*.

        Uses `ls -ldt <dir>` and counts the number of lines returned from the command.

        Returns:
            total_job_num: Int
                The number of jobs in a workflow excluding any jobs that contain the
                substrings in jobs_ignore in the function.
        """
        if self.run_dir == '':
            raise ValueError('ERROR: run_dir is not present in this DAG.')

        total_jobs = []
        job_dir = f'{self.run_dir}/log/job/'
        cmd = f'ls -ldt {job_dir}*/*/'
        jobs = subprocess.run(cmd, capture_output=True, shell=True, text=True)
        jobs_split = jobs.stdout.split('\n')

        for line in jobs_split:
            # skip jobs that contain these keywords, there should not be any
            # analysis, but just to make sure it should be added.
            job_ignore = ['clean', 'pp-starter', 'stage-history', 'analysis']
            if any(keyword in line for keyword in job_ignore):
                continue
            total_jobs.append(line)

        # `.` is counted as a dir in the job_dir, subtract one entry from total_jobs
        total_job_num = len(total_jobs) - 1
        return total_job_num

    def dag_print(self):
        omitted_jobs = max(self.find_total_job_count() - len(self.nodes), 0)

        print(f'\n----DAG Statistics----')
        print(f'Nodes    : {len(self.nodes)}')
        print(f'Omitted  : {omitted_jobs}')
        print(f'Edges    : {len(self.edges)}')
        print(f'Acyclic  : {self.check_cyclic()}')
        print(f'Fidelity : {self.fidelity}/100')
        return

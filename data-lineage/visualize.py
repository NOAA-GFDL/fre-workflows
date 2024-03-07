#!/usr/bin/env python3

import networkx as nx
import matplotlib.pyplot as plt
import fetch

# TODO: import pylint requires pip
# TODO: import joblib for fetch.py

debug = False


# TODO add to new file
def draw(dag):
    pos = nx.planar_layout(dag)
    args = {
        'with_labels': True,
        'arrows': True,
        'node_size': 500,
        'node_color': 'skyblue',
        'font_size': 8,
        'font_weight': 'bold',
        'arrowsize': 20
    }
    nx.draw(dag, pos, **args)

    plt.title("Directed Acyclic Graph for am5_c96L33_amip/run52")
    print("Finished drawing dag, closing the graph window will terminate the program.")
    plt.show()


def add_nodes(dag, job_dict):
    for job in job_dict:
        for next_job in reversed(job_dict):
            if job != next_job:
                job_name = job.split('T0000')[0]
                if debug:
                    print(f'[DEBUG] Job name : {job_name}')
                dag.add_node(job_name)
                if debug:
                    print(f'[DEBUG] added {job_name} as a node')


def create_dag(job_dict):
    dag = nx.MultiDiGraph()

    edge_dict = {}

    add_nodes(dag, job_dict)

    for job in job_dict:
        for next_job in reversed(job_dict):
            if job != next_job:
                job_name = job.split('T0000')[0]
                next_job_name = next_job.split('T0000')[0]
                io_data = job_dict.get(job)
                next_io_data = job_dict.get(next_job)

                for filename, file_info in io_data['output_files'].items():
                    checksum, filepath = file_info
                    if debug:
                        print(f'[DEBUG] filename : {filename}')
                        print(f'[DEBUG] checksum : {str(checksum)}')
                        print(f'[DEBUG] filepath : {filepath}')
                    for next_filename, next_file_info in next_io_data['input_files'].items():
                        next_checksum, next_filepath = next_file_info
                        if filename == next_filename and checksum == next_checksum:

                            # Saves file contents in edge_dict. [(job, next_job)] is the
                            # key and the values are each file that is output from
                            # 'job' and input in 'next_job'
                            edge_link = (job_name, next_job_name)
                            if edge_link in edge_dict:
                                edge_dict[edge_link].append(filename)
                            else:
                                edge_dict[edge_link] = [filename]
                            if debug:
                                print(f'Added {filename} to {edge_link}')

                            if dag.has_edge(job_name, next_job_name):
                                edge = dag[job_name][next_job_name]
                                edge_weight = edge[0]['weight']
                                dag[job_name][next_job_name][0]['weight'] = edge_weight + 1
                                if debug:
                                    print(f'New weight of ({job_name}, {next_job_name}) is {edge_weight + 1}')
                                continue
                            else:
                                dag.add_edge(job_name, next_job_name, weight=1)
                                if debug:
                                    print(f'[DEBUG] Added an edge between {job_name} and {next_job_name}')
    print("Finished creating dag")
    return dag, edge_dict


# TODO add to new file
def traverse_dag(dag, edge_dict):
    print(f'---DAG Stats---')
    print(f'Number of nodes: {len(dag.nodes)}')
    print(f'Number of edges: {len(dag.edges)}')
    print(f'Is Acyclic? {str(nx.is_directed_acyclic_graph(dag))}')
    for node in dag.nodes():
        print(f'\nLooking at node {node}')
        edges = dag.edges(node, data=True)
        if edges:
            print(f'{node} shares an edge with')
            for next_job in edges:
                next_job_name = next_job[1]
                edge_link = (node, next_job_name)
                edge_files = edge_dict[edge_link]
                weight = dag[node][next_job_name][0]["weight"]
                print(f'    ╰ {next_job[1]} with a weight of {weight}')
                for file in edge_files:
                    print(f'        ├ {file}')
        else:
            print(f'{node} does not share any edges')
    print('\nFinished traversing dag')
    return 0


def main():
    job_dict = fetch.main()
    dag, edge_dict = create_dag(job_dict)
    traverse_dag(dag, edge_dict)
    draw(dag)


if __name__ == "__main__":
    main()

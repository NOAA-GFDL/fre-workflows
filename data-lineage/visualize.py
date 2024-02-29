#!/usr/bin/env python3

import networkx as nx
import matplotlib.pyplot as plt
import fetch
import numpy

debug = False


def draw(dag):
    args = {
        'with_labels': True,
        'arrows': True,
        'node_size': 300,
        'font_size': 8,
        'arrowsize': 16
    }
    nx.draw_planar(dag, **args)

    plt.show()
    print("Finished drawing dag")


def create_dag(job_dict):

    dag = nx.DiGraph()

    for job in job_dict:
        for next_job in reversed(job_dict):
            if job != next_job:
                job_name = job.split('T0000')[0]
                next_job_name = next_job.split('T0000')[0]
                io_data = job_dict.get(job)
                next_io_data = job_dict.get(next_job)
                if debug:
                    print(f'[DEBUG] Job name : {job_name}')
                dag.add_node(job_name)
                if debug:
                    print(f'[DEBUG] added {job_name} as a node')

                for filename, file_info in io_data['output_files'].items():
                    checksum, filepath = file_info
                    if debug:
                        print(f'[DEBUG] filename : {filename}')
                        print(f'[DEBUG] checksum : {str(checksum)}')
                        print(f'[DEBUG] filepath : {filepath}')
                    for next_filename, next_file_info in next_io_data['input_files'].items():
                        next_checksum, next_filepath = next_file_info
                        if filename == next_filename and checksum == next_checksum:
                            dag.add_edge(job_name, next_job_name)
                            if debug:
                                print(f'[DEBUG] Added an edge between {job_name} and {next_job_name}')

    print("Finished creating dag")
    return dag


def main():

    job_dict = fetch.main()

    dag = create_dag(job_dict)

    draw(dag)


if __name__ == "__main__":
    main()

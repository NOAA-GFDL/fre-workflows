#!/usr/bin/env python3

import networkx as nx
import matplotlib.pyplot as plt
import fetch

debug = False


def draw(dag):
    args = {
        'with_labels': True,
        'arrows': True,
        'node_size': 600,
        'font_size': 8
    }
    nx.draw(dag, **args)
    plt.show()
    print("Finished drawing dag")


def create_dag(job_dict):

    dag = nx.DiGraph()

    for job in job_dict:
        job_name = job
        io_data = job_dict.get(job)
        if debug:
            print(f'[DEBUG] Job name : {job_name}')
        dag.add_node(job_name)
        if debug:
            print(f'[DEBUG] added {job_name} node')
        for io_type, file_data in io_data.items():
            if debug:
                print(f'[DEBUG] I/O type {io_type}')

            for filename, file_info in file_data.items():
                checksum, filepath = file_info
                if debug:
                    print(f'[DEBUG] filename : {filename}')
                    print(f'[DEBUG] checksum : {str(checksum)}')
                    print(f'[DEBUG] filepath : {filepath}')

    print("Finished creating dag")
    return dag


def main():

    job_dict = fetch.main()

    dag = create_dag(job_dict)

    draw(dag)


if __name__ == "__main__":
    main()

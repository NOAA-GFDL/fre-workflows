#!/usr/bin/env python3

import networkx as nx
import fetch

# TODO: import pylint requires pip
# TODO: import joblib for Fetch.py

debug = False


def add_nodes(dag, job_dict):
    for job in job_dict:
        for next_job in reversed(job_dict):
            if job != next_job:
                job_name = job.split('T0000')[0]
                if debug:
                    print(f'[DEBUG] Job name : {job_name}')
                # dag.add_node(job_name)
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


def main():
    job_dict = fetch.main()
    dag, edge_dict = create_dag(job_dict)


if __name__ == "__main__":
    main()

import fetch
import hashlib
from blockdag import build_block_dag, pretty_prints

# pip install /nbhome/epmt/epmt-4.10.0.tar.gz
# pip install blockdag
# pip install networkx

debug = False
# TODO: import networkx, pip install to coles_py2


def _hashfunc(value):
    return hashlib.sha256(value).hexdigest()


def add_edges(job_dict):
    edge_dict = {}
    edge_list = []

    for job in job_dict:
        for next_job in reversed(job_dict):
            if job != next_job:
                # job_name = job.split('T0000')[0]
                # next_job_name = next_job.split('T0000')[0]
                io_data = job_dict.get(job)
                next_io_data = job_dict.get(next_job)

                for filename, file_info in io_data['output_files'].items():
                    checksum, filepath = file_info
                    for next_filename, next_file_info in next_io_data['input_files'].items():
                        next_checksum, next_filepath = next_file_info
                        if filename == next_filename and checksum == next_checksum:
                            edge_link = (job, next_job)
                            if edge_link in edge_list:
                                continue
                            else:
                                edge_list.append(edge_link)
                            # Saves file contents in edge_dict. [(job, next_job)] is the
                            # key and the values are each file that is output from
                            # 'job' and input in 'next_job'
                            # if edge_link in edge_dict:
                            #     edge_dict[edge_link].append(filename)
                            # else:
                            #     edge_dict[edge_link] = [filename]
    return edge_list


def main():
    vertices = fetch.main()
    edges = add_edges(vertices)
    print('\n----Initialized vertices and edges----')
    print(f'Total vertices:   {len(vertices)}\nTotal edges:      {len(edges)}')

    if debug:
        for vertex in vertices:
            print(vertex)
        for edge in edges:
            print(edge)

    print('\n----Building BlockDAG----')
    dag = build_block_dag(vertices, edges, _hashfunc, ['input_files', 'output_files'])
    print('Build finished, now printing dag')
    print(pretty_prints(vertices, edges, dag))


if __name__ == "__main__":
    main()

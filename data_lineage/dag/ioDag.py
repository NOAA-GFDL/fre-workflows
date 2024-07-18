from data_lineage.dag.Dag import DAG

def create_nodes(jobs):
    nodes = []
    for job_name, job_info in jobs.items():
        job_name = job_name.split('0101')[0].split('.')
        formatted_name = f"{job_name[1]}_{job_name[0]}"
        input_files = job_info['input']
        output_files = job_info['output']
        nodes.append((formatted_name, input_files, output_files))
    return nodes

def create_edges(dag, nodes):
    edge_count = 0
    for node in dag.get_nodes():
        name = node.get_name()
        output = node.get_output()
        for next_node in reversed(dag.get_nodes()):
            next_name = next_node.get_name()
            next_input = next_node.get_input()
            if name == next_name:
                continue
            for output_file, output_file_hash in output.items():
                for input_file, input_file_hash in next_input.items():
                    if output_file == input_file and output_file_hash == input_file_hash:
                        existing_edge = dag.find_edge(node, next_node)
                        if existing_edge:
                            if output_file not in existing_edge.get_contents():
                                existing_edge.add_content(output_file)
                        else:
                            dag.create_edge(node, next_node, output_file)
                            edge_count += 1
                    if output_file == input_file and output_file_hash != input_file_hash:
                        dag.decrement_fidelity()
    return edge_count

def main(jobs, run_dir):

    print('----Constructing DAG----')
    dag = DAG()
    dag.set_run_dir(run_dir)

    print('Adding nodes...')
    nodes = create_nodes(jobs)
    for node_data in nodes:
        dag.create_node(*node_data)
    print(f'Created {len(nodes)} nodes')

    print('Adding edges...')
    edge_count = create_edges(dag, nodes)
    print(f'Created {edge_count} edges')

    dag.dag_print()

    return dag

from data_lineage.dag.Dag import DAG
from data_lineage.dag.Node import Node
from data_lineage.dag.Edge import Edge


def process_graph(data):

    dag = DAG()

    for chunk in data['graph']:
        prefixes = handle_chunk(chunk, data)

        if not prefixes:
            continue

        for step in data['graph'][chunk]:
            previous_jobs = None

            jobs = step.split(' => ')

            for job in jobs:

                current_jobs = job.split(' & ')

                for current_job in current_jobs:

                    if ':succeed-all' in job:
                        job_name = job.split(':')[0].lower()
                        exact_jobs = find_all_nodes_by_name(job_name, dag)
                    else:
                        job_name, job_param = parse_job(current_job)
                        exact_jobs = generate_exact_jobs(job_name, job_param, data, prefixes)

                    for exact_job in exact_jobs:

                        if not dag.find_node(exact_job):
                            dag.add_node(job_name=exact_job)

                        if previous_jobs:

                            for previous_exact_job in previous_jobs:
                                dag.add_edge(dag.find_node((previous_exact_job)), dag.find_node(exact_job))

                previous_jobs = exact_jobs

    dag.dag_print()

    return dag


def handle_chunk(chunk, data):
    prefixes = []
    start = data['start']
    end = data['end']
    duration = end - start + 1

    if chunk == 'R1':
        prefixes = [str(start)]

    elif chunk == 'P1Y':
        for i in range(duration):
            prefixes.append(str(start + i))

    elif 'P2Y' in chunk:
        if duration < 2:
            return None
        for i in range(int(duration / 2)):
            prefixes.append(str(start + i + 1))

    elif 'P4Y' in chunk:
        if duration < 4:
            return None
        for i in range(int(duration / 4)):
            prefixes.append(str(start + i + 3))

    return prefixes


def parse_job(job):
    # Ignore parameters indicated by a '<' character, remove any & signs from multi-line jobs
    # in the config, strip any leading/trailing whitespace, and then convert to lowercase
    job_name = job.split('<')[0].replace('&', '').strip().lower()
    job_name = job_name.replace('p2y', 'P2Y').replace('p4y', 'P4Y')
    job_param = None

    if ':' in job_name:
        job_name = job_name.split(':')[0]

    if '<' in job and '>' in job:
        job_param = job.split('<')[1].split('>')[0]

    return job_name, job_param


def generate_exact_jobs(job_name, job_param, data, prefixes):
    exact_jobs = []

    if job_param:
        exact_jobs = [prefix + '_' + job_name + '_' + param for prefix in prefixes
                      for param in data['task_parameters'][job_param]]
    else:
        exact_jobs = [prefix + '_' + job_name for prefix in prefixes]

    return exact_jobs


def generate_previous_exact_jobs(previous_jobs, data, prefixes):
    previous_exact_jobs = []

    for job in previous_jobs:
        job_name, job_param = parse_job(job)
        previous_exact_jobs = generate_exact_jobs(job_name, job_param, data, prefixes)

    return previous_exact_jobs


def find_all_nodes_by_name(job_name, dag):
    nodes = []

    for node in dag.get_nodes():
        if job_name in node.get_name():
            nodes.append(node.get_name())

    return nodes

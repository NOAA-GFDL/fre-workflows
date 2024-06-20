from data_lineage.dag.Dag import DAG
from data_lineage.dag.Node import Node
from data_lineage.dag.Edge import Edge


def process_graph(config_data):
    """
    Constructs the configuration DAG from data that was scraped from a
    cylc-run's configuration file, which is found at
    cylc-run/exp/runN/log/config/01-start-01.cylc.

    1. Iterate through the different chunks. Eg: P1Y, P2Y ...
    2. Iterate through the step in the chunk, and deconstruct each sequence
       of jobs in the step.
    3. Within this deconstructed sequence, add each exact job to the dag
       as nodes, and use the order of the sequence to add the edges
       between the nodes.

    Args:
        config_data: Dict
            The parsed data from the 01-start-01.cylc configuration file.

    Returns:
        dag: Dag
            A Dag object of the configuration DAG. Uses the Dag class created
            in data_lineage/dag/Dag.py. Does not contain any i/o files or hashes.
    """
    dag = DAG()

    for chunk in config_data['graph']:
        prefixes = handle_chunk(chunk, config_data)

        if not prefixes:
            continue

        for step in config_data['graph'][chunk]:
            previous_jobs = []

            jobs = step.split(' => ')

            for job in jobs:
                current_jobs = job.split(' & ')
                current_exact_jobs = []
                temporary_prefixes = []

                for current_job in current_jobs:
                    # If a job contains the [-P1Y] tag, it is in the 'R1' chunk and is referring to the 'P1Y' version
                    if '[-P1Y]' in current_job:
                        duration = int(config_data['end']) - int(config_data['start'])

                        for i in range(duration + 1):
                            temporary_prefixes.append(str(int(config_data['start']) + i))

                    # All versions must be completed with a successful return
                    if ':succeed-all' in job:
                        job_name = job.split(':')[0].lower()
                        exact_jobs = find_all_nodes_by_name(job_name, dag)
                    else:
                        job_name, job_param = parse_job(current_job)
                        exact_jobs = generate_exact_jobs(job_name, job_param, config_data, temporary_prefixes if temporary_prefixes else prefixes)

                    for exact_job in exact_jobs:
                        current_exact_jobs.append(exact_job)

                        if not dag.find_node(exact_job):
                            dag.create_node(job_name=exact_job)

                        if previous_jobs:
                            for previous_exact_job in previous_jobs:
                                dag.create_edge(dag.find_node((previous_exact_job)), dag.find_node(exact_job))

                previous_jobs = current_exact_jobs

    return dag


def handle_chunk(chunk, config_data):
    """
    Generates the prefixes for jobs in a given chunk. Prefixes are the frequency
    of a job in a workflow.

    If a workflow's duration is 2000 to 2004, and the chunk was 'P2Y', the prefixes
    would be [2000, 2002, 2004].

    Args:
        chunk: String
            Frequency of job occurances.
        config_data: Dict
            The parsed data from the 01-start-01.cylc configuration file.

    """
    prefixes = []
    start = config_data['start']
    end = config_data['end']
    duration = end - start + 1

    # Needs to be tweaked, the prerequisite tasks can be any year, but the result tasks
    # are only run one time throughtout the entire workflow.
    if chunk == 'R1':
        for i in range(duration):
            prefixes.append(str(start + i))

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
    """
    Deconstructs a job into two separate fields.

    Args:
        job: String
            Singular job from config_data

    Returns:
        job_name: String
            The generic name of the job as seen in the `app/` directory
            or the 'site/ppan.cylc' file
        job_param: String
            The task parameter the job is using.
    """
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


def generate_exact_jobs(job_name, job_param, config_data, prefixes):
    """
    Create a list of exact jobs with years and corresponding task parameters.
    Uses the same format that was used when creating nodes for the serial DAG.

    Iterate over the years the job is run or the different parameters the job
    uses, and create a list of these.

    Format should be: YYYY_jobname_taskparameter

    Args:
        job_name: String
            The generic job name as seen in the `app/` directory or `site/ppan.cylc`
        job_param: String
            The specific group of task parameters the job uses
        config_data: Dict
            The parsed data from the 01-start-01.cylc configuration file.
        prefixes: List
            List of different years this job was run for

    Returns:
        exact_jobs: List
            List of jobs with specific years and task parameters added to it
    """
    exact_jobs = []

    if job_param:
        exact_jobs = [prefix + '_' + job_name + '_' + param for prefix in prefixes
                      for param in config_data['task_parameters'][job_param]]
    else:
        exact_jobs = [prefix + '_' + job_name for prefix in prefixes]

    return exact_jobs


def find_all_nodes_by_name(job_name, dag):
    """
    Searches for all nodes in a dag that share a generic job_name.

    Args:
        job_name: String
            The generic job name as seen in the `app/` directory or `site/ppan.cylc`

    Returns:
        dag: Dag
            The configuration file DAG
    """
    nodes = []

    for node in dag.get_nodes():
        if job_name in node.get_name():
            nodes.append(node.get_name())

    return nodes

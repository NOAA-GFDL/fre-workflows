TASK_PARAMETERS_SECTION = '[task parameters]'
TIME_START = 'initial cycle point'
TIME_END = 'final cycle point'
GRAPH_SECTION = '[[graph]]'
CHUNK_START_MARKER = ' = """'
CHUNK_END_MARKER = '\"\"\"'


def parse_task_parameters(config_data, line):
    """
    Given a line that is from the configuration file's [task parameters]
    section, parse the list in it and add the parameters to config_data.

    Args:
        config_data: Dict
            See the example in read_from_file()'s docstrings
        line: String
            Line from the cylc-run's configuration file that contains the
            parsable task parameters

    Returns:
        config_data: Dict
            Updated with the new task parameters
    """
    if '[' not in line:
        task, parameters = line.split('=')
        task = task.strip()
        parameters = parameters.strip()

        config_data['task_parameters'][task] = []
        parameters_array = parameters.split(', ')

        for item in parameters_array:
            config_data['task_parameters'][task].append(item)

    return config_data


def parse_graph(config_data, line, chunk):
    """
    Given a line that is from the configuration file's [[graph]]
    section, parse the list in it and add the jobs to config_data.

    If a line has `=>` in it, the job to the left of the arrow needs to
    return as a success before the job to the right can be started.

    If a line has `&` in it, treat it as a boolean `AND`. The left AND
    right jobs need to be finished before continuing with the following job.

    Args:
        config_data: Dict
            See the example in read_from_file()'s docstrings
        line: String
            Line from the cylc-run's configuration file that contains the
            order which jobs can be started.
        chunk: String
            The frequency a job is run.
                'P1Y' - once for every year
                'P2Y' - once for every other year
                'R1' - once at the start

    Returns:
        config_data: Dict
            Updated with the sequence which jobs are started
    """
    if '=' in line:

        if CHUNK_START_MARKER in line:
            chunk = line.split(' =')[0]
            config_data['graph'][chunk] = []
            return config_data, chunk

        else:
            config_data['graph'][chunk].append(line)

    return config_data, chunk


def read_from_file(run_dir):
    """
    Given a cylc-run path, locate the workflow configuration file and parse it to gather
    the data necessary for building a configuration DAG. Line by line, create the task
    parameters and dependencies.

    Args:
        run_dir: String
            The path of a specific cylc-run. An example
            would be /home/user/cylc-run/exp/runN

    Returns:
        config_data: Dict
            The parsed data from a cylc-run's configuration file.

            config_data = {
                "task_parameters": {
                    "regrid": [param1, ..., ...]
                    "native": [...]
                    ...
                },
                "graph": {
                    "P1Y": [app1 => app2, app1 => app3, ...]
                    "P2Y": [...]
                    ...
                },
                "start": 2020
                "end": 2024
            }

    """
    cylc_file = run_dir + '/log/config/01-start-01.cylc'

    chunk = None
    prev_line = None
    current_section = None
    config_data = {'task_parameters': {}, 'graph': {}}

    with open(cylc_file, 'r') as f:

        for line in f:
            line = line.strip()

            # Skip any commented lines
            if line.startswith('#'):
                continue

            if TIME_START in line:
                config_data['start'] = int(line.split(' = ')[1])

            elif TIME_END in line:
                config_data['end'] = int(line.split(' = ')[1])

            elif line == TASK_PARAMETERS_SECTION:
                current_section = 'task_parameters'

            elif line == GRAPH_SECTION:
                current_section = 'graph'

            elif '[' in line and current_section and not chunk:
                current_section = None

            elif current_section == 'task_parameters':
                config_data = parse_task_parameters(config_data, line)

            elif current_section == 'graph':
                if line == CHUNK_END_MARKER:
                    chunk = None
                    continue

                if line.startswith('&') or line.startswith('=>'):
                    line = prev_line + ' ' +  line

                # Odd bug where some lines would be skipped if they occurred after a chained line
                # that observes next(f)
                if prev_line:
                    if '=>' in prev_line:
                        config_data, chunk = parse_graph(config_data, prev_line, chunk)
                        prev_line = None

                # If several lines are involved in one direction
                if '=>' not in line and CHUNK_START_MARKER not in line:
                    next_line = next(f, None).strip()
                    while next_line.startswith('&') or next_line.startswith('=>'):
                        line = line + ' ' + next_line
                        next_line = next(f, None).strip()
                    prev_line = next_line

                config_data, chunk = parse_graph(config_data, line, chunk)

    return config_data

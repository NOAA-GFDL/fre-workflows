TASK_PARAMETERS_SECTION = '[task parameters]'
TIME_START = 'initial cycle point'
TIME_END = 'final cycle point'
GRAPH_SECTION = '[[graph]]'
CHUNK_START_MARKER = ' = """'
CHUNK_END_MARKER = '\"\"\"'


def parse_task_parameters(data, line):

    if '[' not in line:
        task, parameters = line.split('=')
        task = task.strip()
        parameters = parameters.strip()

        data['task_parameters'][task] = []
        parameters_array = parameters.split(', ')

        for item in parameters_array:
            data['task_parameters'][task].append(item)

    return data


def parse_graph(data, line, chunk):

    if '=' in line:

        if CHUNK_START_MARKER in line:
            chunk = line.split(' =')[0]
            data['graph'][chunk] = []
            return data, chunk

        else:
            data['graph'][chunk].append(line)

    return data, chunk


def read_from_file(run_dir):
    cylc_file = run_dir + '/log/config/01-start-01.cylc'

    parsing_task_parameters = False
    parsing_graph = False
    chunk = None
    data = {}

    with open(cylc_file, 'r') as f:

        for line in f:
            line = line.strip()

            if line.startswith('#'):
                continue

            if TIME_START in line:
                data['start'] = int(line.split(' = ')[1])

            elif TIME_END in line:
                data['end'] = int(line.split(' = ')[1])

            elif line == TASK_PARAMETERS_SECTION:
                parsing_task_parameters = True
                data.setdefault('task_parameters', {})

            elif line == GRAPH_SECTION:
                parsing_graph = True
                data.setdefault('graph', {})

            elif '[' in line and (parsing_task_parameters or parsing_graph) and not chunk:
                parsing_task_parameters = False
                parsing_graph = False

            elif parsing_task_parameters:
                data = parse_task_parameters(data, line)

            elif parsing_graph:
                if line == CHUNK_END_MARKER:
                    chunk = None
                    continue

                # If several lines are involved in one direction
                if '=>' not in line and CHUNK_START_MARKER not in line:
                    next_line = next(f, None).strip()
                    while next_line.startswith('&') or next_line.startswith('=>'):
                        line = line + ' ' + next_line
                        next_line = next(f, None).strip()

                data, chunk = parse_graph(data, line, chunk)

    return data

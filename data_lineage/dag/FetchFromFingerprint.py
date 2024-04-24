import sys
from epmt import epmt_query as eq
from data_lineage.bloomfilter import StringCompression as sc


def get_job_data(job):
    """
    Given a job from epmt's get_jobs query, return the input and output files that were annotated to it.

    Args:
        job: Dictionary
            EPMT's dictionary for a job

    Returns:
        input_files, output_files: Dictionary
            Key: File with absolute path
            Value: File's hash (make sure to include the absolute path in the Key to ensure the hash is unique. Otherwise, there
                                is a possibility two files with the same name but different locations have colliding hashes).
    """
    annotations = job['annotations']
    input_files = {}
    output_files = {}

    job_input = annotations.get('EPMT_DATA_LINEAGE_IN', '')
    job_output = annotations.get('EPMT_DATA_LINEAGE_OUT', '')

    def parse_io_files(annotation, path):
        """
        All input/output files and their hashes are stored in a string and need to be parsed.
        Example: "'input_file1'  'random_hash1','input_file2'  'random_hash2','input_file3'  'random_hash3'"
        """
        files = {}
        for file in annotation.split(','):
            # Signals the end of the list of files
            if not file:
                return files

            # A singular whitespace is the current delimiter that separates a file name and file hash
            file_name, file_hash = file.strip().split(' ')
            file_name = path + file_name  # Append the absolute path to the beginning of the file_name
            files[file_name] = file_hash
        return files

    def process_job_data(io):
        """
        If there is data in `io`
            1. Fill in padding
            2. Convert from string to bytes
            3. Decompress the gizp-compressed data
            4. Grab absolute path
            5. Parse the decompressed data and append the path to the front
        """
        if io:
            # Base64 encodes '=' as padding at the end since it uses 24-bit sequences
            b64_data = io.replace('_pad', '=')

            # https://stackoverflow.com/questions/38763771/how-do-i-remove-double-back-slash-from-a-bytes-object
            compressed_data = b64_data.encode().decode('unicode_escape').encode("raw_unicode_escape")
            decompressed_data = sc.decompress_bytes(compressed_data)

            path_key = 'EPMT_DATA_LINEAGE_IN_PATH' if io == job_input else 'EPMT_DATA_LINEAGE_OUT_PATH'
            path = annotations.get(path_key, '')

            files = parse_io_files(decompressed_data, path)
            return files
        return []

    # TODO add a test in future
    input_files = process_job_data(job_input)
    output_files = process_job_data(job_output)

    return input_files, output_files


def format_jobs(jobs):
    """
    Create our own dictionary object that contains only the data we need from the EPMT query.

    Args:
        jobs: List
            List of job dictionaries that were returned from the EPMT query

    Returns:
        formatted_jobs : Dictionary

            fmt_jobs = {
                "job1":{
                    "input":{
                        "input_file1" : "input_file1_hash"
                    },
                    "output":{
                        "output_file1" : "output_file1_hash"
                    }
                },
                "job2":{
                    "input":{
                        ...
                    },
                    "output":{
                        ...
                    }
                },
                ...
            }

    """
    formatted_jobs = {}

    for job in jobs:

        name = job['jobname']
        annotations = job['annotations']

        # Skip job if there is no i/o files
        # TODO: should these nodes be skipped? or added for completeness?
        if 'EPMT_DATA_LINEAGE_IN' not in annotations \
                and 'EPMT_DATA_LINEAGE_OUT' not in annotations:
            continue

        # Get i/o data from job and store it in i/o dictionaries
        i, o = get_job_data(job)

        # Initialize i/o dictionaries inside job
        if name not in formatted_jobs:
            formatted_jobs[name] = {'input': {}, 'output': {}, 'input_path': '', 'output_path': ''}

        formatted_jobs[name]['input'] = i
        formatted_jobs[name]['output'] = o

    return formatted_jobs


def fetch_jobs(fingerprint):

    jobs = eq.get_jobs(
        fmt='dict',
        tags=f'EPMT_EXP_UUID:{fingerprint}',
    )

    return jobs


def main(fingerprint):
    """
    1. Given a fingerprint, retrieve all jobs that contain the fingerprint in EPMT_TAGS.
    2. Currently, filter out the jobs that do not interact with input OR output files.
    3. Format the remaining jobs into a dict
    """
    job_dict = fetch_jobs(fingerprint)

    formatted_jobs = format_jobs(job_dict)

    # saving run_dir to check if jobs are omitted in Dag.py
    run_dir = job_dict[00]['env_dict']['CYLC_WORKFLOW_RUN_DIR']

    return formatted_jobs, run_dir


if __name__ == "__main__":

    if len(sys.argv) == 1:

        # Fingerprint for testing : 23506d7c-df02-4810-83cf-33a5a213a261
        # Date                    : 2024-03-27 11:00 AM
        # Run Num                 : /run40
        print('--- Testing Mode ---')
        fp = '23506d7c-df02-4810-83cf-33a5a213a261'

    elif len(sys.argv) == 2:

        fp = sys.argv[1]

    else:

        print(f'Non test usage: python FetchFromFingerprint.py <fingerprint>\n'
              f'Testing usage : python FetchFromFingerprint.py')
        sys.exit(1)

    print(f'Fingerprint = {fp}')
    main(fingerprint=fp)

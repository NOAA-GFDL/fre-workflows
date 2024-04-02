import sys
from epmt import epmt_query as eq


def get_job_data(job):
    """
    Given an entry from epmt's get_jobs query, return the input and output files.
    The i/o files contain the absolute file path and the hash.
    """
    annotations = job['annotations']
    input_files = {}
    output_files = {}
    input_path = ''
    output_path = ''

    print(f"     {job['jobname']}")

    job_input = annotations.get('EPMT_DATA_LINEAGE_IN', '')
    job_output = annotations.get('EPMT_DATA_LINEAGE_OUT', '')

    def parse_files(annotation, path):
        """
        All input/output files and their hashes are stored in a string and need to be parsed.
        Example: "'input_file1'  'random_hash1','input_file2'  'random_hash2','input_file3'  'random_hash3'"
        """
        files = {}
        for file in annotation.split(','):
            file_name, file_hash = file.strip().split('  ')
            file_name = path + file_name  # Append the absolute path to the beginning of the file_name
            files[file_name] = file_hash
        return files

    if job_input:
        input_path = annotations.get('EPMT_DATA_LINEAGE_IN_PATH', '')
        input_files = parse_files(job_input, input_path)

    if job_output:
        output_path = annotations.get('EPMT_DATA_LINEAGE_OUT_PATH', '')
        output_files = parse_files(job_output, output_path)

    return input_files, output_files


def format_jobs(jobs):
    fmt_jobs = {}

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
        if name not in fmt_jobs:
            fmt_jobs[name] = {'input': {}, 'output': {}, 'input_path': '', 'output_path': ''}

        fmt_jobs[name]['input'] = i
        fmt_jobs[name]['output'] = o

    return fmt_jobs


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
    3. Format the remaining jobs into a dict with the following structure
            jobs = {
                "job1":{
                    "input":{
                        "input_file1" : "input_file1_hash"
                    },
                    "output":{
                        "output_file1" : "output_file1_hash"
                    }
                },
                "jon2":{
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
    job_dict = fetch_jobs(fingerprint)

    formatted_jobs = format_jobs(job_dict)

    return formatted_jobs


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

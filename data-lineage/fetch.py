#!/usr/env/bin python3

from epmt import epmt_query as eq
print('EPMT successfully loaded')

debug = False


def filter_jobs(jobs):

    jobs_filtered = 0
    idx = 0
    jobs_to_be_removed = []

    for job in jobs:
        if 'EPMT_DATA_LINEAGE_IN' not in job['annotations'] \
                or 'EPMT_DATA_LINEAGE_OUT' not in job['annotations'] \
                or '/run49' not in job['jobname']:
            if debug:
                print(f'[DEBUG] deleting {job["jobname"]}')
                print_job(job)
            jobs_to_be_removed.append(idx)
        idx += 1
    for i in reversed(jobs_to_be_removed):
        jobs.pop(i)
        jobs_filtered += 1
    print(f'Total jobs removed : {jobs_filtered}')
    return jobs


def grab_data(job):

    job_name = job['jobname']
    input_files = ''
    output_files = ''

    if 'EPMT_DATA_LINEAGE_IN' in job['annotations']:
        input_files = job['annotations']['EPMT_DATA_LINEAGE_IN']
    if 'EPMT_DATA_LINEAGE_OUT' in job['annotations']:
        output_files = job['annotations']['EPMT_DATA_LINEAGE_OUT']
    if debug:
        print(f'[DEBUG] analyzing {job["jobname"]}')
        print_job(job)

    return job_name, input_files, output_files


def format_io_file_annotations(files):
    """
    Creates a new data struct for the epmt annotations and makes them easier
    to iterate over. Passed into
    """
    file_pairs = files.split(',')
    file_data = {}

    for pair in file_pairs:
        data = pair.split('  ')
        checksum, file_path = data[0], data[1]
        file_name = file_path.split('/')[-1]
        file_data[file_name] = (checksum, file_path)

    return file_data


def print_job(job):

    job_name = job['jobname']
    input_files = job['annotations']['EPMT_DATA_LINEAGE_IN'] if 'EPMT_DATA_LINEAGE_IN' in job['annotations'] else ''
    output_files = job['annotations']['EPMT_DATA_LINEAGE_OUT'] if 'EPMT_DATA_LINEAGE_OUT' in job['annotations'] else ''
    print(f'[DEBUG] Job : {job}')
    print(f'[DEBUG] jobname : {job_name}')
    print(f'[DEBUG] input files : {input_files}')
    print(f'[DEBUG] output files : {output_files}')
    print('\n')


def main():

    limit = 450
    username = 'Cole.Harvey'
    experiment = 'exp_name:am5_c96L33_amip'
    start_date = -4
    job_dict = {}

    jobs_all = eq.get_jobs(limit=limit,
                           fmt='dict',
                           fltr=(eq.Job.user_id == username),
                           tags=experiment,
                           after=start_date)

    total_job_num = len(jobs_all)
    print(f'Found {total_job_num} jobs from {username} with the tag {experiment}')

    filtered_jobs = filter_jobs(jobs_all)
    print(f'Double check jobs removed : {total_job_num - len(filtered_jobs)}')
    print(f'Jobs remaining : {len(filtered_jobs)}')

    for job in filtered_jobs:
        job_name, input_files, output_files = grab_data(job)
        input_dict = format_io_file_annotations(input_files)
        output_dict = format_io_file_annotations(output_files)
        job_dict[job_name] = {'input_files': input_dict, 'output_files': output_dict}

    return job_dict


if __name__ == "__main__":
    main()

#!/usr/env/bin python3

from epmt import epmt_query as eq
print('[COLE] imported epmt successfully')
debug = False


def filter_jobs(jobs):
    jobs_filtered = 0
    idx = 0
    jobs_to_be_removed = []
    for job in jobs:
        if 'EPMT_DATA_LINEAGE_IN' not in job['annotations'] or 'EPMT_DATA_LINEAGE_OUT' not in job['annotations']:
            if debug:
                print(f'[DEBUG] deleting {job["jobname"]}')
            jobs_to_be_removed.append(idx)
            jobs_filtered += 1
            idx += 1
    for i in jobs_to_be_removed:
        jobs.pop(i)
    print(f'[COLE] Total jobs removed : {jobs_filtered}')
    return jobs


def grab_data(job):

    job_name = job['jobname']
    data_in = ''
    data_out = ''

    if 'EPMT_DATA_LINEAGE_IN' in job['annotations']:
        data_in = job['annotations']['EPMT_DATA_LINEAGE_IN']
    if 'EPMT_DATA_LINEAGE_OUT' in job['annotations']:
        data_out = job['annotations']['EPMT_DATA_LINEAGE_OUT']

    if debug:
        print(f'[DEBUG] Job : {job}')
        print(f'[DEBUG] jobname : {job_name}')
        print(f'[DEBUG] input files : {data_in}')
        print(f'[DEBUG] output files : {data_out}')
        print('\n')


def main():
    limit = 200
    username = 'Cole.Harvey'
    experiment = 'exp_name:am5_c96L33_amip'
    start_date = -2

    jobs_all = eq.get_jobs(limit=limit, fmt='dict', fltr=(eq.Job.user_id == username), tags=experiment, after=start_date)
    print(f'[COLE] Found {len(jobs_all)} jobs from {username} and the tag {experiment}')

    filtered_jobs = filter_jobs(jobs_all)
    print(f'[COLE] Double check jobs removed : {limit - len(filtered_jobs)}')

    for job in filtered_jobs:
        grab_data(job)


if __name__ == "__main__":
    main()

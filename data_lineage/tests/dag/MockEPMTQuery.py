from data_lineage.bloomfilter.StringCompression import compress_string

def mock_job_names():
    return ['PP-STARTER',
            'STAGE-HISTORY',
            'rename-split-to-pp',
            'make-timeavgs_1',
            'make-timeavgs_2',
            'combine-timeavgs',
            'read-archive-files']


def mock_input():
    return {
        'rename-split-to-pp': 'history-file1.nc hash1,history-file2.nc hash2,history-file3.nc hash3',
        'make-timeavgs_1': 'rename-file1.nc hash4,rename-file2.nc hash5',
        'make-timeavgs_2': 'rename-file3.nc hash6',
        'combine-timeavgs': 'timeavg-file1.nc hash7,timeavg-file2.nc hash8,timeavg-file3.nc hash9',
        'read-archive-files': 'archive-file.nc hash14'
    }


def mock_output():
    return {
        'STAGE-HISTORY': 'history-file1.nc hash11,history-file2.nc hash12,history-file3.nc hash13',
        'rename-split-to-pp': 'rename-file1.nc hash4,rename-file2.nc hash5,rename-file3.nc hash6',
        'make-timeavgs_1': 'timeavg-file1.nc hash7,timeavg-file2.nc hash8',
        'make-timeavgs_2': 'timeavg-file3.nc hash9',
        'combine-timeavgs': 'archive-file.nc hash14'
    }


def mock_call():
    """
    Sets up an example that mocks the return value of an EPMT Query.
    """
    rv = []
    MOCK_JOB_NAMES = mock_job_names()
    MOCK_INPUT = mock_input()
    MOCK_OUTPUT = mock_output()

    for job in MOCK_JOB_NAMES:
        job_data = {'jobname': job, 'annotations': {}}
        if job in MOCK_INPUT:
            job_data['annotations']['EPMT_DATA_LINEAGE_IN'] = compress_string(MOCK_INPUT[job])
        if job in MOCK_OUTPUT:
            job_data['annotations']['EPMT_DATA_LINEAGE_OUT'] = compress_string(MOCK_OUTPUT[job])
        rv.append(job_data)
    return rv


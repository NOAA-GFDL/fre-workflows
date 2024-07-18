import pytest
from data_lineage.tests.dag.MockEPMTQuery import mock_call, mock_job_names, mock_input, mock_output
from data_lineage.bloomfilter.StringCompression import decompress_bytes
from data_lineage.dag.FetchData import get_job_data, format_jobs

MOCK_JOB_NAMES = mock_job_names()
MOCK_INPUT = mock_input()
MOCK_OUTPUT = mock_output()

@pytest.fixture
def mock_epmt_call():
    return mock_call()

@pytest.mark.parametrize('job_name', MOCK_JOB_NAMES)
def test_get_job_data(mock_epmt_call, job_name):
    """
    Tests multiple different cases for the function get_job_data().

    PP-STARTER contians no input/output files
    STAGE-HISTORY contains output files but no input files
    read-archive-files contains input files but no output files

    The rest of the tasks contain both input files and output files and ensures the
    files were processed correctly by get_job_data.
    """
    job_data = next(job for job in mock_epmt_call if job['jobname'] == job_name)
    annotations = job_data['annotations']
    input_data, output_data = get_job_data(job_data)

    assert job_data['jobname'] == job_name

    if job_name == 'PP-STARTER':
        # Assert PP-STARTER does not contain EPMT_DATA_LINEAGE_IN/OUT
        assert 'EPMT_DATA_LINEAGE_IN' not in annotations
        assert 'EPMT_DATA_LINEAGE_OUT' not in annotations
        return

    if job_name in MOCK_INPUT:
        assert 'EPMT_DATA_LINEAGE_IN' in annotations
        mock_input_files_array = decompress_bytes(annotations['EPMT_DATA_LINEAGE_IN']).split(',')
        for mock_file in mock_input_files_array:
            file_name, hash = mock_file.split(' ')
            assert file_name in input_data
            assert input_data[file_name] == hash

    if job_name in MOCK_OUTPUT:
        assert 'EPMT_DATA_LINEAGE_OUT' in annotations
        mock_output_files_array = decompress_bytes(annotations['EPMT_DATA_LINEAGE_OUT']).split(',')
        for mock_file in mock_output_files_array:
            file_name, hash = mock_file.split(' ')
            assert file_name in output_data
            assert output_data[file_name] == hash

def test_format_jobs_no_io_edge_cases(mock_epmt_call):
    """
    Checks if tasks without input/output annotations appear in formatted_jobs.

    PP-STARTER should not appear since it has no i/o annotations
    STAGE-HISTORY & read-archive-files should appear since they have one type of i/o annotations
    """
    formatted_jobs = format_jobs(mock_epmt_call)
    assert 'PP-STARTER' not in formatted_jobs
    assert 'STAGE-HISTORY' in formatted_jobs
    assert 'read-archive-files' in formatted_jobs

@pytest.mark.parametrize('job_name', MOCK_JOB_NAMES)
def test_format_jobs(mock_epmt_call, job_name):
    if job_name == 'PP-STARTER':
        return

    job_data = next(job for job in mock_epmt_call if job['jobname'] == job_name)
    annotations = job_data['annotations']
    formatted_jobs = format_jobs(mock_epmt_call)

    assert job_name in formatted_jobs

    job_data = formatted_jobs[job_name]
    input = job_data['input'] or ''
    output = job_data['output'] or ''

    if input:
        mock_input_files_array = decompress_bytes(annotations['EPMT_DATA_LINEAGE_IN']).split(',')
        for mock_file in mock_input_files_array:
            file_name, hash = mock_file.split(' ')
            assert file_name in input
            assert input[file_name] == hash

    if output:
        mock_output_files_array = decompress_bytes(annotations['EPMT_DATA_LINEAGE_OUT']).split(',')
        for mock_file in mock_output_files_array:
            file_name, hash = mock_file.split(' ')
            assert file_name in output
            assert output[file_name] == hash

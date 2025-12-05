'''
tests for PPAN specific job_runner_handler class.

test from the root directory with:
    pytest -v -v -rx ./lib/python/tests/test_PPANHandler.py
'''
import filecmp
from pathlib import Path

from lib.python.ppan_handler import PPANHandler

JOB_FILE_PATH='lib/python/tests/test_files_papiex_tooler/am5_c96L33_amip_mask-atmos-plevel_atmos_scalar_job'

def test_import():
    ''' check that ppan_handler can be imported.'''
    test_handler=PPANHandler()

    assert test_handler is not None
    assert test_handler.check_import() == 0


def test_tool_ops_import_in_handler():
    ''' check that ppan_handler can import tool_ops_w_papiex'''
    test_handler=PPANHandler()

    assert test_handler is not None
    assert test_handler.check_tool_ops_import() == 0

def test_submit():
    ''' check ppan_handler submit behavior with dry_run=True '''
    test_handler=PPANHandler()

    # fudge submit_opts input for dry_run == True
    submit_opts={'env':{}}
    ret_code, ret_out, ret_err = test_handler.submit(
                                   job_file_path = JOB_FILE_PATH,
                                   submit_opts = submit_opts,
                                   dry_run = True, tool_ops = True)

    print(ret_code)
    print(ret_out)
    print(ret_err)
    # check what the function returns
    assert all ( [ ret_code == 0,
                   ret_out  == "HELLO\n",
                   ret_err  == "" ] )

def test_file_cmp_and_clean():
    ''' since tool_ops_w_papiex.py is called, we should make sure the differences are introduced '''
    # check that the files we expect to exist do so after running
    assert Path(JOB_FILE_PATH+'.notags').exists()
    assert Path(JOB_FILE_PATH).exists()

    # check to make sure the two files are not the same
    assert not filecmp.cmp(JOB_FILE_PATH, JOB_FILE_PATH+'.notags')

def test_cleanup():
    ''' sep routine for clean up '''
    # clean up, and make sure we're back at our starting state
    Path(JOB_FILE_PATH).unlink()
    Path(JOB_FILE_PATH+'.notags').rename(JOB_FILE_PATH)
    assert not Path(JOB_FILE_PATH+'.notags').exists()
    assert Path(JOB_FILE_PATH).exists()

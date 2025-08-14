''' tests for PP/AN specific job_runner_handler class '''

def test_import(capfd):
    ''' check that ppan_handler can be imported.'''
    #print(f'__name__=={__name__}')
    from lib.python.ppan_handler import PPANHandler
    test_handler=PPANHandler()

    assert test_handler.test_import() == 0


def test_tool_ops_import_in_handler(capfd):
    ''' check that ppan_handler can import tool_ops_w_papiex'''
    #print(f'__name__=={__name__}')
    from lib.python.ppan_handler import PPANHandler
    test_handler=PPANHandler()

    assert test_handler.test_tool_ops_import() == 0

def test_submit(capfd):
    ''' check ppan_handler submit behavior with dry_run=True '''
    #print(f'__name__=={__name__}')
    from lib.python.ppan_handler import PPANHandler
    test_handler=PPANHandler()
    
    from pathlib import Path
    job_file_path='./tests/test_files_papiex_tooler/am5_c96L33_amip_mask-atmos-plevel_atmos_scalar_job'

    # check for existing test output, remove in order to recreate
    if Path(job_file_path+'.notags').exists():
        Path(job_file_path).unlink()
        Path(job_file_path+'.notags').rename(job_file_path)
        
    # fudge submit_opts input for dry_run == True    
    submit_opts={'env':{}}    
    ret_code, ret_out, ret_err = test_handler.submit(
                                   job_file_path = job_file_path,
                                   submit_opts = submit_opts,
                                   dry_run = True, tool_ops = True)
    assert all ( [ ret_code == 0,
                   ret_out  == "HELLO\n",
                   ret_err  == "",
                   Path(job_file_path+'.notags').exists(),
                   Path(job_file_path).exists() ] ) 



''' tests for PP/AN specific job_runner_handler class '''

import pytest

def test_import():
    ''' check that ppan_handler can be imported.'''
    from lib.python.ppan_handler import PPANHandler
    test_handler=PPANHandler()
    
    assert(test_handler.test_import() == 0)


def test_tool_ops_import_in_handler():
    ''' check that ppan_handler can import tool_ops_w_papiex'''
    from lib.python.ppan_handler import PPANHandler
    test_handler=PPANHandler()
    
    assert(test_handler.test_tool_ops_import() == 0)

#def test_submit():
#    ''' check ppan_handler submit behavior with dry_run=True '''
#    from lib.python.ppan_handler import PPANHandler
#    test_handler=PPANHandler()
#
#    job_file_path=''
#    submit_opts={'env':{}}
#    
#    ret_code, ret_out, ret_err = 
#                         test_handler.submit(
#                                   job_file_path=job_file_path,
#                                     submit_opts=submit_opts,
#                                         dry_run=True)
#    assert(all([ret_code == 0,
#                ret_out is not None,
#                ret_err is not None]))



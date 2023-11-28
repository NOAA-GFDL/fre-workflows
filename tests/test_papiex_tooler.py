''' tests for PP/AN specific ops-tooling of job scripts for PAPIEX'''
import pytest

def test_import():
    ''' check that tool_ops_w_papiex functions can be imported '''
    from  lib.python.tool_ops_w_papiex import test_import
    assert(test_import() == 0)

def test_import_papiex_ops():
    ''' check that op list data can be imported '''
    import lib.python.papiex_ops as po
    assert ( all( [ po.op_list is not None,
                       len(po.op_list) > 0  ] ) )

def test_simple_failing_command():
    ''' check that setting/unsetting PAPIEX_TAGS around an op
    will not touch the exit status of that op '''
    from pathlib import Path
    control_script_targ=str(Path.cwd())+'/tests/test_files_papiex_tooler/simple_failing_command.bash'
    assert Path(control_script_targ).exists() #quick check

    # import subprocess and run "control" process for later comparison
    from subprocess import Popen, PIPE, DEVNULL
    control_proc=None
    try:
        control_proc=Popen( args=['/bin/bash' ,control_script_targ],
                         bufsize=0,
                         executable=None,
                         stdin=DEVNULL, stdout=PIPE, stderr=PIPE,
                         preexec_fn=None, close_fds=False, shell=False)
    except OSError as exc:
        print('problem with running control script before tagging.')
        assert False

    # grab control output
    control_out, control_err= None,None
    control_ret_code=None
    try:
        control_out, control_err = (
            f.decode() for f in control_proc.communicate(DEVNULL) )
        control_ret_code = control_proc.wait()
        print(f'control_out, control_err, control_ret_code = \n {control_out}, \n {control_err}, \n {control_ret_code}')
        assert all( [ control_out is not None,
                      control_err is not None,
                      control_ret_code is not None ] )        
    except OSError as exc:
        print('problem getting output from control proc')
        assert False

    # if we're testing over and over and '.notags' version exists,
    # clobber the tagged version and replace it with '.notags' version
    test_script_targ=control_script_targ+'.tags'
    if Path(test_script_targ).exists():
        Path(test_script_targ).unlink()    

    # call the routine
    from lib.python.tool_ops_w_papiex import tool_ops_w_papiex    
    tool_ops_w_papiex(fin_name = control_script_targ,
                      fms_modulefiles = None)
    
    # check that output files were created as we expect
    assert Path(test_script_targ).exists()
    
    # now check that the script fails, as it should, after tooling
    test_proc=None
    try:
        test_proc=Popen( args=['/bin/bash' ,test_script_targ],
                         bufsize=0,
                         executable=None,
                         stdin=DEVNULL, stdout=PIPE, stderr=PIPE,
                         preexec_fn=None, close_fds=False, shell=False)
    except OSError as exc:
        print('problem with sourcing test script after tagging')
        assert False
                    
    try:
        out, err = (
            f.decode() for f in test_proc.communicate(DEVNULL) )
        ret_code = test_proc.wait()
        print(f'out, err, ret_code = \n {out}, \n {err}, \n {ret_code}')        
    except OSError as exc:
        print('problem getting output from job-submission test_proc.')
        assert False

    # check that the script output, all of it, is unchanged. 
    assert all ( [ control_out == out,
                   control_err == err,
                   control_ret_code == 0, 
                   control_ret_code == ret_code ] )


def test_check_for_diff():    
    ''' check the simple_failing_command script for differences after the
    prev test, which could in theory succeed if tool_ops_w_papiex copies 
    the script but without adding tooling.'''
    
    from pathlib import Path
    control_script_targ=str(Path.cwd())+'/tests/test_files_papiex_tooler/simple_failing_command.bash'
    script_targ=control_script_targ+'.tags'
    assert Path(control_script_targ).exists() #quick check
    assert Path(script_targ).exists() #quick check

    # check quickly that they are different in some manner.
    import filecmp as fc
    is_different=not fc.cmp( control_script_targ, script_targ,
                             shallow=False)
    print(f'different? {is_different}\n\n')
    assert is_different        

    # now we will explicitly check for those differencves
    import difflib as dl
    the_infile = open(control_script_targ)
    infile_contents=the_infile.readlines()
    the_infile.close()
    
    the_outfile = open(script_targ)
    outfile_contents=the_outfile.readlines()
    the_outfile.close()
    differences=dl.ndiff(infile_contents, outfile_contents)

    # better be something in here.
    assert differences is not None
    
    # pytest suppresses print output by default.
    # to view this and other print output in pytest
    # from PASSING tests, run something like:
    #      python -m pytest -rP tests/test_papiex_tooler
    # to get the same for FAILING tests,
    #      python -m pytest -rx tests/test_papiex_tooler
    for line in differences:
        if line[0]=='-' or line[0]=='+':
            print(line)
        else:
            continue

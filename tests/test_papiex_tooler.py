''' tests for PP/AN specific ops-tooling of job scripts for PAPIEX'''
from subprocess import Popen, PIPE, DEVNULL
from pathlib import Path
import filecmp as fc
import difflib as dl
import pytest


def test_import():
    ''' check that tool_ops_w_papiex functions can be imported '''
    from  lib.python.tool_ops_w_papiex import test_import
    assert test_import() == 0


def test_import_papiex_ops():
    ''' check that op list data can be imported '''
    import lib.python.papiex_ops as po
    assert all( [ po.op_list is not None,
                  len(po.op_list) > 0  ] ) 

SIMP_FAIL_BASH_CONTROL = str(Path.cwd()) + \
    '/tests/test_files_papiex_tooler/simple_failing_command.bash'
def test_simple_failing_command():
    ''' check that setting/unsetting PAPIEX_TAGS around an op
    will not touch the exit status of that op '''
    
    control_script_targ = SIMP_FAIL_BASH_CONTROL
    print(f'control_script_targ = {control_script_targ}')
    assert Path(control_script_targ).exists() #quick check

    # import subprocess and run "control" process
    control_proc = None
    try:
        control_proc = Popen( args = ['/bin/bash' ,control_script_targ],
                         bufsize = 0,
                         executable = None,
                         stdin = DEVNULL, stdout = PIPE, stderr = PIPE,
                         preexec_fn = None, close_fds = False, shell = False)
    except OSError as exc:
        print('problem with running control script before tagging.')
        assert False

    # grab captured output from the "control" process for later comparison
    control_out, control_err = None, None
    control_ret_code = None
    try:
        control_out, control_err = (
            f.decode() for f in control_proc.communicate(DEVNULL) )
        control_ret_code = control_proc.wait()
    except OSError as exc:
        print('problem getting output from control proc')
        assert False
        
    print(f'control_out, control_err, control_ret_code = \n' + \
          f'out = \n{control_out},\nret_code = \n{control_ret_code},\nerr = \n{control_err}\n')
    assert all( [ control_out is not None,
                  control_err is not None,
                  control_ret_code is not None,
                  control_ret_code == 0 ] ) # the script returns 0 if it fails like it should

    # if we're testing over and over and '.notags' version exists,
    # clobber the tagged version and replace it with '.notags' version
    test_script_targ = control_script_targ+'.tags'
    if Path(test_script_targ).exists():
        Path(test_script_targ).unlink()
        
    print(f'test_script_targ = {test_script_targ}')
    assert not Path(test_script_targ).exists()

    # call the routine
    from lib.python.tool_ops_w_papiex import tool_ops_w_papiex    
    tool_ops_w_papiex(fin_name = control_script_targ,
                      fms_modulefiles = None)
    
    # check that output files were created as we expect
    assert Path(test_script_targ).exists()

    # run the test proc and capture the output
    test_proc = None
    try:
        test_proc = Popen( args = ['/bin/bash', test_script_targ],
                         bufsize = 0,
                         executable = None,
                         stdin = DEVNULL, stdout = PIPE, stderr = PIPE,
                         preexec_fn = None, close_fds = False, shell = False)
    except OSError as exc:
        print('problem with sourcing test script after tagging')
        assert False
        
    # now check that the script failed, as it should, after tooling                    
    try:
        test_out, test_err = (
            f.decode() for f in test_proc.communicate(DEVNULL) )
        test_ret_code = test_proc.wait()
    except OSError as exc:
        print('problem getting output from job-submission test_proc.')
        assert False

    # check that the script output, all of it, is unchanged. 
    print(f'test_out, test_err, test_ret_code = \n {test_out}, \n {test_err}, \n {test_ret_code}')
    assert all ( [ test_out == control_out,
                   test_err == control_err,
                   test_ret_code == control_ret_code,
                   test_ret_code == 0 ] )

    
def test_check_simple_failing_command_for_diff():    
    ''' check the simple_failing_command script for differences after the
    prev test, which could in theory succeed if tool_ops_w_papiex copies 
    the script but without adding tooling.'''
    
    control_script_targ = SIMP_FAIL_BASH_CONTROL
    assert Path(control_script_targ).exists() #quick check

    test_script_targ = control_script_targ + '.tags'
    assert Path(test_script_targ).exists() #quick check

    # check quickly that they are different in some manner.
    is_different = not fc.cmp( control_script_targ, test_script_targ,
                               shallow = False)
    print(f'different? {is_different}\n\n')
    assert is_different

    # open the input/output files + read the lines
    the_infile = open( control_script_targ )
    infile_contents = the_infile.readlines()
    the_infile.close()
    
    the_outfile = open( test_script_targ )
    outfile_contents = the_outfile.readlines()
    the_outfile.close()
    
    # now we will explicitly check for those differencves
    differences = dl.ndiff( infile_contents, outfile_contents )
    assert differences is not None
    
    # pytest suppresses print output by default.
    # to view this and other print output in pytest
    # from PASSING tests, run something like:
    #      python -m pytest -rP tests/test_papiex_tooler
    # to get the same for FAILING tests,
    #      python -m pytest -rx tests/test_papiex_tooler
    diff_lines_to_check=[]
    for line in differences:
        if line[0]=='-':
            diff_lines_to_check.append(line)
        elif line[0]=='+':
            diff_lines_to_check.append(line)
        else:
            continue
        
    assert diff_lines_to_check != []
    assert diff_lines_to_check[0] == '- if mv DNE_file DNE2_file; then\n'
    assert diff_lines_to_check[1] == '+ if { export PAPIEX_TAGS="op:mv;op_instance:1"; mv DNE_file DNE2_file; ' + \
        'SUCCESS=$?; unset PAPIEX_TAGS; } && [ $SUCCESS -eq 0 ]; then\n'




    
ROSE_TASK_RUN_CONTROL = str(Path.cwd()) + \
    '/tests/test_files_papiex_tooler/am5_c96L33_amip_mask-atmos-plevel_atmos_scalar_job'
def test_rose_task_run_for_diff():    
    control_script_targ = ROSE_TASK_RUN_CONTROL
    assert Path(control_script_targ).exists()
    print(f'control_script_targ = {control_script_targ}')

    # if we're testing over and over and '.notags' version exists,
    # clobber the tagged version and replace it with '.notags' version
    test_script_targ=control_script_targ+'.tags'
    if Path(test_script_targ).exists():
        Path(test_script_targ).unlink()    
    assert not Path(test_script_targ).exists()
    print(f'test_script_targ = {test_script_targ}')    

    # call the routine
    from lib.python.tool_ops_w_papiex import tool_ops_w_papiex    
    tool_ops_w_papiex(fin_name = control_script_targ,
                      fms_modulefiles = None)
    
    # check that output files were created as we expect
    assert Path(test_script_targ).exists()

    # check quickly that they are different in some manner.
    is_different=not fc.cmp( control_script_targ, test_script_targ,
                             shallow=False)
    print(f'different? {is_different}\n\n')
    assert is_different

    # now we will explicitly check for those differences
    the_infile = open(control_script_targ)
    infile_contents=the_infile.readlines()
    the_infile.close()

    the_outfile = open(test_script_targ)
    outfile_contents=the_outfile.readlines()
    the_outfile.close()
    
    differences=dl.ndiff(infile_contents, outfile_contents)
    assert differences is not None
    #print (differences)
    #for diff in differences:
    #    print(diff)

    # pytest suppresses print output by default.
    # to view this and other print output in pytest
    # from PASSING tests, run something like:
    #      python -m pytest -rP tests/test_papiex_tooler
    # to get the same for FAILING tests,
    #      python -m pytest -rx tests/test_papiex_tooler
    def_is_different_for_sure=False
    for line in differences:
        if line[0]=='-' or line[0]=='+':
            def_is_different_for_sure=True
            print(line)
        else:
            continue
            
    # better be something in here.
    assert differences is not None
    assert def_is_different_for_sure



PP_STARTER_CONTROL = str(Path.cwd()) + \
    '/tests/test_files_papiex_tooler/test_pp-starter'
def test_pp_starter_for_no_diff():    
    control_script_targ=PP_STARTER_CONTROL

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


    script_targ=control_script_targ+'.tags'
    assert Path(control_script_targ).exists() #quick check
    assert Path(script_targ).exists() #quick check

    # check quickly that they are different in some manner.
    is_different=not fc.cmp( control_script_targ, script_targ,
                             shallow=False)
    print(f'different? {is_different}\n\n')

    # now we will explicitly check for those differences
    the_infile = open(control_script_targ)
    infile_contents=the_infile.readlines()
    the_infile.close()
    
    the_outfile = open(script_targ)
    outfile_contents=the_outfile.readlines()
    the_outfile.close()
    
    differences=dl.ndiff(infile_contents, outfile_contents)
    assert differences is not None
    #print (differences)


    # pytest suppresses print output by default.
    # to view this and other print output in pytest
    # from PASSING tests, run something like:
    #      python -m pytest -rP tests/test_papiex_tooler
    # to get the same for FAILING tests,
    #      python -m pytest -rx tests/test_papiex_tooler
    def_is_different_for_sure=False
    if differences is not None:
        for line in differences:
            if line[0]=='-' or line[0]=='+':
                def_is_different_for_sure=True
                print(line)
            else:
                continue

    # note- just because the files are the same doesn't
    #       mean that difflib.ndiff returns None
    #assert differences is None
    assert not is_different
    assert not def_is_different_for_sure
    

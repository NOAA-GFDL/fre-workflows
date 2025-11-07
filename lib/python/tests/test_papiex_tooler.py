'''
tests for PP/AN specific ops-tooling of job scripts for PAPIEX
'''

import difflib as dl
import filecmp as fc

from subprocess import Popen, PIPE, DEVNULL
from pathlib import Path

from lib.python.tool_ops_w_papiex import tool_ops_w_papiex

SIMPLE_FAILING_BASH = 'lib/python/tests/test_files_papiex_tooler/simple_failing_command.bash'
AM5_ROSE_TASK = 'lib/python/tests/test_files_papiex_tooler/am5_c96L33_amip_mask-atmos-plevel_atmos_scalar_job'
PP_STARTER_TASK = 'lib/python/tests/test_files_papiex_tooler/test_pp-starter'

def test_import():
    '''
    check that tool_ops_w_papiex functions can be imported
    '''
    from lib.python.tool_ops_w_papiex import test_import
    assert test_import() == 0


def test_import_papiex_ops():
    '''
    check that op list data can be imported
    '''
    import lib.python.papiex_ops as ops
    assert all( [ ops.op_list is not None,
                     len(ops.op_list) > 0  ] )


def test_running_a_simple_failing_command():
    '''
    run a simple script that fails in a control manner and make sure it fails in the intended manner.
    the failure should occur with an exit code of 0 by design.
    '''

    control_script_targ = SIMPLE_FAILING_BASH
    assert Path(control_script_targ).exists() #quick check

    # run "control" process for later comparison
    control_proc = None
    try:
        control_proc = Popen( args = ['/bin/bash', control_script_targ],
                              bufsize = 0,
                              executable = None,
                              stdin = DEVNULL, stdout = PIPE, stderr = PIPE,
                              preexec_fn = None, close_fds = False, shell = False)
    except OSError as exc:
        print('problem with running control script before tagging.')
        assert False

    # grab control output
    control_out, control_err = None, None
    control_ret_code = None
    try:
        # output is byte-code, have to decode
        control_out, control_err = (
            f.decode() for f in control_proc.communicate(DEVNULL) )
        control_ret_code = control_proc.wait()
        print(f'control_out, control_err, control_ret_code = ' + \
              f'\n {control_out}, \n{control_err}, \n{control_ret_code}')
        assert all( [ control_out == '',
                      control_err == "mv: cannot stat 'DNE_file': No such file or directory\n",
                      control_ret_code == 0 ] )
    except OSError as exc:
        print('problem getting output from control proc')
        assert False


def test_tagging_a_simple_failing_command():
    '''
    check that setting/unsetting PAPIEX_TAGS around an op will not affect the outcome of the previous
    failing script.
    '''
    # if we're testing over and over and '.notags' version exists,
    # clobber the tagged version and replace it with '.notags' version
    control_script_targ = SIMPLE_FAILING_BASH
    test_script_targ = control_script_targ + '.tags'
    if Path(test_script_targ).exists():
        Path(test_script_targ).unlink()

    # call the routine
    tool_ops_w_papiex(fin_name = control_script_targ)


    # check that output files were created as we expect
    assert Path(test_script_targ).exists()

    # now check that the script fails, as it should, after tooling
    test_proc = None
    try:
        test_proc = Popen( args = ['/bin/bash', test_script_targ],
                           bufsize = 0,
                           executable = None,
                           stdin = DEVNULL, stdout = PIPE, stderr = PIPE,
                           preexec_fn = None, close_fds = False, shell = False )
    except OSError as exc:
        print('problem with sourcing test script after tagging')
        assert False

    try:
        # output is byte-code, have to decode
        out, err = (
            f.decode() for f in test_proc.communicate(DEVNULL) )
        ret_code = test_proc.wait()
        print(f'out, err, ret_code = \n {out}, \n {err}, \n {ret_code}')
    except OSError as exc:
        print('problem getting output from job-submission test_proc.')
        assert False

    # check that the script output, all of it, is unchanged.
    assert all ( [ out == '',
                   err == "mv: cannot stat 'DNE_file': No such file or directory\n",
                   ret_code == 0 ] )


def test_check_simple_failing_command_for_diff():
    '''
    check the simple_failing_command script for differences after the
    prev test, which could in theory succeed if tool_ops_w_papiex copies
    the script but without adding tooling.
    '''

    control_script_targ = SIMPLE_FAILING_BASH
    assert Path(control_script_targ).exists() #quick check

    test_script_targ = control_script_targ + '.tags'
    assert Path(test_script_targ).exists() #sanity

    # check quickly that they are different in some manner.
    is_different = not fc.cmp( control_script_targ, test_script_targ,
                               shallow = False)
    print(f'different? {is_different}\n\n')
    assert is_different

    # now we will explicitly check for those differencves
    the_infile = open(control_script_targ)
    infile_contents = the_infile.readlines()
    the_infile.close()
    assert infile_contents is not None

    the_outfile = open(test_script_targ)
    outfile_contents = the_outfile.readlines()
    the_outfile.close()
    assert outfile_contents is not None

    # better be something in here.
    differences = dl.ndiff(infile_contents, outfile_contents)
    assert differences is not None

    ## DEBUG
    ## pytest suppresses print output by default.
    ## to view this and other print output in pytest
    ## from PASSING tests, run something like:
    ##      python -m pytest -rP tests/test_papiex_tooler
    ## to get the same for FAILING tests,
    ##      python -m pytest -rx tests/test_papiex_tooler
    #for line in differences:
    #    if line[0] == '-' or line[0] == '+':
    #        print(line)
    #    else:
    #        continue

    # cleanup
    assert Path(test_script_targ).exists()
    Path(test_script_targ).unlink()


def test_rose_task_run_for_diff():
    '''
    check that a rose-app-run call gets tagged appropriately
    '''
    control_script_targ = AM5_ROSE_TASK
    assert Path(control_script_targ).exists() #quick check

    # if we're testing over and over and '.notags' version exists,
    # clobber the tagged version and replace it with '.notags' version
    test_script_targ = control_script_targ + '.tags'
    if Path(test_script_targ).exists():
        Path(test_script_targ).unlink()

    # call the routine
    tool_ops_w_papiex(fin_name = control_script_targ)


    # check that output files were created as we expect
    assert Path(test_script_targ).exists()

    # check quickly that they are different in some manner.
    is_different = not fc.cmp( control_script_targ, test_script_targ,
                             shallow = False)
    print(f'different? {is_different}\n\n')
    assert is_different

    # open the original file and read it's contents
    the_infile = open(control_script_targ)
    infile_contents = the_infile.readlines()
    the_infile.close()
    assert infile_contents is not None

    # open the output file and read it's contents
    the_outfile = open(test_script_targ)
    outfile_contents = the_outfile.readlines()
    the_outfile.close()
    assert outfile_contents is not None

    # now we will explicitly check for those differences
    differences = dl.ndiff(infile_contents, outfile_contents)
    assert differences is not None

    # sanity check
    def_is_different_for_sure = False
    for line in differences:
        if line[0] == '-' or line[0] == '+':
            def_is_different_for_sure = True
            print(line)
        else:
            continue
    assert def_is_different_for_sure

    # cleanup
    Path(test_script_targ).unlink()


def test_pp_starter_for_no_diff():
    '''
    make sure a pp-starter task doesnt get tagged
    '''
    control_script_targ = PP_STARTER_TASK
    assert Path(control_script_targ).exists()

    # if we're testing over and over and '.notags' version exists,
    # clobber the tagged version and replace it with '.notags' version
    test_script_targ = control_script_targ + '.tags'
    if Path(test_script_targ).exists():
        Path(test_script_targ).unlink()

    # call the routine
    tool_ops_w_papiex(fin_name = control_script_targ)


    # check that output files were created as we expect
    assert Path(test_script_targ).exists()

    # check the input file was not accidentally clobbered too
    assert Path(control_script_targ).exists()

    # check quickly that they are different in some manner.
    is_different = not fc.cmp( control_script_targ, test_script_targ,
                             shallow = False)
    print(f'different? {is_different}\n\n')
    assert not is_different

    # open the original file and read it's contents
    the_infile = open(control_script_targ)
    infile_contents = the_infile.readlines()
    the_infile.close()

    # open the output file and read it's contents
    the_outfile = open(test_script_targ)
    outfile_contents = the_outfile.readlines()
    the_outfile.close()

    # now we will explicitly check for those differences
    differences = dl.ndiff(infile_contents, outfile_contents)
    #assert differences is None # ndiff doesn't return None for 0 differences

    def_is_different_for_sure = False
    if differences is not None:
        for line in differences:
            if line[0] == '-' or line[0] == '+':
                def_is_different_for_sure = True
                print(line)
            else:
                continue
    # the real check for a lack of differences
    assert not def_is_different_for_sure

    # cleanup
    Path(test_script_targ).unlink()

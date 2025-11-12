#!/usr/bin/env python
'''
tags specific operations for data-scraping via PAPIEX and EPMT
this is an adaptation of the following for FRE Canopy specifically
https://gitlab.gfdl.noaa.gov/fre-legacy/fre-commands/-/blob/
387bfb136361373a8532a2c9a12bab497f9ea654/bin/frepp#L8059-L8258
'''

# TODO rename: tool_ops_w_papiex --> tag_ops_ ?
# TODO typing/type hints
# TODO logging that is easy to turn off***
import logging
import re

logger = logging.getLogger(__name__)
logger.warning('tool_ops_w_papiex imported successfully. logger set. configuring logger.')

FORMAT = "[%(levelname)5s:%(filename)24s:%(funcName)20s] %(message)s"
#logging.basicConfig(level = logging.WARNING,
#logging.basicConfig(level = logging.DEBUG,
logging.basicConfig(level = logging.INFO,
                    format = FORMAT,
                    filename = None,
                    encoding = 'utf-8' )
logger.debug('logger configured')

try:
    if any([ 'lib.python'  in __name__ ,
             'tests.test_' in __name__  ]) :
        logger.info('attempting RELATIVE import of .papiex_ops ...')
        from .papiex_ops import op_list
    else:
        logger.info('attempting ABSOLUTE import of papiex_ops ...')
        from papiex_ops import op_list # pylint: disable=import-error
except Exception as exc:
    logger.error('error! op_list import issues.')
    raise ImportError('could not find and/or import papiex_ops') from exc

def test_import():
    '''
    for testing import of module via pytest only
    '''
    return 0

def log_assign_append( msg: str,
                       line: str,
                       script: list[str] ) -> str:
    '''
    logs a message at DEBUG using msg and the line. appends the line to script.

    returns the line.
    '''
    logger.debug('%s %s', msg, line)
    script.append(line)
    return line

def op_is_in_line( op_name: str,
                   line: str ) -> bool:
    '''
    searches a line for an operation string with regex, emits messages if any are found and returns True.
    Otherwise, the tool is silent and returns False.
    '''
    #op_s_string = r'[\s?|^]' + op_name + r'(?:\s+|$)' #missing rm -rf when at the start of a line
    op_s_string = r'(?:\s|^)' + op_name + r'(?:\s+|$)' #seems good...
    re_search_result = re.search(op_s_string, line)
    if re_search_result is None:
        return False
    logger.info("found op = %s in line = \n %s", op_name, line)
    logger.debug("regex search string was: %s", op_s_string)
    return True

def check_op_in_typical_line_again( line: str,
                                    op_name: str ) -> bool:
    '''
    given a line with op_name in it, split it in half where op_name was, pick the left half,
    and make sure it's whitespace or empty
    '''
    left_side_of_line = line.split(op_name)[0]
    return left_side_of_line.isspace() or left_side_of_line == ''

def look_for_ops( op_list_in: list[dict],
                  line: str ) -> dict:
    '''
    searches a line for operations in the op_list dictionary

    returns data dictionary of found operations if one matches. Otherwise, None
    '''
    for op in op_list_in:
        if not op_is_in_line(op['op_name'], line):
            continue
        return op

def get_new_bashif_line( line: str,
                         op_found: dict ) -> str:
    '''
    edits a bash-if/elif line for a found operation and returns it
    '''
    # if there is logic, the tag must work such that exit code of the command is still checked/preserved
    then_loc_group_span = re.search('; then', line).span()
    logger.debug('bash-if case, found the \'then\' part of if/elif: %s', then_loc_group_span)
    line = line[0:then_loc_group_span[0]]
    logger.debug('bash-if case, selected part of line, now line = \n %s', line)
    line = line.replace(op_found['op_name']+' ',
                        '{ export PAPIEX_TAGS="op:' + op_found['op_tag'] + \
                        ';op_instance:OP_INSTANCE"; ' + op_found['op_name'] + ' ' )
    logger.debug('bash-if case, replaced part of line, now line = \n %s', line)
    line += '; SUCCESS=$?; unset PAPIEX_TAGS; } && [ $SUCCESS -eq 0 ]; then'
    logger.info('bash-if case, appended to line, now = line = \n %s', line)
    return line

def get_new_rose_task_run_line( line: str,
                                op_found: dict ) -> str:
    '''
    edits a rose task-run line for a found operation and returns it
    '''
    # this is one of the easiest cases, because the job script is effectively a single line of interest
    logger.debug('rose case before, line = \n %s', line)
    line = 'export PAPIEX_TAGS="op:' + op_found['op_tag'] + \
           ';op_instance:OP_INSTANCE"; ' + line + '; unset PAPIEX_TAGS;'
    logger.info('rose case after, line = \n %s', line)
    return line

def get_new_bash_line( line: str,
                         op_found: dict ) -> str:
    '''
    edits a bash line (not an if/elif statement, not a rose task run either) for a found operation and returns it
    '''
    # no logic, tool in the usual way.
    logger.debug("op_found = %s", op_found['op_name'])
    logger.debug('other case, before, line = \n %s', line)
    line = line.replace( op_found['op_name'] + ' ',
                         'export PAPIEX_TAGS="op:' + op_found['op_tag'] + \
                         ';op_instance:OP_INSTANCE"; ' + op_found['op_name'] + ' ' )
    line += '; unset PAPIEX_TAGS;'
    logger.info('other case, after, line = \n %s', line)

    return line

def tool_ops_w_papiex( fin_name: str ) -> None:
    '''
    parses a job bash-script assembled by script, tags operations of interest.
    accomplished by setting/unsetting PAPIEX_TAGS env var around operation of interest,
    referred to as a caliper approach.
    an if-statement in bash will have a slightly different structure to preserve the
    exit status and the resultant if/elif/else continuation of the job script
    '''

    logger.info('init op_instance (cnt)')
    for op in op_list:
        logger.debug("initializing op_instance count for %s", op['op_name'])
        op['op_instance'] = 0

    logger.info('init lists of lines (list[strs]), prevline (str)')
    lines = []
    script = []
    prevline = ''

    logger.info('opening %s', fin_name)
    with open(fin_name, 'r', encoding='utf-8') as file :
        lines = file.read().splitlines()

    if not len(lines) > 0:
        raise IOError(f'could not read file {fin_name}')
    logger.info('file opened and split into lines successfully')

    an_op_was_tagged = False
    logger.info('about to parse the file line-by-line')
    for line in lines:

        if re.match( r'\s*#', line) is not None:
            prevline = log_assign_append('skip, line is a comment: ', line, script)
            continue

        if re.match( r'\s*export', line) is not None:
            prevline = log_assign_append('skip, line is an export: ', line, script)
            continue

        if re.match( r'\s*module ', line) is not None:
            prevline = log_assign_append('skip, line is a module load: ', line, script)
            continue

        if re.match( r'\s*type ', line) is not None:
            prevline = log_assign_append('skip, line declares a bash type: ', line, script)
            continue

        op_found = look_for_ops(op_list, line)
        has_op = op_found is not None
        if not has_op:
            prevline = log_assign_append('skip, line has no ops of interest: ', line, script)
            continue

        logger.debug('further analyzing line holding op of interest... (conditional? rose task? etc)')
        is_bashif = False
        is_rose_task_run = False
        if any([ re.search('if ', line)   is not None,
                 re.search('elif ', line) is not None ]):
            logger.debug('line with op is an if (or elif) statement in bash')
            is_bashif = True

        elif re.search('rose task-run ', line) is not None:
            logger.debug('line with op is a rose task-run line')
            is_rose_task_run = True

        else:
            logger.debug('neither a rose task nor a bash if statement. typical shell line.')
            if not check_op_in_typical_line_again(line, op_found['op_name']):
                prevline = log_assign_append('skip, this line likely isn\'t a call to the op: ', line, script)
                continue

        logger.debug('now editing the line accordingly to type of line')
        if is_bashif:
            line = get_new_bashif_line( line, op_found )
        elif is_rose_task_run:
            line = get_new_rose_task_run_line( line, op_found )
        else:
            line = get_new_bash_line( line, op_found )

        ### Refine the PAPIEX_TAGS for a particular operation ###
        # is the op a retry? If so, mark as such via tag and OP_INSTANCE
        # this assists in identifying operation correlations and/or
        # pathologies across jobs that should be similar.
        if 'failure, retrying' in prevline:
            retry = ';retry:1'
            logger.debug('previous line was a RETRY logging statement, so this line must be a retry! retry = %s', retry)
        else:
            retry = ''

        # Increment the operation instance.
        # op_instance correlates to a specific line in the script.
        for op in op_list:
            if op_found['op_tag'] != op['op_tag']:
                continue
            logger.debug('incrementing op_instance for op = %s', op['op_name'])
            op['op_instance'] += 1

            logger.debug('replacing op_instance, before, line = \n %s', line)
            line = line.replace( "OP_INSTANCE",
                                 str(op['op_instance'] ) + retry)
            logger.debug('replacing op_instance, after, line = \n %s', line)
            break

        # track previous line to catch retry ops
        #logger.debug('before, prevline = \n %s', prevline)
        prevline = log_assign_append('appending line with tagged op: \n ', line, script)
        #logger.debug('before, prevline = \n %s', prevline)
        an_op_was_tagged = True

    # script must end in newline, cylc requirement i think?
    script[-1] += '\n'

    if an_op_was_tagged:
        logger.info('tagged at least one operation in this script. done tagging!')
    else:
        logger.info('no operations of interest found, nothing tagged.')

    fout_name = fin_name + '.tags'
    logger.debug('writing output job script: %s', fout_name)
    with open(fout_name, 'w', encoding='utf-8') as file:
        file.write('\n'.join(script))

    logger.debug('writing output job script written. cleaning up script from memory')
    del script




def annotate_metadata(): #TODO 7
    '''
    parses a job bash-script assembled by script, annotating metadata of interest.
    accomplished by adding lines, that call `epmt annotate EPMT_JOB_TAGS=<dict>`, and
    parsing the job script for metadata of interest.
    '''
    raise NotImplementedError()

    ## Reset the EPMT_JOB_TAGS root
    #EPMT_JOB_TAGS = "epmt annotate EPMT_JOB_TAGS='"
    #
    ## Since all the information needed is in the top of the file, form the EPMT_JOB_TAG first
    #sname = {}
    #for line in lines:
    #  # No information of interest after this line
    #  if '#platform_csh' in line: break
    #  for k,v in jtag_dict.items():
    #    if v in line:
    #      l = len(v)
    #      EPMT_JOB_TAGS = EPMT_JOB_TAGS + k + ":" + line[l:].lstrip() + ";"
    #      if k == 'exp_name': sname['exp_name'] = line[l:].lstrip()
    #      if k == 'exp_component': sname['exp_component'] = line[l:].lstrip()
    #      if k == 'exp_time': sname['exp_time'] = line[l:].lstrip()
    #
    #EPMT_JOB_TAGS += 'script_name:'
    #if sname.get('exp_name')      is not None: EPMT_JOB_TAGS += sname['exp_name']      +"_"
    #if sname.get('exp_component') is not None: EPMT_JOB_TAGS += sname['exp_component'] +"_"
    #if sname.get('exp_time')      is not None: EPMT_JOB_TAGS += sname['exp_time']      +"'"
    #
    #epmt_instrument = 'setenv PAPIEX_OPTIONS $PAPIEX_OLD_OPTIONS; \
    #.                  setenv LD_PRELOAD $PAPIEX_LD_PRELOAD; \
    #                   setenv PAPIEX_OUTPUT $PAPIEX_OLD_OUTPUT;'
    #epmt_uninstrument = 'unsetenv PAPIEX_OUTPUT PAPIEX_OPTIONS LD_PRELOAD'

    #print('parsing lines again!')

    ## Place the EPMT_JOB_TAGS
    #if '#INFO:max_years' in prevline:
    #   script.append('')
    #   script.append('if ( $?SLURM_JOBID ) then')
    #   script.append('    source $MODULESHOME/init/csh')
    #   script.append('    module use -a ' + fms_modulefiles)
    #   script.append('    module load epmt')
    #   script.append('    set PAPIEX_OLD_OUTPUT=$PAPIEX_OUTPUT')
    #   script.append('    set PAPIEX_OLD_OPTIONS=$PAPIEX_OPTIONS')
    #   script.append('    ' + epmt_uninstrument)
    #   script.append('    ' + EPMT_JOB_TAGS)
    #   script.append('    ' + epmt_instrument)
    #   script.append('endif')

if __name__ == '__main__':


    #
    import glob
    from pathlib import Path
    import pprint
    import shutil
    test_scripts = glob.glob('/home/inl/cylc-run/test_pp_locally__ptest__ttest/log/job/198?0101T0000Z/*/01/job')
    logger.debug('test_scripts = %s', pprint.pformat(test_scripts) )
    for test_script in test_scripts:
#        if 'regrid' not in test_script:
#            continue
        if Path(test_script+'.notags').exists():
            Path(test_script).unlink()
            shutil.copy(test_script+'.notags', test_script)
        logger.info('\n\n\n\nparsing test_script = %s', test_script)
        tool_ops_w_papiex(test_script)
#        break


    ####### local testing/debugging, ONE script input to test on.
    #infile = 'lib/python/tests/test_files_papiex_tooler/am5_c96L33_amip_mask-atmos-plevel_atmos_scalar_job'
    #tool_ops_w_papiex(infile)


    ###### local testing/debugging, ONE script input to test on.
    #infile = 'lib/python/tests/test_files_papiex_tooler/simple_failing_command.bash'
    #tool_ops_w_papiex(infile)

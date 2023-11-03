#!/usr/bin/env python
''' tags specific operations for data-scraping via PAPIEX and EPMT 
this is an adaptation of the following for FRE Canopy specifically
https://gitlab.gfdl.noaa.gov/fre-legacy/fre-commands/-/blob/
387bfb136361373a8532a2c9a12bab497f9ea654/bin/frepp#L8059-L8258 '''

# should this be a class? #TODO 1
# should we rename some things? e.g. tool_ops_w_papiex --> papiex_ops_tooler ? #TODO 2
# typing/type hints? #TODO 3
import re
import pathlib as pl

try:
    if any([ 'lib.python'  in __name__ ,
             'tests.test_' in __name__  ]) :
        print('(tool_ops_w_papiex) attempting RELATIVE import from .papiex_ops ...\n')
        from .papiex_ops import op_list
    else:
        print('(tool_ops_w_papiex) attempting import from papiex_ops ... \n')
        from papiex_ops import op_list
except:
    print(f'(tool_ops_w_papiex) error! op_list import issues.')

def test_import():
    ''' for testing import of module via pytest only '''
    return 0

def tool_ops_w_papiex(fin_name, fms_modulefiles):
    ''' parses a job bash-script assembled by script, tags operations of interest.
    accomplished by setting/unsetting PAPIEX_TAGS env var around operation of interest,
    referred to as a caliper approach.
    an if-statement in bash will have a slightly different structure to preserve the 
    exit status and the resultant if/elif/else continuation of the job script '''

    # init op_instance (cnt)
    for op in op_list:
        #print(f"initializing op_instance count for {op}")
        op['op_instance'] = 0

    # init lists of lines (list[strs]), prevline (str)
    lines = []
    script = []
    prevline = ''
    #first_time = True

    # Read in the file
    with open(fin_name, 'r') as file :
        lines = file.read().splitlines()    

    # parse line-by-line
    for line in lines:

        # is this line a comment? skip.
        if re.match( r'[ \t\r\f\v]*#', line) is not None:
            script.append(line)
            continue

        # is this line a module-load kind of step? skip.
        if re.match( r'[ \t\r\f\v]*module ', line) is not None:
            script.append(line)
            continue
    
        # does the line have an op of interest?
        has_op=False
        for op in op_list:
            if re.search(op['s_string'],line) is not None:
                #print(f"found op={op['op_name']} \n {line}")
                has_op=True
                op_found=op
                break

        # if no op, add line as-is and continue.
        if not has_op:
            script.append(line)
            continue
        
        # if there's an op, is it locked up in a condition statement?
        is_bashif=False
        if any([ re.search('if ', line)   is not None,
                 re.search('elif ', line) is not None ]):
            #print(f'found bash if-statement')
            is_bashif=True

        # if there's an op, is it a rose script-run or task-run type line?
        # NotYetImplemented #TODO 4

        # now edit the line accordingly to whether it's guarded by a bash if(or elif)-statement
        #print(f'changing line ...  {line}')
        if not is_bashif: 
            # if no logic, tool in the usual way.
            line = line.replace(op['s_string'], op['r_string']) + ' ; unset PAPIEX_TAGS'
        else: 
            # if there is logic, tool such that exit code preserved
            then_loc_group_span=re.search('; then',line).span()
            line =  line[0:then_loc_group_span[0]]            
            line =  line.replace(op['s_string'], op['r_string_w_if'])
            line += '; export SUCCESS=$?; unset PAPIEX_TAGS; } && [ $SUCCESS -eq 0 ]; then'
        #print(f'line changed  ...  \n {line}')

        ### Refine the PAPIEX_TAGS for a particular operation ###
        # is the op a retry? If so, mark as such via tag and OP_INSTANCE
        # this assists in identifying operation correlations and/or
        # pathologies across jobs that should be similar.
        if 'failure, retrying' in prevline:
            retry = ';retry:1'
        else:
            retry = ''
                
        # Increment the operation instance. 
        # op_instance correlates to a specific line in the script.
        this_op = re.search('PAPIEX_TAGS="op:(.*);op_instance:OP_INSTANCE',line)
        assert(this_op is not None)
        this_op = this_op.group(1)
        for op in op_list:
            if this_op == op['op_name']:
                op['op_instance'] += 1
                line = line.replace( "OP_INSTANCE", 
                                     str(op['op_instance'] ) + retry)
                break

        # done with this line, append and track what we just did 
        # to catch retry ops
        script.append(line)
        prevline = line    

    # end file with a new line, write out the file.
    # this script (not tool_ops_w_papiex) should do the replacing of old script
    # renaming... etc. #TODO 5
    # more flexible options? replace? keep both? #TODO 6
    script[-1] += '\n'
    fout_name = fin_name + '.tags'
    with open(fout_name, 'w') as file:
        file.write('\n'.join(script))
    
    del script


    
def annotate_metadata(): #TODO 7
    ''' parses a job bash-script assembled by script, annotating metadata of interest.
    accomplished by adding lines, that call `epmt annotate EPMT_JOB_TAGS=<dict>`, and
    parsing the job script for metadata of interest. '''
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


def test_papiex_tooling(infile = None):
    ''' local testing/debugging, ONE script input to test on. '''    
    outfile=infile+".tags"
    if pl.Path(outfile).exists():
        #print(f'removing output {outfile}')
        pl.Path(outfile).unlink()
        
    print('/////// ----------------- calling: tool_ops_w_papiex --------------- /////////')
    tool_ops_w_papiex(infile, '')
    
    import filecmp as fc
    is_different=not fc.cmp(infile, outfile, shallow=False)
    #print(f'different? {is_different}\n\n')
    if not is_different:
        print('output == input, continue. \n')
        return
    

    import sys
    import difflib as dl
    
    the_infile = open(infile)
    infile_contents=the_infile.readlines()
    the_infile.close()
    
    the_outfile = open(outfile)
    outfile_contents=the_outfile.readlines()
    the_outfile.close()

    for line in dl.ndiff(infile_contents, outfile_contents):
        if line[0]=='-' or line[0]=='+':
            print(line)
        else:
            continue




def many_tests_papiex_tooling( run_this_many_tests=1):
    ''' local debug test, to be moved to top-level dir tests? '''
    with open('./scripts_to_test_papiex_tooling_with.txt', 'r') as filelist_in :
        count=0
        for line in filelist_in.read().splitlines() :
            #print(f'line={line}')
            print(f'testing job script={line}')
            test_papiex_tooling(line)
            count+=1
            if count >= run_this_many_tests: break
        return
    

if __name__=='__main__':
    tool_ops_w_papiex('FOO',None)

    ###### local testing/debugging, ONE script input to test on.
    ##infile='/home/Ian.Laflotte/Working/59.postprocessing/test_tooling_ops.sh'
    #infile='/home/Ian.Laflotte/Working/59.postprocessing/am5_c96L33_amip_job_stage-history'
    #test_papiex_tooling(infile)
    ##### local testing/debugging, MANY input scripts to test on.
    #many_tests_papiex_tooling(200000)





#!/usr/bin/env python
''' tags specific operations for data-scraping via PAPIEX and EPMT '''

import re
import pathlib as pl
# this is an adaptation of the following for FRE Canopy specifically
# https://gitlab.gfdl.noaa.gov/fre-legacy/fre-commands/-/blob/
#     387bfb136361373a8532a2c9a12bab497f9ea654/bin/frepp#L8059-L8258

## Set up postprocessing operation dictionaries
#cp = {'op_name'       : 'cp',
#      'op_instance'   : 0,
#      's_string'      : 'cp ',
#      'r_string'      : 'export PAPIEX_TAGS="op:cp;op_instance:OP_INSTANCE" ; cp ',
#      'r_string_w_if' : '{ export PAPIEX_TAGS="op:cp;op_instance:OP_INSTANCE"; cp '
#}
##dmput = {'op_name' : 'dmput',    'op_instance' : 0,
##    's_string' : '/usr/bin/time -f "     TIME for dmput:     real %e user %U sys %S"',
##    'r_string' : 'export PAPIEX_TAGS="op:dmput;op_instance:OP_INSTANCE";'}
##dmget = {'op_name' : 'dmget',    'op_instance' : 0,
##    's_string' : '/usr/bin/time -f "     TIME for dmget:     real %e user %U sys %S"',
##    'r_string' : 'export PAPIEX_TAGS="op:dmget;op_instance:OP_INSTANCE";'}
##fregrid = {'op_name' : 'fregrid',    'op_instance' : 0,
##    's_string' : '/usr/bin/time -f "     TIME for fregrid:   real %e user %U sys %S"',
##    'r_string' : 'export PAPIEX_TAGS="op:fregrid;op_instance:OP_INSTANCE";'}
#hsmget = {'op_name'       : 'hsmget',
#          'op_instance'   : 0,
#          's_string'      : 'hsmget ',
#          'r_string'      : 'export PAPIEX_TAGS="op:hsmget;op_instance:OP_INSTANCE" ; hsmget ',
#          'r_string_w_if' : '{ export PAPIEX_TAGS="op:hsmget;op_instance:OP_INSTANCE"; hsmget '
#}
#hsmput = {'op_name'       : 'hsmput',
#          'op_instance'   : 0,
#          's_string'      : 'hsmput ',
#          'r_string'      : 'export PAPIEX_TAGS="op:hsmput;op_instance:OP_INSTANCE" ; hsmput ',
#          'r_string_w_if' : '{ export PAPIEX_TAGS="op:hsmput;op_instance:OP_INSTANCE"; hsmput '
#}
#gcp = {'op_name'       : 'gcp',
#       'op_instance'   : 0,
#       's_string'      : 'gcp ',
#       'r_string'      : 'export PAPIEX_TAGS="op:gcp;op_instance:OP_INSTANCE" ; gcp ',
#       'r_string_w_if' : '{ export PAPIEX_TAGS="op:gcp;op_instance:OP_INSTANCE"; gcp '
#}
#
#mv = {'op_name'       : 'mv',
#      'op_instance'   : 0,
#      's_string'      : 'mv ',
#      'r_string'      : 'export PAPIEX_TAGS="op:mv;op_instance:OP_INSTANCE" ; mv ',
#      'r_string_w_if' : '{ export PAPIEX_TAGS="op:mv;op_instance:OP_INSTANCE"; mv '
#}
##ncatted = {'op_name' : 'ncatted',    'op_instance' : 0,
##    's_string' : '/usr/bin/time -f "     TIME for ncatted:   real %e user %U sys %S"',
##    'r_string' : 'export PAPIEX_TAGS="op:ncatted;op_instance:OP_INSTANCE";'}
##nccopy = {'op_name' : 'nccopy',    'op_instance' : 0,
##    's_string' : '/usr/bin/time -f "     TIME for nccopy:    real %e user %U sys %S"',
##    'r_string' : 'export PAPIEX_TAGS="op:nccopy;op_instance:OP_INSTANCE";'}
##ncks = {'op_name' : 'ncks',    'op_instance' : 0,
##    's_string' : '/usr/bin/time -f "     TIME for ncks:      real %e user %U sys %S"',
##    'r_string' : 'export PAPIEX_TAGS="op:ncks;op_instance:OP_INSTANCE";'}
##ncrcat = {'op_name' : 'ncrcat',    'op_instance' : 0,
##    's_string' : '/usr/bin/time -f "     TIME for ncrcat:    real %e user %U sys %S"',
##    'r_string' : 'export PAPIEX_TAGS="op:ncrcat;op_instance:OP_INSTANCE";'}
##plevel = {'op_name' : 'plevel',    'op_instance' : 0,
##    's_string' : '/usr/bin/time -f "     TIME for plevel:    real %e user %U sys %S"',
##    'r_string' : 'export PAPIEX_TAGS="op:plevel;op_instance:OP_INSTANCE";'}
#rm = {'op_name'       : 'rm',
#      'op_instance'   : 0,
#      's_string'      : 'rm ',
#      'r_string'      : 'export PAPIEX_TAGS="op:rm;op_instance:OP_INSTANCE" ; rm ',
#      'r_string_w_if' : '{ export PAPIEX_TAGS="op:rm;op_instance:OP_INSTANCE"; rm '
#}
##splitvars = {'op_name' : 'splitvars',    'op_instance' : 0,
##    's_string' : '/usr/bin/time -f "     TIME for splitvars: real %e user %U sys %S"',
##    'r_string' : 'export PAPIEX_TAGS="op:splitvars;op_instance:OP_INSTANCE";'}
#tar = {'op_name'       : 'tar',
#       'op_instance'   : 0,
#       's_string'      : 'tar ',
#       'r_string'      : 'export PAPIEX_TAGS="op:tar;op_instance:OP_INSTANCE" ; tar ',
#       'r_string_w_if' : '{ export PAPIEX_TAGS="op:tar;op_instance:OP_INSTANCE"; tar '
#}
#timavg = {'op_name'       : 'make-timeavgs',
#          'op_instance'   : 0,
#          's_string'      : 'make-timeavgs ',
#          'r_string'      : 'export PAPIEX_TAGS="op:timavg;op_instance:OP_INSTANCE" ; make-timeavgs ',
#          'r_string_w_if' : '{ export PAPIEX_TAGS="op:timavg;op_instance:OP_INSTANCE"; make-timeavgs '
#}
##untar = {'op_name' : 'untar',    'op_instance' : 0,
##    's_string' : '/usr/bin/time -f "     TIME for untar:     real %e user %U sys %S"',
##    'r_string' : 'export PAPIEX_TAGS="op:untar;op_instance:OP_INSTANCE";'}
#
#op_list = [
#    cp,
##    dmput,
##    dmget,
##    fregrid,
#    hsmget,
#    hsmput,
#    gcp,
#    mv,
##    ncatted,
##    nccopy,
##    ncks,
##    ncrcat,
##    plevel,
#    rm,
##    splitvars,
#    tar,
#    timavg#,
##    untar
#]
#
## for metadata annotations. 
#jtag_dict = {'exp_name' : 'set name =',
#             'exp_component' : '#INFO:component=',
#             'exp_time' : 'set oname =',
#             'exp_platform' : 'set platform =',
#             'exp_target' : 'set target =',
#             'exp_seg_months' : 'set segment_months ='}

import lib.python.papiex_ops as po
op_list=po.op_list

def test_import():
    return 0

#def papiex_tag_file(fin_name, fms_modulefiles):
def tool_ops_w_papiex(fin_name, fms_modulefiles):

    # Reset op_instance (cnt)
    for op in op_list:
        #print(f"initializing op_instance count for {op}")
        op['op_instance'] = 0

    # Read in the file
    lines = []
    with open(fin_name, 'r') as file :
        #script = file.read()
        lines = file.read().splitlines()
    
    script = []
    prevline = ''
    #first_time = True

    ## we are gonna strip this out- the papiex options are tricky enough and the metadata annotation
    ## is handled OK by Jinja2 at this point the way it is. 
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
    #epmt_instrument = 'setenv PAPIEX_OPTIONS $PAPIEX_OLD_OPTIONS; setenv LD_PRELOAD $PAPIEX_LD_PRELOAD; setenv PAPIEX_OUTPUT $PAPIEX_OLD_OUTPUT;'
    #epmt_uninstrument = 'unsetenv PAPIEX_OUTPUT PAPIEX_OPTIONS LD_PRELOAD'

    #print('parsing lines again!')


    for line in lines:

        # is it a comment? skip.
        if re.match( r'[ \t\r\f\v]*#', line) is not None:
            script.append(line)
            continue

        # is it a module-load kind of step? skip.
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
        if not has_op:
            script.append(line)
            continue
        
        # if there's an op, is it locked up in a condition statement?
        is_bashif=False
        if any([ re.search('if ', line)   is not None,
                 re.search('elif ', line) is not None ]):
            #print(f'found bash if-statement')
            is_bashif=True

        # now edit the line accordingly to whether it's guarded by a bash if(or elif)-statement
        #print(f'changing line ...  {line}')
        if not is_bashif: # if no logic to worry about, tool in the usual way.
            line=line.replace(op['s_string'], op['r_string']) + ' ; unset PAPIEX_TAGS'
        else: # if there is logic to worry about, tool such that exit code preserved
            then_loc_group_span=re.search('; then',line).span()
            line =  line[0:then_loc_group_span[0]]            
            line =  line.replace(op['s_string'], op['r_string_w_if'])
            line += '; export SUCCESS=$?; unset PAPIEX_TAGS; } && [ $SUCCESS -eq 0 ]; then'
        #print(f'line changed  ...  \n {line}')

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
    
        # Refine the PAPIEX_TAGS for a particular operation
    
        # Is this operation actually a retrun of the previous? If so, mark as such. 
        # Note that the operations sequence value is *not* incremented. This is
        # intended to assist in identifying operation correlations and/or
        # pathologies across jobs that should be similar.
        if 'failure, retrying' in prevline:
            retry = ';retry:1'
        else:
            retry = ''
                
        # Increment the operation instance. 
        # op_instance correlates to a specific line in the script.
        this_op = re.search('PAPIEX_TAGS="op:(.*);op_instance:OP_INSTANCE',line)
        assert(this_op is not None)
        
        #if this_op is None:
            #print('this_op is NONE, PAPIEX_TAGS not found...')
            
        #else:
        #    print('this_op found PAPIEX_TAGS, i think (not None == True)')
        this_op = this_op.group(1)
        #print(f'this_op.group(1)={this_op}')
        for op in op_list:
            if this_op == op['op_name']:
                #print(f'found this_op instance, incrementing and unsetting PAPIEX_TAGS')
                op['op_instance'] += 1
                line = line.replace("OP_INSTANCE",str(op['op_instance'])+retry)
                            
        script.append(line)
        prevline = line
    
    script[-1] += '\n'

    # Write the file out again
    fout_name = fin_name + '.tags'
    with open(fout_name, 'w') as file:
        file.write('\n'.join(script))
    
    del script





##### local testing/debugging, ONE script input to test on.
def test_papiex_tooling(infile = None):
    
    outfile=infile+".tags"
    if pl.Path(outfile).exists():
        #print(f'removing output {outfile}')
        pl.Path(outfile).unlink()
        
    print('//////////////----------------- calling: tool_ops_w_papiex ---------------///////////////// ')
    tool_ops_w_papiex(infile, '')
    #print('\\\\\\\\\\\\\\-------------DONE calling: tool_ops_w_papiex DONE-----------\\\\\\\\\\\\\\\\\ ')
    
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


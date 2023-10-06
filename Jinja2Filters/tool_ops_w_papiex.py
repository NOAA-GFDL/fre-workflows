#!/app/conda/miniconda/envs/cylc/bin/python

import re

# this script comes from
# https://gitlab.gfdl.noaa.gov/fre-legacy/fre-commands/-/blob/387bfb136361373a8532a2c9a12bab497f9ea654/bin/frepp#L8059-L8258

# Set up postp operation dictionaries

cp = {'op_name' : 'cp',    'op_instance' : 0,
#    's_string' : '/usr/bin/time -f "     TIME for cp:        real %e user %U sys %S"',
      's_string' : 'cp ',
    'r_string' : 'setenv PAPIEX_TAGS "op:cp;op_instance:OP_INSTANCE"; cp '}
dmput = {'op_name' : 'dmput',    'op_instance' : 0,
    's_string' : '/usr/bin/time -f "     TIME for dmput:     real %e user %U sys %S"',
    'r_string' : 'setenv PAPIEX_TAGS "op:dmput;op_instance:OP_INSTANCE";'}
dmget = {'op_name' : 'dmget',    'op_instance' : 0,
    's_string' : '/usr/bin/time -f "     TIME for dmget:     real %e user %U sys %S"',
    'r_string' : 'setenv PAPIEX_TAGS "op:dmget;op_instance:OP_INSTANCE";'}
fregrid = {'op_name' : 'fregrid',    'op_instance' : 0,
    's_string' : '/usr/bin/time -f "     TIME for fregrid:   real %e user %U sys %S"',
    'r_string' : 'setenv PAPIEX_TAGS "op:fregrid;op_instance:OP_INSTANCE";'}
hsmget = {'op_name' : 'hsmget',    'op_instance' : 0,
    's_string' : '/usr/bin/time -f "     TIME for hsmget:    real %e user %U sys %S"',
    'r_string' : 'setenv PAPIEX_TAGS "op:hsmget;op_instance:OP_INSTANCE";'}
hsmput = {'op_name' : 'hsmput',    'op_instance' : 0,
    's_string' : '/usr/bin/time -f "     TIME for hsmput:    real %e user %U sys %S"',
    'r_string' : 'setenv PAPIEX_TAGS "op:hsmput;op_instance:OP_INSTANCE";'}
gcp = {'op_name' : 'gcp',    'op_instance' : 0,
    's_string' : '/usr/bin/time -f "     TIME for gcp:       real %e user %U sys %S"',
    'r_string' : 'setenv PAPIEX_TAGS "op:gcp;op_instance:OP_INSTANCE";'}
mv = {'op_name' : 'mv',    'op_instance' : 0,
#    's_string' : '/usr/bin/time -f "     TIME for move:      real %e user %U sys %S"',
      's_string' : 'mv ',
    'r_string' : 'setenv PAPIEX_TAGS "op:mv;op_instance:OP_INSTANCE"; mv '}
ncatted = {'op_name' : 'ncatted',    'op_instance' : 0,
    's_string' : '/usr/bin/time -f "     TIME for ncatted:   real %e user %U sys %S"',
    'r_string' : 'setenv PAPIEX_TAGS "op:ncatted;op_instance:OP_INSTANCE";'}
nccopy = {'op_name' : 'nccopy',    'op_instance' : 0,
    's_string' : '/usr/bin/time -f "     TIME for nccopy:    real %e user %U sys %S"',
    'r_string' : 'setenv PAPIEX_TAGS "op:nccopy;op_instance:OP_INSTANCE";'}
ncks = {'op_name' : 'ncks',    'op_instance' : 0,
    's_string' : '/usr/bin/time -f "     TIME for ncks:      real %e user %U sys %S"',
    'r_string' : 'setenv PAPIEX_TAGS "op:ncks;op_instance:OP_INSTANCE";'}
ncrcat = {'op_name' : 'ncrcat',    'op_instance' : 0,
    's_string' : '/usr/bin/time -f "     TIME for ncrcat:    real %e user %U sys %S"',
    'r_string' : 'setenv PAPIEX_TAGS "op:ncrcat;op_instance:OP_INSTANCE";'}
plevel = {'op_name' : 'plevel',    'op_instance' : 0,
    's_string' : '/usr/bin/time -f "     TIME for plevel:    real %e user %U sys %S"',
    'r_string' : 'setenv PAPIEX_TAGS "op:plevel;op_instance:OP_INSTANCE";'}
rm = {'op_name' : 'rm',    'op_instance' : 0,
    's_string' : '/usr/bin/time -f "     TIME for remove:    real %e user %U sys %S"',
    'r_string' : 'setenv PAPIEX_TAGS "op:rm;op_instance:OP_INSTANCE";'}
splitvars = {'op_name' : 'splitvars',    'op_instance' : 0,
    's_string' : '/usr/bin/time -f "     TIME for splitvars: real %e user %U sys %S"',
    'r_string' : 'setenv PAPIEX_TAGS "op:splitvars;op_instance:OP_INSTANCE";'}
tar = {'op_name' : 'tar',    'op_instance' : 0,
#    's_string' : '/usr/bin/time -f "     TIME for tar:       real %e user %U sys %S"',
    's_string' : 'tar ',
    'r_string' : 'setenv PAPIEX_TAGS "op:tar;op_instance:OP_INSTANCE";'}
timavg = {'op_name' : 'timavg',    'op_instance' : 0,
    's_string' : '/usr/bin/time -f "     TIME for timavg:    real %e user %U sys %S"',
    'r_string' : 'setenv PAPIEX_TAGS "op:timavg;op_instance:OP_INSTANCE";'}
untar = {'op_name' : 'untar',    'op_instance' : 0,
    's_string' : '/usr/bin/time -f "     TIME for untar:     real %e user %U sys %S"',
    'r_string' : 'setenv PAPIEX_TAGS "op:untar;op_instance:OP_INSTANCE";'}

op_list = [
    cp,
    dmput,
    dmget,
    fregrid,
    hsmget,
    hsmput,
    gcp,
    mv,
    ncatted,
    nccopy,
    ncks,
    ncrcat,
    plevel,
    rm,
    splitvars,
    tar,
    timavg,
    untar
]

jtag_dict = {'exp_name' : 'set name =',
             'exp_component' : '#INFO:component=',
             'exp_time' : 'set oname =',
             'exp_platform' : 'set platform =',
             'exp_target' : 'set target =',
             'exp_seg_months' : 'set segment_months ='}

#def papiex_tag_file(fin_name, fms_modulefiles):
def tool_ops_w_papiex(fin_name, fms_modulefiles):
    fout_name = fin_name + '.tags'

    # Read in the file
    with open(fin_name, 'r') as file :
        script = file.read()

    # Replace the timing string with the PAPIEX_TAGS template string
    for op in op_list:
        script = script.replace(op['s_string'],op['r_string'])

    #print(f"script={script}")
    #return

    lines = script.splitlines()
    del script

    script = []
    pline = ''
    first_time = True

    # Reset op_instance (cnt) for each file
    for op in op_list:
        op['op_instance'] = 0

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


    for line in lines:

        ## Place the EPMT_JOB_TAGS
        #if '#INFO:max_years' in pline:
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
        if "PAPIEX_TAGS" in line:
            # Is this operation actually a retrun of the previous? If so, mark as such. 
            # Note that the operations sequence value is *not* incremented. This is
            # intended to assist in identifying operation correlations and/or
            # pathologies across jobs that should be similar.
            if 'failure, retrying' in pline:
                retry = ';retry:1'
            else:
                retry = ''
                
            # Increment the operation instance. 
            # op_instance correlates to a specific line in the script.
            this_op = re.search('PAPIEX_TAGS "op:(.*);op_instance:OP_INSTANCE',line)
            if this_op is not None: print('this_op found PAPIEX_TAGS, i think (not None == True)')
            if this_op:
              this_op = this_op.group(1)
              print(f'this_op.group(1)={this_op}')
              for op in op_list:
                  if this_op == op['op_name']:
                      print(f'found this_op instance, incrementing and unsetting PAPIEX_TAGS')
                      op['op_instance'] += 1
                      line = line.replace("OP_INSTANCE",str(op['op_instance'])+retry)
                      line = line + ' ;unsetenv PAPIEX_TAGS'
        script.append(line)
        pline = line

    script[-1] += '\n'

    # Write the file out again
    with open(fout_name, 'w') as file:
        file.write('\n'.join(script))
    
    del script



###### local testing/debugging
#import pathlib as pl
#infile='/home/Ian.Laflotte/Working/59.postprocessing/test_tooling_ops.sh'
#outfile='/home/Ian.Laflotte/Working/59.postprocessing/test_tooling_ops.sh.tags'
#if pl.Path(outfile).exists():
#    print(f'to recreate- removing output {outfile}')
#    pl.Path(outfile).unlink()
#papiex_tag_file('/home/Ian.Laflotte/Working/59.postprocessing/test_tooling_ops.sh', '')
#
#import filecmp as fc
#print(f'different? {not fc.cmp(infile, outfile, shallow=False)}\n\n')

#import sys
#import difflib as dl
#the_infile = open(infile)
#infile_contents=the_infile.readlines()
#the_infile.close()
#the_outfile = open(outfile)
#outfile_contents=the_outfile.readlines()
#the_outfile.close()
#for line in dl.ndiff(infile_contents, outfile_contents):
#    print(line)



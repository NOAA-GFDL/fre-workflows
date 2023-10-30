# Set up postprocessing operation dictionaries
cp = {'op_name'       : 'cp',
      'op_instance'   : 0,
      's_string'      : 'cp ',
      'r_string'      : 'export PAPIEX_TAGS="op:cp;op_instance:OP_INSTANCE" ; cp ',
      'r_string_w_if' : '{ export PAPIEX_TAGS="op:cp;op_instance:OP_INSTANCE"; cp '
}
#dmput = {'op_name' : 'dmput',    'op_instance' : 0,
#    's_string' : '/usr/bin/time -f "     TIME for dmput:     real %e user %U sys %S"',
#    'r_string' : 'export PAPIEX_TAGS="op:dmput;op_instance:OP_INSTANCE";'}
#dmget = {'op_name' : 'dmget',    'op_instance' : 0,
#    's_string' : '/usr/bin/time -f "     TIME for dmget:     real %e user %U sys %S"',
#    'r_string' : 'export PAPIEX_TAGS="op:dmget;op_instance:OP_INSTANCE";'}
#fregrid = {'op_name' : 'fregrid',    'op_instance' : 0,
#    's_string' : '/usr/bin/time -f "     TIME for fregrid:   real %e user %U sys %S"',
#    'r_string' : 'export PAPIEX_TAGS="op:fregrid;op_instance:OP_INSTANCE";'}
hsmget = {'op_name'       : 'hsmget',
          'op_instance'   : 0,
          's_string'      : 'hsmget ',
          'r_string'      : 'export PAPIEX_TAGS="op:hsmget;op_instance:OP_INSTANCE" ; hsmget ',
          'r_string_w_if' : '{ export PAPIEX_TAGS="op:hsmget;op_instance:OP_INSTANCE"; hsmget '
}
hsmput = {'op_name'       : 'hsmput',
          'op_instance'   : 0,
          's_string'      : 'hsmput ',
          'r_string'      : 'export PAPIEX_TAGS="op:hsmput;op_instance:OP_INSTANCE" ; hsmput ',
          'r_string_w_if' : '{ export PAPIEX_TAGS="op:hsmput;op_instance:OP_INSTANCE"; hsmput '
}
gcp = {'op_name'       : 'gcp',
       'op_instance'   : 0,
       's_string'      : 'gcp ',
       'r_string'      : 'export PAPIEX_TAGS="op:gcp;op_instance:OP_INSTANCE" ; gcp ',
       'r_string_w_if' : '{ export PAPIEX_TAGS="op:gcp;op_instance:OP_INSTANCE"; gcp '
}

mv = {'op_name'       : 'mv',
      'op_instance'   : 0,
      's_string'      : 'mv ',
      'r_string'      : 'export PAPIEX_TAGS="op:mv;op_instance:OP_INSTANCE" ; mv ',
      'r_string_w_if' : '{ export PAPIEX_TAGS="op:mv;op_instance:OP_INSTANCE"; mv '
}
#ncatted = {'op_name' : 'ncatted',    'op_instance' : 0,
#    's_string' : '/usr/bin/time -f "     TIME for ncatted:   real %e user %U sys %S"',
#    'r_string' : 'export PAPIEX_TAGS="op:ncatted;op_instance:OP_INSTANCE";'}
#nccopy = {'op_name' : 'nccopy',    'op_instance' : 0,
#    's_string' : '/usr/bin/time -f "     TIME for nccopy:    real %e user %U sys %S"',
#    'r_string' : 'export PAPIEX_TAGS="op:nccopy;op_instance:OP_INSTANCE";'}
#ncks = {'op_name' : 'ncks',    'op_instance' : 0,
#    's_string' : '/usr/bin/time -f "     TIME for ncks:      real %e user %U sys %S"',
#    'r_string' : 'export PAPIEX_TAGS="op:ncks;op_instance:OP_INSTANCE";'}
#ncrcat = {'op_name' : 'ncrcat',    'op_instance' : 0,
#    's_string' : '/usr/bin/time -f "     TIME for ncrcat:    real %e user %U sys %S"',
#    'r_string' : 'export PAPIEX_TAGS="op:ncrcat;op_instance:OP_INSTANCE";'}
#plevel = {'op_name' : 'plevel',    'op_instance' : 0,
#    's_string' : '/usr/bin/time -f "     TIME for plevel:    real %e user %U sys %S"',
#    'r_string' : 'export PAPIEX_TAGS="op:plevel;op_instance:OP_INSTANCE";'}
rm = {'op_name'       : 'rm',
      'op_instance'   : 0,
      's_string'      : 'rm ',
      'r_string'      : 'export PAPIEX_TAGS="op:rm;op_instance:OP_INSTANCE" ; rm ',
      'r_string_w_if' : '{ export PAPIEX_TAGS="op:rm;op_instance:OP_INSTANCE"; rm '
}
#splitvars = {'op_name' : 'splitvars',    'op_instance' : 0,
#    's_string' : '/usr/bin/time -f "     TIME for splitvars: real %e user %U sys %S"',
#    'r_string' : 'export PAPIEX_TAGS="op:splitvars;op_instance:OP_INSTANCE";'}
tar = {'op_name'       : 'tar',
       'op_instance'   : 0,
       's_string'      : 'tar ',
       'r_string'      : 'export PAPIEX_TAGS="op:tar;op_instance:OP_INSTANCE" ; tar ',
       'r_string_w_if' : '{ export PAPIEX_TAGS="op:tar;op_instance:OP_INSTANCE"; tar '
}
timavg = {'op_name'       : 'make-timeavgs',
          'op_instance'   : 0,
          's_string'      : 'make-timeavgs ',
          'r_string'      : 'export PAPIEX_TAGS="op:timavg;op_instance:OP_INSTANCE" ; make-timeavgs ',
          'r_string_w_if' : '{ export PAPIEX_TAGS="op:timavg;op_instance:OP_INSTANCE"; make-timeavgs '
}
#untar = {'op_name' : 'untar',    'op_instance' : 0,
#    's_string' : '/usr/bin/time -f "     TIME for untar:     real %e user %U sys %S"',
#    'r_string' : 'export PAPIEX_TAGS="op:untar;op_instance:OP_INSTANCE";'}

op_list = [
    cp,
#    dmput,
#    dmget,
#    fregrid,
    hsmget,
    hsmput,
    gcp,
    mv,
#    ncatted,
#    nccopy,
#    ncks,
#    ncrcat,
#    plevel,
    rm,
#    splitvars,
    tar,
    timavg#,
#    untar
]

# for metadata annotations. 
jtag_dict = {'exp_name' : 'set name =',
             'exp_component' : '#INFO:component=',
             'exp_time' : 'set oname =',
             'exp_platform' : 'set platform =',
             'exp_target' : 'set target =',
             'exp_seg_months' : 'set segment_months ='}


'''
this file shows the target ops of interest within the FRE/Canopy
postprocessing repo. this file is strictly data.
'''

# regex note 1 -
#    [\s?|^] matches a single whitespace character if present
#    or the beginning of a string
# regex note 2 -
#    (?:\s+|$) matches a single whitespace character, or the
#    end of a line, or the end of a string, i think... see
#    https://stackoverflow.com/questions/16519744

### specialized data movement operations
dmget = {'op_name'       : 'dmget',
          'op_instance'   : 0,
          's_string'      : r'[\s?|^]dmget(?:\s+|$)',
          'r_string'      : 'export PAPIEX_TAGS="op:dmget;op_instance:OP_INSTANCE"; dmget ',
          'r_string_w_if' : '{ export PAPIEX_TAGS="op:dmget;op_instance:OP_INSTANCE"; dmget ',
          'r_string_rose' : None
}
dmput = {'op_name'       : 'dmput',
          'op_instance'   : 0,
          's_string'      : r'[\s?|^]dmput(?:\s+|$)',
          'r_string'      : 'export PAPIEX_TAGS="op:dmput;op_instance:OP_INSTANCE"; dmput ',
          'r_string_w_if' : '{ export PAPIEX_TAGS="op:dmput;op_instance:OP_INSTANCE"; dmput ',
          'r_string_rose' : None
}
hsmget = {'op_name'       : 'hsmget',
          'op_instance'   : 0,
          's_string'      : r'[\s?|^]hsmget(?:\s+|$)',
          'r_string'      : 'export PAPIEX_TAGS="op:hsmget;op_instance:OP_INSTANCE"; hsmget ',
          'r_string_w_if' : '{ export PAPIEX_TAGS="op:hsmget;op_instance:OP_INSTANCE"; hsmget ',
          'r_string_rose' : None
}
hsmput = {'op_name'       : 'hsmput',
          'op_instance'   : 0,
          's_string'      : r'[\s?|^]hsmput(?:\s+|$)',
          'r_string'      : 'export PAPIEX_TAGS="op:hsmput;op_instance:OP_INSTANCE"; hsmput ',
          'r_string_w_if' : '{ export PAPIEX_TAGS="op:hsmput;op_instance:OP_INSTANCE"; hsmput ',
          'r_string_rose' : None
}
gcp = {'op_name'       : 'gcp',
       'op_instance'   : 0,
       's_string'      : r'[\s?|^]gcp(?:\s+|$)',
       'r_string'      : 'export PAPIEX_TAGS="op:gcp;op_instance:OP_INSTANCE"; gcp ',
       'r_string_w_if' : '{ export PAPIEX_TAGS="op:gcp;op_instance:OP_INSTANCE"; gcp ',
       'r_string_rose' : None
}

### typical data movement operations
cp = {'op_name'       : 'cp',
      'op_instance'   : 0,
      's_string'      : r'[\s?|^]cp(?:\s+|$)',
      'r_string'      : 'export PAPIEX_TAGS="op:cp;op_instance:OP_INSTANCE"; cp ',
      'r_string_w_if' : '{ export PAPIEX_TAGS="op:cp;op_instance:OP_INSTANCE"; cp ',
      'r_string_rose' : None
}
mv = {'op_name'       : 'mv',
      'op_instance'   : 0,
      's_string'      : r'[\s?|^]mv(?:\s+|$)',
      'r_string'      : 'export PAPIEX_TAGS="op:mv;op_instance:OP_INSTANCE"; mv ',
      'r_string_w_if' : '{ export PAPIEX_TAGS="op:mv;op_instance:OP_INSTANCE"; mv ',
      'r_string_rose' : None
}
rm = {'op_name'       : 'rm',
      'op_instance'   : 0,
      's_string'      : r'[\s?|^]rm(?:\s+|$)',
      'r_string'      : 'export PAPIEX_TAGS="op:rm;op_instance:OP_INSTANCE"; rm ',
      'r_string_w_if' : '{ export PAPIEX_TAGS="op:rm;op_instance:OP_INSTANCE"; rm ',
      'r_string_rose' : None
}
tar = {'op_name'       : 'tar',
       'op_instance'   : 0,
       's_string'      : r'[\s?|^]tar(?:\s+|$)',
       'r_string'      : 'export PAPIEX_TAGS="op:tar;op_instance:OP_INSTANCE"; tar ',
       'r_string_w_if' : '{ export PAPIEX_TAGS="op:tar;op_instance:OP_INSTANCE"; tar ',
       'r_string_rose' : None
}


### legacy calls
## from FRE-bronx
fregrid = {'op_name'      : 'fregrid',
          'op_instance'  : 0,
          's_string'     : r'[\s?|^]regrid-xy(?:\s+|$)',
          'r_string'     : None,
          'r_string_w_if': None,
          'r_string_rose': 'export PAPIEX_TAGS="op:fregrid;op_instance:OP_INSTANCE"; ',
}
plevel = {'op_name'      : 'plevel',
          'op_instance'  : 0,
          's_string'     : r'[\s?|^]mask-atmos-plevel(?:\s+|$)',
          'r_string'     : None,
          'r_string_w_if': None,
          'r_string_rose': 'export PAPIEX_TAGS="op:plevel;op_instance:OP_INSTANCE"; ',
}

## from app/
timavg = {'op_name'       : 'timavg',
          'op_instance'   : 0,
          's_string'      : r'[\s?|^]make-timeavgs(?:\s+|$)',
          'r_string'      : None,
          'r_string_w_if' : None,
          'r_string_rose' : 'export PAPIEX_TAGS="op:timavg;op_instance:OP_INSTANCE"; '
}
timser = {'op_name'       : 'timser',
          'op_instance'   : 0,
          's_string'      : r'[\s?|^]make-timeseries(?:\s+|$)',
          'r_string'      : None,
          'r_string_w_if' : None,
          'r_string_rose' : 'export PAPIEX_TAGS="op:timser;op_instance:OP_INSTANCE"; '
}



### fre calls
## fre analysis
## fre app
regrid = {'op_name'      : 'regrid',
          'op_instance'  : 0,
          's_string'     : r'[\s?|^]fre -vv app regrid (?:\s+|$)',
          'r_string'     : None,
          'r_string_w_if': None,
          'r_string_rose': 'export PAPIEX_TAGS="op:regrid;op_instance:OP_INSTANCE"; ',
}
maskatm = {'op_name'      : 'maskatm',
          'op_instance'  : 0,
          's_string'     : r'[\s?|^]fre -vv app mask-atmos-plevel(?:\s+|$)',
          'r_string'     : None,
          'r_string_w_if': None,
          'r_string_rose': 'export PAPIEX_TAGS="op:plevel;op_instance:OP_INSTANCE"; ',
}
## fre catalog
## fre cmor
## fre list
## fre make
## fre pp
## fre run
## fre yamltools

# list of all op dictionaries shown above
op_list = [
### specialized data movement operations
    dmget,
    dmput,
    hsmget,
    hsmput,
    gcp,
### typical data movement operations
    cp,
    mv,
    rm,
    tar,
### legacy calls
## from FRE-bronx
#    fregrid,
#    plevel,
#    list_ncvars, # add TODO
## from app/
#    combtimavgs, # add TODO
#    combstatics, # add TODO
    timavg, # doublecheck TODO
    timser, # doublecheck TODO
### fre calls
## fre analysis
## fre app
#    regrid, # add TODO
#    maskatm, # add TODO
#    remap, # add TODO
## fre catalog
#    catalog, # add TODO
## fre cmor
## fre list
## fre make
## fre pp
#    histval, # add TODO
#    splitncwrap, # add TODO
#    renamesplit2pp, # add TODO
## fre run
## fre yamltools
]

# for metadata annotations.
jtag_dict = {'exp_name' : 'set name =',
             'exp_component' : '#INFO:component=',
             'exp_time' : 'set oname =',
             'exp_platform' : 'set platform =',
             'exp_target' : 'set target =',
             'exp_seg_months' : 'set segment_months ='}

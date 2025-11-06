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
         'op_tag'        : 'dmget',
         'op_instance'   : 0,
         'r_string'      : 'export PAPIEX_TAGS="op:dmget;op_instance:OP_INSTANCE"; dmget ',
         'r_string_w_if' : '{ export PAPIEX_TAGS="op:dmget;op_instance:OP_INSTANCE"; dmget ',
         'r_string_rose' : None,
}
dmput = {'op_name'       : 'dmput',
         'op_tag'        : 'dmput',
         'op_instance'   : 0,
         'r_string'      : 'export PAPIEX_TAGS="op:dmput;op_instance:OP_INSTANCE"; dmput ',
         'r_string_w_if' : '{ export PAPIEX_TAGS="op:dmput;op_instance:OP_INSTANCE"; dmput ',
         'r_string_rose' : None,
}
hsmget = {'op_name'       : 'hsmget',
          'op_tag'        : 'hsmget',
          'op_instance'   : 0,
          'r_string'      : 'export PAPIEX_TAGS="op:hsmget;op_instance:OP_INSTANCE"; hsmget ',
          'r_string_w_if' : '{ export PAPIEX_TAGS="op:hsmget;op_instance:OP_INSTANCE"; hsmget ',
          'r_string_rose' : None,
}
hsmput = {'op_name'       : 'hsmput',
          'op_tag'        : 'hsmput',
          'op_instance'   : 0,
          'r_string'      : 'export PAPIEX_TAGS="op:hsmput;op_instance:OP_INSTANCE"; hsmput ',
          'r_string_w_if' : '{ export PAPIEX_TAGS="op:hsmput;op_instance:OP_INSTANCE"; hsmput ',
          'r_string_rose' : None,
}
gcp = {'op_name'       : 'gcp',
       'op_tag'        : 'gcp',
       'op_instance'   : 0,
       'r_string'      : 'export PAPIEX_TAGS="op:gcp;op_instance:OP_INSTANCE"; gcp ',
       'r_string_w_if' : '{ export PAPIEX_TAGS="op:gcp;op_instance:OP_INSTANCE"; gcp ',
       'r_string_rose' : None,
}

### typical data movement operations
cp = {'op_name'       : 'cp',
      'op_tag'        : 'cp',
      'op_instance'   : 0,
      'r_string'      : 'export PAPIEX_TAGS="op:cp;op_instance:OP_INSTANCE"; cp ',
      'r_string_w_if' : '{ export PAPIEX_TAGS="op:cp;op_instance:OP_INSTANCE"; cp ',
      'r_string_rose' : None,
}
mv = {'op_name'       : 'mv',
      'op_tag'        : 'mv',
      'op_instance'   : 0,
      'r_string'      : 'export PAPIEX_TAGS="op:mv;op_instance:OP_INSTANCE"; mv ',
      'r_string_w_if' : '{ export PAPIEX_TAGS="op:mv;op_instance:OP_INSTANCE"; mv ',
      'r_string_rose' : None,
}
rm = {'op_name'       : 'rm',
      'op_tag'        : 'rm',
      'op_instance'   : 0,
      'r_string'      : 'export PAPIEX_TAGS="op:rm;op_instance:OP_INSTANCE"; rm ',
      'r_string_w_if' : '{ export PAPIEX_TAGS="op:rm;op_instance:OP_INSTANCE"; rm ',
      'r_string_rose' : None,
}
tar = {'op_name'       : 'tar',
       'op_tag'        : 'tar',
       'op_instance'   : 0,
       'r_string'      : 'export PAPIEX_TAGS="op:tar;op_instance:OP_INSTANCE"; tar ',
       'r_string_w_if' : '{ export PAPIEX_TAGS="op:tar;op_instance:OP_INSTANCE"; tar ',
       'r_string_rose' : None,
}


### from app/
timavg = {'op_name'       : 'make-timeavgs',
          'op_tag'        : 'timavg',
          'op_instance'   : 0,
          'r_string'      : None,
          'r_string_w_if' : None,
          'r_string_rose' : 'export PAPIEX_TAGS="op:timavg;op_instance:OP_INSTANCE"; '
}
timser = {'op_name'       : 'make-timeseries',
          'op_tag'        : 'timser',
          'op_instance'   : 0,
          'r_string'      : None,
          'r_string_w_if' : None,
          'r_string_rose' : 'export PAPIEX_TAGS="op:timser;op_instance:OP_INSTANCE"; '
}



### fre calls
## fre analysis
## fre app
regrid = {'op_name'      : 'fre -vv app regrid',
          'op_tag'       : 'regrid',
          'op_instance'  : 0,
          'r_string'     : 'export PAPIEX_TAGS="op:regrid;op_instance:OP_INSTANCE"; fre -vv app regrid ',
          'r_string_w_if': None,
          'r_string_rose': None,
}
maskatm = {'op_name'      : 'fre -vv app mask-atmos-plevel',
           'op_tag'       : 'maskatm',
           'op_instance'  : 0,
           'r_string'     : 'export PAPIEX_TAGS="op:maskatm;op_instance:OP_INSTANCE"; fre -vv app mask-atmos-plevel ',
           'r_string_w_if': None,
           'r_string_rose': None,
}
histval = {'op_name'      : 'fre -vv pp histval',
           'op_tag'       : 'histval',
           'op_instance'  : 0,
           'r_string'     : 'export PAPIEX_TAGS="op:histval;op_instance:OP_INSTANCE"; fre -vv pp histval ',
           'r_string_w_if': None,
           'r_string_rose': None,
}
## fre catalog
## fre cmor
## fre list
## fre make
## fre pp
## fre run
## fre yamltools

### from FRE-bronx
fregrid = {'op_name'      : 'fregrid',
           'op_tag'       : 'fregrid',
           'op_instance'  : 0,
           'r_string'     : None,
           'r_string_w_if': None,
           'r_string_rose': 'export PAPIEX_TAGS="op:fregrid;op_instance:OP_INSTANCE"; ',
}
plevel = {'op_name'      : 'mask-atmos-plevel',
          'op_tag'       : 'plevel',
          'op_instance'  : 0,
          'r_string'     : None,
          'r_string_w_if': None,
          'r_string_rose': 'export PAPIEX_TAGS="op:plevel;op_instance:OP_INSTANCE"; ',
}

# list of all op dictionaries shown above
op_list = [
## from app/
#    combtimavgs, # add TODO
#    combstatics, # add TODO
    timavg, # doublecheck TODO
    timser, # doublecheck TODO
### fre calls
## fre analysis
## fre app
    regrid, # add TODO
    maskatm, # add TODO
#    remap, # add TODO
## fre catalog
#    catalog, # add TODO
## fre cmor
## fre list
## fre make
## fre pp
    histval, # add TODO
#    splitncwrap, # add TODO
#    renamesplit2pp, # add TODO
## fre run
## fre yamltools
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
    fregrid,
    plevel,
#    list_ncvars, # add TODO
]

# for metadata annotations.
jtag_dict = {'exp_name' : 'set name =',
             'exp_component' : '#INFO:component=',
             'exp_time' : 'set oname =',
             'exp_platform' : 'set platform =',
             'exp_target' : 'set target =',
             'exp_seg_months' : 'set segment_months ='}

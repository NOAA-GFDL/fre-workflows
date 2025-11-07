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
}
dmput = {'op_name'       : 'dmput',
         'op_tag'        : 'dmput',
         'op_instance'   : 0,
}
hsmget = {'op_name'       : 'hsmget',
          'op_tag'        : 'hsmget',
          'op_instance'   : 0,
}
hsmput = {'op_name'       : 'hsmput',
          'op_tag'        : 'hsmput',
          'op_instance'   : 0,
}
gcp = {'op_name'       : 'gcp',
       'op_tag'        : 'gcp',
       'op_instance'   : 0,
}

### typical data movement operations
cp = {'op_name'       : 'cp',
      'op_tag'        : 'cp',
      'op_instance'   : 0,
}
mv = {'op_name'       : 'mv',
      'op_tag'        : 'mv',
      'op_instance'   : 0,
}
rm = {'op_name'       : 'rm',
      'op_tag'        : 'rm',
      'op_instance'   : 0,
}
tar = {'op_name'       : 'tar',
       'op_tag'        : 'tar',
       'op_instance'   : 0,
}


### from app/
combstatics = {'op_name'       : 'combine-statics',
              'op_tag'        : 'combstatics',
              'op_instance'   : 0,
}
combtimavg = {'op_name'       : 'combine-timeavgs',
              'op_tag'        : 'combtimavg',
              'op_instance'   : 0,
}
timavg = {'op_name'       : 'make-timeavgs',
          'op_tag'        : 'timavg',
          'op_instance'   : 0,
}
timser = {'op_name'       : 'make-timeseries',
          'op_tag'        : 'timser',
          'op_instance'   : 0,
}
renamesplittopp = {'op_name'       : 'rename-split-to-pp',
                   'op_tag'        : 'renamesplittopp',
                   'op_instance'   : 0,
}



### fre calls
## fre analysis
## fre app
regrid = {'op_name'      : 'fre -vv app regrid',
          'op_tag'       : 'regrid',
          'op_instance'  : 0,
}
remap = {'op_name'      : 'fre -vv app remap',
          'op_tag'       : 'remap',
          'op_instance'  : 0,
}
maskatm = {'op_name'      : 'fre -vv app mask-atmos-plevel',
           'op_tag'       : 'maskatm',
           'op_instance'  : 0,
}
histval = {'op_name'      : 'fre -vv pp histval',
           'op_tag'       : 'histval',
           'op_instance'  : 0,
}
## fre catalog
## fre cmor
## fre list
## fre make
## fre pp
splitncwrap = {'op_name'      : 'fre -vv pp split-netcdf-wrapper',
               'op_tag'       : 'splitncwrap',
               'op_instance'  : 0,
}

## fre run
## fre yamltools

### from FRE-bronx
fregrid = {'op_name'      : 'fregrid',
           'op_tag'       : 'fregrid',
           'op_instance'  : 0,
}
plevel = {'op_name'      : 'mask-atmos-plevel',
          'op_tag'       : 'plevel',
          'op_instance'  : 0,
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
    regrid,
    remap,
    maskatm,
## fre catalog
#    catalog, # add TODO
## fre cmor
## fre list
## fre make
## fre pp
    histval,
    splitncwrap,
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

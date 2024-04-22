#!/app/conda/miniconda/envs/cylc/bin/python3
'''
  remaps scalar and/or vector fields. It is capable of remapping
  from a spherical grid onto a different one, e.g. spherical,
  or tripolar. By default, it does so using a conservative scheme.
  most valid input args to fregrid are valid in this script
'''

import subprocess
import shutil
import os
from pathlib import Path

#3rd party
import metomi.rose.config as rose_cfg
from netCDF4 import Dataset

# in-house
import shared as sh


def test_import():
    '''for quickly testing import within pytest'''
    return 1

def safe_rose_config_get(config, section, field):
    '''read optional variables from rose configuration, and don't error on None value'''
    config_dict = config.get( [section,field] )
    return None if config_dict is None else config_dict.get_value()


def get_mosaic_file_name(grid_spec_file, mosaic_type):
    '''read string from a numpy masked array WHY'''
    grid_spec_nc = Dataset(grid_spec_file, 'r')
    masked_data = grid_spec_nc[mosaic_type][:].copy() # maskedArray
    grid_spec_nc.close()
    unmasked_data = masked_data[~masked_data.mask]
    file_name = ''.join([ one_char.decode() for one_char in unmasked_data ])
    return file_name


def get_mosaic_grid_file_name(input_mosaic):
    '''get mosaic grid file name from NESTED numpy masked array WHY'''
    input_mosaic_nc = Dataset(input_mosaic,'r')
    masked_data = input_mosaic_nc['gridfiles'][0].copy()
    input_mosaic_nc.close()
    unmasked_data = masked_data[~masked_data.mask]
    grid_file_name = ''.join([ one_char.decode() for one_char in unmasked_data ])
    return grid_file_name


def check_interp_method( nc_variable, interp_method):
    '''print warning if optional interp_method clashes with nc file attribute field, if present'''
    attr_list=nc_variable.ncattrs()
    if 'interp_method' not in attr_list:
        pass
    elif nc_variable.interp_method != interp_method:
        print(f'WARNING: interp_method={interp_method} differs from what is in target_file')
        print(f'WARNING: interp_method used may not be {interp_method}!')


def check_per_component_settings(component_list, rose_app_cfg):
    '''for a source file ref'd by multiple components check per-component
    settings for uniqueness. output list of bools of same length to check
    in componenet loop'''
    do_regridding = [True] #first component will always be run
    curr_out_grid_type_list = [safe_rose_config_get( \
                                               rose_app_cfg, component_list[0], 'outputGridType')]
    for i in range( 1, len(component_list) ):
        next_comp=component_list[i]
        next_out_grid_type=safe_rose_config_get( rose_app_cfg, next_comp, 'outputGridType')
        if next_out_grid_type not in curr_out_grid_type_list:
            do_regridding.append(True)
            curr_out_grid_type_list.append(next_out_grid_type)
        else:
            do_regridding.append(False)
    if len(do_regridding) != len(component_list) :
        raise Exception('problem with checking per-component settings for uniqueness')
    return do_regridding




def make_component_list(config, source):
    '''make list of relevant component names where source file appears in sources'''
    comp_list=[] #will not contain env, or command
    try:
        for keys, sub_node in config.walk():
            sources = sub_node.get_value(keys=['sources'])#.split(' ')
            if any( [ len(keys) < 1,
                      keys[0] in ['env', 'command'],
                      keys[0] in comp_list,
                      sources is None                ] ):
                continue
            sources = sources.split(' ')
            if source in sources:
                comp_list.append(keys[0])
    except Exception as exc:
        raise Exception(f'config = {config} may be an empty file... check the config') \
            from exc
    return comp_list


def make_regrid_var_list(target_file, interp_method = None):
    '''create default list of variables to be regridded within target file.'''
    fin = Dataset(target_file,'r')
    all_fin_vars = fin.variables
    regrid_vars = []
    for var_name in all_fin_vars:
        if var_name in ['average_T1','average_T2',
                        'average_DT','time_bnds' ]:
            continue
        if len(all_fin_vars[var_name].shape) < 2 :
            continue
        regrid_vars.append(var_name)
        if interp_method is not None:
            check_interp_method( all_fin_vars[var_name] , interp_method)

    fin.close()
    return regrid_vars


def regrid_xy( ):
    '''
    calls fre-nctools' fregrid to regrid net cdf files
    '''

    ## rose config load check
    config_name = os.getcwd()
    config_name += '/rose-app-run.conf'
    #config_name += '/rose-app.conf'
    print(f'config_name = {config_name}')
    try:
        rose_app_config = rose_cfg.load(config_name)
    except Exception as exc:
        raise Exception(f'config_name = {config_name} not found.') \
            from exc


    # mandatory arguments- code exits if any of these are not present
    input_dir     = os.getenv( 'inputDir'        )
    output_dir    = os.getenv( 'outputDir'       )
    begin         = os.getenv( 'begin'           )
    tmp_dir       = os.getenv( 'TMPDIR'          )
    remap_dir     = os.getenv( 'fregridRemapDir' )
    source        = os.getenv( 'source'          )
    grid_spec     = os.getenv( 'gridSpec'        )
    def_xy_interp = os.getenv( 'defaultxyInterp' )
    if None in [ input_dir , output_dir    ,
                 begin     , tmp_dir       ,
                 remap_dir , source        ,
                 grid_spec , def_xy_interp  ]:
        raise Exception(f'a mandatory input argument is not present in {config_name})')
    #    if any( [ input_dir is None, output_dir    is None,
    #              begin     is None, tmp_dir       is None,
    #              remap_dir is None, source        is None,
    #              grid_spec is None, def_xy_interp is None ] ):
    #        raise Exception(f'a mandatory input argument is not present in {config_name}')

    def_xy_interp    = def_xy_interp.split(',')
    def_xy_interp[0] = def_xy_interp[0].replace('"', '')
    def_xy_interp[1] = def_xy_interp[1].replace('"', '')
    print( f'input_dir         = { input_dir        }\n' + \
           f'output_dir        = { output_dir       }\n' + \
           f'begin             = { begin            }\n' + \
           f'tmp_dir           = { tmp_dir          }\n' + \
           f'remap_dir         = { remap_dir        }\n' + \
           f'source            = { source           }\n' + \
           f'grid_spec         = { grid_spec        }\n' + \
           f'def_xy_interp     = { def_xy_interp    }\n' + \
           f'def_xy_interp[0]  = { def_xy_interp[0] }\n' + \
           f'def_xy_interp[1]  = { def_xy_interp[1] }'       )
    if any( [  def_xy_interp == [] or len(def_xy_interp) != 2  ] ):
        raise Exception(
            f'default xy interpolation has invalid format: \n def_xy_interp = {def_xy_interp}')

    # input dir must exist
    if not Path( input_dir ).exists():
        raise Exception(f'input_dir={input_dir} \n does not exist')

    # tmp_dir check
    if not Path( tmp_dir ).exists():
        raise Exception(f'tmp_dir={tmp_dir} \n does not exist.')

    # output dir check
    Path( output_dir ).mkdir( parents = True, exist_ok = True )
    if not Path( output_dir ).exists() :
        raise Exception('the following does not exist and/or could not be created:' +
                        f'output_dir=\n{output_dir}')

    # work/ dir check
    work_dir = tmp_dir + 'work/'
    Path( work_dir ).mkdir( exist_ok = True )
    if not Path( work_dir ).exists():
        raise Exception('the following does not exist and/or could not be created:' +
                        f'work_dir=\n{work_dir}')


    # fregrid remap dir check
    if not Path( remap_dir ).exists():
        try:
            Path( remap_dir ).mkdir( )
        except Exception as exc:
            raise Exception(f'{remap_dir} could not be created') \
                from exc


    # grid_spec file management
    starting_dir = os.getcwd()
    os.chdir(work_dir)
    if '.tar' in grid_spec:
        untar_sp = \
            subprocess.run( ['tar', '-xvf', grid_spec], check = False )
        if untar_sp.returncode != 0:
            raise Exception(f'untarring of grid_spec={grid_spec} file did not succeed')
        if Path( 'mosaic.nc' ).exists():
            grid_spec_file='mosaic.nc'
        elif Path( 'grid_spec.nc' ).exists():
            grid_spec_file='grid_spec.nc'
        else:
            raise Exception(f'grid_spec_file cannot be determined from grid_spec={grid_spec}')
    else:
        try:
            grid_spec_file=grid_spec.split('/').pop()
            shutil.copy(grid_spec, grid_spec_file )
        except Exception as exc:
            raise Exception(f'grid_spec={grid_spec} could not be copied.') \
                from exc

    # ------------------------------------------------------------------ component loop
    component_list = make_component_list(rose_app_config, source)
    if len(component_list) == 0:
        raise Exception('component list empty- source file not found in any source file list!')
    if len(component_list) > 1: # check settings for uniqueness
        do_regridding = \
            check_per_component_settings( \
                                          component_list, rose_app_config)
        print(f'component_list = {component_list}')
        print(f'do_regridding  = {do_regridding}')
    else:
        do_regridding=[True]

    for component in component_list:
        if not do_regridding[
                component_list.index(component) ]:
            continue
        print(f'\n\nregridding \nsource={source} for \ncomponent={component}\n')

        # mandatory per-component inputs, will error if nothing in rose config
        input_realm, interp_method, input_grid = None, None, None
        try:
            input_realm   = rose_app_config.get( [component, 'inputRealm'] ).get_value()
            interp_method = rose_app_config.get( [component, 'interpMethod'] ).get_value()
            input_grid    = rose_app_config.get( [component, 'inputGrid'] ).get_value()
        except Exception as exc:
            raise Exception('at least one of the following are None: ' + \
                            f'input_grid=\n{input_grid}\n,input_realm=' + \
                            f'\n{input_realm}\n,/interp_method=\n{interp_method}') \
                            from exc
        print(f'input_grid    = {input_grid    }' + \
              f'input_realm   = {input_realm   }' + \
              f'interp_method = {interp_method }'     )

        #target input variable resolution
        is_tiled = 'cubedsphere' in input_grid
        target_file  = input_dir
        target_file += f"/{sh.truncate_date(begin,'P1D')}.{source}.tile1.nc" \
            if is_tiled \
            else  f"/{sh.truncate_date(begin,'P1D')}.{source}.nc"
        if not Path( target_file ).exists():
            raise Exception(f'regrid_xy target does not exist. \ntarget_file={target_file}')
        print(f'target_file={target_file}') #DELETE


        # optional per-component inputs
        output_grid_type = safe_rose_config_get( rose_app_config, component, 'outputGridType')
        remap_file       = safe_rose_config_get( rose_app_config, component, 'fregridRemapFile')
        more_options     = safe_rose_config_get( rose_app_config, component, 'fregridMoreOptions')
        regrid_vars      = safe_rose_config_get( rose_app_config, component, 'variables')
        output_grid_lon  = safe_rose_config_get( rose_app_config, component, 'outputGridLon')
        output_grid_lat  = safe_rose_config_get( rose_app_config, component, 'outputGridLat')
        if output_grid_lon is None:
            output_grid_lon = def_xy_interp(0)
        if output_grid_lat is None:
            output_grid_lat = def_xy_interp(1)

        print( f'output_grid_type = {output_grid_type }' + \
               f'remap_file       = {remap_file       }' + \
               f'more_options     = {more_options     }' + \
               f'output_grid_lon  = {output_grid_lon  }' + \
               f'output_grid_lat  = {output_grid_lat  }' + \
               f'regrid_vars      = {regrid_vars      }'     )



        # prepare to create input_mosaic via ncks call
        if input_realm in ['atmos', 'aerosol']:
            mosaic_type = 'atm_mosaic_file'
        elif input_realm == 'ocean':
            mosaic_type = 'ocn_mosaic_file'
        elif input_realm == 'land':
            mosaic_type = 'lnd_mosaic_file'
        else:
            raise Exception(f'input_realm={input_realm} not recognized.')

        # this is just to get the grid_file name
        input_mosaic = get_mosaic_file_name(grid_spec_file, mosaic_type)
        print(f'input_mosaic = {input_mosaic}') #DELETE

        ## this is to get the tile1 filename?
        mosaic_grid_file = get_mosaic_grid_file_name(input_mosaic)
        print(f'mosaic_grid_file = {mosaic_grid_file}') #DELETE

        # need source file dimenions for lat/lon
        source_nx = str(int(Dataset(mosaic_grid_file).dimensions['nx'].size / 2 ))
        source_ny = str(int(Dataset(mosaic_grid_file).dimensions['ny'].size / 2 ))
        print(f'source_[nx,ny] = ({source_nx},{source_ny})')
        Dataset(mosaic_grid_file).close()


        if remap_file is not None:
            try:
                shutil.copy( remap_file,
                             remap_file.split('/').pop() )
            except Exception as exc:
                raise Exception('remap_file={remap_file} could not be copied to local dir') \
                    from exc
        else:
            print('remap_file was not specified nor found. looking for default one')
            remap_file= f'fregrid_remap_file_{output_grid_lon}_by_{output_grid_lat}.nc' \
                                if \
                                   all( [output_grid_lon is not None,
                                         output_grid_lat is not None]) \
                                else \
                                   f'fregrid_remap_file_{def_xy_interp(0)}_by_{def_xy_interp(1)}.nc'
            remap_cache_file = \
                f'{remap_dir}/{input_grid}/{input_realm}/' + \
                f'{source_nx}-by-{source_ny}/{interp_method}/{remap_file}'
            central_remap_cache_file = \
                f'/home/fms/shared_remap_files/{input_grid}/' + \
                f'{source_nx}_by_{source_ny}/{remap_file}'

            print(f'remap_file               = {remap_file              }' + \
                  f'remap_cache_file         = {remap_cache_file        }' + \
                  f'central_remap_cache_file = {central_remap_cache_file}' )

            if Path( remap_cache_file ).exists():
                print(f'NOTE: using cached remap file {remap_cache_file}')
                shutil.copy(remap_cache_file,
                            remap_cache_file.split('/').pop())
            elif Path( central_remap_cache_file ).exists():
                print(f'NOTE: using centrally cached remap file {remap_cache_file}')
                shutil.copy(central_remap_cache_file,
                            central_remap_cache_file.split('/').pop())



        # if no variables in config, find the interesting ones to regrid
        if regrid_vars is None:
            regrid_vars=make_regrid_var_list( target_file , interp_method)
        print(f'regrid_vars = {regrid_vars}') #DELETE

        #check if there's anything worth regridding
        if len(regrid_vars) < 1:
            raise Exception('make_regrid_var_list found no vars to regrid. and no vars given. exit')
        print(f'regridding {len(regrid_vars)} variables: {regrid_vars}')
        regrid_vars_str=','.join(regrid_vars) # fregrid needs comma-demarcated list of vars



        # massage input file argument to fregrid.
        input_file = target_file.replace('.tile1.nc','') \
                             if '.tile1' in target_file \
                             else target_file
        input_file=input_file.split('/').pop()

        # create output file argument...
        output_file = target_file.replace('.tile1','') \
                      if 'tile1' in target_file \
                      else target_file
        output_file = output_file.split('/').pop()

        fregrid_command = [
            'fregrid',
            '--debug',
            '--standard_dimension',
            '--input_mosaic', f'{input_mosaic}',
            '--input_dir', f'{input_dir}',
            '--input_file', f'{input_file}',
            '--associated_file_dir', f'{input_dir}',
            '--interp_method', f'{interp_method}',
            '--remap_file', f'{remap_file}',
            '--nlon', f'{str(output_grid_lon)}',
            '--nlat', f'{str(output_grid_lat)}',
            '--scalar_field', f'{regrid_vars_str}',
            '--output_file', f'{output_file}']
        if more_options is not None:
            fregrid_command.append(f'{more_options}')

        print(f"\n\nabout to run the following command: \n{' '.join(fregrid_command)}\n")
        fregrid_proc = subprocess.run( fregrid_command, check = False )#i hate it
        fregrid_rc =fregrid_proc.returncode
        print(f'fregrid_result.returncode()={fregrid_rc}')


        # output wrangling

        # copy the remap file to the cache location
        if not Path( remap_cache_file ).exists():
            remap_cache_file_dir='/'.join(remap_cache_file.split('/')[0:-1])
            Path( remap_cache_file_dir ).mkdir( parents = True , exist_ok = True)
            print(f'copying \nremap_file={remap_file} to')
            print(f'remap_cache_file_dir={remap_cache_file_dir}')
            shutil.copy(remap_file, remap_cache_file_dir)

        # more output wrangling
        final_output_dir = output_dir \
            if output_grid_type is None \
            else output_dir + '/' + output_grid_type
        Path( final_output_dir ).mkdir( exist_ok = True)

        print(f'TRYING TO COPY {output_file} TO {final_output_dir}')
        shutil.copy(output_file, final_output_dir)

        continue # end of comp loop, exit or next one.

    os.chdir(starting_dir) # not clear this is necessary.
    print('done running regrid_xy()')
    return 0


def main():
    '''steering, local test/debug'''
    return regrid_xy()

if __name__=='__main__':
    main()

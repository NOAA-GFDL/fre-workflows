from pathlib import Path
import pytest
import subprocess

DATA_DIR_IN  = Path("/archive/oar.gfdl.fre_test/canopy_test_data/app/regrid-xy")
DATA_FILE_GRID = Path("C96_mosaic.cdl")
DATA_FILE_NC_GRID = Path("C96_mosaic.nc")
GOLD_GRID_SPEC = Path("/archive/gold/datasets/OM4_05/mosaic_c96.v20180227.tar")
GLOBAL_TEST_DIR = Path("/home/Ian.Laflotte/Working/postprocessing_regridxy_pyrewrite/app/regrid-xy/t/test_inputs_outputs")
DATA_DIR_OUT  = Path("out-test-dir")

"""
The purpose of the code is to recreate a *.nc file(s) based on the timesteps within that file which it could be days,
months or years.  It is a pytest collection of routines.  all test_* routines will be called in the order defined.
First is to test and check for the creation of required directories and a *.nc file from *.cdl text file. FRE Canopy
app regrid_xy tests by successfully regridding and remapping files with rose app as the valid definitions are being
called by the environment.

Usage on runnung this app test for regrid_xy is as follows:
0) cd /path/to/postprocessing/
1) module load fre/bronx-20 cylc python
2) cd app/regrid_xy
3) python -m pytest t/test_regrid_xy.py

To rerun when using GLOBAL_TEST_DIR, remove created output:
4) rm -rf t/test_inputs_outputs/* && python -m pytest t/test_regrid-xy.py
"""


def test_make_ncgen3_inputs(capfd):
        '''set-up test: ncgen3 inputs for later steps'''
        global d, dt
        d = GLOBAL_TEST_DIR / '20030101.nc'
        d.mkdir()
        d = str(d)
        dt = str(DATA_DIR_IN)

        ex = [ 'ncgen3', '-k', 'netCDF-4 classic model', '-o', str(d / DATA_FILE_NC_GRID), str(DATA_DIR_IN / DATA_FILE_GRID) ];
        print (' '.join(ex));
        sp = subprocess.run( ex )
        assert sp.returncode == 0  
        out, err = capfd.readouterr()


def test_make_ncgen_tile_inputs(capfd):
        '''set-up test: ncgen tile inputs for later steps'''
        for i in range(1, 6+1):
          i = str(i)
          ex = [ 'ncgen', '-o', f'{d}/20030101.atmos_static_cmip.tile{i}.nc', f'{dt}/20030101.atmos_static_cmip.tile{i}.cdl' ];
          print (' '.join(ex));
          sp = subprocess.run( ex )
          assert sp.returncode == 0
          out, err = capfd.readouterr()
          
        for i in range(1, 6+1):
          i = str(i)
          ex = [ 'ncgen', '-o', f'{d}/20030101.grid_spec.tile{i}.nc', f'{dt}/20030101.grid_spec.tile{i}.cdl' ];
          print (' '.join(ex));
          sp = subprocess.run( ex )
          assert sp.returncode == 0
          out, err = capfd.readouterr()
                  

def test_make_hgrid_gold_input(capfd):
        '''set-up test: hgrid gold inputs for later steps'''
        
        # this "gold" C96 file seems to have been made with fre/bronx-4 according to the netcdf header...
        # remaking locally.. then will move..
        ex = [ "make_hgrid", "--grid_type", "gnomonic_ed", "--nlon", "192", "--grid_name", "C96_grid" ]
        print (' '.join(ex))
        sp = subprocess.run( ex )
        assert sp.returncode == 0
        out, err = capfd.readouterr()
                        
        # now move the files...
        for i in range(1, 6+1):
          i = str(i)
          ex = [ 'mv', '-f', f'./C96_grid.tile{i}.nc', f'{d}/C96_grid.tile{i}.nc' ]
          print (' '.join(ex))
          sp = subprocess.run( ex )
          assert sp.returncode == 0
          out, err = capfd.readouterr()

          
def test_makehgrid_input(capfd):
        """
        Subroutine input arguments is tmp_path which is a randomly generated temporary directory of type pathlib.Path
        The capfd argument that allows to capture access to stdout/stderr output created during test execution.
        Regridding the file is executed via the proper fregrid and python libraries.
        """ 
        global dir_tmp, remap_dir_out, file_output_dir
        global outputFile, fregridRemapFile 

        dir_tmp = GLOBAL_TEST_DIR / '20030101.nc'

        input_mosaic = str(dir_tmp)
        input_dir = str(dir_tmp)

        remap_dir_out = GLOBAL_TEST_DIR / 'remap-test-dir'
        file_output_dir = GLOBAL_TEST_DIR / 'out-test-dir'

        #output_dir = GLOBAL_TEST_DIR / str(DATA_DIR_OUT)
        output_dir = GLOBAL_TEST_DIR / DATA_DIR_OUT
        output_dir.mkdir()
        output_dir = str(output_dir)

        remap_dir = GLOBAL_TEST_DIR / 'remap-test-dir' 
        remap_dir.mkdir()
        remap_dir = str(remap_dir)

        nlat=180
        nlon=288
        #vars = 'grid_xt,grid_yt,orog,time'
        vars = 'grid_xt,grid_yt,orog'
        fregrid_input_file = '20030101.atmos_static_cmip'
        outputFile = '20030101.atmos_static_cmip.nc'
        fregridRemapFile = 'fregrid_remap_file_288_by_180.nc' 
        
        input_mosaic_file = str(DATA_FILE_NC_GRID)

        ex = [ 'fregrid', '--standard_dimension',
               '--input_mosaic', f'{input_mosaic}/{input_mosaic_file}',
               '--input_dir', f'{input_dir}',
               '--input_file', f'{fregrid_input_file}',
               '--associated_file_dir', f'{input_dir}',
               '--remap_file', f'{remap_dir}/{fregridRemapFile}', 
              '--nlon', f'{nlon}',
               '--nlat', f'{nlat}',
               '--scalar_field', f'{vars}',
               '--output_file', f'{output_dir}/{outputFile}' ];
        print (' '.join(ex))
        sp = subprocess.run( ex )        
        assert sp.returncode == 0
        out, err = capfd.readouterr()


def test_failure_wrong_DT_regrid_xy(capfd):
    """
    In this test app checks for failure  of regridding files with rose app             
    as the invalid date definition is being called by the environment.
    """
    global inputGrid, inputRealm, interpMethod
    inputGrid = 'cubedsphere'
    inputRealm = 'atmos'
    interpMethod = 'conserve_order1'

    global fake_tmp_dir, dout
    fake_tmp_dir = GLOBAL_TEST_DIR
    fake_tmp_dir = str(fake_tmp_dir)

    din = str(dir_tmp)

    dout = GLOBAL_TEST_DIR / 'out-dir'
    dout.mkdir()
    dout = str(dout)

    dremap = GLOBAL_TEST_DIR / 'remap-dir'
    dremap.mkdir()
    dremap = str(dremap)

    ex = [ 'rose', 'app-run',
           '-D', f'[env]inputDir={din}',
           '-D',  '[env]begin=99999999T999999',
           '-D', f'[env]outputDir={dout}',
           '-D', f'[env]fregridRemapDir={dremap}',
           '-D',  '[env]component=atmos_static_cmip',
           '-D', f'[env]gridSpec={GOLD_GRID_SPEC}',
           '-D', f'[env]TMPDIR={fake_tmp_dir}',
           '-D',  '[env]defaultxyInterp="288,180"',
           '-D',  '[atmos_static_cmip]sources=atmos_static_cmip',
           '-D',  f'[atmos_static_cmip]inputGrid={inputGrid}',
           '-D',  f'[atmos_static_cmip]inputRealm={inputRealm}',
           '-D',  f'[atmos_static_cmip]interpMethod={interpMethod}',
           '-D',  '[atmos_static_cmip]outputGridLon=288',
           '-D',  '[atmos_static_cmip]outputGridLat=180'
          ];

    print (' '.join(ex));
    sp = subprocess.run( ex )
    assert sp.returncode != 0 #assert sp.returncode == 2 # specific code for cylc cycle-point CLI utility
    out, err = capfd.readouterr()

def test_success_regrid_xy(capfd):
    """
    In this test app checks for success of regridding files with rose app 
    as the valid definitions are being called by the environment.
    """

    global dr_remap_out, dr_file_output
    dr_file_output = GLOBAL_TEST_DIR / 'out-dir'
    dr_remap_out = GLOBAL_TEST_DIR / 'remap-dir'

    dr_remap = GLOBAL_TEST_DIR / 'remap-dir'
    dr_remap = str(dr_remap)

    din = str(dir_tmp)

    ex = [ 'rose', 'app-run',
           '-D', f'[env]inputDir={din}',
           '-D',  '[env]begin=20030101T000000',
           '-D', f'[env]outputDir={dout}',
           '-D', f'[env]fregridRemapDir={dr_remap}',
           '-D',  '[env]component=atmos_static_cmip',
           '-D', f'[env]gridSpec={GOLD_GRID_SPEC}',
           '-D', f'[env]TMPDIR={fake_tmp_dir}',
           '-D',  '[env]defaultxyInterp="288,180"',
           '-D',  '[atmos_static_cmip]sources=atmos_static_cmip',
           '-D',  '[atmos_static_cmip]inputGrid=cubedsphere',
           '-D',  '[atmos_static_cmip]inputRealm=atmos',
           '-D',  '[atmos_static_cmip]interpMethod=conserve_order1',           
           '-D',  '[atmos_static_cmip]outputGridLon=288',
           '-D',  '[atmos_static_cmip]outputGridLat=180'
          ]
    print (' '.join(ex));
    sp = subprocess.run( ex )
    assert sp.returncode == 0
#    assert False
    out, err = capfd.readouterr()


def test_nccmp1_regrid_xy(capfd):
    """
    This test compares the output of make_hgrid and fregrid, which are expected to be identical
    """
    sources_xy = '96-by-96'

    nccmp= [ 'nccmp', '-m', '--force', str(dr_remap_out / inputGrid / inputRealm / sources_xy / interpMethod / fregridRemapFile), str(remap_dir_out / fregridRemapFile) ];
    print (' '.join(nccmp));
    sp = subprocess.run(nccmp)
    assert sp.returncode == 0
    out, err = capfd.readouterr()

    
def test_nccmp2_regrid_xy(capfd):
    """
    This test compares the regridded source file output(s), which are expected to be identical
    """

    nccmp= [ 'nccmp', '-m', '--force', str(dr_file_output / outputFile), str(file_output_dir / outputFile) ];
    print (' '.join(nccmp));
    sp = subprocess.run(nccmp)
    assert sp.returncode == 0
    out, err = capfd.readouterr()



from pathlib import Path
import pytest
import subprocess

DATA_DIR  = Path("/archive/oar.gfdl.fre_test/canopy_test_data/app/regrid-xy")
DATA_DIR_OUT  = Path("out-test-dir")
DATA_FILE_GRID = Path("C96_mosaic.cdl")
DATA_FILE_NC_GRID = Path("C96_mosaic.nc")

"""The purpose of the code is to recreate a *.nc file(s) based on the timesteps within that file which it could be days, months or years.  It is a pytest collection of routines.  all test_* routines will be called in the order defined.  First is to test and check for the creation of required directories and a *.nc file from *.cdl text file.  
FRE Canopy app regrid_xy tests by successfully regridding and remapping files with rose app as the valid definitions are being called by the environment.
"""

"""Usage on runnung this app test for regrid_xy is as follows: 
1) module load fre/test cylc cdo python/3.9
2) cd regrid_xy 
3) pytest t/test_regrid_xy.py
"""

def test_regrid_xy(capfd, tmp_path):
        """Subroutine input arguments is tmp_path which is a randomly generated temporary directory of type pathlib.Path
        The capfd argument that allows to capture access to stdout/stderr output created during test execution.
        Regridding the file is executed via the proper fregrid and python libraries.
        """ 
        global dir_tmp, remap_dir_out, file_output_dir
        global outputFile, fregridRemapFile 

        dir_tmp = tmp_path / '20030101.nc'
        d = tmp_path / '20030101.nc'
        d.mkdir()
        d = str(d)
        dt = str(DATA_DIR)
        input_mosaic = str(dir_tmp)
        input_dir = str(dir_tmp)

        remap_dir_out = tmp_path / 'remap-test-dir'
        file_output_dir = tmp_path / 'out-test-dir'

        output_dir = tmp_path / str(DATA_DIR_OUT)
        output_dir.mkdir()
        output_dir = str(output_dir)

        remap_dir = tmp_path / 'remap-test-dir' 
        remap_dir.mkdir()
        remap_dir = str(remap_dir)

        nlat=180
        nlon=288
        vars = 'grid_xt,grid_yt,orog,time'
        fregrid_input_file = '20030101.atmos_static_cmip'
        outputFile = '20030101.atmos_static_cmip.nc'
        fregridRemapFile = 'fregrid_remap_file_288_by_180.nc' 
        
        ex = [ 'ncgen3', '-k', 'netCDF-4 classic model', '-o', d / DATA_FILE_NC_GRID, DATA_DIR / DATA_FILE_GRID ];
        print (ex);
        sp = subprocess.run( ex )
        assert sp.returncode == 0  

        input_mosaic_file = str(DATA_FILE_NC_GRID)

        for i in range(1, 6+1):
          i = str(i)
          ex = [ 'ncgen', '-o', f'{d}/20030101.atmos_static_cmip.tile{i}.nc', f'{dt}/20030101.atmos_static_cmip.tile{i}.cdl' ];
          print (ex);
          sp = subprocess.run( ex )
        for i in range(1, 6+1):
          i = str(i)
          ex = [ 'ncgen', '-o', f'{d}/20030101.grid_spec.tile{i}.nc', f'{dt}/20030101.grid_spec.tile{i}.cdl' ];
          print (ex);
          sp = subprocess.run( ex )
        for i in range(1, 6+1):
          i = str(i)
          ex = [ 'ncgen', '-o', f'{d}/C96_grid.tile{i}.nc', f'{dt}/C96_grid.tile{i}.cdl' ];
          print (ex);
          sp = subprocess.run( ex )

        ex = [ 'fregrid', '--standard_dimension', '--input_mosaic', f'{input_mosaic}/{input_mosaic_file}', '--input_dir', f'{input_dir}', '--input_file', f'{fregrid_input_file}', '--associated_file_dir', f'{input_dir}', '--remap_file', f'{remap_dir}/{fregridRemapFile}', '--nlon', f'{nlon}', '--nlat', f'{nlat}', '--scalar_field', f'{vars}','--output_file', f'{output_dir}/{outputFile}' ];
        sp = subprocess.run( ex )
        assert sp.returncode == 0

@pytest.mark.skip(reason='currently passing when should be failing')
def test_failure_regrid_xy(capfd, tmp_path):
    """In this test app checks for failure  of regridding files with rose app             
    as the invalid date definition is being called by the environment.
    """
    din = str(dir_tmp)
    dout = tmp_path / 'out-dir'
    dout.mkdir()
    dout = str(dout)
    dremap = tmp_path / 'remap-dir'
    dremap.mkdir()
    dremap = str(dremap)
    ex = [ "rose", "app-run",
           '-D',  '[env]inputDir='f'{din}',
           '-D',  '[env]begin=20220101T120000',
           '-D',  '[env]outputDir='f'{dout}',
           '-D',  '[env]fregridRemapDir='f'{dremap}',
           '-D',  '[env]component=atmos_static_cmip',
           '-D',  '[atmos_static_cmip]sources=atmos_static_cmip',
           '-D',  '[atmos_static_cmip]inputGrid=cubedsphere',
           '-D',  '[atmos_static_cmip]inputRealm=atmos',
           '-D',  '[atmos_static_cmip]outputGridLon=288',
           '-D',  '[atmos_static_cmip]outputGridLat=180',
           '-D',  '[atmos_static_cmip]gridSpec=/archive/gold/datasets/OM4_05/mosaic_c96.v20180227.tar'
          ]
    print (ex);
    sp = subprocess.run( ex )
    assert sp.returncode == 1 
    captured = capfd.readouterr()

def test_success_regrid_xy(capfd, tmp_path):
    """In this test app checks for success of regridding files with rose app 
    as the valid definitions are being called by the environment.
    """
    din = str(dir_tmp)
    global dr_remap_out, dr_file_output
    dr_file_output = tmp_path / 'out-dir'
    dr_remap_out = tmp_path / 'remap-dir'
    dout = tmp_path / 'out-dir'
    dout.mkdir()
    dout = str(dout)
    dr_remap = tmp_path / 'remap-dir'
    dr_remap.mkdir()
    dr_remap = str(dr_remap)
    ex = [ 'rose', 'app-run',
           '-D',  '[env]inputDir='f'{din}',
           '-D',  '[env]begin=20030101T000000',
           '-D',  '[env]outputDir='f'{dout}',
           '-D',  '[env]fregridRemapDir='f'{dr_remap}',
           '-D',  '[env]component=atmos_static_cmip',
           '-D',  '[atmos_static_cmip]sources=atmos_static_cmip',
           '-D',  '[atmos_static_cmip]inputGrid=cubedsphere',
           '-D',  '[atmos_static_cmip]inputRealm=atmos',
           '-D',  '[atmos_static_cmip]outputGridLon=288',
           '-D',  '[atmos_static_cmip]outputGridLat=180',
           '-D',  '[atmos_static_cmip]gridSpec=/archive/gold/datasets/OM4_05/mosaic_c96.v20180227.tar'
          ]
    print (ex);
    sp = subprocess.run( ex )
    assert sp.returncode == 0
    captured = capfd.readouterr()

@pytest.mark.skip(reason='TBD')
def test_nccmp_regrid_xy(capfd, tmp_path):
    """This test compares the results of both above success tests making sure that the two new created regrid files are the same.
    """
    inputGrid = 'cubedsphere'
    inputRealm = 'atmos'
    sources_xy = '96-by-96'

    nccmp= [ 'nccmp', '-m', '--force', dr_remap_out / inputGrid / inputRealm / sources_xy / fregridRemapFile, remap_dir_out / fregridRemapFile ];
    sp = subprocess.run(nccmp)
    assert sp.returncode == 0
    captured = capfd.readouterr()

    nccmp= [ 'nccmp', '-m', '--force', dr_file_output / outputFile, file_output_dir / outputFile ];
    sp = subprocess.run(nccmp)
    assert sp.returncode == 0
    captured = capfd.readouterr()

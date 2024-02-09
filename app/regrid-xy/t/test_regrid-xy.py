from pathlib import Path
import pytest
import subprocess

"""
The purpose of the code is to recreate a *.nc file(s) based on the timesteps within that file which it could be days,
months or years.  It is a pytest collection of routines.  all test_* routines will be called in the order defined.
First is to test and check for the creation of required directories and a *.nc file from *.cdl text file. FRE Canopy
app regrid_xy tests by successfully regridding and remapping files with rose app as the valid definitions are being
called by the environment.

Usage on runnung this app test for regrid_xy is as follows:
1) module load fre/test cylc cdo python/3.9
2) cd regrid_xy
3) pytest t/test_regrid_xy.py
"""

DATA_DIR  = Path("/archive/oar.gfdl.fre_test/canopy_test_data/app/regrid-xy")
DATA_DIR_OUT  = Path("out-test-dir")
DATA_FILE_GRID = Path("C96_mosaic.cdl")
DATA_FILE_NC_GRID = Path("C96_mosaic.nc")
GOLD_GRID_SPEC = Path("/archive/gold/datasets/OM4_05/mosaic_c96.v20180227.tar")


def test_define_globals(capfd, tmp_path):
        """
        to deal with file I/O
        """
        
        global dir_tmp
        dir_tmp = tmp_path / '20030101.nc'
        dir_tmp.mkdir()

        global d
        d = str(dir_tmp)

        global outputFile, fregridRemapFile
        outputFile = '20030101.atmos_static_cmip.nc'
        fregridRemapFile = 'fregrid_remap_file_288_by_180.nc'

        global remap_dir_out
        remap_dir_out = tmp_path / 'remap-test-dir'        

        assert True

# needed to remake the C96 grid file with make_hgrid
#@pytest.mark.skip(reason='works. convenience skip.')
def test_regrid_xy(capfd, tmp_path):
        """
        Subroutine input arguments is tmp_path which is a randomly generated temporary directory of type
        pathlib.Path. The capfd argument that allows to capture access to stdout/stderr output created during
        test execution. Regridding the file is executed via the proper fregrid and python libraries.
        """
        
        d = str(dir_tmp)
        
        #global  remap_dir_out, file_output_dir
        #global outputFile, fregridRemapFile
        

        #dir_tmp = tmp_path / '20030101.nc'
        #input_dir = str(dir_tmp)
        #
        #remap_dir_out = tmp_path / 'remap-test-dir'
        #file_output_dir = tmp_path / 'out-test-dir'

        #print('skipping bulk of first test')
        #assert True

        
        targ1_ncgen3 = str( dir_tmp / DATA_FILE_NC_GRID )
        targ2_ncgen3 = str( DATA_DIR / DATA_FILE_GRID )
        ex = [ 'ncgen3', '-k', 'netCDF-4 classic model', '-o', targ1_ncgen3, targ2_ncgen3 ];
        print (ex);
        sp = subprocess.run( ex )
        assert sp.returncode == 0

        # ncgen atmos_static_cmip tile files
        for i in range(1, 6+1):
          i = str(i)
          targ1_ncgen = str( dir_tmp )  + f'/20030101.atmos_static_cmip.tile{i}.nc'
          targ2_ncgen = str( DATA_DIR ) + f'/20030101.atmos_static_cmip.tile{i}.cdl'
          ex = [ 'ncgen', '-o', targ1_ncgen, targ2_ncgen ];
          print( ' '.join( ex ) )
          sp = subprocess.run( ex )
          assert sp.returncode ==0

        # ncgen grid_spec tile files
        for i in range(1, 6+1):
          i = str(i)
          targ1_ncgen = str( dir_tmp )  + f'/20030101.grid_spec.tile{i}.nc'
          targ2_ncgen = str( DATA_DIR ) + f'/20030101.grid_spec.tile{i}.cdl'
          ex = [ 'ncgen', '-o', targ1_ncgen, targ2_ncgen ];
          print(' '.join( ex ) )
          sp = subprocess.run( ex )
          assert sp.returncode ==0
          
        # make_hgrid, C96_grid
        # this "gold" C96 file seems to have been made with fre/bronx-4 according to the netcdf header...
        # remaking locally.. then will move..
        ex = [ "make_hgrid", "--grid_type", "gnomonic_ed", "--nlon", "192", "--grid_name", "C96_grid" ]
        print(' '.join(ex))
        sp = subprocess.run( ex )
        assert sp.returncode == 0
        
        # move hgrids made with C96_grid
        for i in range(1, 6+1):
          i = str(i)
          targ1_mv = f'./C96_grid.tile{i}.nc'
          targ2_mv = f'{d}/C96_grid.tile{i}.nc'
          ex = [ 'mv', '-f', targ1_mv, targ2_mv ]; 
          print(' '.join(ex))
          sp = subprocess.run( ex )
          assert sp.returncode == 0

        output_dir = tmp_path / str(DATA_DIR_OUT)
        output_dir.mkdir()
        output_dir = str(output_dir)
        
        remap_dir = tmp_path / 'remap-test-dir'
        remap_dir.mkdir()
        remap_dir = str(remap_dir)
        
        input_mosaic = d
        input_mosaic_file = str(DATA_FILE_NC_GRID)

        fregrid_input_file = '20030101.atmos_static_cmip'

        nlat=180
        nlon=288
        targ_vars = 'grid_xt,grid_yt,orog,time'


        ex = [ 'fregrid', '--standard_dimension', '--input_mosaic', f'{input_mosaic}/{input_mosaic_file}',
               '--input_dir', f'{d}', '--input_file', f'{fregrid_input_file}', '--associated_file_dir',
               f'{d}', '--remap_file', f'{remap_dir}/{fregridRemapFile}', '--nlon', f'{nlon}', '--nlat',
               f'{nlat}', '--scalar_field', f'{targ_vars}','--output_file', f'{output_dir}/{outputFile}' ];        
        for fregrid_arg in ex:
                print(f'{fregrid_arg}')
                
        sp = subprocess.run( ex )
        assert sp.returncode == 0




@pytest.mark.skip(reason='not failling appropriately.')
def test_failure_regrid_xy(capfd, tmp_path):
    """
    In this test app checks for failure  of regridding files with rose app
    as the invalid date definition is being called by the environment.
    """
    input_dir = str(dir_tmp)

    output_dir = tmp_path / 'out-dir'
    output_dir.mkdir()
    output_dir = str(output_dir)

    dir_remap = tmp_path / 'remap-dir'
    dir_remap.mkdir()
    dir_remap = str(dremap)

    ex = [ "rose", "app-run", "-v", "--debug",
           '-D',  f'[env]inputDir={input_dir}',
           '-D',  f'[env]outputDir={output_dir}',
           '-D',   '[env]begin=20220101T120000',
           '-D',  f'[env]fregridRemapDir={dir_emap}',
           '-D',   '[env]component=atmos_static_cmip',
           '-D',  f'[env]gridSpec={GOLD_GRID_SPEC}',
           '-D',   '[env]defaultxyInterp="288,180"',           
           '-D',   '[atmos_static_cmip]sources=atmos_static_cmip',
           '-D',   '[atmos_static_cmip]inputGrid=cubedsphere',
           '-D',   '[atmos_static_cmip]inputRealm=atmos',
           '-D',   '[atmos_static_cmip]outputGridLon=288',
           '-D',   '[atmos_static_cmip]outputGridLat=180' ]

    print (' '.join(ex));
    sp = subprocess.run( ex )
    assert sp.returncode != 0
    captured = capfd.readouterr()


# if the prev test didn't run, this test will not succeed.
#@pytest.mark.skip(reason='works, convenience skip.')
def test_success_regrid_xy(capfd, tmp_path):
    """In this test app checks for success of regridding files with rose app
    as the valid definitions are being called by the environment.
    """
    
    #global dr_remap_out, dr_file_output
    #dr_file_output = tmp_path / 'out-dir'
    #dr_remap_out = tmp_path / 'remap-dir'

    input_dir = str(dir_tmp)
    
    output_dir = tmp_path / 'out-dir'
    output_dir.mkdir()
    output_dir = str(output_dir)
    
    dir_remap = tmp_path / 'remap-dir'
    dir_remap.mkdir()
    dir_remap = str(dir_remap)
    
    ex = [ 'rose', 'app-run', '--debug', '-v', '--profile',
           '-D', f'[env]inputDir={input_dir}',
           '-D', f'[env]outputDir={output_dir}',
           '-D',  '[env]begin=20030101T000000',
           '-D', f'[env]fregridRemapDir={dir_remap}',
           '-D',  '[env]component=atmos_static_cmip',
           '-D', f'[env]gridSpec="{GOLD_GRID_SPEC}"',
           '-D',  '[env]defaultxyInterp="288,180"',
           '-D',  '[atmos_static_cmip]sources=atmos_static_cmip',
           '-D',  '[atmos_static_cmip]inputGrid=cubedsphere',
           '-D',  '[atmos_static_cmip]inputRealm=atmos',
           '-D',  '[atmos_static_cmip]outputGridLon=288',
           '-D',  '[atmos_static_cmip]outputGridLat=180' ]
    print (' '.join(ex));
    sp = subprocess.run( ex )
    assert sp.returncode == 0
    captured = capfd.readouterr()


#TODO: why's it TBD...
#@pytest.mark.skip(reason='file paths seeem wrong... one min.')
def test_nccmp_regrid_xy(capfd, tmp_path):
    """
    This test compares the results of both above success tests making sure that the two new created regrid files are the same.
    """
    
    dir_remap = tmp_path / 'remap-dir'
    dir_remap.mkdir()

    inputGrid = 'cubedsphere'
    inputRealm = 'atmos'
    sources_xy = '96-by-96'


    # first comparison
    # not being found...
    assert dir_remap.exists()
    assert ( dir_remap / inputGrid ).mkdir()
    assert ( dir_remap / inputGrid ).exists()
    assert ( dir_remap / inputGrid / inputRealm ).exists()
    assert ( dir_remap / inputGrid / inputRealm / sources_xy ).exists()
    assert ( dir_remap / inputGrid / inputRealm / fregridRemapFile ).exists()
    targ1_nccmp = str( dir_remap / inputGrid / inputRealm / sources_xy / fregridRemapFile )
    print (f'targ1_nccmp={targ1_nccmp}')
    print('')

    # i hate this.
    # i hate the directories and the paths in this test file.
    # how does anyone live like this honestly. 
    dir_remap.mkdir()
    dir_remap = str(dir_remap)

    remap_test_dir = tmp_path / 'remap-test-dir'

    targ2_nccmp = str( remap_dir_out / fregridRemapFile )
    print (f'targ2_nccmp={targ2_nccmp}')
    print('')

    # forcefully compare metadata
    nccmp = [ 'nccmp', '-b', '--debug', '-m', '--force', targ1_nccmp, targ2_nccmp ];
    print (' '.join(nccmp));

    sp = subprocess.run(nccmp)
    captured = capfd.readouterr()
    for capt in captured:
            print(capt)
            #print(captured)
    assert sp.returncode == 0



    # second comparison
    #targ1_nccmp = str(dr_file_output / outputFile)
    #print (f'targ1_nccmp={targ1_nccmp}')
    #print('')
    #
    #targ2_nccmp = str(file_output_dir / outputFile)
    #print (f'targ2_nccmp={targ2_nccmp}')
    #print('')
    #
    #nccmp = [ 'nccmp', '-m', '--force', targ1_nccmp, targ2_nccmp ];
    #print (' '.join(nccmp));
    #print ('')
    #
    #sp = subprocess.run(nccmp)
    #captured = capfd.readouterr()
    #print(captured)
    #assert sp.returncode == 0

    

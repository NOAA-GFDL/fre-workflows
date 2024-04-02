from pathlib import Path
import pytest
import subprocess, os

DATA_DIR  = Path("test-data")
DATA_FILE_BK = Path("atmos_tracer.bk.cdl")
DATA_FILE_BK_NC = Path("atmos_tracer.bk.nc")

def test_remap_pp_components(capfd, tmp_path):
        """Following this test check for the creation of required directories and a *.nc file from *.cdl text file
        using command ncgen -o
        Test checks for success of remapping a file based on a default outputDRS 
        """
        global dir_tmp, compout, dir_tmp_out, remapped_new_file
        dir_tmp_out = tmp_path / "out_dir"
 
        dir_tmp = tmp_path  
        compout='atmos_tracer'

        din_check = f'{tmp_path}/regrid-xy/{compout}/P0Y/P0Y'
        os.makedirs( din_check, exist_ok = True )
        
        var = str(DATA_FILE_BK)[13:15]
 
        ex = [ "ncgen", "-o", din_check / DATA_FILE_BK_NC, DATA_DIR / DATA_FILE_BK ];
        print (ex);
        sp = subprocess.run( ex )
        assert sp.returncode == 0
        captured = capfd.readouterr()

        remapped_new_file = f'{compout}.{var}.nc'

        dout = tmp_path / "out_dir"
        dout.mkdir()

        newfileln=[ "ln",  din_check / DATA_FILE_BK_NC, dout / remapped_new_file ];
        sp = subprocess.run(newfileln)

def test_rose_remap_pp_components(capfd, tmp_path):
    """In this test app checks for success of remapping a file with rose app
    as the valid definitions are being called by the environment.
    """
    din = str(dir_tmp)
    global dr_in, dr_out
    dr_in = dir_tmp_out
    dr_out = tmp_path / "out_dir"
    dout = tmp_path / "out_dir"
    dout.mkdir()
    dout = str(dout)
    ex = [ "rose", "app-run",
           '-D',  '[env]inputDir='f'{din}',
           '-D',  '[env]begin=00010101T0000Z',
           '-D',  '[env]outputDir='f'{dout}',
           '-D',  '[env]currentChunk=P0Y',
           '-D',  '[env]outputDRS=default',
           '-D',  '[env]component=atmos_tracer',
           '-D',  '[atmos_tracer]chunk=P0Y',
           '-D',  '[atmos_tracer]freq=P0Y',
           '-D',  '[atmos_tracer]grid=regrid-xy',
           '-D',  '[atmos_tracer]source=atmos_tracer'
          ]
    print (ex);
    sp = subprocess.run( ex )
    assert sp.returncode == 0
    captured = capfd.readouterr()

def test_nccmp_remap_pp_components(capfd, tmp_path):
    """This test compares the results of both above tests making sure that the two new created remapped files are identical.
    """
    freq = 'P0Y'
    chunk = 'P0Y'

    nccmp= [ "nccmp", "-d", dr_out / compout / freq / chunk / remapped_new_file, dr_in / remapped_new_file ];
    sp = subprocess.run(nccmp)
    assert sp.returncode == 0
    captured = capfd.readouterr()

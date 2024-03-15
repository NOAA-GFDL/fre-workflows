from pathlib import Path
import pytest
import subprocess, os
import shutil

DATA_DIR  = Path("test-data")
DATA_FILE_BK = Path("atmos_tracer.bk.cdl")
DATA_FILE_BK_NC = Path("atmos_tracer.bk.nc")
tmp_path = "/home/Dana.Singh/pp/refactor/remap-python/app/remap-pp-components/tpath_output/"
os.environ["product"]="ts"
os.environ["dirTSWorkaround"]="1"
os.environ["COPY_TOOL"]="gcp"

def test_ncgen_remap_pp_components(capfd):
        """Following this test check for the creation of required directories and a *.nc file from *.cdl text file
        using command ncgen -o
        Test checks for success of remapping a file based on a default outputDRS 
        """
        global dir_tmp, compout, dir_tmp_out, remapped_new_file
        dir_tmp_out = tmp_path + "out_dir"
        print(f"TMPPATH: {dir_tmp_out}") 
        dir_tmp = tmp_path  
        compout='atmos_tracer'

        din_check = f'{tmp_path}/remap-pp-components/{compout}/P0Y/P0Y'
        os.makedirs( din_check, exist_ok = True )
        
        var = str(DATA_FILE_BK)[13:15]
 
        ex = [ "ncgen", "-o", Path(din_check) / DATA_FILE_BK_NC, DATA_DIR / DATA_FILE_BK ];
        print (ex);
        sp = subprocess.run( ex )
        assert sp.returncode == 0
        out, err = capfd.readouterr()

        remapped_new_file = f'{compout}.{var}.nc'

        dout = tmp_path + "out_dir"

        if os.path.exists(dout): 
            shutil.rmtree(dout)
            os.mkdir(dout)
        else:
            os.mkdir(dout)

        newfileln=[ "ln",  Path(din_check) / DATA_FILE_BK_NC, Path(dout) / remapped_new_file ];
        sp = subprocess.run(newfileln)
        assert sp.returncode == 0
        out, err = capfd.readouterr()

def test_rose_remap_pp_components(capfd):
    """In this test app checks for success of remapping a file with rose app
    as the valid definitions are being called by the environment.
    """
    dir_tmp = tmp_path
    dir_tmp_out = tmp_path + "out_dir" 
    din = str(dir_tmp)
    global dr_in, dr_out
    dr_in = dir_tmp_out
    dr_out = tmp_path + "out_dir"
    dout = tmp_path + "out_dir"
   
    if os.path.exists(dout):
        shutil.rmtree(dout)
        os.mkdir(dout)
    else:
        os.mkdir(dout)
#    dout = str(dout)

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
    out, err = capfd.readouterr()

'''
def test_nccmp_remap_pp_components(capfd):#, tmp_path):
    """This test compares the results of both above tests making sure that the two new created remapped files are identical.
    """
    freq = 'P0Y'
    chunk = 'P0Y'

    nccmp= [ "nccmp", "-d", Path(dr_out) / compout / freq / chunk / remapped_new_file, Path(dr_in) / remapped_new_file ];
    sp = subprocess.run(nccmp)
    assert sp.returncode == 0
    captured = capfd.readouterr()
'''

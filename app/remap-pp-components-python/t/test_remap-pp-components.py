from pathlib import Path
import pytest
import subprocess, os
import shutil

DATA_DIR  = Path("test-data")
#DATA_FILE_BK = Path("atmos_tracer.bk.cdl")
#DATA_FILE_BK_NC = Path("atmos_tracer.bk.nc")

DATA_FILE_OROG = Path("atmos_diurnal.orog.cdl")
DATA_FILE_OROG_NC = Path("atmos_diurnal.orog.nc")


tmp_path = "/home/Dana.Singh/pp/refactor/REMAP/app/remap-pp-components-python/tpath_output/"
#tmp_path = "./tpath_output/"
os.environ["product"]="ts"
os.environ["dirTSWorkaround"]=""
os.environ["COPY_TOOL"]="gcp"
#os.environ["ens_mem"]="01"

if os.path.exists(tmp_path):
  shutil.rmtree(tmp_path)
  os.mkdir(tmp_path)
else:
  os.mkdir(tmp_path)

def test_ncgen_remap_pp_components(capfd):
        """Following this test check for the creation of required directories and a *.nc file from *.cdl text file
        using command ncgen -o
        Test checks for success of remapping a file based on a default outputDRS 
        """
        global compout, ncgen_dir_tmp_out, remapped_new_file, din_check
        ncgen_dir_tmp_out = tmp_path + "out_dir" + "/ncgen-remap"
        
        print(f"TMPPATH: {ncgen_dir_tmp_out}") 
        #compout='atmos_tracer'
        compout = "atmos_diurnal" 

        din_check = f'{tmp_path}/ncgen-remap-pp-components/{compout}/P0Y/P0Y'
        os.makedirs( din_check, exist_ok = True )
        
        #var = str(DATA_FILE_BK)[13:15]
        var = str(DATA_FILE_OROG)[14:18] 

        # ncgen -o [outputfile] [inputfile]
        ex = [ "ncgen", "-k", "64-bit offset" , "-o", Path(din_check) / DATA_FILE_OROG_NC, DATA_DIR / DATA_FILE_OROG ];
        print (ex);
        sp = subprocess.run( ex )
        assert sp.returncode == 0
        out, err = capfd.readouterr()

        remapped_new_file = f'{compout}.{var}.nc'

        if os.path.exists(ncgen_dir_tmp_out): 
            shutil.rmtree(ncgen_dir_tmp_out)
            os.makedirs(ncgen_dir_tmp_out)
        else:
            os.makedirs(ncgen_dir_tmp_out)

        newfileln=[ "ln",  Path(din_check) / DATA_FILE_OROG_NC, Path(ncgen_dir_tmp_out) / remapped_new_file ];
        sp = subprocess.run(newfileln)
        assert sp.returncode == 0
        out, err = capfd.readouterr()

def test_rose_remap_pp_components(capfd):
    """In this test app checks for success of remapping a file with rose app
    as the valid definitions are being called by the environment.
    """
   
    global rose_dir_tmp_out
    rose_dir_tmp_out = tmp_path + "out_dir" + "/rose-remap" 
    din = str(tmp_path)

    #Define/make previous locations
    regrid_path = tmp_path + "/regrid-xy"
    comp_path = regrid_path + "/atmos_diurnal"
    freq_path = comp_path + "/P0Y"
    chunk_path = freq_path + "/P0Y"

    paths = [rose_dir_tmp_out, regrid_path, comp_path, freq_path, chunk_path] 

    for p in paths:
      if os.path.exists(p):
        shutil.rmtree(p)
        os.makedirs(p)
      else:
        os.makedirs(p)  
  
    # DO I NEED TO DO THIS? FIGURE OUT IF THE STEP BEFORE REMAP PUT A TILE FILE IN WHATEVER DIR THAT THIS IS GOING TO BE GOING IN .... or is a nc file cretaed?
    #rename test cdl bk.file to tile.nc file...?
    #shutil.copyfile(DATA_DIR/DATA_FILE_BK, chunk_path/DATA_FILE_BK_NC)
    shutil.copyfile(DATA_DIR/DATA_FILE_OROG_NC, chunk_path/DATA_FILE_OROG_NC)

    #Rose functionality
#    ex = [ "rose", "app-run",
#           '-D',  '[env]inputDir='f'{din}',
#           '-D',  '[env]begin=00010101T0000Z',
#           '-D',  '[env]outputDir='f'{rose_dir_tmp_out}',
#           '-D',  '[env]currentChunk=P0Y',
##           '-D',  '[env]outputDRS=default',
#           '-D',  '[env]component=atmos_tracer',
#           '-D',  '[atmos_tracer]chunk=P0Y',
#           '-D',  '[atmos_tracer]freq=P0Y',
#           '-D',  '[atmos_tracer]grid=regrid-xy',
#           '-D',  '[atmos_tracer]sources=atmos_tracer'
#          ]

    ex = [ "rose", "app-run",
           '-D',  '[env]inputDir='f'{din}',
           '-D',  '[env]begin=00010101T0000Z',
           '-D',  '[env]outputDir='f'{rose_dir_tmp_out}',
           '-D',  '[env]currentChunk=P0Y',
#           '-D',  '[env]outputDRS=default',
           '-D',  '[env]component=atmos_diurnal',
           '-D',  '[atmos_diurnal]chunk=P0Y',
           '-D',  '[atmos_diurnal]freq=P0Y',
           '-D',  '[atmos_diurnal]grid=regrid-xy',
           '-D',  '[atmos_diurnal]sources=atmos_diurnal' 
         ]

    print (ex);
    sp = subprocess.run( ex )

    assert sp.returncode == 0
    out, err = capfd.readouterr()


def test_nccmp_remap_pp_components(capfd):
    """This test compares the results of both above tests making sure that the two new created remapped files are identical.
    """
    freq = 'P0Y'
    chunk = 'P0Y'

#    print( Path(din_check) / remapped_new_file) 
#    print( Path(dir_tmp_out) / compout / freq / chunk / DATA_FILE_TILE_NC)
#    nccmp= [ "nccmp", "-d", Path(dir_tmp_out) / compout / freq / chunk / remapped_new_file, Path(dir_tmp_out) / remapped_new_file ];
    nccmp = [ "nccmp", "-d", Path(ncgen_dir_tmp_out) / remapped_new_file, Path(rose_dir_tmp_out) / compout / freq / chunk / remapped_new_file ];

    sp = subprocess.run(nccmp)    
    assert sp.returncode == 0


from pathlib import Path
import pytest
import subprocess, os
import shutil


# Define paths and environment variables
#Path to test data
path = os.getcwd()
DATA_DIR  = Path(f"{path}/test-data")
# CDL file to generate nc file from ncgen
DATA_FILE_CDL = Path("atmos_scalar.198001-198412.co2mass.cdl")
# NC file to test remap functionality  
DATA_FILE_NC = Path("atmos_scalar.198001-198412.co2mass.nc")


#test_outDir = Path("/home/Dana.Singh/pp/refactor/REMAP/app/remap-pp-components-python/test_outDir")
test_outDir = Path(f"{path}/test_outDir")
os.environ["product"]="ts"
os.environ["dirTSWorkaround"]=""
os.environ["COPY_TOOL"]="cp"
os.environ["ens_mem"]=""
#os.environ["ens_mem"]="01"

if os.path.exists(test_outDir):
  shutil.rmtree(test_outDir)
  os.mkdir(test_outDir)
else:
  os.mkdir(test_outDir)


def test_ncgen_remap_pp_components(capfd):
        """Following this test check for the creation of required directories and a *.nc file from *.cdl text file
        using command ncgen -o
        Test checks for success of remapping a file based on a default outputDRS 
        """
        global compout, ncgen_dir_tmp_out, remapped_new_file, din_check
        ncgen_dir_tmp_out = test_outDir / "ncgen-remap"
       
        # Check if path exists or create path
        if os.path.exists(ncgen_dir_tmp_out): 
            shutil.rmtree(ncgen_dir_tmp_out)
            os.makedirs(ncgen_dir_tmp_out)
        else:
            os.makedirs(ncgen_dir_tmp_out)
        print(f"TMPPATH: {ncgen_dir_tmp_out}")

        # Define component 
        compout = "atmos_scalar" 

        # Define output location; create if it does not exist
        din_check = f'{ncgen_dir_tmp_out}/ncgen-remap-pp-components/{compout}/P1M/P5Y'
        os.makedirs( din_check, exist_ok = True )
        
        # Define variable 
        var = str(DATA_FILE_CDL)[27:34] 
 
        # NCGEN command: ncgen -o [outputfile] [inputfile]
        ex = [ "ncgen", "-k", "64-bit offset", "-o", Path(din_check) / "atmos_scalar.198001-198412.co2mass.nc", DATA_DIR / DATA_FILE_CDL ];
        print (ex);

        # Run ncgen command
        sp = subprocess.run( ex )
 
        # Error checking 
        assert sp.returncode == 0
        out, err = capfd.readouterr()

        # Define name of new remapped file 
        remapped_new_file = f'{compout}.{var}.nc'

        # Soft link remapped file 
        newfileln=[ "ln",  Path(din_check) / "atmos_scalar.198001-198412.co2mass.nc", Path(ncgen_dir_tmp_out) / remapped_new_file ];
        sp = subprocess.run(newfileln)
        assert sp.returncode == 0
        out, err = capfd.readouterr()

def test_original_remap_pp_components(capfd):
    """In this test, app checks for success of remapping a file with rose app
    as the valid definitions are being called by the environment.
    """
    #FIX THIS
    script = Path("/home/Dana.Singh/pp/refactor/REMAP/app/remap-pp-components")

    global orig_dir_tmp_out
    # Define output location
    orig_dir_tmp_out = test_outDir / "orig-rose-remap"

    #Define/create necessary locations
    grid_path = orig_dir_tmp_out / "native"
    comp_path = grid_path / "atmos_scalar"
    freq_path = comp_path / "P1M"
    chunk_path = freq_path / "P1Y"

    paths = [orig_dir_tmp_out, grid_path, comp_path, freq_path, chunk_path] 

    for p in paths:
      if os.path.exists(p):
        shutil.rmtree(p)
        os.makedirs(p, exist_ok=True)
      else:
        os.makedirs(p, exist_ok=True)  
 
    # Input/test data
    shutil.copyfile(DATA_DIR/DATA_FILE_NC, chunk_path/"atmos_scalar.198001-198412.co2mass.nc")

    # Rose functionality
    # Create a test rose-app configuration
    ex = [ "rose", "app-run",
           '-D',  '[env]inputDir='f'{orig_dir_tmp_out}',
           '-D',  '[env]begin=00010101T0000Z',
           '-D',  '[env]outputDir='f'{orig_dir_tmp_out}',
           '-D',  '[env]currentChunk=P5Y',
           '-D',  '[env]component=atmos_scalar',
           '-D',  '[atmos_scalar]chunk=P1Y',
           '-D',  '[atmos_scalar]freq=P1M',
           '-D',  '[atmos_scalar]grid=native',
           '-D',  '[atmos_scalar]sources=atmos_scalar',
           '-C',  script 
         ]

    print (ex);

    # Run the remap-pp-components script using the rose-app configuration
    sp = subprocess.run( ex )

    # Error checking 
    assert sp.returncode == 0
    out, err = capfd.readouterr()

def test_rewrite_remap_pp_components(capfd):
    """In this test app checks for success of remapping a file with rose app using the rewritten remap-pp-components script as the valid definitions are being called by the environment.
    """
    script = Path(path)

    global rewrite_dir_tmp_out
    rewrite_dir_tmp_out = test_outDir / "rewrite-rose-remap"

    #Define/make previous locations
    grid_path = rewrite_dir_tmp_out / "native"
    comp_path = grid_path / "atmos_scalar"
    freq_path = comp_path / "P1M"
    chunk_path = freq_path / "P1Y"

    paths = [rewrite_dir_tmp_out, grid_path, comp_path, freq_path, chunk_path]

    for p in paths:
      if os.path.exists(p):
        shutil.rmtree(p)
        os.makedirs(p, exist_ok=True)
      else:
        os.makedirs(p, exist_ok=True)

    # Inputdir/test data
    shutil.copyfile(DATA_DIR/DATA_FILE_NC, chunk_path/"atmos_scalar.198001-198412.co2mass.nc")

    # Create a test rose-app configuration ... Do I need this again?
    ex = [ "rose", "app-run",
           '-D',  '[env]inputDir='f'{rewrite_dir_tmp_out}',
           '-D',  '[env]begin=00010101T0000Z',
           '-D',  '[env]outputDir='f'{rewrite_dir_tmp_out}',
           '-D',  '[env]currentChunk=P5Y',
           '-D',  '[env]component=atmos_scalar',
           '-D',  '[atmos_scalar]chunk=P1Y',
           '-D',  '[atmos_scalar]freq=P1M',
           '-D',  '[atmos_scalar]grid=native',
           '-D',  '[atmos_scalar]sources=atmos_scalar',
           '-C',  script
         ]

    print (ex);
    
    # Run the rewritten remap-pp-components script using the rose-app configuration
    sp = subprocess.run( ex )

    # Error checking
    assert sp.returncode == 0
    out, err = capfd.readouterr()

##TO-DO: FAILURE TESTS
'''
def test_nccmp_remap_pp_components(capfd):
    """This test compares the results of both above tests making sure that the two new created remapped files are identical.
    """
    grid = "native"
    freq = "P1M"
    chunk = "P5Y"

    #print( Path(ncgen_dir_tmp_out) / remapped_new_file) 
    #print( Path(orig_dir_tmp_out) / grid / compout / freq / chunk / "atmos_scalar.198001-198412.co2mass.nc")
    nccmp = [ "nccmp", "-d", Path(ncgen_dir_tmp_out) / remapped_new_file, Path(orig_dir_tmp_out) / grid / compout / freq / chunk / "atmos_scalar.198001-198412.co2mass.nc" ];

    sp = subprocess.run(nccmp)    
    assert sp.returncode == 0
'''

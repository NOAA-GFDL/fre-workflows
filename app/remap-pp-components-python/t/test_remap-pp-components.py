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
# Output directory
test_outDir = Path(f"{path}/test-outDir")

#If output directory exists, remove and create again
if os.path.exists(test_outDir):
  shutil.rmtree(test_outDir)
  os.mkdir(test_outDir)
else:
  os.mkdir(test_outDir)


def test_ncgen_remap_pp_components(capfd):
        """Following this test, check for the creation of required 
           directories and a *.nc file from *.cdl text file using 
           command ncgen. Test checks for success of ncgen command.
        """
        global compout, ncgen_dir_tmp_out, var, remapped_new_file, din_check
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

def test_ncgen_output(capfd):
        """Check for the creation of required directories and 
           a *.nc generated from ncgen command in 
           ncgen_remap_pp_components test.
        """
        global remapped_new_file, newfileln
        # Define name of new remapped file 
        remapped_new_file = f'{compout}.{var}.nc'

        # Soft link remapped file 
        newfileln=[ "ln",  Path(din_check) / "atmos_scalar.198001-198412.co2mass.nc", Path(ncgen_dir_tmp_out) / remapped_new_file ];
        sp = subprocess.run(newfileln)

        # Error checking
        assert sp.returncode == 0
        out, err = capfd.readouterr()

def test_original_remap_pp_components(capfd):
    """In this test, app checks for success of remapping a file with rose app
    as the valid definitions are being called by the environment with the original 
    remap-pp-components script.
    """
    # Go to original remap script directory
    os.chdir("../remap-pp-components")
    script = Path(os.getcwd())

    global orig_dir_tmp_out
    # Define output location
    orig_dir_tmp_in = test_outDir / "orig-rose-remap-input"
    orig_dir_tmp_out = test_outDir / "orig-rose-remap-output"

    #Define/create necessary locations
    grid_path = orig_dir_tmp_in / "native"
    comp_path = grid_path / "atmos_scalar"
    freq_path = comp_path / "P1M"
    chunk_path = freq_path / "P5Y"

    paths = [orig_dir_tmp_in, orig_dir_tmp_out, grid_path, comp_path, freq_path, chunk_path] 

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
           '-D',  '[env]inputDir='f'{orig_dir_tmp_in}',
           '-D',  '[env]outputDir='f'{orig_dir_tmp_out}',
           '-D',  '[env]currentChunk=P5Y',
           '-D',  '[env]component=atmos_scalar',
           '-D',  '[env]components=atmos_scalar',
           '-D',  '[env]begin=19800101T0000Z',
           '-D',  '[env]product=ts',
           '-D',  '[env]dirTSWorkaround=1',
           '-D',  '[env]ens_mem=',
           '-D',  '[env]COPY_TOOL=cp',
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
    """In this test app checks for success of remapping a file with rose app 
       using the rewritten remap-pp-components script as the valid definitions 
       are being called by the environment.
    """
    script = Path(path)

    global rewrite_dir_tmp_out
    rewrite_dir_tmp_in = test_outDir / "rewrite-rose-remap-input"
    rewrite_dir_tmp_out = test_outDir / "rewrite-rose-remap-output"

    #Define/make previous locations
    grid_path = rewrite_dir_tmp_in / "native"
    comp_path = grid_path / "atmos_scalar"
    freq_path = comp_path / "P1M"
    chunk_path = freq_path / "P5Y"

    paths = [rewrite_dir_tmp_in, rewrite_dir_tmp_out, grid_path, comp_path, freq_path, chunk_path]

    for p in paths:
      if os.path.exists(p):
        shutil.rmtree(p)
        os.makedirs(p, exist_ok=True)
      else:
        os.makedirs(p, exist_ok=True)

    # Inputdir/test data
    shutil.copyfile(DATA_DIR/DATA_FILE_NC, chunk_path/"atmos_scalar.198001-198412.co2mass.nc")

    # Create a test rose-app configuration
    ex = [ "rose", "app-run",
           '-D',  '[env]inputDir='f'{rewrite_dir_tmp_in}',
           '-D',  '[env]outputDir='f'{rewrite_dir_tmp_out}',
           '-D',  '[env]currentChunk=P5Y',
           '-D',  '[env]components=atmos_scalar',
           '-D',  '[env]begin=19800101T0000Z',
           '-D',  '[env]product=ts',
           '-D',  '[env]dirTSWorkaround=1',
           '-D',  '[env]ens_mem=',
           '-D',  '[env]COPY_TOOL=cp',
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

def test_nccmp_ncgen_origremap(capfd):
    """This test compares the results of ncgen and orig_remap,
       making sure that the two new created remapped files are identical.
    """

    grid = "native"
    freq = "P1M"
    chunk = "P5Y"

    nccmp = [ "nccmp", "-d", Path(ncgen_dir_tmp_out) / remapped_new_file, Path(orig_dir_tmp_out) / compout / "ts" / freq / chunk / "atmos_scalar.198001-198412.co2mass.nc" ];

    sp = subprocess.run(nccmp)    
    assert sp.returncode == 0

def test_nccmp_ncgen_rewriteremap(capfd):
    """This test compares the results of ncgen and rewrite_remap,
        making sure that the two new created remapped files are identical.
    """

    grid = "native"
    freq = "P1M"
    chunk = "P5Y"

    nccmp = [ "nccmp", "-d", Path(ncgen_dir_tmp_out) / remapped_new_file, Path(orig_dir_tmp_out) / compout / "ts" / freq / chunk / "atmos_scalar.198001-198412.co2mass.nc" ];

    sp = subprocess.run(nccmp)    
    assert sp.returncode == 0

def test_nccmp_origremap_rewriteremap(capfd):
    """This test compares the results of orig_remap and rewrite_remap,
       making sure that the two new created remapped files are identical.
    """

    grid = "native"
    freq = "P1M"
    chunk = "P5Y"

    nccmp = [ "nccmp", "-d", Path(orig_dir_tmp_out) / compout / "ts" / freq / chunk / "atmos_scalar.198001-198412.co2mass.nc" , Path(rewrite_dir_tmp_out) / compout / "ts" / freq / chunk / "atmos_scalar.198001-198412.co2mass.nc" ];

    sp = subprocess.run(nccmp)    
    assert sp.returncode == 0


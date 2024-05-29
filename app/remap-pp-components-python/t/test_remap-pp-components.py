from pathlib import Path
import pytest
import subprocess, os
import shutil


# Define paths and environment variables
#Path to test data
cwd = os.getcwd()

DATA_DIR  = Path(f"{cwd}/test-data")
# CDL file to generate nc file from ncgen
DATA_FILE_CDL = Path("atmos_scalar.198001-198412.co2mass.cdl")
# NC file name to test remap functionality  
DATA_FILE_NC = Path("atmos_scalar.198001-198412.co2mass.nc")
# Output directory
test_outDir = Path(f"{cwd}/test-outDir")

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
    global compout, grid, freq, chunk, ncgen_dir_tmp_out, grid_path, chunk_path 
    ncgen_dir_tmp_out = test_outDir / "ncgen-remap"

    # Define component
    compout = "atmos_scalar"
    grid = "native"
    freq = "P1M"
    chunk = "P5Y"

    #Define/create necessary locations (location previously made in flow.cylc workflow)
    grid_path = ncgen_dir_tmp_out / grid
    comp_path = grid_path / compout
    freq_path = comp_path / freq
    chunk_path = freq_path / chunk

    paths = [ncgen_dir_tmp_out, grid_path, comp_path, freq_path, chunk_path]

    for p in paths:
        if os.path.exists(p):
            shutil.rmtree(p)
            os.makedirs(p, exist_ok=True)
        else:
            os.makedirs(p, exist_ok=True)
       
    print(f"NCGEN OUTPUT DIRECTORY: {chunk_path}")

    # NCGEN command: ncgen -o [outputfile] [inputfile]
    ex = [ "ncgen", "-k", "64-bit offset", "-o", Path(chunk_path) / DATA_FILE_NC, DATA_DIR / DATA_FILE_CDL ];
    print (ex);

    # Run ncgen command
    sp = subprocess.run( ex )
 
    # Error checking 
    assert sp.returncode == 0
    out, err = capfd.readouterr()

def test_rewrite_remap_pp_components(capfd):
    """In this test app checks for success of remapping a file with rose app 
       using the rewritten remap-pp-components script as the valid definitions 
       are being called by the environment.
    """
    # script: directory with /bin folder with remap script
    script = Path(cwd)

    global rewrite_dir_tmp_out
    #Define input and output locations
    rewrite_dir_tmp_out = test_outDir / "remap-rewrite-output"
    os.makedirs(rewrite_dir_tmp_out, exist_ok=True)

    # Create a test rose-app configuration
    ex = [ "rose", "app-run",
           '-D',  '[env]inputDir='f'{ncgen_dir_tmp_out}',
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

    print (ex)
    
    # Run the rewritten remap-pp-components script using the rose-app configuration
    sp = subprocess.run( ex )

    # Error checking
    assert sp.returncode == 0
    out, err = capfd.readouterr()

def test_rewrite_remap_with_ens(capfd):
    """Checks for success of remap script
       with ensemble members.
    """
    # script: directory with /bin folder with remap script
    script = Path(cwd)

    global rewrite_dir_tmp_out
    #Define input and output locations
    rewrite_dir_tmp_out = test_outDir / "remap-rewrite-output-ens"
    ens_path = grid_path / "ens_01"
    comp_enspath = ens_path / compout
    freq_enspath = comp_enspath / freq
    chunk_enspath = freq_enspath / chunk

    paths = [rewrite_dir_tmp_out, ens_path, comp_enspath, freq_enspath, chunk_enspath]

    for p in paths:
        if os.path.exists(p):
            shutil.rmtree(p)
            os.makedirs(p, exist_ok=True)
        else:
            os.makedirs(p, exist_ok=True)

    # Copy input file from ncgen test in ensemble input directory as well
    shutil.copyfile(Path(chunk_path) / DATA_FILE_NC, chunk_enspath/DATA_FILE_NC)

    # Create a test rose-app configuration
    ex = [ "rose", "app-run",
           '-D',  '[env]inputDir='f'{ncgen_dir_tmp_out}',
           '-D',  '[env]outputDir='f'{rewrite_dir_tmp_out}',
           '-D',  '[env]currentChunk=P5Y',
           '-D',  '[env]components=atmos_scalar',
           '-D',  '[env]begin=19800101T0000Z',
           '-D',  '[env]product=ts',
           '-D',  '[env]dirTSWorkaround=1',
           '-D',  '[env]ens_mem=ens_01',
           '-D',  '[env]COPY_TOOL=cp',
           '-D',  '[atmos_scalar]grid=native',
           '-D',  '[atmos_scalar]sources=atmos_scalar',
           '-C',  script
         ]

    print (ex)

    # Run the rewritten remap-pp-components script using the rose-app configuration
    sp = subprocess.run( ex )

    # Error check
    assert sp.returncode == 0
    out, err = capfd.readouterr()

def test_rewrite_remap_product_failure(capfd):
    """Checks for failure of the remap script when 
       ts or av is not given for the product.
    """
    # script: directory with /bin folder with remap script
    script = Path(cwd)

    global rewrite_dir_tmp_out
    #Define input and output locations
    rewrite_dir_tmp_out = test_outDir / "remap-rewrite-output"
    os.makedirs(rewrite_dir_tmp_out, exist_ok=True)

    # Create a test rose-app configuration
    ex = [ "rose", "app-run",
           '-D',  '[env]inputDir='f'{ncgen_dir_tmp_out}',
           '-D',  '[env]outputDir='f'{rewrite_dir_tmp_out}',
           '-D',  '[env]currentChunk=P5Y',
           '-D',  '[env]components=atmos_scalar',
           '-D',  '[env]begin=19800101T0000Z',
           '-D',  '[env]product=nottsorav',
           '-D',  '[env]dirTSWorkaround=1',
           '-D',  '[env]ens_mem=',
           '-D',  '[env]COPY_TOOL=cp',
           '-D',  '[atmos_scalar]grid=native',
           '-D',  '[atmos_scalar]sources=atmos_scalar',
           '-C',  script
         ]

    print (ex)

    # Run the rewritten remap-pp-components script using the rose-app configuration
    sp = subprocess.run( ex )

    # Failure check 
    assert sp.returncode != 0
    out, err = capfd.readouterr()

def test_rewrite_remap_beginDate_failure(capfd):
    """Checks for failure of the remap script when
       an incorrect begin date is given.
    """
    # script: directory with /bin folder with remap script
    script = Path(cwd)

    global rewrite_dir_tmp_out
    #Define input and output locations
    rewrite_dir_tmp_out = test_outDir / "remap-rewrite-output"
    os.makedirs(rewrite_dir_tmp_out, exist_ok=True)

    # Create a test rose-app configuration
    ex = [ "rose", "app-run",
           '-D',  '[env]inputDir='f'{ncgen_dir_tmp_out}',
           '-D',  '[env]outputDir='f'{rewrite_dir_tmp_out}',
           '-D',  '[env]currentChunk=P5Y',
           '-D',  '[env]components=atmos_scalar',
           '-D',  '[env]begin=0123456789T0000Z',
           '-D',  '[env]product=ts',
           '-D',  '[env]dirTSWorkaround=1',
           '-D',  '[env]ens_mem=',
           '-D',  '[env]COPY_TOOL=cp',
           '-D',  '[atmos_scalar]grid=native',
           '-D',  '[atmos_scalar]sources=atmos_scalar',
           '-C',  script
         ]

    print (ex)

    # Run the rewritten remap-pp-components script using the rose-app configuration
    sp = subprocess.run( ex )

    # Failure check
    assert sp.returncode != 0
    out, err = capfd.readouterr()

# Comparison
def test_nccmp_ncgen_rewriteremap(capfd):
    """This test compares the results of ncgen and rewrite_remap,
        making sure that the remapped files are identical.
    """

    nccmp = [ "nccmp", "-d", Path(ncgen_dir_tmp_out) / grid / compout / freq / chunk / DATA_FILE_NC, Path(rewrite_dir_tmp_out) / compout / "ts" / freq / chunk / DATA_FILE_NC ];

    sp = subprocess.run(nccmp)    
    assert sp.returncode == 0

# Original remap script 
@pytest.mark.skip(reason='comparison with original remap script')
def test_original_remap_pp_components(capfd):
    """In this test, app checks for success of remapping a file with rose app
    as the valid definitions are being called by the environment with the original
    remap-pp-components script.
    """
    # Go to original remap script directory
    os.chdir("../remap-pp-components")
    script = Path(os.getcwd())
    print(script)

    global orig_dir_tmp_out #, remapped_new_file
    # Define input and output locations
    orig_dir_tmp_out = test_outDir / "orig-remap-output"

    os.makedirs(orig_dir_tmp_out, exist_ok=True)

    # Rose functionality
    # Create a test rose-app configuration
    ex = [ "rose", "app-run",
           '-D',  '[env]inputDir='f'{ncgen_dir_tmp_out}',
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

    print (ex)

    # Run the remap-pp-components script using the rose-app configuration
    sp = subprocess.run( ex )

    # Error checking
    assert sp.returncode == 0
    out, err = capfd.readouterr()

@pytest.mark.skip(reason='comparison with original remap script')
def test_nccmp_ncgen_origremap(capfd):
    """This test compares the results of ncgen and orig_remap,
       making sure that the two new created remapped files are identical.
    """

    grid = "native"
    freq = "P1M"
    chunk = "P5Y"

    nccmp = [ "nccmp", "-d", Path(ncgen_dir_tmp_out) /  grid / compout / freq / chunk / DATA_FILE_NC, Path(orig_dir_tmp_out) / compout / "ts" / freq / chunk / DATA_FILE_NC ];

    sp = subprocess.run(nccmp)
    assert sp.returncode == 0

@pytest.mark.skip(reason='comparison with original remap script')
def test_nccmp_origremap_rewriteremap(capfd):
    """This test compares the results of orig_remap and rewrite_remap,
       making sure that the two new created remapped files are identical.
    """

    grid = "native"
    freq = "P1M"
    chunk = "P5Y"

    nccmp = [ "nccmp", "-d", Path(orig_dir_tmp_out) / compout / "ts" / freq / chunk / DATA_FILE_NC , Path(rewrite_dir_tmp_out) / compout / "ts" / freq / chunk / DATA_FILE_NC ];

    sp = subprocess.run(nccmp)    
    assert sp.returncode == 0

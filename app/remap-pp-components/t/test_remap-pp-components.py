import os
import subprocess
import shutil
from pathlib import Path
import pytest

cwd = os.getcwd()

# Path to test data
DATA_DIR  = Path(f"{cwd}/test-data")
# CDL file to generate nc file from ncgen
DATA_FILE_CDL = Path("atmos_scalar.198001-198412.co2mass.cdl")
# Create NC file name to test remap functionality
DATA_FILE_NC = Path("atmos_scalar.198001-198412.co2mass.nc")

# Define variables
COMPOUT = "atmos_scalar"
GRID = "native"
FREQ = "P1M"
CHUNK = "P5Y"
PRODUCT = "ts"
COPY_TOOL = "cp"

#Define/create necessary locatiions
test_outDir = Path(f"{cwd}/test-outDir")
remap_in = test_outDir / "ncgen-output"
remap_out = test_outDir / "remap-output"

# Set up input directory (location previously made in flow.cylc workflow)
ncgen_out = Path(remap_in) / GRID / COMPOUT / FREQ / CHUNK

#If output directory exists, remove and create again
if Path(test_outDir).exists():
    shutil.rmtree(test_outDir)
    Path(ncgen_out).mkdir(parents=True,exist_ok=True)
    Path(remap_out).mkdir(parents=True,exist_ok=True)
else:
    Path(ncgen_out).mkdir(parents=True,exist_ok=True)
    Path(remap_out).mkdir(parents=True,exist_ok=True)

def test_create_ncfile_with_ncgen_cdl(capfd):
    """
       Check for the creation of required directories
       and a *.nc file from *.cdl text file using
       command ncgen. This file will be used as an input
       file for the rewrite remap tests.
       Test checks for success of ncgen command.
    """
    print(f"NCGEN OUTPUT DIRECTORY: {ncgen_out}")

    # NCGEN command: ncgen -o [outputfile] [inputfile]
    ex = [ "ncgen", "-k", "64-bit offset",
           "-o", Path(ncgen_out) / DATA_FILE_NC,
           DATA_DIR / DATA_FILE_CDL ]

    print (ex)

    # Run ncgen command
    sp = subprocess.run( ex, check = False )

    # Check for
    # 1. ncgen command success
    # 2. nc file creation
    assert all([sp.returncode == 0,
               Path(ncgen_out / DATA_FILE_NC).exists()])
    out, err = capfd.readouterr()

def test_remap_pp_components(capfd):
    """Checks for success of remapping a file with rose app using
       the remap-pp-components script as the valid definitions
       are being called by the environment.
    """
    # script: directory with /bin folder with remap script
    script = Path(cwd)

    # Create a test rose-app configuration
    ex = [ "rose", "app-run",
           '-D',  '[env]inputDir='f'{remap_in}',
           '-D',  '[env]outputDir='f'{remap_out}',
           '-D',  '[env]currentChunk=P5Y',
           '-D',  '[env]components='f'"{COMPOUT}, atmos_month"',
           '-D',  '[env]begin=19800101T0000Z',
           '-D',  '[env]product='f'{PRODUCT}',
           '-D',  '[env]dirTSWorkaround=1',
           '-D',  '[env]ens_mem=',
           '-D',  '[env]COPY_TOOL='f'{COPY_TOOL}',
           '-D',  '[atmos_scalar]grid='f'{GRID}',
           '-D',  '[atmos_scalar]sources=atmos_scalar',
           '-C',  script
         ]

    print (ex)

    # Run the rewritten remap-pp-components script using the rose-app configuration
    sp = subprocess.run( ex, check = False )

    # Check for
    # 1. success of remap script
    # 2. creation of output directory structre,
    # 3. link to nc file in output location
    assert all([sp.returncode == 0,
                Path(remap_out/COMPOUT/PRODUCT/FREQ/CHUNK).exists(),
                Path(remap_out/COMPOUT/PRODUCT/FREQ/CHUNK/DATA_FILE_NC).exists()])
    out, err = capfd.readouterr()
'''
def test_remap_pp_components_with_ensmem(capfd):
    """Checks for success of remapping a file with rose app config using
       the remap-pp-components script when ens_mem is defined.
    """
    # script: directory with /bin folder with remap script
    script = Path(cwd)

    # Redefine ens input and output directories
    remap_ens_in = test_outDir / "ncgen-ens-output"
    ncgen_ens_out = Path(remap_ens_in) / GRID / "ens_01" / COMPOUT / FREQ / CHUNK
    remap_ens_out = test_outDir / "remap-ens-output"

    # Create ensemble locations
    Path(ncgen_ens_out).mkdir(parents=True,exist_ok=True)
    Path(remap_ens_out).mkdir(parents=True,exist_ok=True)

    # Make sure input nc file is also in ens input location
    shutil.copyfile(Path(ncgen_out) / DATA_FILE_NC, Path(ncgen_ens_out) / DATA_FILE_NC)

    # Create a test rose-app configuration
    ex = [ "rose", "app-run",
           '-D',  '[env]inputDir='f'{remap_ens_in}',
           '-D',  '[env]outputDir='f'{remap_ens_out}',
           '-D',  '[env]currentChunk=P5Y',
           '-D',  '[env]components='f'{COMPOUT}',
           '-D',  '[env]begin=19800101T0000Z',
           '-D',  '[env]product='f'{PRODUCT}',
           '-D',  '[env]dirTSWorkaround=1',
           '-D',  '[env]ens_mem=ens_01',
           '-D',  '[env]COPY_TOOL='f'{COPY_TOOL}',
           '-D',  '[atmos_scalar]grid='f'{GRID}',
           '-D',  '[atmos_scalar]sources=atmos_scalar',
           '-C',  script
         ]

    print (ex)

    # Run the rewritten remap-pp-components script using the rose-app configuration
    sp = subprocess.run( ex, check = False )

    # Check for
    # 1. success of remap script
    # 2. creation of output directory structre,
    # 3. link to nc file in output location
    assert all([sp.returncode == 0,
                Path(remap_ens_out/COMPOUT/PRODUCT/"ens_01"/FREQ/CHUNK).exists(),
                Path(remap_ens_out/COMPOUT/PRODUCT/"ens_01"/FREQ/CHUNK/DATA_FILE_NC).exists()])
    out, err = capfd.readouterr()

def test_remap_pp_components_product_failure(capfd):
    """Checks for failure of remapping a file with rose app using
       the remap-pp-components script when the product is ill-defined.
       (not ts or av)
    """
    # script: directory with /bin folder with remap script
    script = Path(cwd)

    # Create a test rose-app configuration
    ex = [ "rose", "app-run",
           '-D',  '[env]inputDir='f'{remap_in}',
           '-D',  '[env]outputDir='f'{remap_out}',
           '-D',  '[env]currentChunk=P5Y',
           '-D',  '[env]components='f'{COMPOUT}',
           '-D',  '[env]begin=19800101T0000Z',
           '-D',  '[env]product=not-ts-or-av',
           '-D',  '[env]dirTSWorkaround=1',
           '-D',  '[env]ens_mem=',
           '-D',  '[env]COPY_TOOL='f'{COPY_TOOL}',
           '-D',  '[atmos_scalar]grid='f'{GRID}',
           '-D',  '[atmos_scalar]sources=atmos_scalar',
           '-C',  script
         ]

    print (ex)

    # Run the rewritten remap-pp-components script using the rose-app configuration
    sp = subprocess.run( ex, check = False )

    # Check for
    # 1. failure of remap script
    assert sp.returncode != 0
    out, err = capfd.readouterr()

def test_remap_pp_components_begin_date_failure(capfd):
    """Checks for failure of remapping a file with rose app using
       the remap-pp-components script when the begin variable is
       ill-defined.
    """
    # script: directory with /bin folder with remap script
    script = Path(cwd)

    # Create a test rose-app configuration
    ex = [ "rose", "app-run",
           '-D',  '[env]inputDir='f'{remap_in}',
           '-D',  '[env]outputDir='f'{remap_out}',
           '-D',  '[env]currentChunk=P5Y',
           '-D',  '[env]components='f'{COMPOUT}',
           '-D',  '[env]begin=123456789T0000Z',
           '-D',  '[env]product='f'{PRODUCT}',
           '-D',  '[env]dirTSWorkaround=1',
           '-D',  '[env]ens_mem=',
           '-D',  '[env]COPY_TOOL='f'{COPY_TOOL}',
           '-D',  '[atmos_scalar]grid='f'{GRID}',
           '-D',  '[atmos_scalar]sources=atmos_scalar',
           '-C',  script
         ]

    print (ex)

    # Run the rewritten remap-pp-components script using the rose-app configuration
    sp = subprocess.run( ex, check = False )

    # Check for
    # 1. failure of remap script
    assert sp.returncode != 0
    out, err = capfd.readouterr()

# Comparison
def test_nccmp_ncgen_remap(capfd):
    """This test compares the results of ncgen and rewrite_remap,
        making sure that the remapped files are identical.
    """
    nccmp = [ "nccmp", "-d",
              Path(remap_in) / GRID / COMPOUT / FREQ / CHUNK / DATA_FILE_NC,
              Path(remap_out) / COMPOUT / PRODUCT / FREQ / CHUNK / DATA_FILE_NC ]

    sp = subprocess.run( nccmp, check = False)
    assert sp.returncode == 0
    out, err = capfd.readouterr()

# Comparison
def test_nccmp_ncgen_remap_ens_mem(capfd):
    """This test compares the results of ncgen and rewrite_remap,
        making sure that the remapped files are identical.
    """
    # Redefine ens input and output directories
    remap_ens_in = test_outDir / "ncgen-ens-output"
    remap_ens_out = test_outDir / "remap-ens-output"

    nccmp = [ "nccmp", "-d",
              Path(remap_ens_in) / GRID / "ens_01" / COMPOUT / FREQ / CHUNK / DATA_FILE_NC,
              Path(remap_ens_out) / COMPOUT / PRODUCT / "ens_01" / FREQ / CHUNK / DATA_FILE_NC ]

    sp = subprocess.run( nccmp, check = False)
    assert sp.returncode == 0
    out, err = capfd.readouterr()
'''

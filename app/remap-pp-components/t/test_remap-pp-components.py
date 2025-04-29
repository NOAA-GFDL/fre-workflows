import os
import subprocess
import shutil
from pathlib import Path
import pytest
from remap_pp_components import remap

CWD = os.getcwd()

# Path to test data
DATA_DIR  = Path(f"{CWD}/test-data")
# CDL file to generate nc file from ncgen
DATA_FILE_CDL = Path("atmos_scalar.198001-198412.co2mass.cdl")
# Create NC file name to test remap functionality
DATA_FILE_NC = Path("atmos_scalar.198001-198412.co2mass.nc")
# YAML configuration example file
YAML_EX = f"{DATA_DIR}/yaml_ex.yaml"

# Define/create necessary locatiions
TEST_OUTDIR = f"{CWD}/test-outDir"
REMAP_IN = f"{TEST_OUTDIR}/ncgen-output"
REMAP_OUT = f"{TEST_OUTDIR}/remap-output"

# Define variables
COMPOUT = "atmos_scalar"
GRID = "native"
FREQ = "P1M"
CHUNK = "P5Y"
PRODUCT = "ts"
COPY_TOOL = "cp"

# environment variables
os.environ['inputDir'] = REMAP_IN
os.environ['outputDir'] = REMAP_OUT
os.environ['currentChunk'] = "P5Y"
os.environ['components'] = COMPOUT
os.environ['begin'] = "19800101T0000Z"
os.environ['product'] = PRODUCT
os.environ['dirTSWorkaround'] = "1"
os.environ['ens_mem'] = ""
os.environ['COPY_TOOL'] = COPY_TOOL
os.environ['yaml_config'] = YAML_EX

# Set up input directory (location previously made in flow.cylc workflow)
ncgen_out = Path(REMAP_IN) / GRID / COMPOUT / FREQ / CHUNK

#If output directory exists, remove and create again
if Path(TEST_OUTDIR).exists():
    shutil.rmtree(TEST_OUTDIR)
    Path(ncgen_out).mkdir(parents=True,exist_ok=True)
    Path(REMAP_OUT).mkdir(parents=True,exist_ok=True)
else:
    Path(ncgen_out).mkdir(parents=True,exist_ok=True)
    Path(REMAP_OUT).mkdir(parents=True,exist_ok=True)


##REMAP NOW USES YAML CONFIG, NOT ROSE APPS
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
    """
    Checks for success of remapping a file with rose app using
    the remap-pp-components script as the valid definitions
    are being called by the environment.
    """
    # run script
    try:
        remap()
    except:
        assert False

    # Check for
    # 1. creation of output directory structre,
    # 2. link to nc file in output location
    assert all([Path(f"{REMAP_OUT}/{COMPOUT}/{PRODUCT}/monthly/5yr").exists(),
                Path(f"{REMAP_OUT}/{COMPOUT}/{PRODUCT}/monthly/5yr/{DATA_FILE_NC}").exists()])
    out, err = capfd.readouterr()

 ####are freq and chunk supposed to be like that?####

def test_remap_pp_components_with_ensmem(capfd):
    """
    Checks for success of remapping a file with rose app config using
    the remap-pp-components script when ens_mem is defined.
    """
    # Redefine ens input and output directories
    remap_ens_in = f"{TEST_OUTDIR}/ncgen-ens-output"
    ncgen_ens_out = Path(remap_ens_in) / GRID / "ens_01" / COMPOUT / FREQ / CHUNK
    remap_ens_out = f"{TEST_OUTDIR}/remap-ens-output"

    # Specify environment variables
    os.environ['inputDir'] = remap_ens_in
    os.environ['outputDir'] = remap_ens_out
    os.environ['currentChunk'] = "P5Y"
    os.environ['components'] = COMPOUT
    os.environ['begin'] = "19800101T0000Z"
    os.environ['product'] = PRODUCT
    os.environ['dirTSWorkaround'] = "1"
    os.environ['ens_mem'] = "ens_01"
    os.environ['COPY_TOOL'] = COPY_TOOL
    os.environ['yaml_config'] = YAML_EX

    # Create ensemble locations
    Path(ncgen_ens_out).mkdir(parents=True,exist_ok=True)
    Path(remap_ens_out).mkdir(parents=True,exist_ok=True)

    # Make sure input nc file is also in ens input location
    shutil.copyfile(Path(ncgen_out) / DATA_FILE_NC, Path(ncgen_ens_out) / DATA_FILE_NC)

    # run script
    try:
        remap()
    except:
        assert False

    # Check for
    # 1. creation of output directory structre,
    # 2. link to nc file in output location
    assert all([Path(f"{remap_ens_out}/{COMPOUT}/{PRODUCT}/{os.getenv('ens_mem')}/monthly/5yr").exists(),
                Path(f"{remap_ens_out}/{COMPOUT}/{PRODUCT}/{os.getenv('ens_mem')}/monthly/5yr/{DATA_FILE_NC}").exists()])
    out, err = capfd.readouterr()

@pytest.mark.xfail #uncomment to ensure it's the right failure
def test_remap_pp_components_product_failure(capfd):
    """
    Checks for failure of remapping a file with rose app using
    the remap-pp-components script when the product is ill-defined.
    (not ts or av)
    """
    # Specify environment variables
    os.environ['inputDir'] = REMAP_IN
    os.environ['outputDir'] = REMAP_OUT
    os.environ['currentChunk'] = "P5Y"
    os.environ['components'] = COMPOUT
    os.environ['begin'] = "19800101T0000Z"
    os.environ['product'] = "not-ts-or-av" # change product value
    os.environ['dirTSWorkaround'] = "1"
    os.environ['ens_mem'] = ""
    os.environ['COPY_TOOL'] = COPY_TOOL
    os.environ['yaml_config'] = YAML_EX

    # run script
    remap()

@pytest.mark.xfail
def test_remap_pp_components_begin_date_failure(capfd):
    """
    Checks for failure of remapping a file with rose app using
    the remap-pp-components script when the begin variable is
    ill-defined.
    """
    # Specify environment variables
    os.environ['inputDir'] = REMAP_IN
    os.environ['outputDir'] = REMAP_OUT
    os.environ['currentChunk'] = "P5Y"
    os.environ['components'] = COMPOUT
    os.environ['begin'] = "123456789T0000Z" # change begin value
    os.environ['product'] = PRODUCT
    os.environ['dirTSWorkaround'] = "1"
    os.environ['ens_mem'] = ""
    os.environ['COPY_TOOL'] = COPY_TOOL
    os.environ['yaml_config'] = YAML_EX

    # run script
    remap()

# Comparison tests
def test_nccmp_ncgen_remap(capfd):
    """
    This test compares the results of ncgen and rewrite_remap,
    making sure that the remapped files are identical.
    """
    nccmp = [ "nccmp", "-d",
              Path(f"{REMAP_IN}/{GRID}/{COMPOUT}/{FREQ}/{CHUNK}/{DATA_FILE_NC}"),
              Path(f"{REMAP_OUT}/{COMPOUT}/{PRODUCT}/monthly/5yr/{DATA_FILE_NC}") ]

    sp = subprocess.run( nccmp, check = False)
    assert sp.returncode == 0
    out, err = capfd.readouterr()

def test_nccmp_ncgen_remap_ens_mem(capfd):
    """
    This test compares the results of ncgen and rewrite_remap,
    making sure that the remapped files are identical.
    """
    # Redefine ens input and output directories
    remap_ens_in = f"{TEST_OUTDIR}/ncgen-ens-output"
    remap_ens_out = f"{TEST_OUTDIR}/remap-ens-output"

    nccmp = [ "nccmp", "-d",
              Path(f"{remap_ens_in}/{GRID}/ens_01/{COMPOUT}/{FREQ}/{CHUNK}/{DATA_FILE_NC}"),
              Path(f"{remap_ens_out}/{COMPOUT}/{PRODUCT}/ens_01/monthly/5yr/{DATA_FILE_NC}") ]

    sp = subprocess.run( nccmp, check = False)
    assert sp.returncode == 0
    out, err = capfd.readouterr()

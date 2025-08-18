"""
Test combine-statics task script
"""
import os
import re
import subprocess
import shutil
from pathlib import Path
from netCDF4 import Dataset

# Define test dirs
COMBINE_STATICS_DIR = Path(__file__).resolve().parents[1]
TEST_DIR = Path(f"{COMBINE_STATICS_DIR}/tests")
DATA_DIR = Path(f"{TEST_DIR}/test-data")
COMP_NAME = "atmos_static_scalar"

# Data files available
STATIC_DATA_CDLFILE = ["atmos_static_scalar_1.bk.cdl",
                       "atmos_static_scalar_2.ak.cdl",
                       "atmos_static_scalar_3.ck.cdl"]

# netCDF files to generate
STATIC_DATA_NCFILE  = ["atmos_static_scalar_1.bk.nc",
                       "atmos_static_scalar_2.ak.nc",
                       "atmos_static_scalar_3.ck.nc"]

# Input/Output directories
# OutDir for generating netcdf files; used as input for combine-statics task
NCGEN_OUT = f"{TEST_DIR}/test-output/ncgen-output"
# OutDir for running the combine-statics script
COMBINE_STATICS_OUT = f"{TEST_DIR}/test-output/combine-statics-output"

# If output paths exist already, remove them and create fresh
# If they don't exist already, create them
if Path(NCGEN_OUT).exists() and Path(COMBINE_STATICS_OUT).exists():
    shutil.rmtree(NCGEN_OUT)
    shutil.rmtree(COMBINE_STATICS_OUT)
    Path(f"{NCGEN_OUT}/{COMP_NAME}/P0Y/P0Y").mkdir(parents=True,exist_ok=True)
    Path(COMBINE_STATICS_OUT).mkdir(parents=True,exist_ok=True)
else:
    Path(f"{NCGEN_OUT}/{COMP_NAME}/P0Y/P0Y").mkdir(parents=True,exist_ok=True)
    Path(COMBINE_STATICS_OUT).mkdir(parents=True,exist_ok=True)

def test_cdl_file_exists():
    """
    Test for the existence of static cdl test files
    """
    assert all([Path(f"{DATA_DIR}/{STATIC_DATA_CDLFILE[0]}").exists(),
                Path(f"{DATA_DIR}/{STATIC_DATA_CDLFILE[1]}").exists(),
                Path(f"{DATA_DIR}/{STATIC_DATA_CDLFILE[2]}").exists()])

def test_ncgen_static_nc_files():
    """
    Generate netcdf files from cdl files; test they were created successfully
    and exist in the right location (input dir for other tests)
    """
    # NCGEN command: ncgen -o [outputfile] [inputfile]
    for num in range(3):
        inputfile = STATIC_DATA_CDLFILE[num]
        outputfile = STATIC_DATA_NCFILE[num]
        output = f"{NCGEN_OUT}/{COMP_NAME}/P0Y/P0Y/{outputfile}"

        ex = ["ncgen", "-k", "64-bit offset",
              "-o", output,
              f"{DATA_DIR}/{inputfile}"]

        # Run ncgen command
        sp = subprocess.run( ex, check = False )
        # Check for
        # 1. ncgen command success
        # 2. nc file creation
        assert all([sp.returncode == 0,
                    Path(f"{NCGEN_OUT}/{COMP_NAME}/P0Y/P0Y/{outputfile}").exists()])

def test_valid_input_dir():
    """
    Test that the input directory is valid and not empty
    """
    assert all([Path(f"{NCGEN_OUT}/{COMP_NAME}/P0Y/P0Y").is_dir(),
                len(os.listdir(f"{NCGEN_OUT}/{COMP_NAME}/P0Y/P0Y")) != 0])

def test_valid_output_dir():
    """
    Test that the output directory exists and is valid
    """
    assert all([Path(COMBINE_STATICS_OUT).exists(),
                Path(COMBINE_STATICS_OUT).is_dir])

def test_combine_statics(monkeypatch):
    """
    Test that combine-statics script was successful
    """
    monkeypatch.setenv("inputDir", NCGEN_OUT)
    monkeypatch.setenv("outputDir", COMBINE_STATICS_OUT)

    script = f"{COMBINE_STATICS_DIR}/bin/combine-statics"
    sp = subprocess.run(script, check = False)

    # Check for
    # 1. combine-statics script success
    # 2. output file existence
    assert all ([sp.returncode == 0,
                 Path(f"{COMBINE_STATICS_OUT}/{COMP_NAME}/atmos_static_scalar.static.nc").is_file()])

def test_combine_statics_output_content():
    """
    Test that netcdf output file has cdo merge call with the correct files
    """
    outfile = "atmos_static_scalar.static.nc"

    # read output static netcdf file
    with Dataset(f"{COMBINE_STATICS_OUT}/{COMP_NAME}/{outfile}", 'r') as sf:
        history_str = sf.__dict__.get("history")

    ncfiles = " ".join(STATIC_DATA_NCFILE)
    expected_cdo_str = f"cdo -O merge {ncfiles} .*{outfile}"

    assert all ([re.search(expected_cdo_str, history_str),
                 all(comp in history_str for comp in STATIC_DATA_NCFILE)])

# TO-DO: Having issues trying to generate an expected failure when adding a static netcdf file that should fail at cdo merge 
#def test_combine_statics_failure():

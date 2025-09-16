"""
Test combine-statics task script
"""
import os
import re
import subprocess
import shutil
from pathlib import Path
#from netCDF4 import Dataset
import xarray as xr
import numpy as np
import pytest

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
    Path(f"{NCGEN_OUT}/{COMP_NAME}/P0Y/P0Y").mkdir(parents=True,exist_ok=False)
    Path(COMBINE_STATICS_OUT).mkdir(parents=True,exist_ok=False)
else:
    Path(f"{NCGEN_OUT}/{COMP_NAME}/P0Y/P0Y").mkdir(parents=True,exist_ok=False)
    Path(COMBINE_STATICS_OUT).mkdir(parents=True,exist_ok=False)

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
        sp = subprocess.run( ex, check = True )
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
    sp = subprocess.run(script, check = True)

    # Check for
    # 1. combine-statics script success
    # 2. output file existence
    assert all ([sp.returncode == 0,
                 Path(f"{COMBINE_STATICS_OUT}/{COMP_NAME}/atmos_static_scalar.static.nc").is_file()])

@pytest.fixture(name="load_ncfile")
def load_dataset():
    """
    Load and open the final netcdf file using xarray
    """
    outfile = "atmos_static_scalar.static.nc"

    # read output static netcdf file
    # xarray dataset object
    sf = xr.open_dataset(f"{COMBINE_STATICS_OUT}/{COMP_NAME}/{outfile}")
    # sf available to use for test
    yield sf
    # close dataset
    sf.close()

#### CHECK NC FILE OUTPUT ####
def test_combine_statics_output_cdomergecmd(load_ncfile):
    """
    Test that netcdf output file has expected cdo merge call with the correct files
    """
    outfile = "atmos_static_scalar.static.nc"

    # Use pytest fixture to open netcdf file
    static_file = load_ncfile

    # sf.attrs: dict
    history_str = static_file.attrs['history']

    ncfiles = " ".join(STATIC_DATA_NCFILE)
    expected_cdo_str = f"cdo -O merge {ncfiles} .*{outfile}"

    assert all ([re.search(expected_cdo_str, history_str),
                 all(comp in history_str for comp in STATIC_DATA_NCFILE)])

def test_combine_statics_output_dimensions(load_ncfile):
    """
    Test for expected dimnesions and dimensions values in 
    final netcdf file.
    """
    # Use pytest fixture to open netcdf file
    static_file = load_ncfile

    ## Check dimensions/dimension values ##
    # sf.dims - xarray class
    assert "lat" in static_file.dims
    assert "lon" in static_file.dims

    # sf.sizes: sizes object; specialized dictionary of dimensions sizes
    assert static_file.sizes["lat"] == 4
    assert static_file.sizes["lon"] == 5

def test_combine_statics_output_variables(load_ncfile):
    """
    Test for expected variables (and correct variable types)
    are included in final netcdf file.
    """
    # Use pytest fixture to open netcdf file
    static_file = load_ncfile

    ## Check variables/variable types ##
    # sf.data_vars - xarray class
    nc_varlist = static_file.data_vars

    for v in ['bk', 'ak', 'ck']: #variables from the 3 nc files
        # Ensure variables include var_list
        assert v in nc_varlist

        # Ensure data types of variables are float32
        nc_vartype = nc_varlist[f'{v}'].dtype
        assert nc_vartype == 'float32'
        #print(f"{v} is of type: {nc_vartype}")

def test_combine_statics_output_data(load_ncfile):
    """
    Test for expected data values in final netcdf file. 
    """
    # Use pytest fixture to open netcdf file
    static_file = load_ncfile

    nc_varlist = static_file.data_vars

    expected_data = np.array([[1, 2, 3, 4, 5],
                             [6, 7, 8, 9, 10],
                             [11, 12, 13, 14, 15],
                             [16, 17, 18, 19, 20]])

    for v in ['bk', 'ak', 'ck']:
        val = nc_varlist[f'{v}'].values
        assert (val == expected_data).all()
        #print(f"{v} has values: {val}")

#####assert only one lat and lon exists...........
# TO-DO: Having issues trying to generate an expected failure when
#        adding a static netcdf file that should fail at cdo merge
#def test_combine_statics_failure():

"""
Test combine-statics task script
"""
import os
import subprocess
import shutil
from pathlib import Path
from netCDF4 import Dataset

COMBINE_STATICS_DIR = Path(__file__).resolve().parents[1]
TEST_DIR = Path(f"{COMBINE_STATICS_DIR}/tests")
DATA_DIR = Path(f"{TEST_DIR}/test-data")

COMP_NAME = "atmos_static_scalar"
STATIC_DATA_CDLFILE = ["atmos_static_scalar.bk1.cdl",
                       "atmos_static_scalar.bk2.cdl",
                       "atmos_static_scalar.bk3.cdl"]
STATIC_DATA_NCFILE  = ["atmos_static_scalar.bk1.nc",
                       "atmos_static_scalar.bk2.nc",
                       "atmos_static_scalar.bk3.nc"]

# Output dir from generating netcdf files
NCGEN_OUT = f"{TEST_DIR}/ncgen_output/atmos_static_scalar"
COMBINE_STATICS_OUT = f"{TEST_DIR}/combine_statics_output"

if Path(NCGEN_OUT).exists() and Path(COMBINE_STATICS_OUT).exists():
    shutil.rmtree(NCGEN_OUT)
    shutil.rmtree(COMBINE_STATICS_OUT)
    Path(f"{NCGEN_OUT}/P0Y/P0Y").mkdir(parents=True,exist_ok=True)
    Path(COMBINE_STATICS_OUT).mkdir(parents=True,exist_ok=True)
else:
    Path(f"{NCGEN_OUT}/P0Y/P0Y").mkdir(parents=True,exist_ok=True)
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
    Generate netcdf files from cdl files; test they were created
    successfully and exist
    """
    # NCGEN command: ncgen -o [outputfile] [inputfile]
    for num in range(3):
        inputfile = STATIC_DATA_CDLFILE[num]
        outputfile = STATIC_DATA_NCFILE[num]
        output_path = f"{TEST_DIR}/ncgen_output/{COMP_NAME}/P0Y/P0Y/{outputfile}"

        ex = ["ncgen", "-k", "64-bit offset",
              "-o", output_path,
              f"{DATA_DIR}/{inputfile}"]

        # Run ncgen command
        sp = subprocess.run( ex, check = False )

        # Check for
        # 1. ncgen command success
        # 2. nc file creation
        assert all([sp.returncode == 0,
                    Path(f"{TEST_DIR}/ncgen_output/{COMP_NAME}/P0Y/P0Y/{outputfile}").exists()])

def test_valid_input_dir():
    """
    Test that the input directory and input files
    exist and are valid
    """
    for num in range(3):
        outputfile = STATIC_DATA_NCFILE[num]

        assert all([Path(f"{NCGEN_OUT}/P0Y/P0Y").is_dir(),
                    len(os.listdir(f"{NCGEN_OUT}/P0Y/P0Y")) != 0,
                    Path(f"{TEST_DIR}/ncgen_output/{COMP_NAME}/P0Y/P0Y/{outputfile}").is_file()])

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
    monkeypatch.setenv("inputDir", f"{TEST_DIR}/ncgen_output")
    monkeypatch.setenv("outputDir", COMBINE_STATICS_OUT)

    script = f"{COMBINE_STATICS_DIR}/bin/combine-statics"
    test = subprocess.run(script, check = False)

    assert all ([test.returncode == 0,
                 Path(f"{COMBINE_STATICS_OUT}/atmos_static_scalar/atmos_static_scalar.static.nc").is_file()])

def test_cdo_merge_output_content():
    """
    Test that netcdf output file has cdo merge call with the correct files
    """
    outfile = f"{COMBINE_STATICS_OUT}/atmos_static_scalar/atmos_static_scalar.static.nc"

    # read output static netcdf file
    with Dataset(outfile, 'r') as sf:
        cdo_call = """cdo -O merge atmos_static_scalar.bk1.nc atmos_static_scalar.bk2.nc atmos_static_scalar.bk3.nc /home/Dana.Singh/fre/combine-statics-test/fre-workflows/app/combine-statics/tests/combine_statics_output/atmos_static_scalar/atmos_static_scalar.static.nc"""
        history_str = sf.__dict__.get("history")

    assert all ([cdo_call in history_str,
                 "atmos_static_scalar.bk1.nc","atmos_static_scalar.bk2.nc","atmos_static_scalar.bk3.nc"])

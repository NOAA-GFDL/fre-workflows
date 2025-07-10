import os
import subprocess
import shutil
from pathlib import Path
import pytest

COMBINE_STATICS_DIR = Path(__file__).resolve().parents[1]
TEST_DIR = Path(f"{COMBINE_STATICS_DIR}/tests")
DATA_DIR = Path(f"{TEST_DIR}/test-data")

STATIC_DATA_CDLFILE = ["atmos_static_scalar.bk1.cdl", "atmos_static_scalar.bk2.cdl", "atmos_static_scalar.bk3.cdl"]
STATIC_DATA_NCFILE  = ["atmos_static_scalar.bk1.nc", "atmos_static_scalar.bk2.nc", "atmos_static_scalar.bk3.nc"]

# Output dir from generating netcdf files
NCGEN_OUT = f"{TEST_DIR}/ncgen_output"

if Path(NCGEN_OUT).exists():
    shutil.rmtree(NCGEN_OUT)
    Path(NCGEN_OUT).mkdir(parents=True,exist_ok=True)
else:
    Path(NCGEN_OUT).mkdir(parents=True,exist_ok=True)

def test_cdl_file_exists(capfd):
    """
    Test for the existence of static cdl test files
    """
    assert all([Path(f"{DATA_DIR}/{STATIC_DATA_CDLFILE[0]}").exists(),
                Path(f"{DATA_DIR}/{STATIC_DATA_CDLFILE[1]}").exists(),
                Path(f"{DATA_DIR}/{STATIC_DATA_CDLFILE[2]}").exists()])

def test_ncgen_static_nc_files(capfd):
    """
    test..................
    """
    # NCGEN command: ncgen -o [outputfile] [inputfile]
    for num in range(3):
        ex = ["ncgen", "-k", "64-bit offset",
              "-o", Path(NCGEN_OUT) / STATIC_DATA_NCFILE[num],
              DATA_DIR / STATIC_DATA_CDLFILE[num]]

        # Run ncgen command
        sp = subprocess.run( ex, check = False )

        # Check for
        # 1. ncgen command success
        # 2. nc file creation
        assert all([sp.returncode == 0,
                    Path(f"{NCGEN_OUT}/{STATIC_DATA_NCFILE[num]}").exists()])
        out, err = capfd.readouterr()

#    assert all([Path(NCGEN_OUT / STATIC_DATA_FILE_NC[0]).exists(),
#                Path(NCGEN_OUT / STATIC_DATA_FILE_NC[1]).exists(),
#                Path(NCGEN_OUT / STATIC_DATA_FILE_NC[2]).exists()])

def test_valid_input_dir():
    """
    """
    assert all([Path(NCGEN_OUT).is_dir(),
                len(os.listdir(NCGEN_OUT)) != 0,
                Path(f"{NCGEN_OUT}/{STATIC_DATA_NCFILE[0]}").is_file(),
                Path(f"{NCGEN_OUT}/{STATIC_DATA_NCFILE[1]}").is_file(),
                Path(f"{NCGEN_OUT}/{STATIC_DATA_NCFILE[2]}").is_file()])

#def test_valid_output_dir():
#    """
#    """
#exists

#def test_cdo_merge():
#for sucess
#content in nc --> shows cdo merge call

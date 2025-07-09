import os
import subprocess
import shutil
from pathlib import Path
import pytest

TEST_DIR = Path(__file__).resolve().parents[0]

# Path to test data
DATA_DIR  = Path(f"{TEST_DIR}/test-data")

def test_cdl_file_exists(capfd):
    """
    Test for the existence of static cdl test files
    """
    assert all([Path(f"{DATA_DIR}/{STATIC_DATA_CDLFILE_01}").exists(),
                Path(f"{DATA_DIR}/{STATIC_DATA_CDLFILE_02}").exists(),
                Path(f"{DATA_DIR}/{STATIC_DATA_CDLFILE_03}").exists()])

def ncgen_static_nc_files():
    """
    """
#    print(f"NCGEN OUTPUT DIRECTORY: {ncgen_static_out}")

    # NCGEN command: ncgen -o [outputfile] [inputfile]
    ex = ["ncgen", "-k", "64-bit offset",
          "-o", Path(ncgen_static_out) / STATIC_DATA_NCFILE,
          DATA_DIR / STATIC_DATA_CDLFILE]

    print (ex)

    # Run ncgen command
    sp = subprocess.run( ex, check = False )

    # Check for
    # 1. ncgen command success
    # 2. nc file creation
    assert all([sp.returncode == 0,
               Path(ncgen_static_out / STATIC_DATA_FILE_NC).exists()])
    out, err = capfd.readouterr()

def test_valid_input_dir():
#exists
#has static file in it

def test_valid_output_dir():
#exists

def test_cdo_merge():
#for sucess
#content in nc --> shows cdo merge call

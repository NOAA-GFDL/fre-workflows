"""Unit tests for the FRE make-timeseries workflow.

These tests verify creation and merging of NetCDF files from CDL sources, Rose app integration,
and output comparison, using pytest, subprocess, and temporary directories.
"""

import os
import subprocess
from pathlib import Path

# constants
VAR = "average_DT"
FREQ = "P2Y"
INPUT_CHUNK = "P2Y"
OUTPUT_CHUNK = "P4Y"
COMPONENT = "atmos_tracer"

# Test data paths
DATA_DIR = Path(__file__).parent / "files"
APP_DIR = Path(__file__).parent.parent
DATA_FILE_1ST_YEAR    = Path(f"{COMPONENT}.000501-000512.{VAR}.cdl")
DATA_FILE_2ND_YEAR    = Path(f"{COMPONENT}.000601-000612.{VAR}.cdl")
DATA_FILE_NC_1ST_YEAR = Path(f"{COMPONENT}.000501-000512.{VAR}.nc")
DATA_FILE_NC_2ND_YEAR = Path(f"{COMPONENT}.000601-000612.{VAR}.nc")

# Output file name follows FRE convention
INIT_DATE = str(DATA_FILE_NC_1ST_YEAR)[13:19]
END_DATE = str(DATA_FILE_NC_2ND_YEAR)[20:26]
COMPONENT_NEW_FILE = f"{COMPONENT}.{INIT_DATE}-{END_DATE}.{VAR}.nc"


# Global test state (pytest discourages globals, but used here to mimic original logic)
DIR_TMP_IN = None
DIR_TMP_OUT = None
NEW_DIR = None
ROSE_DIR = None


def test_make_timeseries(capfd, tmp_path):
    """Test creation of NetCDF files from CDL and merging with CDO."""
    global DIR_TMP_IN, NEW_DIR, DIR_TMP_OUT

    # Create input directory structure
    DIR_TMP_IN = tmp_path / "in_dir"
    din_check = DIR_TMP_IN / COMPONENT / FREQ / INPUT_CHUNK
    os.makedirs(din_check, exist_ok=True)

    # Create output directory
    DIR_TMP_OUT = tmp_path / "out_dir"
    DIR_TMP_OUT.mkdir()
    dout_check = str(DIR_TMP_OUT)

    # Convert CDL to NetCDF using ncgen
    target_path_1 = din_check / DATA_FILE_NC_1ST_YEAR
    ex = [
        "ncgen", "-o", str(din_check / DATA_FILE_NC_1ST_YEAR), str(DATA_DIR / DATA_FILE_1ST_YEAR)
    ]
    sp = subprocess.run(ex, check=True)
    assert sp.returncode == 0, f"ncgen failed to create {DATA_FILE_NC_1ST_YEAR}"
    assert target_path_1.exists(), (
        f"Output file {DATA_FILE_NC_1ST_YEAR} was not created"
    )

    target_path_2 = din_check / DATA_FILE_NC_2ND_YEAR
    ex = [
        "ncgen", "-o", str(din_check / DATA_FILE_NC_2ND_YEAR), str(DATA_DIR / DATA_FILE_2ND_YEAR)
    ]
    sp = subprocess.run(ex, check=True)
    assert sp.returncode == 0, f"ncgen failed to create {DATA_FILE_NC_2ND_YEAR}"
    assert target_path_2.exists(), (
        f"Output file {DATA_FILE_NC_2ND_YEAR} was not created"
    )

    # Extract date ranges from filenames
    NEW_DIR = dout_check
    end_point_din = str(din_check)

    # Merge time series using CDO
    input_files = f"{end_point_din}/{DATA_FILE_NC_1ST_YEAR} {end_point_din}/{DATA_FILE_NC_2ND_YEAR}"
    output_file = f"{dout_check}/{COMPONENT_NEW_FILE}"
    ex = [
        "cdo", "--history", "-O", "mergetime", input_files, output_file
    ]
    sp = subprocess.run(ex, check=True)
    assert sp.returncode == 0, "CDO mergetime failed"
    assert Path(output_file).exists()
    capfd.readouterr()  # Clear captured output


def test_rose_failure_make_timeseries(capfd, tmp_path):
    """Test Rose app-run failure with incorrect component name."""
    global ROSE_DIR
    din_check = str(DIR_TMP_IN)
    dout_check = tmp_path / "out_dir"
    dout_check.mkdir()
    dout_check = str(dout_check)

    ROSE_DIR = f"{tmp_path}/out_dir/{COMPONENT}/{FREQ}/{OUTPUT_CHUNK}"
    os.makedirs(ROSE_DIR, exist_ok=True)

    original_cwd = os.getcwd()
    os.chdir(APP_DIR)
    try:
        ex = [
            "rose", "app-run",
            "-D", f"[env]inputDir={din_check}",
            "-D", "[env]begin=00050101T0000Z",
            "-D", f"[env]outputDir={dout_check}",
            "-D", f"[env]inputChunk={INPUT_CHUNK}",
            "-D", f"[env]outputChunk={OUTPUT_CHUNK}",
            "-D", "[env]component=atmos",  # Incorrect component, should fail
            "-D", "[env]pp_stop=00070101T0000Z"   # Required parameter
        ]
        sp = subprocess.run(ex, check=False)
        assert sp.returncode == 1, "Rose app-run should fail with wrong component"
    finally:
        os.chdir(original_cwd)
    capfd.readouterr()  # Clear captured output


def test_rose_success_make_timeseries(capfd, tmp_path):
    """Test Rose app-run success with correct component and pp_stop."""
    global ROSE_DIR
    din_check = str(DIR_TMP_IN)

    dout_check = tmp_path / "out_dir"
    dout_check.mkdir()
    dout_check = str(dout_check)

    ROSE_DIR = f"{tmp_path}/out_dir/{COMPONENT}/{FREQ}/{OUTPUT_CHUNK}"
    os.makedirs(ROSE_DIR, exist_ok=True)

    original_cwd = os.getcwd()
    os.chdir(APP_DIR)
    try:
        ex = [
            "rose", "app-run",
            "-D", f"[env]inputDir={din_check}",
            "-D", "[env]begin=00050101T0000Z",
            "-D", f"[env]outputDir={dout_check}",
            "-D", f"[env]inputChunk={INPUT_CHUNK}",
            "-D", f"[env]outputChunk={OUTPUT_CHUNK}",
            "-D", f"[env]component={COMPONENT}",  # Correct component
            "-D", "[env]pp_stop=00070101T0000Z"   # Required parameter
        ]
        sp = subprocess.run(ex, check=True)
        assert sp.returncode == 0, "Rose app-run should succeed with correct setup"
    finally:
        os.chdir(original_cwd)
    capfd.readouterr()  # Clear captured output


def test_nccmp_make_timeseries(capfd):
    """Compare output files from manual CDO and Rose app runs with nccmp."""
    nccmp_ex = [
        "nccmp", "-d",
        f"{NEW_DIR}/{COMPONENT_NEW_FILE}",
        f"{ROSE_DIR}/{COMPONENT_NEW_FILE}"
    ]
    sp = subprocess.run(nccmp_ex, check=True)
    assert sp.returncode == 0, "nccmp comparison failed"
    capfd.readouterr()  # Clear captured output

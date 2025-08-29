"""Unit tests for the FRE make-timeseries workflow.

These tests verify creation and merging of NetCDF files from CDL sources, Rose app integration,
and output comparison, using pytest, subprocess, and temporary directories.
"""

import os
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import pytest

# Paths for test data and app
DATA_DIR = Path(__file__).parent / "files"
DATA_FILE_P1Y = Path("atmos_tracer.000501-000512.average_DT.cdl")
DATA_FILE_P2Y = Path("atmos_tracer.000601-000612.average_DT.cdl")
DATA_FILE_NC_P1Y = Path("atmos_tracer.000501-000512.average_DT.nc")
DATA_FILE_NC_P2Y = Path("atmos_tracer.000601-000612.average_DT.nc")
APP_DIR = Path(__file__).parent.parent

# Global test state (pytest discourages globals, but used here to mimic original logic)
dir_tmp_in = None
dir_tmp_out = None
new_dir = None
rose_dir = None
component_new_file = None
freq = None
component = None


def test_make_timeseries(capfd, tmp_path):
    """Test creation of NetCDF files from CDL and merging with CDO."""
    global dir_tmp_in, new_dir, freq, component, dir_tmp_out, component_new_file

    # Test configuration
    begin_cycle_point = "00050101T0000Z"
    chunk = "P2Y"
    freq = "P2Y"
    var = "average_DT"
    component = "atmos_tracer"
    files = []

    # Create input directory structure
    dir_tmp_in = tmp_path / "in_dir"
    din_check = dir_tmp_in / component / freq / chunk
    os.makedirs(din_check, exist_ok=True)

    # Create output directory
    dir_tmp_out = tmp_path / "out_dir"
    dir_tmp_out.mkdir()
    dout_check = str(dir_tmp_out)

    # Convert CDL to NetCDF using ncgen
    ex = [
        "ncgen", "-o", str(din_check / DATA_FILE_NC_P1Y), str(DATA_DIR / DATA_FILE_P1Y)
    ]
    sp = subprocess.run(ex)
    assert sp.returncode == 0, f"ncgen failed to create {DATA_FILE_NC_P1Y}"
    assert (din_check / DATA_FILE_NC_P1Y).exists(), f"Output file {DATA_FILE_NC_P1Y} was not created"

    ex = [
        "ncgen", "-o", str(din_check / DATA_FILE_NC_P2Y), str(DATA_DIR / DATA_FILE_P2Y)
    ]
    sp = subprocess.run(ex)
    assert sp.returncode == 0, f"ncgen failed to create {DATA_FILE_NC_P2Y}"
    assert (din_check / DATA_FILE_NC_P2Y).exists(), f"Output file {DATA_FILE_NC_P2Y} was not created"

    # Extract date ranges from filenames
    files.append(str(DATA_FILE_NC_P1Y))
    files.append(str(DATA_FILE_NC_P2Y))

    init_date = files[0][13:19]
    end_date = files[1][20:26]
    new_dir = dout_check
    end_point_din = str(din_check)

    # Output file name follows FRE convention
    component_new_file = f"{component}.{init_date}-{end_date}.{var}.nc"

    # Merge time series using CDO
    ex = [
        "cdo", "--history", "-O", "mergetime",
        f"{end_point_din}/{files[0]} {end_point_din}/{files[1]}",
        f"{dout_check}/{component_new_file}"
    ]
    sp = subprocess.run(ex)
    assert sp.returncode == 0, "CDO mergetime failed"
    capfd.readouterr()  # Clear captured output


def test_rose_failure_make_timeseries(capfd, tmp_path):
    """Test Rose app-run failure with incorrect component name."""
    global rose_dir
    din_check = str(dir_tmp_in)
    output_chunk = "P4Y"
    dout_check = tmp_path / "out_dir"
    dout_check.mkdir()
    dout_check = str(dout_check)

    rose_dir = f"{tmp_path}/out_dir/{component}/{freq}/{output_chunk}"
    os.makedirs(rose_dir, exist_ok=True)

    original_cwd = os.getcwd()
    os.chdir(APP_DIR)
    try:
        ex = [
            "rose", "app-run",
            "-D", f"[env]inputDir={din_check}",
            "-D", "[env]begin=00050101T0000Z",
            "-D", f"[env]outputDir={dout_check}",
            "-D", "[env]inputChunk=P2Y",
            "-D", "[env]outputChunk=P4Y",
            "-D", "[env]component=atmos"  # Incorrect component, should fail
        ]
        sp = subprocess.run(ex)
        assert sp.returncode == 1, "Rose app-run should fail with wrong component"
    finally:
        os.chdir(original_cwd)
    capfd.readouterr()  # Clear captured output


def test_rose_success_make_timeseries(capfd, tmp_path):
    """Test Rose app-run success with correct component and pp_stop."""
    global rose_dir
    din_check = str(dir_tmp_in)
    output_chunk = "P4Y"
    dout_check = tmp_path / "out_dir"
    dout_check.mkdir()
    dout_check = str(dout_check)

    rose_dir = f"{tmp_path}/out_dir/{component}/{freq}/{output_chunk}"
    os.makedirs(rose_dir, exist_ok=True)

    original_cwd = os.getcwd()
    os.chdir(APP_DIR)
    try:
        ex = [
            "rose", "app-run",
            "-D", f"[env]inputDir={din_check}",
            "-D", "[env]begin=00050101T0000Z",
            "-D", f"[env]outputDir={dout_check}",
            "-D", "[env]inputChunk=P2Y",
            "-D", "[env]outputChunk=P4Y",
            "-D", "[env]component=atmos_tracer",  # Correct component
            "-D", "[env]pp_stop=00070101T0000Z"   # Required parameter
        ]
        sp = subprocess.run(ex)
        assert sp.returncode == 0, "Rose app-run should succeed with correct setup"
    finally:
        os.chdir(original_cwd)
    capfd.readouterr()  # Clear captured output


def test_nccmp_make_timeseries(capfd, tmp_path):
    """Compare output files from manual CDO and Rose app runs with nccmp."""
    global new_dir, component_new_file, rose_dir
    nccmp_ex = [
        "nccmp", "-d",
        f"{new_dir}/{component_new_file}",
        f"{rose_dir}/{component_new_file}"
    ]
    sp = subprocess.run(nccmp_ex)
    assert sp.returncode == 0, "nccmp comparison failed"
    capfd.readouterr()  # Clear captured output

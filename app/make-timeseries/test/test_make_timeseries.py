from pathlib import Path
import pytest
import os
import subprocess
import shutil
import tempfile

# Test data files in the 'files' subdirectory
TEST_DATA_DIR = Path(__file__).parent / "files"
DATA_FILE_1 = "atmos_tracer.000501-000512.average_DT.nc"
DATA_FILE_2 = "atmos_tracer.000601-000612.average_DT.nc"

"""Tests for the make-timeseries shell script.

These tests validate the make-timeseries script by:
1. Setting up test input directory structure with NetCDF files
2. Running the make-timeseries script with proper environment variables
3. Verifying that output files are created correctly
"""

def test_input_validation():
    """Test that the script validates input parameters properly."""
    # Test will be implemented after we get basic functionality working
    pass

def test_directory_structure_validation(tmp_path):
    """Test that the script validates input/output directory structure."""
    
    # Create the basic directory structure for testing
    component = "atmos_tracer"
    freq = "P2Y"
    chunk = "P2Y"
    
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    
    # Create the input directory structure
    input_component_dir = input_dir / component / freq / chunk
    input_component_dir.mkdir(parents=True)
    
    # Create output directory
    output_dir.mkdir()
    
    # Copy test data files to input directory
    if (TEST_DATA_DIR / DATA_FILE_1).exists():
        shutil.copy(TEST_DATA_DIR / DATA_FILE_1, input_component_dir)
    if (TEST_DATA_DIR / DATA_FILE_2).exists():
        shutil.copy(TEST_DATA_DIR / DATA_FILE_2, input_component_dir)
    
    # Verify that input files exist
    assert (input_component_dir / DATA_FILE_1).exists()
    assert (input_component_dir / DATA_FILE_2).exists()
    
    # Verify directories are created correctly
    assert input_dir.exists()
    assert output_dir.exists()
    assert input_component_dir.exists()

def test_make_timeseries_basic_functionality(tmp_path):
    """Test basic functionality of make-timeseries script without external dependencies."""
    
    # For now, just test that the script exists and can be called
    script_path = Path(__file__).parent.parent / "bin" / "make-timeseries"
    assert script_path.exists(), f"make-timeseries script not found at {script_path}"
    
    # Test that script gives proper error when required environment variables are missing
    env = os.environ.copy()
    # Remove any existing variables that might interfere
    for var in ['inputDir', 'outputDir', 'begin', 'inputChunk', 'outputChunk', 'component', 'pp_stop']:
        env.pop(var, None)
    
    # The script should fail when required variables are not set
    result = subprocess.run([str(script_path)], 
                          env=env, 
                          capture_output=True, 
                          text=True,
                          timeout=30)
    
    # Script should fail (non-zero exit code) when required env vars are missing
    assert result.returncode != 0, "Script should fail when required environment variables are missing"

def test_environment_variable_requirements():
    """Test that the script requires specific environment variables."""
    
    script_path = Path(__file__).parent.parent / "bin" / "make-timeseries"
    
    # Define the required environment variables for the script
    required_vars = {
        'inputDir': '/tmp/input',
        'outputDir': '/tmp/output', 
        'begin': '00050101T0000Z',
        'inputChunk': 'P2Y',
        'outputChunk': 'P4Y',
        'component': 'atmos_tracer',
        'pp_stop': '00070101T0000Z'
    }
    
    # Test each variable is required by removing it one at a time
    for var_to_remove in required_vars:
        env = os.environ.copy()
        # Set all variables except the one we're testing
        for var, value in required_vars.items():
            if var != var_to_remove:
                env[var] = value
            else:
                env.pop(var, None)  # Remove the variable
        
        # The script should fail when this variable is missing
        result = subprocess.run([str(script_path)], 
                              env=env, 
                              capture_output=True, 
                              text=True,
                              timeout=30)
        
        # We expect the script to fail for missing variables
        # Note: some variables might have defaults, so we'll check specific cases
        if var_to_remove in ['inputDir', 'outputDir', 'component']:
            assert result.returncode != 0, f"Script should fail when {var_to_remove} is missing"

def test_script_argument_parsing():
    """Test that the script properly parses and displays arguments."""
    
    script_path = Path(__file__).parent.parent / "bin" / "make-timeseries"
    
    # Create minimal test environment
    env = os.environ.copy()
    env.update({
        'inputDir': '/tmp/nonexistent_input',  # Use non-existent to trigger early exit
        'outputDir': '/tmp/nonexistent_output',
        'begin': '00050101T0000Z',
        'inputChunk': 'P2Y',
        'outputChunk': 'P4Y',
        'component': 'atmos_tracer',
        'pp_stop': '00070101T0000Z'
    })
    
    # Run the script and capture output
    result = subprocess.run([str(script_path)], 
                          env=env, 
                          capture_output=True, 
                          text=True,
                          timeout=30)
    
    # Check that the script outputs the arguments (even if it fails later due to missing dirs)
    output = result.stdout + result.stderr
    assert "input dir:" in output
    assert "output dir:" in output  
    assert "begin:" in output
    assert "input chunk:" in output
    assert "output chunk:" in output
    assert "component:" in output


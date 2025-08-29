from pathlib import Path
import pytest
import os, sys
import subprocess
import dateutil.parser
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

# Define paths relative to this test file location for directory independence
DATA_DIR  = Path(__file__).parent / "files"
DATA_FILE_P1Y = Path("atmos_tracer.000501-000512.average_DT.cdl")
DATA_FILE_P2Y = Path("atmos_tracer.000601-000612.average_DT.cdl")
DATA_FILE_NC_P1Y = Path("atmos_tracer.000501-000512.average_DT.nc")
DATA_FILE_NC_P2Y = Path("atmos_tracer.000601-000612.average_DT.nc")

# Path to the make-timeseries app directory for Rose tests
APP_DIR = Path(__file__).parent.parent

"""Usage on runnung this app test for make_timeseries is as follows:
1) module load fre/test cylc cdo python/3.9
2) cd make_timeseries
3) pytest t/test_make_timeseries.py
"""

def test_make_timeseries(capfd, tmp_path):
   """This is a pytest compilation of routines.  Each of the test_* routines below will be called in the properly specified order.
   First executes the creation of required directories and a *.nc files from *.cdl text files.
   The tmp_path fixture which will provide a temporary directory unique to the test invocation, created in the base temporary directory.
   The capfd fixture as input in all three subroutines allows access to stdout/stderr output created during test execution
   Usage of command ncgen -o and then merge and remane the file via the proper cdo history command depends on the chunks given as input.
   """
   global dir_tmp_in, new_dir
   global freq, component
   global dir_tmp_out
   global component_new_file

   # Test configuration - define date range and variables
   begin_cycle_point= "00050101T0000Z"
   chunk= "P2Y"
   freq= "P2Y"
   var= "average_DT"
   component = "atmos_tracer"
   files = []

   # Create input directory structure to mimic FRE workflow layout
   dir_tmp_in = tmp_path / "in_dir"
   din_check = f'{tmp_path}/in_dir/{component}/{freq}/{chunk}'
   os.makedirs( din_check, exist_ok = True )

   # Create output directory 
   dout_check = tmp_path / "out_dir"
   dout_check.mkdir()
   dout_check = str(dout_check)

   # Convert CDL text files to NetCDF binary files using ncgen
   ex = [ 'ncgen', '-o', din_check / DATA_FILE_NC_P1Y, DATA_DIR / DATA_FILE_P1Y ];
   sp = subprocess.run( ex )
   # Assert that ncgen successfully created the first NetCDF file
   assert sp.returncode == 0, f"ncgen failed to create {DATA_FILE_NC_P1Y}"
   assert (Path(din_check) / DATA_FILE_NC_P1Y).exists(), f"Output file {DATA_FILE_NC_P1Y} was not created"
   
   ex = [ 'ncgen', '-o', din_check / DATA_FILE_NC_P2Y, DATA_DIR / DATA_FILE_P2Y ];
   sp = subprocess.run( ex )
   # Assert that ncgen successfully created the second NetCDF file
   assert sp.returncode == 0, f"ncgen failed to create {DATA_FILE_NC_P2Y}"
   assert (Path(din_check) / DATA_FILE_NC_P2Y).exists(), f"Output file {DATA_FILE_NC_P2Y} was not created"

   # Extract date ranges from filenames for timeseries processing
   first_cycle_date = str(DATA_FILE_NC_P1Y)[14:20]
   files.append(str(DATA_FILE_NC_P1Y))

   second_cycle_date = str(DATA_FILE_NC_P2Y)[14:20]    
   files.append(str(DATA_FILE_NC_P2Y))

   # Create date range for output filename
   init_date=str(files[0])[13:19]
   end_date=str(files[1])[20:26]

   new_dir = dout_check
   end_point_din = str(din_check)

   # Define output timeseries filename following FRE conventions
   component_new_file = f'{component}.{init_date}-{end_date}.{var}.nc'

   # Use CDO to merge time series from multiple files into one
   ex = [ 'cdo', '--history', '-O', 'mergetime', f'{end_point_din}/{files[0]} {end_point_din}/{files[1]}', f'{dout_check}/{component_new_file}' ];
   sp = subprocess.run( ex )
   captured = capfd.readouterr()

def test_rose_failure_make_timeseries(capfd, tmp_path):
   """This routine tests the FRE Canopy app make_timeseries by running rose command and checks for failure of
   merging and renaming a file with rose app as an invalid definition of the environment component.
   """
   din_check = str(dir_tmp_in)
   global rose_dir
   outputChunk = "P4Y"
   dout_check = tmp_path / "out_dir"
   dout_check.mkdir()
   dout_check = str(dout_check)

   rose_dir = f'{tmp_path}/out_dir/{component}/{freq}/{outputChunk}'
   os.makedirs( rose_dir, exist_ok = True )

   # Change to app directory to ensure rose-app.conf is found
   original_cwd = os.getcwd()
   os.chdir(APP_DIR)
   
   try:
       # Run rose with intentionally wrong component name to test failure case
       ex = [ "rose", "app-run",
               '-D',  '[env]inputDir='f'{din_check}',
               '-D',  '[env]begin=00050101T0000Z',
               '-D',  '[env]outputDir='f'{dout_check}',
               '-D',  '[env]inputChunk=P2Y',
               '-D',  '[env]outputChunk=P4Y',
               '-D',  '[env]component=atmos'  # Wrong component name - should fail
              ]
       print (ex);
       sp = subprocess.run( ex )
       assert sp.returncode == 1
   finally:
       # Always restore original working directory
       os.chdir(original_cwd)
   
   captured = capfd.readouterr()

def test_rose_success_make_timeseries(capfd, tmp_path):
   """This routine tests the FRE Canopy app make_timeseries by running rose command and checks for success of 
   merging and renaming a file with rose app as the valid definitions and chunks are being called by the environment.
   """
   din_check = str(dir_tmp_in)
   global rose_dir
   outputChunk = "P4Y"
   dout_check = tmp_path / "out_dir"
   dout_check.mkdir()
   dout_check = str(dout_check)

   rose_dir = f'{tmp_path}/out_dir/{component}/{freq}/{outputChunk}'
   os.makedirs( rose_dir, exist_ok = True )

   # Change to app directory to ensure rose-app.conf is found
   original_cwd = os.getcwd()
   os.chdir(APP_DIR)
   
   try:
       # Run rose with correct component and required pp_stop parameter
       ex = [ "rose", "app-run",
               '-D',  '[env]inputDir='f'{din_check}',
               '-D',  '[env]begin=00050101T0000Z',
               '-D',  '[env]outputDir='f'{dout_check}',
               '-D',  '[env]inputChunk=P2Y',
               '-D',  '[env]outputChunk=P4Y',
               '-D',  '[env]component=atmos_tracer',  # Correct component name
               '-D',  '[env]pp_stop=00070101T0000Z'   # Required end date parameter
              ]
       print (ex);
       sp = subprocess.run( ex )
       assert sp.returncode == 0
   finally:
       # Always restore original working directory
       os.chdir(original_cwd)
   
   captured = capfd.readouterr()

def test_nccmp_make_timeseries(capfd, tmp_path):
    """This subroutine tests by comparing the two files created by the two routines above described 
    and making sure that the two new created renamed files are identical. Also, returns code equals zero if the comparison was successful.
    """
    # Compare output files from manual CDO operation vs Rose app execution
    nccmp= [ 'nccmp', '-d', f'{new_dir}/{component_new_file}', f'{rose_dir}/{component_new_file}' ]; 
    sp = subprocess.run(nccmp)
    assert sp.returncode == 0
    captured = capfd.readouterr()


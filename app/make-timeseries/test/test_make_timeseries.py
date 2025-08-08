from pathlib import Path
import pytest
import os, sys
import subprocess
import dateutil.parser
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

DATA_DIR  = Path("test-data")
DATA_FILE_P1Y = Path("atmos_tracer.000501-000512.average_DT.cdl")
DATA_FILE_P2Y = Path("atmos_tracer.000601-000612.average_DT.cdl")
DATA_FILE_NC_P1Y = Path("atmos_tracer.000501-000512.average_DT.nc")
DATA_FILE_NC_P2Y = Path("atmos_tracer.000601-000612.average_DT.nc")

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

   begin_cycle_point= "00050101T0000Z"
   chunk= "P2Y"
   freq= "P2Y"
   var= "average_DT"
   component = "atmos_tracer"
   files = []

   dir_tmp_in = tmp_path / "in_dir"
    
   din_check = f'{tmp_path}/in_dir/{component}/{freq}/{chunk}'
   os.makedirs( din_check, exist_ok = True )

   dout_check = tmp_path / "out_dir"
   dout_check.mkdir()
   dout_check = str(dout_check)

   ex = [ 'ncgen', '-o', din_check / DATA_FILE_NC_P1Y, DATA_DIR / DATA_FILE_P1Y ];
   sp = subprocess.run( ex )
   ex = [ 'ncgen', '-o', din_check / DATA_FILE_NC_P2Y, DATA_DIR / DATA_FILE_P2Y ];
   sp = subprocess.run( ex )

   first_cycle_date = str(DATA_FILE_NC_P1Y)[14:20]

   files.append(str(DATA_FILE_NC_P1Y))

   second_cycle_date = str(DATA_FILE_NC_P2Y)[14:20]    
    
   files.append(str(DATA_FILE_NC_P2Y))

   init_date=str(files[0])[13:19]

   end_date=str(files[1])[20:26]

   new_dir = dout_check
   end_point_din = str(din_check)

   component_new_file = f'{component}.{init_date}-{end_date}.{var}.nc'

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

   ex = [ "rose", "app-run",
           '-D',  '[env]inputDir='f'{din_check}',
           '-D',  '[env]begin=00050101T0000Z',
           '-D',  '[env]outputDir='f'{dout_check}',
           '-D',  '[env]inputChunk=P2Y',
           '-D',  '[env]outputChunk=P4Y',
           '-D',  '[env]component=atmos'
          ]
   print (ex);
   sp = subprocess.run( ex )
   assert sp.returncode == 1
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

   ex = [ "rose", "app-run",
           '-D',  '[env]inputDir='f'{din_check}',
           '-D',  '[env]begin=00050101T0000Z',
           '-D',  '[env]outputDir='f'{dout_check}',
           '-D',  '[env]inputChunk=P2Y',
           '-D',  '[env]outputChunk=P4Y',
           '-D',  '[env]component=atmos_tracer'
           '-S',  './../rose-app.conf'
          ]
   print (ex);
   sp = subprocess.run( ex )
   assert sp.returncode == 0
   captured = capfd.readouterr()

def test_nccmp_make_timeseries(capfd, tmp_path):
    """This subroutine tests by comparing the two files created by the two routines above described 
    and making sure that the two new created renamed files are identical. Also, returns code equals zero if the comparison was successful.
    """
    nccmp= [ 'nccmp', '-d', f'{new_dir}/{component_new_file}', f'{rose_dir}/{component_new_file}' ]; 
    sp = subprocess.run(nccmp)
    assert sp.returncode == 0
    captured = capfd.readouterr()


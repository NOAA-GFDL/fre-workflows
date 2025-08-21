from pathlib import Path
import pytest
import os, sys
import subprocess
import dateutil.parser
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta



"""Usage on runnung this app test for make_timeseries is as follows:
1) module load fre/test cylc cdo python/3.9
2) cd make_timeseries
3) pytest t/test_make_timeseries.py
"""


def test_make_timeseries(capfd, tmp_path):
    global dir_tmp_in, new_dir
    global freq, component
    global dir_tmp_out
    global component_new_file

    TEST_DIR = Path(__file__).resolve().parents[0]
    DATA_DIR = Path(f'{TEST_DIR}/files')
    DATA_FILE_P1Y = Path("atmos_tracer.000501-000512.average_DT.cdl")
    DATA_FILE_P2Y = Path("atmos_tracer.000601-000612.average_DT.cdl")
    DATA_FILE_NC_P1Y = Path("atmos_tracer.000501-000512.average_DT.nc")
    DATA_FILE_NC_P2Y = Path("atmos_tracer.000601-000612.average_DT.nc")
    
    component = "atmos_tracer"
    chunk = freq = "P2Y"
    dir_tmp_in = tmp_path / "in_dir"
    din_check = f'{tmp_path}/in_dir/{component}/{freq}/{chunk}'
    os.makedirs(din_check, exist_ok = True)

    dout_check = tmp_path / "out_dir"
    dout_check.mkdir()
    dout_check = str(dout_check)

    ex = ['ncgen', '-o', din_check / DATA_FILE_NC_P1Y, DATA_DIR / DATA_FILE_P1Y]
    sp = subprocess.run(ex)
    assert sp.returncode == 0, f'ncgen failed: {ex}'

    ex = ['ncgen', '-o', din_check / DATA_FILE_NC_P2Y, DATA_DIR / DATA_FILE_P2Y]
    sp = subprocess.run(ex)
    assert sp.returncode == 0, f'ncgen failed: {ex}'

    first_cycle_date = str(DATA_FILE_NC_P1Y)[14:20]
    second_cycle_date = str(DATA_FILE_NC_P2Y)[14:20]
    
    new_dir = dout_check
    component_new_file = f'{component}.{first_cycle_date}-{second_cycle_date}.average_DT.nc'

    ex = ['cdo', '--history', '-O', 'mergetime', f'{din_check}/{DATA_FILE_NC_P1Y.name}', f'{din_check}/{DATA_FILE_NC_P2Y.name}', f'{dout_check}/{component_new_file}']
    print(f'Running: {ex}')
    sp = subprocess.run(ex)
    assert sp.returncode == 0, f'cdo failed: {ex}'
    captured = capfd.readouterr()

    # Now file creation is confirmed
    assert Path(f'{din_check}/{DATA_FILE_NC_P1Y.name}').exists()
    assert Path(f'{din_check}/{DATA_FILE_NC_P2Y.name}').exists()
    assert Path(f'{dout_check}/{component_new_file}').exists()


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

   rose_dir = f'app/make-timeseries/test/{tmp_path}/out_dir/{component}/{freq}/{outputChunk}'
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
           '-D',  f'[env]inputDir={din_check}',
           '-D',  '[env]begin=00050101T0000Z',
           '-D',  f'[env]outputDir={dout_check}',
           '-D',  '[env]inputChunk=P2Y',
           '-D',  '[env]outputChunk=P4Y',
           '-D',  '[env]component=atmos_tracer',
           '-D',  '[env]pp_stop=00070102T0000Z',
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
    captured = capfd.readouterr()
    print("THE ERROR OUTPUT FOR NCCMP IS   ",captured)
    assert sp.returncode == 0


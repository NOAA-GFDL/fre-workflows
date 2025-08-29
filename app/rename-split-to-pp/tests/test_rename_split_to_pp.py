#tests rename_split_to_pp with a minimal python wrapper
#test cases: regrid/native, static/ts
#fail test cases: no files in your input directory/subdirs; input files are not named according to our very specific naming conventions


#https://stackoverflow.com/questions/67631/how-can-i-import-a-module-dynamically-given-the-full-path
#/archive/cew/CMIP7/ESM4/DEV/ESM4.5_staticfix/ppan-prod-openmp/history/00010101.nc.tar

import pytest
import sys
import os
from os import path as osp
import subprocess
import re
import pprint

ROOTDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print("Root directory: " + ROOTDIR)

TEST_DATA_DIR = os.path.join(ROOTDIR, "tests/test-data")
print(TEST_DATA_DIR)
INDIR = os.path.join(TEST_DATA_DIR, "input")
OUTDIR = os.path.join(TEST_DATA_DIR, "output")
OG = os.path.join(TEST_DATA_DIR, "orig-output")

#RENAME_SPLIT_TO_PP = osp.join(ROOTDIR, "app/rename-split-to-pp/bin/rename_split_to_pp_wrapper.py")
sys.path.append(os.path.join(ROOTDIR, "bin"))
print(sys.path)
from rename_split_to_pp_wrapper import call_rename_split_to_pp

def test_rename_split_to_pp_setup():
    '''
    sets up the test files for the test cases
    '''
    nc_files = []; ncgen_commands = []
    for path,subdirs,files in os.walk(TEST_DATA_DIR):
      for name in files:
        if name.endswith("cdl"):
          name_out = re.sub(".cdl", ".nc", name)
          cdl_cmd = ["ncgen3", "-k", "netCDF-4", "-o", osp.join(path,name_out), osp.join(path,name)]
          nc_files.append(osp.join(path,name_out))
          ncgen_commands.append(cdl_cmd)
    for cmd in ncgen_commands:
      out0 = subprocess.run(cmd, capture_output=True)
      if out0.returncode != 0:
        print(out0.stdout)
    nc_exists = [osp.isfile(el) for el in nc_files]
    assert all(nc_exists)
    

# cases = {'ts_rg': [osp.join(INDIR, "atmos_daily-regrid"),   osp.join(OUTDIR,"atmos_daily-regrid"), osp.join(OG, "atmos_daily-regrid/regrid/atmos_daily/P1D/P6M/")], 
#          'ts_nrg':  [osp.join(INDIR, "atmos_daily-native"), osp.join(OUTDIR,"atmos_daily-native"), osp.join(OG, "atmos_daily-native/atmos_daily/P1D/P6M/")],
#          'st_rg': [osp.join(INDIR, "ocean_static-regrid"),  osp.join(OUTDIR,"ocean_static-regrid"), osp.join(OG, "ocean_static-regrid/regrid/ocean_static/P0Y/P0Y/")], 
#          'st_nrg':  [osp.join(INDIR, "ocean_static-native"),osp.join(OUTDIR,"ocean_static-native"), osp.join(OG, "ocean_static-native/ocean_static/P0Y/P0Y/")],
#          'f_bf':   [osp.join(INDIR, "fail_filenames"), osp.join(OUTDIR,"fail_filenames"), ""], 
#          'f_nf':   [osp.join(INDIR, "fail_nofiles"),   osp.join(OUTDIR,"fail_nofiles"), ""]}
#             
# @pytest.mark.parametrize("inputDir,outputDir,hist_source,do_regrid,expected_dirpath", 
#                         [ pytest.param(cases['ts_nrg'][0], cases['ts_nrg'][1], 'atmos_daily', "False", cases['ts_nrg'][2], id="ts_noregrid"),
#                           pytest.param(cases['ts_rg'][0], cases['ts_rg'][1], 'atmos_daily', "True", cases['ts_rg'][2],id="ts_regrid"),
#                           pytest.param(cases['st_nrg'][0], cases['st_nrg'][1], 'ocean_static', "False", cases['st_nrg'][2],id="static_noregrid"),
#                           pytest.param(cases['st_rg'][0], cases['st_rg'][1], 'ocean_static', "True", cases['st_rg'][2], id="static_regrid"),
#                           pytest.param(cases['f_bf'][0], cases['f_bf'][1], 'atmos_daily', "True", cases['f_bf'][2], id="fail_badfilename", marks=pytest.mark.xfail()),
#                           pytest.param(cases['f_nf'][0], cases['f_nf'][1], 'atmos_daily', "False", cases['f_nf'][2], id="fail_noinput", marks=pytest.mark.xfail())
#                          ])
@pytest.mark.parametrize("hist_source,do_regrid,og_suffix", 
                          [ pytest.param("atmos_daily", False, "P1D/P6M/", id="day-native"),
                          pytest.param("atmos_daily", True, "P1D/P6M/", id="day-regrid"),
                          # pytest.param("river_month", False, "P1D/P6M/", id="mon-native"),
                          # pytest.param("river_month", True, "P1D/P6M/", id="mon-regrid"),
                          # pytest.param("ocean_annual", False, "P1D/P6M/", id="year-native"),
                          # pytest.param("ocean_annual", True, "P1D/P6M/", id="year-regrid"),
                          pytest.param("ocean_static", False, "P0Y/P0Y/", id="static-native"),
                          pytest.param("ocean_static", True, "P0Y/P0Y/", id="static-regrid"),
                          pytest.param("fail_filenames", False, "", id="fail-badfilename", marks=pytest.mark.xfail()),
                          pytest.param("fail_nofiles", False, "", id="fail-noinput", marks=pytest.mark.xfail()) ])
def test_rename_split_to_pp_run(hist_source, do_regrid, og_suffix):
    '''
    Tests the running of rename-split-to-pp, which takes 3 input args:
      hist_source: source of the history data, used to build input and output paths
      do_regrid: whether to do regridding, boolean, changes dir structure
      og_suffix: the frequency suffix that rename-split-to-pp should be adding to
         the output data dir structure
    rename-split-to-pp takes 4 arguments, which are set as env variables:
      inputDir (inputDir)  - location of your input files, output from split-netcdf
      outputDir (outputDir) - location to which to write your output files
      component (history_source) - VERY BADLY NAMED. What split-netcdf is calling the hist_source after the rewrite.
      use_subdirs (do_regrid) - either set to 1 or unset. 1 is used for the regridding case. 
    These tests operate under several test cases:
      - sucess:
        - timeseries, no regridding
        - timeseries, regridding
        - static file, no regridding
        - static file, regridding
      - failure:
        - files in input don't match naming convention, raises error TBD
        - no files in input dir, raises error TBD
    For the moment, rename=split-to-pp isn't doing any rewriting of files -
    it's copying files to new locations and verifying that they have the 
    right number of timesteps. 
    I've included hooks for functions that check on data + metadata, but we
    really don't need them yet.
    TODO:
      - when this is ported to python, the xfail tests should check for the python error that gets raised - 
      but until that point, not a whole lot of point in checking on a raised exception here
    '''
    # if not os.path.isdir(outputDir):
    #   os.mkdir(outputDir)
    # callstat = call_rename_split_to_pp(inputDir, outputDir, hist_source, do_regrid)
    # # #####
    
    print("do_regrid " + str(do_regrid))
    if do_regrid:
        print("do_regrid is set to True")
        os.environ["use_subdirs"] = "True"
        dir_suffix = hist_source + "-regrid"
        origDir = osp.join(OG, dir_suffix, "regrid", hist_source, og_suffix)
    else:
        dir_suffix = hist_source + "-native"
        origDir = osp.join(OG, dir_suffix, hist_source, og_suffix)
    
    inputDir = osp.join(INDIR, dir_suffix)
    outputDir = osp.join(OUTDIR, dir_suffix)
    
    os.environ["inputDir"]  = inputDir
    os.environ["outputDir"] = outputDir
    os.environ["component"] = hist_source
    
    if not osp.exists(outputDir):
      os.makedirs(outputDir)

    cmd = osp.join(ROOTDIR, "bin/rename-split-to-pp")
    out0 = subprocess.run(cmd, capture_output=True)
    if out0.returncode == 0:
      #check for 2 things:
      #are there files at the output dir path
      #is there a file in output dir path for each file in orig-output
      print(origDir)
      expected_files = [os.path.join(origDir, el) for el in os.listdir(origDir)]
      expected_files = [el for el in expected_files if el.endswith(".nc")]
      print("OG: " + ",".join(expected_files))
      print("OG_outdir: " + OUTDIR)
      out_files = [re.sub(OG, OUTDIR, el) for el in expected_files]
      print("printing output files:")
      print(" outfiles: " + ",".join(out_files))
      files_there = len(out_files) > 0
      print("files_there " + str(files_there))
      if files_there:
        outdir = os.path.dirname(out_files[0])
        print("outdir " + outdir)
        actual_out_files = [os.path.join(outdir,el) for el in os.listdir(outdir) if el.endswith(".nc")]
        print(actual_out_files)
        out_files.sort()
        actual_out_files.sort()
        files_paired = all([el[0] == el[1] for el in zip(out_files, actual_out_files)])
      else:
        files_paired = False
      assert all([files_there, files_paired])
    else:
      pprint.pp(out0.stdout.split(b"\n"), width=240)
      pprint.pp(out0.stderr.split(b"\n"), width=240)
      print("nonzero returncode")
      assert False

def test_rename_split_to_pp_cleanup():
    '''
    deletes the test files (any file ending with .nc) and output directories
    (any directory under output/)
    '''
    el_list = []
    dir_list = []
    #all dirs under output
    for path, subdirs, files in os.walk(OUTDIR):
      for name in subdirs:
        dir_list.append(osp.join(path,name))
    #all netcdf files
    for path, subdirs, files in os.walk(TEST_DATA_DIR):
      for name in files:
        if name.endswith(".nc"):
          el_list.append(osp.join(path,name))
    el_list = list(set(el_list))
    for f in el_list:
      os.remove(f)
    dir_list.sort(reverse=True)
    for d in dir_list:
      os.rmdir(d)
    dir_deleted = [not osp.isdir(el) for el in dir_list]
    el_deleted = [not osp.isdir(el) for el in el_list]
    assert all(el_deleted + dir_deleted)

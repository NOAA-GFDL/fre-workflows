#tests rename_split_to_pp with a minimal python wrapper
#test cases: regrid/native, static/ts
#fail test cases: no files in your input directory/subdirs; input files are not named according to our very specific naming conventions


#https://stackoverflow.com/questions/67631/how-can-i-import-a-module-dynamically-given-the-full-path
#/archive/cew/CMIP7/ESM4/DEV/ESM4.5_staticfix/ppan-prod-openmp/history/00010101.nc.tar

import pytest
import os
from os import path

ROOTDIR = dirname(dirname(os.path.abspath(__file__)))
print("Root directory: " + ROOTDIR)

TESTDIR = os.path.join(ROOTDIR, "tests")
INDIR = os.path.join(TESTDIR, "test_files_rename_split_to_pp/input")
OUTDIR = os.path.join(TESTDIR, "test_files_rename_split_to_pp/output")


RENAME_SPLIT_TO_PP = osp.join(ROOTDIR, "app/rename-split-to-pp/bin/rename_split_to_pp_wrapper.py")

def test_rename_split_to_pp_setup():
    '''
    sets up the test files for the test cases
    '''
    nc_files = []; ncgen_commands = []
    for path,subdirs,files in os.walk(testdir):
      for name in files:
        if name.endswith("cdl"):
          name_out = re.sub(".cdl", ".nc", name)
            cdl_cmd = ["ncgen3", "-k", "netCDF-4", "-o", name_out, name]
            nc_files.append(name_out)
            ncgen_commands.append(cdl_cmd)

@pytest.mark.parametrize("workdir,infile,outfiledir,varlist", 
                             [pytest.param(casedirs[0], cases["ts"]["nc"],
                                "new_all_ts_varlist",  "all", 
                                id="ts_all"), 
                              pytest.param(casedirs[0], cases["ts"]["nc"], 
                                "new_some_ts_varlist",
                                ",".join(some_ts_varlist),
                                id="ts_some"), 
                              pytest.param(casedirs[0], cases["ts"]["nc"], 
                                "new_none_ts_varlist", 
                                ",".join(none_ts_varlist), id='none'), 
                              pytest.param(casedirs[1], cases["static"]["nc"], 
                                "new_all_static_varlist",  "all", 
                                id="static_all"), 
                              pytest.param(casedirs[1], cases["static"]["nc"], 
                                "new_some_static_varlist",
                                ",".join(some_static_varlist),
                                id="static_some")])
def test_rename_split_to_pp_run():
    '''
    tests running rename-split-to-pp with various cases
    '''
    
def test_rename_split_to_pp_data():
    '''
    compare output data against saved output data
    '''

def test_rename_split_to_pp_metadata():
    '''
    compare output data against saved output metadata
    '''

def test_rename_split_to_pp_cleanup():
    '''
    deletes the test files and outputs for the test cases
    '''
    el_list = []
    dir_list = []
    for path, subdirs, files in os.walk(OUTPUT):
      for name in files:
        el_list.append(osp.join(path, name))
      for name in subdirs:
        dir_list.append(osp.join(path,name))
    netcdf_files = [el for el in el_list if el.endswith(".nc")]
    for nc in netcdf_files:
      pathlib.Path.unlink(Path(nc))
    newdir = [el for el in dir_list if osp.basename(el).startswith("new_")]
    for nd in newdir:
      pathlib.Path.rmdir(Path(nd))
    dir_deleted = [not osp.isdir(el) for el in newdir]
    el_deleted = [not osp.isdir(el) for el in netcdf_files]
    assert all(el_deleted + dir_deleted)

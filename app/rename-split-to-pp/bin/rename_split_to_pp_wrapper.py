#python wrapper for rename_split_to_pp
#used for the pytest tests, intended to be replaced
#once a full replacement for rename-split-to-pp exists

import os
import subprocess

def call_rename_split_to_pp(inputDir, outputDir, history_source, do_regrid):
    '''
    Calls rename-split-to-pp, which takes 4 environment variables:
      inputDir (inputDir)  - location of your input files, output from split-netcdf
      outputDir (outputDir) - location to which to write your output files
      component (history_source) - VERY BADLY NAMED. What split-netcdf is calling the hist_source after the rewrite.
      use_subdirs (do_regrid) - either set to 1 or unset. 1 is used for the regridding case.  
    '''
    os.environ["inputDir"]  = inputDir
    os.environ["outputDir"] = outputDir
    os.environ["component"] = history_source
    if do_regrid:
        os.environ["use_subdirs"] = 1
    #rename-split-to-pp is a bash script    
    app_loc = os.path.abspath("app/rename-split-to-pp/bin/rename-split-to-pp")
    ##and this file is currently located 3 directories up from the root of the repo
    #thisloc = os.path.abspath(__file__)
    out0,err0 = subprocess.run(app_loc, capture_output=True)
    

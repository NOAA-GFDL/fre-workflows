#!/usr/bin/env python


# QUESTION: is app/ really the right place for a python script like this? 
'''
old README seems to contradict internal desc in bash script.

 desc in bash version:
  Regrid variables from latlon/cubed-sphere/tripolar to latlon

 old desc in README:
  remaps from a spherical grid or (scalar or vector) data onto
  any grid (spherical or tripolar) using conservative scheme.
  Alternative schemes can be added if needed.

 my reworded desc in README:
  remaps scalar and/or vector fields. It is capable of remapping
  from a spherical grid onto a different (spherical, or tripolar)
  grid. By default, it does so using a conservative scheme.
  Additional, alternative schemes can be defined and used as well. 
'''

import os
from os import PathLike
import sys


import subprocess
from subprocess import Popen, PIPE


#import glob # maybe?
import pathlib
from pathlib import Path


# hopefully in the cylc conda env
import cdo


# thankfully i did that quick pythion rewrite of shared...
# now to see how well I did...
from . import shared
# i bet you i'll have to try all of these...
#import shared as shrd
#from shared import *
#from .shared import *

import typing
from typing import Tuple, List




### MAKE SURE THE TYPING HINTS ARE APPROPRIATE FOR PATHLIB
###                            THIS IS NONTRIVIAL
### see: https://stackoverflow.com/questions/72614755/python-typing-how-to-declare-a-variable-that-is-either-a-path-like-object-os-p
### see: https://stackoverflow.com/questions/58541722/what-is-the-correct-way-in-python-to-annotate-a-path-with-type-hints
def regrid_xy(input_dir: str = None, #this should probably be an os.PathLike, or pathlib.Path [not allowed though]
              output_dir: str = None,
              tmp_dir: str = None, 
              fregrid_remap_dir: str = None,
              grid_spec: str = None,
              begin: str = None,    # ISO datetime instead? 
              xy_interp: Tuple = ( ), # this has been a "default", but should be checked against yaml/roseconf
              component: List = [] ) :
    '''
    xy_interp = (lat, lon), tuple for immutability, lat/lon should be ints
    componenet = [string1, string2], list for mutability
 
    '''
    print('hello world')
    
    if any( [  input_dir is None , output_dir is None , tmp_dir is None ,
               fregrid_remap_dir is None , grid_spec is None ,
               components is None) or (componenets == []) or (len(components) = 0,
               xy_interp == ()) or (xy_interp  is None,
               len(xy_interp) != 2  ] ):
        raise Exception('input_dir) or (output_dir is none')

    



    
    
    return


# steering, local test/debug
if __name__=='__main__':
    regrid_xy()

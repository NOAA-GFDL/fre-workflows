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
import sys
import subprocess

#import glob # maybe?
import pathlib as pl

# hopefully in the cylc conda env
import cdo


# thankfully i did that quick pythion rewrite of shared...
# now to see how well I did...
from . import shared
# i bet you i'll have to try all of these...
#import shared as shrd
#from shared import *
#from .shared import *


def regrid_xy():
    print('hello world')
    return


# steering, local test/debug
if __name__=='__main__':
    regrid_xy()

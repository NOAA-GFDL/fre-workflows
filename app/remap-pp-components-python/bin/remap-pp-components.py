#!/bin/python

# Description:

import os
import glob
import sys
from pathlib import Path

# Read rose config files (for now)

# Parse yaml directly for rose-app info
#use configure to parse and save variables???? then use variables in here?

# Set variables
inputDir = os.environ['inputDir']
outputDir = os.environ['outputDir']
begin = os.environ['begin']
currentChunk = os.environ['currentChunk']
component = os.environ['component']
product = os.environ['product']
dirTSWorkaround = os.environ['dirTSWorkaround']

print("Arguments:")
print("    input dir: "+inputDir)
print("    output dir: "+outputDir)
print("    begin: "+begin)
print("    current chunk: "+currentChunk)
print("    components: "+component)
print("    product: "+product)
print("    dirTSWorkaround: "+dirTSWorkaround)
print("Utilities:")
COPY_TOOL = os.environ['COPY_TOOL']
type(COPY_TOOL)

# Verify input directory exists and is a directory
# Verify input directory exists and is a directory
if os.path.isdir(inputDir):
    print("Input directory is a valid directory")
else
    print("Error: Input directory "+ inputDir + " is not a valid directory")
    sys.exit(1)

# Verify output directory exists and is a directory
if os.path.isdir(outputDir):
    print("Output directory is a valid directory")
else
    print("Error: Output directory" + outputDir + " is not a valid directory")
    sys.exit(1)

# 

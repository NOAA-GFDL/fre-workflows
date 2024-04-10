#!/usr/bin/env python

# Description:

import os
import glob
import sys
#from pathlib import Path
import shared
import metomi.rose.config as mrc

# Set variables to play with
outputDir = os.getcwd()+"/rewrite_outputDir"
inputDir = os.getcwd()+"/rewrite_inputDir"
dirTSWorkaround = "1"
#ens_mem = "01"
product = "ts"

##################################
## Parse yaml directly for rose-app info
##use configure to parse and save variables???? then use variables in here?
#
## Set variables
#inputDir = os.environ['inputDir']
#outputDir = os.environ['outputDir']
#begin = os.environ['begin']
#currentChunk = os.environ['currentChunk']
#component = os.environ['component']
#product = os.environ['product']
#dirTSWorkaround = os.environ['dirTSWorkaround']
#
#print("Arguments:")
#print("    input dir: "+inputDir)
#print("    output dir: "+outputDir)
#print("    begin: "+begin)
#print("    current chunk: "+currentChunk)
#print("    components: "+component)
#print("    product: "+product)
#print("    dirTSWorkaround: "+dirTSWorkaround)
#print("Utilities:")
#COPY_TOOL = os.environ['COPY_TOOL']
#type(COPY_TOOL)

# Verify input directory exists and is a directory
if os.path.isdir(inputDir):
    print("Input directory is a valid directory")
else:
    print("Error: Input directory "+ inputDir + " is not a valid directory")
    sys.exit(1)

# Verify output directory exists and is a directory
if os.path.isdir(outputDir):
    print("Output directory is a valid directory")
else:
    print("Error: Output directory" + outputDir + " is not a valid directory")
    sys.exit(1)
###################################

# Read rose config files (for now)
# Define config file
# for now
config = mrc.load("/home/Dana.Singh/pp/refactor/REMAP/app/remap-pp-components-python/bin/rose-app.conf")
#config = mrc.load("/home/Dana.Singh/pp/refactor/REMAP/app/remap-pp-components-python/rose-app-run.conf")

#def movedirs(dict,field):
#  #if ens_mem != None:
#  #  c = dict.get(field).get_value()
#  #  #os.makedirs(c+"/"+ens_mem,exist_ok=True)
#  #  os.chdir(c+"/"+ens_mem)
#  #else:
#    c = dict.get(field).get_value()
#    #os.makedirs(c,exist_ok=True)
#    os.chdir(c)
#  #print(os.getcwd())


#os.chdir(inputDir)
#print(os.getcwd())

for comp in config.get():
  #print(comp)
  os.chdir(inputDir)
  if comp != "env" and comp != "command":
    #print(comp)
    #if comp != None and comp != components:
    #    break
 
    #print(config.get([comp]))
    compOut = config.get([comp])
    fields = compOut.get_value()
    #print(fields)
    #print(compOut)
    #print(compOut.get_value().get("grid")) #get("grid"))

    #GRID
    if fields.get("grid"):
      #movedirs(fields,"grid")
      #if ens_mem != None:
      #else:
      grid = fields.get("grid").get_value()
      #os.makedirs(grid,exist_ok=True)
      os.chdir(grid)

      #SOURCES
      if fields.get("sources"):
        #movedirs(fields,"sources")
        sources = fields.get("sources").get_value()
        #os.makedirs(sources,exist_ok=True)
        os.chdir(sources)


        #FREQ
        if fields.get("freq"):
          #movedirs(fields,"freq")
          freq = fields.get("freq").get_value()
          #os.makedirs(freq,exist_ok=True)
          os.chdir(freq)


          #CHUNK
          if fields.get("chunk"):
            #movedirs(fields,"chunk")
            chunk = fields.get("chunk").get_value()
            #os.makedirs(chunk,exist_ok=True)
            os.chdir(chunk)

            # DEFINE DIR
            #if ens
              #if dirTSWorkaround:
              #  dir = f"{outputDir}/{comp}/ts/{ens_mem}/{freq}/{chunk}"
              #else
              #  dir = f"{outputDir}/{comp}/{ens_mem}/{freq}/{chunk}"
            #else
            if dirTSWorkaround:
              dir = f"{outputDir}/{comp}/ts/{freq}/{chunk}" 
              #print(dir)
            else:
              dir = f"{outputDir}/{comp}/{freq}/{chunk}"
          
            os.makedirs(dir,exist_ok=True)

            ## Create bronx-style symlinks for TS only
            hi = shared.freq_to_legacy()
            #
            #
 
            files = []
            if freq == "P0Y":
              #print(freq)
              files.append("hi")
              files.append("bye")
              files.append("seeya")
              #if vars
              #else
            #else:
            #  if product == "ts":
            #  elif product == "av":
            #  else:
            #   
            #  if vars:
            #  else
            #  if product == "av" and currentChunk == "P1Y":
            #

            #### A LOT OF OUTPUT THOUGH....B/C ITS FOR EACH FILE
            for f in files:
              #print(f)
              if not os.path.exists(os.getcwd()+"/"+f):
                print(f"\nError: No input files found. \n{f} not in {os.getcwd()}")
                sys.exit(1)
              
              #newfile = comp.file
              #if not os.path.isfile("f{dir}/{newfile}"):
                #copy/softlink
            

## To-do: what if theres multiple sources?

#!/usr/bin/env python

# Description:

import os
import glob
import sys
#from pathlib import Path
import shared
import metomi.rose.config as mrc

# Set variables to play with
inputDir = os.getcwd()+"/rewrite_inputDir"
outputDir = os.getcwd()+"/rewrite_outputDir"
begin = "00010101T0000Z" 
currentChunk = "P0Y"
components = ["atmos", "ocean"]
product = "ts"
dirTSWorkaround = "1"
ens_mem = "" 
#ens_mem = "01"


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
#ens_mem = os.environ['ens_mem']
#
#print("Arguments:")
#print("    input dir: "+inputDir)
#print("    output dir: "+outputDir)
#print("    begin: "+begin)
#print("    current chunk: "+currentChunk)
#print("    components: "+component)
#print("    product: "+product)
#print("    dirTSWorkaround: "+dirTSWorkaround)
#print("    ens_mem: "+ensmem)
#print("Utilities:")
#COPY_TOOL = os.environ['COPY_TOOL']
#type(COPY_TOOL)

def bronx_style(freq, chunk, ens_member, outDir, component):
  freq_legacy = shared.freq_to_legacy(freq)
  chunk_legacy = shared.chunk_to_legacy(chunk)
  if chunk_legacy == "error":
    print(f"Error: Skipping legacy directory for chunk: {chunk}")
  else:
    if ens_member:
      dir1 = f"{outDir}/{component}/ts/{ens_member}"
      os.chdir(f"{outDir}/{component}/ts/{ens_member}")
    else:
      dir1 = f"{outDir}/{component}/ts"
      os.chdir(f"{outDir}/{component}/ts")
    
    os.makedirs(freq_legacy, exist_ok=True)
    os.chdir(freq_legacy)
    
    if not os.path.exists(chunk_legacy):
      os.symlink(f"{dir1}/{freq}/{chunk}", chunk_legacy)

##############################################################
def remap(inputDir,outputDir,begin,currentChunk,components,product,dirTSWorkaround,ens_mem):
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
  # JUST FOR DEVELOPMENT
  config = mrc.load("/home/Dana.Singh/pp/refactor/REMAP/app/remap-pp-components-python/bin/rose-app.conf")

  for comp in config.get():
    #print(config.get())
    os.chdir(inputDir)
    if comp != "env" and comp != "command":
      #print(comp)
      if components != None and comp not in components:
        continue  
   
      ## TO-DO: define vars (FIX)
      #vars = config
      vars = "all"
      #print(vars)
  
      #compOut: variable/field per component in rose config
      compOut = config.get([comp])
      #fields: info for each field 
      fields = compOut.get_value()
  
      #GRID
      if fields.get("grid"):
        grid = fields.get("grid").get_value()
        if ens_mem != None:
          newdir = f"{grid}/{ens_mem}"
          os.makedirs(newdir,exist_ok=True)
          os.chdir(newdir)
        else:
          os.makedirs(grid,exist_ok=True)
          os.chdir(grid)

        #SOURCES
        if fields.get("sources"):
          sources = fields.get("sources").get_value()
          #print(sources)
          os.makedirs(sources,exist_ok=True)
          os.chdir(sources)

          #FREQ
          if fields.get("freq"):
            freq = fields.get("freq").get_value()
            os.makedirs(freq,exist_ok=True)
            os.chdir(freq)

            #CHUNK
            if fields.get("chunk"):
              chunk = fields.get("chunk").get_value()
              os.makedirs(chunk,exist_ok=True)
              os.chdir(chunk)

              # DEFINE DIR
              if ens_mem:
                if dirTSWorkaround:
                  dir = f"{outputDir}/{comp}/ts/{ens_mem}/{freq}/{chunk}"
                else:
                  dir = f"{outputDir}/{comp}/{ens_mem}/{freq}/{chunk}"
              else:
                if dirTSWorkaround:
                  dir = f"{outputDir}/{comp}/ts/{freq}/{chunk}" 
                  #print(dir)
                else:
                  dir = f"{outputDir}/{comp}/{freq}/{chunk}"
          
              os.makedirs(dir,exist_ok=True)

              # Create bronx-style symlinks for TS only
              if dirTSWorkaround:
                bronx_style(freq = freq, 
                            chunk = chunk, 
                            ens_member = ens_mem,
                            outDir = outputDir,
                            component = comp)

########################################################################### 
              FILES = []
              if freq == "P0Y":
                if vars == "all":
                  files = glob.glob(f"{sources}.*.tile?.nc")
                  #print(files)
                else:
                  for v in vars: 
                    files = glob.glob(f"{sources}.{v}?.tile?.nc")
              else:
                if product == "ts":
                  date = shared.truncate_date(begin, freq)
                elif product == "av":
                  date = shared.truncate_date(begin, "P1Y")
                else:
                  print("Product not set to ts or av.")
                  sys.exit(2)

                if vars == "all":
                  files = glob.glob(f"{sources}/{date1}-*.tile?.nc")
                else:
                  files = ""
                  for v in vars:
                    files = glob.glob(f"{sources}.{date1}-*.{v}?.tile?.nc")

                if product == "av" and currentChunk == "P1Y":
                  files = glob.glob(f"{sources}.{date1}.*.tile?.nc")
	
#############
#              #print(freq)
#              files.append("atmos_month.bk.tile2.nc")
#              files.append("bye")
#              files.append("seeya")


              #### could be a lot of output
              for f in files:
                #print(f)
                if not os.path.exists(os.getcwd()+"/"+f):
                  print(f"\nError: No input file found. \n{f} not in {os.getcwd()}")
                  sys.exit(1)
                else:
                  newfile = f"{comp}.{f}"

                  if os.path.exists(f"{dir}/{newfile}"):
                    os.remove(f"{dir}/{newfile}")
                
                  #soft link
                  os.symlink(f"{os.getcwd()}/{f}",f"{dir}/{newfile}") 
                  ## OR COPY TOOL??????           

## To-do: what if theres multiple sources?

  print("Component remapping complete")


if __name__ == '__main__':
   remap(inputDir,outputDir,begin,currentChunk,components,product,dirTSWorkaround,ens_mem)

#def main():
#    return remap()
#
## steering, local test/debug
#if __name__=='__main__':
#    main()


#!/app/conda/miniconda/envs/python-3.9-20220720/bin/python

# Author: Dana Singh
# Description: Script parses user-edit yaml, creates/implements the changes in rose-suite-exp.conf, rose-app.conf, bin/install-exp, and checks that filepaths exist

import os
from pathlib import Path  
import yaml
import click
#from jsonschema import validate, ValidationError, SchemaError
#import json

# Function to parse and validate user defined edits.yaml 
def parseyaml(file):
    # Load yaml
    with open(file,'r') as f:
        y=yaml.safe_load(f)

    ### TO-DO: validate user-yaml
    # Load the json schema: .load() (vs .loads()) reads and parses the json in one
    #with open("schema.json") as s:
    #    schema = json.load(s)
    
    # Validate the YAML
    #try:
    #    validate(instance=y,schema=schema)
    #    print("Yaml configuration validated")
    #except:
    #    print('ERR')
 
    d=[]
    for k1 in y:
        for k2 in y[k1]:
            for dict in y[k1][k2]:
                d.append(dict)    
    return d

@click.command()
@click.argument('yamlfile', nargs=1)
def yamlInfo(yamlfile):
    yml = parseyaml(yamlfile)
    # Parse information in dictionary 
    for items in yml:
        for key,value in items.items():
            # Define paths in yaml
            if key == 'path' and value != None:
                p=Path(value)
            ## ROSE-SUITE-EXP-CONFIG EDITS
            # Create rose-suite-exp.conf and populate it with user-defined edits in edits.yaml
            if key == "rose-suite-exp-configuration":
                with open(p,'w') as f:
                    f.write('[template variables]\n')
                    f.write('## Information for requested postprocessing, info to pass to refineDiag/preanalysis scripts, info for epmt, and info to pass to analysis scripts \n')
    
                for key,value in value.items():
                    # If there is a defined value in the yaml, create and write to a rose-suite-EXP.conf
                    if value != None:
                        with open(p,'a') as f:
                            # Add in comment for experiment specific information
                            if key == "HISTORY_DIR":
                                f.write("## Information about experiment\n")

                            # If value is of type boolean, do not add quotes in configuration. If the value is a string, write value in configuration with quotes.
                            if value == True or value == False:
                                f.write(f'{key}={value}\n\n')
                            else:
                                f.write(f'{key}="{value}"\n\n')

            ## Check if filepath exists. If path does not exist, output error message. 
            if key == 'path' and value != None:
                if p.exists() == True:
                    print(f"Path to {p} EXISTS")
                elif p.exists() == False:
                    print(f"ERR: Path {p} MUST BE CREATED")
  
            ## ROSE-APP-CONFIG EDITS
            # Open and write to rose-app.conf for regrid-xy and remap-pp-components 
            # Populate configurations with info defined in edits.yaml; path should exist
            if os.path.exists(p) and key == "rose-app-configuration":
                #regrid-xy and remap-pp-components 
                for v in value:
                    for key,value in v.items():
                         #write empty file and close; ensures file always starts empty 
                         open(p,'w').close()
                         for k in value:
                             for key,value in k.items():
                                 if value != None:
                                     # Append defined regrid and remap information from yaml
                                     with open(p,"a") as f:
                                         # Component is written on own line with brackets, followed by information for that component
                                         if key == "type":
                                             f.write("["+value+"]\n")
                                         if key != "type":
                                             f.write(key+"="+value+"\n")
    
            ## INSTALL-EXP SCRIPT EDIT
            # If alternate path for cylc-run directory defined in edits.yaml, add symlink creation option onto cylc install command
            # The file should exist, hence the file is read and lines are replaced with defined values in the yaml.
            if os.path.exists(p) and key == "install-option":
                for key,value in value.items():
                    with open(p,"r") as f:
                        rf=f.readlines()
                        if value != None:
                            for line in rf:
                                #for optional cylc install addition edit
                                if "cylc install -O" in line:
                                    line_num=rf.index(line)
                                    rf[line_num]='cylc install -O $1 --workflow-name $1 '+value+'\n'
                                    with open(p,'w') as f:
                                        for line in rf:
                                            f.write(line)

# Use parseyaml function to parse created edits.yaml
if __name__ == '__main__':
    yamlInfo()
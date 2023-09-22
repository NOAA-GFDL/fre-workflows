#!/app/conda/miniconda/envs/python-3.9-20220720/bin/python

# Author: Dana Singh

import os
from pathlib import Path  
import yaml

## Parse user defined edits.yaml 
def parseyaml(file):
    with open(file,'r') as f:
        y=yaml.safe_load(f)

    d=[]
    for k1 in y:
        for k2 in y[k1]:
            for dict in y[k1][k2]:
                d.append(dict)    
    return d

##################################################
# Use parseyaml function to parse created edits.yaml
yml = parseyaml("edits2.yaml")

for items in yml:
    for key,value in items.items():
        #print(f"{key}:{value}")
        if key == 'path' and value != None:
            p=Path(value)

        ## ROSE-SUITE-EXP-CONFIG EDITS
        # Create rose-suite-exp.conf and populate it with user-defined edits in edits.yaml
        if key == "rose-suite-exp-configuration":
            with open(p,'w') as f:
                f.write('[template variables]\n')
                f.write('## Information for requested postprocessing, info to pass to refineDiag/preanalysis scripts, info for epmt, and info to pass to analysis scripts \n')
        
            for key,value in value.items():
                if value != None:
                    with open(p,'a') as f:
                        if key == "HISTORY_DIR":
                            f.write("## Information about experiment\n")
                        if value == True or value == False:
                            f.write(f'{key}={value}\n\n')
                        else:
                            f.write(f'{key}="{value}"\n\n')

        ## ROSE-APP-CONFIG EDITS
        # Open and write to rose-app.conf for regrid-xy and remap-pp-components 
        # Populate configurations with info defined in edits.yaml
        if os.path.exists(p) and key == "rose-app-configuration":
            #regrid-xy and remap-pp-components 
            for v in value:
                for key,value in v.items():
                    #write empty file 
                     open(p,'w').close()
                     for k in value:
                         for key,value in k.items():
                             if value != None:
                                 with open(p,"a") as f:
                                     if key == "type":
                                         f.write("["+value+"]\n")
                                     if key != "type":
                                         f.write(key+"="+value+"\n")
 
        ## INSTALL-EXP SCRIPT EDIT
        # If alternate path for cylc-run directory defined in edits.yaml, add symlink creation option onto cylc install command
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

        ## Filepath check 
        if key == 'path' and value != None:
            if p.exists() == True: 
               print(f"Directory for {p} exists")
            elif p.exists() == False:
                print(f"Path {p} created")

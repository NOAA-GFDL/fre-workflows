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

#############################################################
yml = parseyaml('edits.yaml')

for items in yml:
    for key,value in items.items():
        #print(f"{key} : {value}")
        if key == 'path':
            if value:
                p=Path(value)

        ## TMPDIR and PTMPDIR CREATION if needed
        if os.path.isdir(p):
            print(f"Directory for {k2} already exists")
        elif p.exists() == False:
            print(f"Error: create {p}")
            #os.mkdir(p)

        ## ROSE-SUITE-CONFIG EDITS
        # Open rose-suite.conf file and replace lines with those defined in edit.yaml
        if os.path.exists(p) and key == 'rose-suite-configuration':
            for key,value in value.items():
                with open(p,"r+") as f:
                    rf=f.readlines()
                    if value != None:
                        for line in rf:
                            if ('#'+key+'=') in line or (key+'=') in line:
                                if str(value) == "True" or str(value) == "False":
                                     line_num=rf.index(line)
                                     rf[line_num]=key+'='+str(value)+'\n'
                                else:
                                     line_num=rf.index(line)
                                     rf[line_num]=key+'="'+str(value)+'"\n'
                                with open(p,'w') as f:
                                    for line in rf:     
                                        f.write(line)

                    elif value == None:
                        for line in rf:
                            if key in line and ('##'+key) not in line:
                                line_num=rf.index(line)
                                rf[line_num]='##'+line
                                with open(p,"w") as f:
                                    for line in rf:
                                        f.write(line)

        ## ROSE-SUITE-EXP-CONFIG EDITS
        # Create rose-suite-exp.conf and populate it with user-defined edits in edits.yaml
        if key == "rose-suite-exp-configuration":
            with open(p,'w') as f:
                f.write('[template variables]\n')
                f.write('## Settings include those for: \n# history files, requested postprocessing, info to pass to refineDiag/preanalysis scripts, info for epmt, and info to pass to analysis scripts \n')
            for key,value in value.items():
                if value != None:
                    with open(p,'a') as f:
                        if str(value) == "True" or str(value) == "False":
                            f.write(key+'='+str(value)+'\n\n')
                        else:
                           f.write(key+'="'+value+'"\n\n')

        ## ROSE-APP-CONFIG EDITS
        # Open and write to rose-app.conf for regrid-xy and remap-pp-components 
        # Populate configurations with info defined in edits.yaml
        if os.path.exists(p) and key == "rose-app-configuration":
            #regrid-xy and remap-pp-components 
            #write empty file
            for v in value:
                 for key,value in v.items(): 
                     open(p,'w').close()
                     for k in value:
                                 for key,value in k.items():
                                     if value != None:
                                         with open(p,"a") as f:
                                             if key == "type":
                                                 f.write('['+value+']\n')
                                             if key != "type":
                                                 f.write(key+'='+value+'\n')

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

#verify path exist, otherwise either error check or make the path


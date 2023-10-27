# Implentation of User-edits

The purpose of the edits yaml and python script is to consolidate necessary changes to rose configurations and other workflow scripts to one yaml. The python script will then parse the yaml apply these changes where needed for easy use and convenience of post-processing the workflow. 

## Instructions
To apply the user-edits to configurations and scripts, the user must copy the edits-template.yaml and fill in necessary data. Most of these fields are required for post-procesing capabilities. Once that is complete, the user runs the apply-edits.py script, passing in the edits yaml they created. 

### Edits-template.yaml
The edits-template yaml houses information for the experiment, for requested postprocessing, for the refineDiag and preanalysis scripts, for epmt, for the analysis scripts, as well as other optional inclusions. 

In order for the cylc scheduler to run the workflow, most of the information for the experiment and rose-app configurations are needed. For the TMPDIR fields, this edit/path is only neede when not working on pp/an. There is an optional user change included in the INSTALL-EXP-SCRIPT field. This edit allows the user to add other options onto the cylc install line in the bin/install-exp script. For example, when installing an experiment, a cylc-run directory is, by default, created in the user's HOME location. However, there may not be enough space for postproce3ssing the workflow here. In this case, the option `--symlink-dirs='run=/path/to/larger/space/location` can be included.
   
### Apply-edits.py
Once the edits are filled into the yaml, the `apply-edits.py` can be run from the `user-edits` directory, using the yaml that was populated (this is required): 
```
./apply-edits.py edits.yaml
```

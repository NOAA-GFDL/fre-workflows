# Implentation of User-edits

The purpose of the edits yaml and python script is to consolidate necessary changes to rose configurations and other workflow scripts to one yaml. A python script will then parse the yaml and apply these changes where needed for easy use and convenience of post-processing the workflow.

## Instructions
To apply the user-edits to configurations and scripts, the user must copy the edits-template.yaml and fill in necessary data. Most of these fields are required for post-procesing capabilities. Once that is complete, the user runs the apply-edits.py script, passing in the edits yaml they created.

### Edits-template.yaml
The edits-template yaml houses information for the experiment, for requested postprocessing, for the refineDiag and preanalysis scripts, for epmt, for the analysis scripts, as well as other optional inclusions. 

In order for the cylc scheduler to run the workflow, most of the information for the experiment and rose-app configurations are needed.

For the TMPDIR fields, this defined path is used for the stage-history task of the postprocessing workflow and is only needed when not working on pp/an. 

There is another optional user change included in the INSTALL-EXP-SCRIPT field. This edit allows the user to add other options onto the cylc install line in the bin/install-exp script. For example, when installing an experiment, a cylc-run directory is, by default, created in the user's HOME location. However, there may not be enough space for postprocessing the workflow here. In this case, the option `--symlink-dirs='run=/path/to/larger/space/location` can be included.

### Apply-edits.py
<ins>**Non-container use**</ins>

In order to run the apply-edits script without the use of a container, the following packages are necessary: pyyaml, pathlib, jsonschema, and click. Once the edits are filled into the yaml, the `apply-edits.py` can be run from the `user-edits` directory, using the yaml that was populated:

1) In the postprocessing repo, copy the edits-template.yaml
	
	a. Can be named anything the user likes, such as `edit.yaml` or, for a more organized use example, `[exp name].yaml`  

2) Fill out the created user-edit yaml
3) `./apply-edits.py [edits.yaml]`

<ins>**Container Use**</ins>

A container was created to run the apply-edits script. In order to run the container, 3 things are needed: the `.sif` container file, the postprocessing repository, and the runscript for the container. Currently, for testing purposes, these are the locations of usable locations:

1) On Gaea:
	
		a. Container build info and `.sif` file: `/lustre/f2/dev/Dana.Singh/edits-container/containerbuild`
	
		b. Postprocessing repo: `/lustre/f2/dev/Dana.Singh/edits-container/postprocessing` 
	
		c. Runscript directory: `/lustre/f2/dev/Dana.Singh/edits-container/run`

1) On PP/AN:
	
		a. Container build info and `.sif` file: fill in 
	
		b. Postprocessing repo: fill in  
	
		c. Runscript directory: fill in 

**To run the container, follow these steps:**

1) In the postprocessing repo, copy the edits-template.yaml
	
	a. Can be named anything the user likes, such as `edit.yaml` or, for a more organized use example, `[exp name].yaml`  

2) Fill out the created user-edit yaml
3) Running the container: follow this command:
	
	a. On Gaea: 

	Follow this command: `apptainer run -B [pp dir] -B [run dir] [sif file]`

	*The -B bind mounts the following directory to the container.*
		
	```
	apptainer run -B /lustre/f2/dev/Dana.Singh/edits-container/postprocessing:/mntpp -B /lustre/f2/dev/Dana.Singh/edits-container/run:/mntrun /lustre/f2/dev/Dana.Singh/edits-container/containerbuild/edits.sif
	```
	
	b. On PP/AN: 

	Follow this command: `singularity run -B [pp dir] -B [run dir] [sif file]`
		
	```
	fill in 
	```

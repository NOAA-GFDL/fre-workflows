Cylc is a general purpose workflow scheduler that is very efficient for cycling systems. For more documentation, visit https://cylc.github.io/cylc-doc/stable/html. 

The usage of cylc includes configuration files: workflow configuration, global.cylc, site configurations, rose-suite configuration, and rose-suite-experiment configrations. 

The workflow configuration (flow.cylc) defines the workflow, what scripts to use throughout the workfow, and task dependencies. The global.cylc defines default cylc flow settings, including the job runner and platform information (further used in user site configurations). The site configurations define the platform to be used and other site specific user settings, such as site specific tools utilized. Furthermore, the rose-suite configuration references a default configuration file for all experiments. These settings can be applied to all experiments but can also be overwritten by experiment configurations. Rose-suite-exp. configurations include specific info for the experiment such as the history file location, the output directory location, pp components to process, etc. 

# Workflow Configuration
To help understand the workflow configuration, the following diagram was created. It is laid out in sections.

```mermaid
flowchart TD

subgraph Parts of Workflow 
%%C["Cylc Workflow:\nGeneral purpose workflow engine that \norchestrates cycling systems very efficiently\n\n(https://cylc.github.io/cylc-doc/stable/html/)"]
F[Cylc workflow: \nflow.cylc]
F-->S{{1. site\n-set user site\n-can be gfdl-ws, generic, or ppan}}
F--->f1{{2. meta: \n-information about the workflow}} 
%%-.-> RS
F---->f2{{"3. schedule: \n-settings for the scheduler\n-non-task-specific workflow configuration"}}
F----->f3{{4.task parameters: \n-define task parameters values and parameter templates}}
F------>f4{{5.scheduling: \n-allows cylc to determine when tasks are ready to run\n-define families\n-defines qualifiers}}
F------->f5{{"6.runtime: \n-determines how, where, and what to execute when tasks are ready \n-can specify what script to execute, what compute resources to use, \n and how to run a task"}}
end
```

# Portable workflow 
The portable workflow (flow.cylc) was created by utilizing conda environments with workflow tools and moving gfdl site specific tools to the ppan.cylc site configuration file, in addition to creating a generic.cylc site configuration to be used in its place. 

The generic.cylc is where the conda environments containing tools needed for the workflow are activated, as seen below. The site configurations also define the platform used which references the global.cylc. As mentioned, the global.cylc contains info about the platform

```mermaid
flowchart TD
SS[Site] --> s1[gfdl-ws.cylc]
SS-->s2[ppan.cylc]
SS-->s3[generic.cylc]

subgraph gdfl-ws configuration
s1-->wsp[platform = localhost]
end

subgraph pp/an configuration
s2-->ppanp[platform = ppan]
s2-->info[gfdl site specific workflow and tools]
end

subgraph generic configuration
s3-->E
E[activate envs]-->e1[cylc.yaml: \n-cylc dependencies] & e2[task-tools.yaml: \ntools used by workflow]
s3-->genp[platform = localhost]
end

G[global.cylc] --> g1["-defines default Cylc Flow settings for a user or site \n-includes info for each platform used in the site configs"]
wsp -.->G
ppanp -.->G
genp -..->G
```

# Instructions for portable workflow (as of now)
1. Install conda
```
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
chmod +x Miniconda3-latest-Linux-x86_64.sh
./Miniconda3-latest-Linux-x86_64.sh
```

2. Install mamba
```
conda install -c conda-forge mamba
```

3. If not enough space, move conda directories and packages to another location (collab1 on Niagara)
```
conda config --add envs_dirs /collab1/data/$USER/envs  #for niagara
conda config --add pkgs_dirs /collab1/data/$USER/pkgs  #for niagara
```

4. Create and install environments

Environment yamls: cylc and task-tools, where task-tools includes hsm, fre-nctools, nco, cdo, and netcdf-cxx4. To create an environment: 
```
mamba env create --file cylc.yaml
mamba env create --file task-tools.yaml
conda activate cylc                      #activate cylc environment
```

5. Transfer data

Globus online was used to transfer experiment data and any other necessary data (HISTORY_DIR, PP_GRID_SPEC) 

6. Canopy PP steps
a. Edits:

	i. Rose-suite.conf

		1. If not on gfdl pp/an, set `site` = `generic`
		2. Correct PTMPDIR path - create ptmp directory
		3. DO_REFINEDIAG=False
		4. DO_PREANALYSIS=False

	ii. opt/rose-suite-experiment configurations

		1. Correct history directory path (wherever data was transferred to)
		2. Comment out HISTORY_DIR_REFINED
			a. Comment this out along with DO_REFINEDIAG=False
				a.1 This means there is no refinediag processing
		3. Correct PP directory path
		4. Correct PP_GRID_SPEC directory path (wherever data was tranferred to)

	iii. Macro.py issue (if seen in rose macro --validate step)

		1. Clone Chris Blanton's fork of the rose repo: git clone -b default-validator-change https://github.com/ceblanton/rose.git
		2. Checkout rose fork: git checkout default-validator-change
		3. Locate your macro.py in cylc env. installation: 
			a. Ex.: /collab1/data/$USER/envs/cylc/lib/python3.10/site-packages/metomi/rose/macro.py
		4. Replace/overwrite that macro.py with the one in Chris' rose repo:
			a. In directory with Chris' macro.py: cp -f [path/to/your/macro.py] macro.py

	iv. app/regrid-xy/rose-app.conf

		1. Fill in regridding instructions and regridding labels as in README.md

	v. app/remap-pp-components/rose-app.conf

		1. Fill in grid and sources information as in README.md

	vi. bin/install-exp (optional)

		1. --symlink-dirs='run=/collab1/data/$USER' was added to the `cylc install` command
			a. the `run` path is niagara-specific
			b. This edit was done due to limited space on niagara

    vii. tmp directory

        1. create tmp directory - set environment variable TMPDIR in steps below


b. Steps to run workflow:
```
# make sure conda environment is activated

bin/list-exps
rose macro --validate
export CYLC_CONF_PATH=/path/to/generic-global-config  #this points to the global.cylc used for for `site=generic`
                                                      #in generic-global-config folder in the postprocessing template repository (fre2/workflows/postprocessing/generic-global-config)
export TMPDIR=/path/to/TMPDIR/tmp    #for TMPDIR environment variable for stage-history task
bin/install-exp [exp]
cylc play [exp]
```
c. To monitor status:
See debugging messages:
``` 
cylc play --no-detach --debug [exp] 
```

Monitor status of each task: 
```
watch -n 5 cylc workflow-state [exp]  
```
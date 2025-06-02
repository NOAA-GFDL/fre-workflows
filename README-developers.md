User-Specific settings

User settings

You hae to have a file in your /home directory that looks like this: 

```
> cat /home/Carolyn.Whitlock/.bash_profile
# this is essential Cylc configuration below
export PATH="${PATH}:/home/fms/local/opt/cylc/bin"
```
We need this to run on ppan. Without a cylc binary in your $PATH variable, 
the initial setup of the workflow sever (check terminology) fails, and we can't
edit the environment with a module load or similar until it's running.

We'd like a longer-term solution by adding a link to the binary in one of the
places that is already added to our $PATH, but that's in progress.


Experiment settings

The current organization of the yaml has a bunch of experiment-wide settings in
a file called settings.yaml: 

```
yaml_workflow/pp/settings.yaml:
  directories:
  history_dir: !join [/archive/$USER/, *FRE_STEM, /, *name, /, *platform, -, *target, /, history]
  pp_dir: !join [/archive/$USER/, *FRE_STEM, /, *name, /, *platform, -, *target, /, pp]
  analysis_dir: !join [/nbhome/$USER/, *FRE_STEM, /, *name]
  ptmp_dir: "/xtmp/$USER/ptmp"

postprocess:
  settings:
    site: "ppan"
    history_segment: "P1Y"
    pp_start: *PP_START_YEAR 
    pp_stop: *PP_STOP_YEAR
    pp_chunks: [*PP_CMIP_CHUNK]
    pp_grid_spec: *PP_GRID_SPEC
  switches:
    do_timeavgs:                False
    clean_work:                 False
    do_refinediag:              False
    do_atmos_plevel_masking:    False
    do_preanalysis:             False
    do_analysis:                False
    do_analysis_only:           False
```
You'll see reference to some of the settings in this file throughout the workflow
as variables. It's useful to make sure some of these are set to specific values
for developer work:

  postprocess:settings:clean_work 
  what it does: Whether you clean up the contents of the intermediate directories
    produced by your experiment before going on to the next step - for example, 
    removing the local history directory once you have all files split by
    split.netcdf
  value for production:  True
  value for development: False
  why: It's a lot easier to debug what may have gone wrong with previous steps
   when you can refer to the actual files produced in those steps and selectively
   re-run. However, this is not necessary on a production run and the intermediate
   files take up a LOT of space.
  
  
  
  


Batch environment setup and fre-cli

The slurm jobs that cylc submits are run from a bare environment, not a copy of
the local environment you submitted the jobs from. This means that if you want to
invoke fre-cli tools from within fre-workflows, you need to add fre-cli to the 
batch environment. How you do this depends on how far along the development 
pipeline the features that you want to include in fre-cli are.  

To do this, you use the pre-script defined for each task. You can see an example
of a pre-script in flow.cylc:

```
    [[RENAME-SPLIT-TO-PP]]
        pre-script = mkdir -p $outputDir
        script = rose task-run --verbose --app-key rename-split-to-pp
```

However, that's NOT where we want to put our edits. Cylc has hierarchical
layers of configuration - settings can be set in more than one place, and the
most specific settings are prioritized over the least specific settings. The
overall hierarchy looks something like this:

highest priority---  experiment yaml > sites/$sitefile.cylc > flow.cylc ---lowest priority

Prioritization does not mean that the settings in any file are ignored - but if 
the settings in two files disagree, cylc goes with the setting value in the 
higher-priority file over the lower-prioirty one.

We currently have pre-scripts defined for every step of the workflow in
sites/$sitefile.cylc, and that means YOU NEED TO EDIT THERE. Fot testing at the
lab, that means you are editing site/ppan.cylc . 

How you edit sites/ppan.cylc looks different depending on how far along in the 
development process the features that you are testing are: 

Features in fre-cli are part of a release

If the features that you want to include are part of a fre release, you can 
load a fre module from the pre-script of your cylc task: 

```
    [[SPLIT-NETCDF]]
        pre-script = module load fre/{{ VERSION }}; mkdir -p $outputDir
```

Features in fre-cli are merged into main

If the features that you want to include are merged into main but not yet part 
of a fre release, you can use them by loading fre/test. 

```
    [[SPLIT-NETCDF]]
        pre-script = module load fre/test; mkdir -p $outputDir
```


Features in fre-cli are in a development branch

If you wish to work with changes that are not yet merged into main, the
setup-script needs to set up your conda environment for the fre-cli repo that 
you are working with. Remember: the slurm job scripts are executed as you, and 
have access to your conda environments.

```
    [[SPLIT-NETCDF]]
        pre-script = """
                     module load miniforge
                     set +u
                     conda activate fre-cli
                     set -u
                     mkdir -p $outputDir
                     """
```
The set +u/-u turns off and on strict variable checking respectively. Loading
a conda environment requires less strict variable checking than cylc normally
implements, so we need to turn that setting on and off for a single operation.

If this is not set/unset, you're going to see an unset variable error when you
try to load the conda environment



For more information on conda environment setup for fre-cli, see: 

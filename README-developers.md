# User-Specific settings

## User settings

You have to have a file in your /home directory that looks like this: 

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


## Experiment settings

The current organization of the yaml has a bunch of experiment-wide settings in
a file called settings.yaml: 


```
> cat yaml_workflow/pp/settings.yaml:

directories:
  history_dir: "/archive/$USER/CMIP7/ESM4/DEV/ESM4.5_candidateA/ppan-prod-openmp/history"
  pp_dir: "/archive/$USER/CMIP7/ESM4/DEV/ESM4.5_candidateA/ppan-prod-openmp/pp"
  analysis_dir: "/nbhome/$USER/CMIP7/ESM4/DEV/ESM4.5_candidateA"
  ptmp_dir: "/xtmp/$USER/ptmp"
postprocess:
  settings:
    site: "ppan"
    history_segment: "P1Y"
    pp_start: 0002 
    pp_stop: 0003
    pp_chunks: ["P5Y"]
    pp_grid_spec: "/work/Niki.Zadeh/mosaic_generation/exchange_grid_toolset/workdir/mosaic_c96om5b04v20240410.20240423.an105/mosaic_c96om5b04v20240410.20240423.an105.tar"
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


  postprocess:switches:clean_work 
  
  *what it does:* Whether you clean up the contents of the intermediate directories
    produced by your experiment before going on to the next step - for example, 
    removing the local history directory once you have all files split by
    split.netcdf
  *value for production:*  True
  *value for development:* False
  *why:* It's a lot easier to debug what may have gone wrong with previous steps
   when you can refer to the actual files produced in those steps and selectively
   re-run. However, this is not necessary on a production run and the intermediate
   files take up a LOT of space.
  
  
  
  


# Batch environment setup and fre-cli

## Local environment setup
Currently we do NOT recommend running fre-workflows experiments using the 
developer conda environments. Instead, we recommend using the gfdl modulefiles
for cylc and the latest fre release:

```
module load cylc
module load fre/2025.03
```

This applies even if you're testing fre features as we describe later in this 
document; generally, the changes you are testing are changes meant to run in the 
batch jobs, not as part of the submission process. The submission process is
standardized enough that you can use the lab-standard modules, which is going to
eliminate a possible source of error in your environment setup.

## Remote environment setup
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

highest priority---  sites/$sitefile.cylc > flow.cylc ---lowest priority

Prioritization does not mean that the settings in any file are ignored - but if 
the settings in two files disagree, cylc goes with the setting value in the 
higher-priority file over the lower-prioirty one.

We currently have pre-scripts defined for every step of the workflow in
sites/$sitefile.cylc, and that means YOU NEED TO EDIT THERE. For testing at the
lab, that means you are editing site/ppan.cylc . 


*Please note:* these steps may include changes that you do not want to include
in your git history for safety's sake. To avoid adding these to your git 
history, you can edit the code in ~/cylc-src/$your_test_experiment directly
after checking it out with a fre pp checkout: 

```
> fre pp checkout -b 51.var.filtering -e ESM4.5_candidateA -p ppan -t prod-openmp
> pushd ~/cylc-src/ESM4.5_candidateA__ppan__prod-openmp
> ls 
app/	       environment.yml	       etc/		       Jinja2Filters/  pytest.ini	     README-portability.md    site/
bin/	       envs/		       flow.cylc	       lib/	       README-developers.md  README_using_fre-cli.md  tests/
ESM4.5_candidateA.yaml  generic-global-config/  meta/	       README.md	     rose-suite.conf
> emacs site/ppan.cylc
```

The code that cylc runs from in ~/cylc-run/$your_test_experiment is copied from
~/cylc-src/$your_test_experiment , not re-cloned from git. It's a bad idea to 
put any changes you want to be permanent in ~/cylc-src/$your_test_experiment - 
but you probably do not want these changes to be permanent. This is a little bit
risky - it can be hard to keep track of where your edits are taking place - but
allows you to avoid awkward back-and-forth edits in your git history.


How you edit sites/ppan.cylc looks different depending on how far along in the 
development process the features that you are testing are: 

### Features in fre-cli are part of a release

If the features that you want to include are part of a fre release, you can 
load a fre module from the pre-script of your cylc task: 

```
    [[SPLIT-NETCDF]]
        pre-script = module load fre/{{ VERSION }}; mkdir -p $outputDir
```

### Features in fre-cli are merged into main

If the features that you want to include are merged into main but not yet part 
of a fre release, you can use them by loading fre/test. 

```
    [[SPLIT-NETCDF]]
        pre-script = module load fre/test; mkdir -p $outputDir
```


### Features in fre-cli are in a development branch

If you wish to work with changes that are not yet merged into main, the
setup-script needs to set up your conda environment for the fre-cli repo that 
you are working with. Remember: the slurm job scripts are executed as you, and 
have access to your conda environments.

```
    [[SPLIT-NETCDF]]
        pre-script = """
                     module load miniforge
                     set +u
                     conda activate my-fre-cli-env
                     set -u
                     mkdir -p $outputDir
                     """
```
The set +u/-u turns off and on strict variable checking respectively. Loading
a conda environment requires less strict variable checking than cylc normally
implements, so we need to turn that setting on and off for a single operation.

If this is not set/unset, you're going to see an unset variable error when you
try to load the conda environment.

This should be generic to all sites, though we have not yet had a chance to run
this outside of the lab (i.e. Gaea).


For more information on conda environment setup for fre-cli, see: 

# Developer Guide

1. [Configuration Settings](#configuration-settings)

2. [Batch environment setup and fre-cli](#batch-environment-setup-and-fre-cli)

3. [Post-processing guide using fre-cli and cylc](#guide)

# Configuration Settings

`fre-workflows` has primarily been developed and tested on PPAN. The following are guidelines for developing
on **PPAN**.

## Cylc User settings

The path to the Cylc binary must be added to your `$PATH` environment variable first. Without the cylc binary,
the initial setup of the workflow server fails. This can be done by modifying your PATH in your bash_profile
as follows:

```
> cat /home/First.Last/.bash_profile
# this is essential Cylc configuration below
export PATH="${PATH}:/home/fms/local/opt/cylc/bin"
```

## Experiment settings

In regards to post-processing, the yaml framework consists of the model, settings, and post-processing
yaml files. 

    - model yaml: contains yaml anchors (i.e. variables that can be used throughout the yaml framework)
                  and paths that point to the settings and post-processing yaml giles
    - settings yaml: experiment-specific settings and switches; can also define more experiment-specific
                     yaml anchors
    - post-processing yaml: information about the components to be post-processed

It's helpful to be familiar with information in the `settings.yaml` as switches and settings can help
developers for debugging purposes.

Example `settings.yaml`:

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

For developers, you can set some of the yaml keys, such as `clean_work`, to specific values:

  ```
  postprocess:
    switches:
      clean_work: True/False
  ```

  - *what it does:* Switch to clean or keep the contents of the intermediate directories
    produced by your post-processing workflow run before going on to the next step - for example,
    removing the local history directory once you have all files split by
    split.netcdf

  - *value for production:*  True

      - intermediate files take up a LOT of space if kept

  - *value for development:* False

      - easier to debug errors if files are available

For more information on the yaml framework, see [fre-cli's README and documentation on the yaml files](https://noaa-gfdl.readthedocs.io/projects/fre-cli/en/latest/usage.html#model-yaml).

# Batch environment setup and fre-cli for testing workflow changes

## Local environment setup
Currently, when submitting/testing a pp workflow, we HIGHLY recommend using the gfdl
modulefiles for cylc and fre instead of developer conda environments, as different cylc
and fre-cli versions may cause more confusion when debugging:

```
module load cylc
module load fre/2025.04
```

Generally, edits pertaining to the workflow or fre-cli tool usage in the workflow are code
changes meant to run through the cylc created batch job scripts, submitted by the cylc scheduler.

Even if you are developing and testing a fre-cli tool for use in the workflow in a local conda environment,
the workflow itself, should still be submitted using the modulefiles to eliminate any possible sources of error
in your environment setup.

In this submission process via `fre pp run`, the platform passed on the command line determines the job
runner. For PP/AN platforms, the job scripts are submitted through slurm. On other sites, scripts are
submitted as background jobs.

## Remote environment setup
Each slurm job that cylc submits is run from a bare environment. If the jobs were 
submitted in a local conda environment, that environment will not be used within the
workflow. Thus, if you want to invoke fre-cli tools from within a fre-workflows task,
you need to add fre-cli to the batch environment.

To do this, you use the pre-script defined for each task. You can see an example
of a pre-script in `flow.cylc`:

```
    [[RENAME-SPLIT-TO-PP]]
        pre-script = mkdir -p $outputDir
        script = rose task-run --verbose --app-key rename-split-to-pp
```

However, the `flow.cylc` is **NOT** where we want to put our edits. Cylc has hierarchical
layers of configuration - settings can be set in more than one place, and the
most specific settings are prioritized over the least specific settings.

The overall hierarchy looks something like this:

highest priority---  `site/[sitefile].cylc` > `flow.cylc` ---lowest priority

Prioritization does not mean that the settings in any file are ignored - but if
the settings in two files disagree, cylc uses the setting value in the
higher-priority file over the lower-priority one. We currently have pre-scripts
defined for every step of the workflow in `site/[sitefile].cylc` - **DEVELOPERS SHOULD EDIT HERE**.

**For testing at the lab, site/ppan.cylc should be edited.**

*Please note:* these steps may include changes that you do not want to include
in your git history for safety's sake. To avoid adding these to your git
history, you can edit the code in `~/cylc-src/[your_test_experiment_workflow_id]`
directly after checking it out with the fre-cli subtool `fre pp checkout`:

```
> fre pp checkout -b 51.var.filtering -e ESM4.5_candidateA -p ppan -t prod-openmp
> pushd ~/cylc-src/ESM4.5_candidateA__ppan__prod-openmp
> ls
app/	       environment.yml	       etc/		       Jinja2Filters/  pytest.ini	     README-portability.md    site/
bin/	       envs/		       flow.cylc	       lib/	       README-developers.md  README_using_fre-cli.md  tests/
ESM4.5_candidateA.yaml  generic-global-config/  meta/	       README.md	     rose-suite.conf
> emacs site/ppan.cylc
```

The code that cylc runs from in `~/cylc-run/[your_test_experiment_workflow_id]` is copied from
`~/cylc-src/[your_test_experiment_workflow_id]`, not re-cloned from git. It is not advisable to
put any changes you want to be permanent in `~/cylc-src/[your_test_experiment_workflow_id]`. This
is a little bit risky - it can be hard to keep track of where your edits are taking place, but
allows you to avoid awkward back-and-forth edits in your git history.

How you edit `site/ppan.cylc` for the environment you would like to use might look different
depending on the developmental progress of the features you wish to test:

### Features in fre-cli that are part of a release

If the features that you want to include are part of a fre release, you can
load a fre module from the pre-script of your cylc task (if not already specified
in the `[[root]]` section of the site file - this section is "inherited" by all tasks):

```
    [[SPLIT-NETCDF]]
        pre-script = module load fre/{{ VERSION }}; mkdir -p $outputDir
```

### Features in fre-cli that are merged into main

If the features that you want to include are merged into main but not yet part
of a fre release, you can use them by loading fre/test.

```
    [[SPLIT-NETCDF]]
        pre-script = module load fre/test; mkdir -p $outputDir
```


### Features in fre-cli that are in a development branch

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

For more information on conda environment setup for fre-cli, see [fre-cli's README and documentation](https://github.com/NOAA-GFDL/fre-cli/blob/main/README.md).

# Guide

## Postprocess FMS history files
To postprocess FMS history files on GFDL's PP/AN, users can follow fre-cli post-processing steps [here](https://noaa-gfdl.readthedocs.io/projects/fre-cli/en/latest/usage.html#id1).

NOTE: After the first two steps, `fre pp checkout` and `fre pp configure-yaml`, users can edit the `ppan.cylc` site file under `~/cylc-src/$your_test_experiment/site/ppan.cylc`, the combined yaml file, and the rose-suite.conf files. 

If further edits needs to be made for troubleshooting, users can edit files in the
`~/cylc-src/[your_test_experiment_workflow_id]` directory and follow this clean up
procedure:

```
# If the experiment needs to be stopped
cylc stop --now [your_test_experiment_workflow_id]

# Removes the cylc-run directory and associated symlinks
cylc clean [your_test_experiment_workflow_id]

# From here, you can skip the checkout and configure-yaml steps, and proceed with validate, install, and run
```

## Inspect workflow progress with an interface (GUI or TUI)
The workflow will run and shutdown when all tasks are complete. If tasks fail, the workflow
may stall, in which case it will shutdown in error after a period of time.

`cylc` has two workflow viewing interfaces (full GUI and text UI), and a variety of CLI
commands that can expose workflow and task information. The text-based GUI can be
launched via:
```
cylc tui [workflow_id]
```

The full GUI can be launched on jhan or jhanbigmem (an107 or an201).
```
cylc gui --ip=`hostname -f` --port=`jhp 1` --no-browser
```
Then, navigate to one of the two links printed to screen in your web browser.
If one just wants a quick look at the state of their workflow, the user-interfaces
can be completely avoided by using the `workflow-state` command, two examples of which are:

```
cylc workflow-state -v [workflow_id]                # show all jobs
cylc workflow-state -v [workflow_id] | grep failed  # show only failed ones
```

## Inspect workflow progress with a terminal CLI
Various other `cylc` commands are useful for inspecting a running workflow.
Try `cylc help`, and `cylc <command> --help` for more information on how to
use these tools to your advantage!

- `cylc scan` Lists running workflows
- `cylc cat-log [workflow_id]` Show the scheduler log
- `cylc list` Lists all tasks
- `cylc report-timings`

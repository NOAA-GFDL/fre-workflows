# PPAN `fre-workflows` Developer Guide

`fre-workflows` has primarily been developed and tested on PPAN. The following are guidelines for developing
on **PPAN**.




## Contents
1. [Configuration](#configuration)
    1. [`cylc` doc](#cylcfunctioning)
    2. [global `cylc` config](#globalcylcconfig)
    3. [default PPAN settings](#ppandefaults)
    4. [terminal UTF encoding](#utfencodeerrors)
    5. [`fre.yamltools` framework](#freyamlframework)
2. [Running and testing workflows, generally and on PPAN](#runtestworkflows)
    1. [local PPAN testing](#localppantesting)
    2. [default local env setup](#deflocalsetup)
	3. [default remote env setup](#remotenvsetup)
3. [`cylc` workflow monitoring](#cylcmontips)
    1. [via GUI or TUI](#guituimon)
    2. [via CLI](#cliprogressmon)




## Configuration <a name="configuration"></a>



### `cylc` functionality <a name="cylcfunctioning"></a>

`fre-workflows` developers should be intimately familiar with
[`cylc` documentation](https://cylc.github.io/cylc-doc/stable/html/index.html).


### `global.cylc` configuration <a name="globalcylcconfig"></a>

If `cylc` is in your `PATH`, you can check your global configuration with
```
cylc config -d
```

You can define your own global configuration for `cylc` by putting a configuration file in the expected location.
For some fields at least, the user's global configuration overrides the defaults even using a `module load`ed
version. To start from a given global configuration:
```
mkdir --parents /home/$USER/.cylc/flow
cylc config -d > /home/$USER/.cylc/flow/global.cylc
# edit the file to your heart's content
```



### default `PATH` and `cylc` on PPAN <a name="ppandefaults"></a>

On PPAN, your `PATH` by default has `cylc` in it. This can be seen on login with `which cylc`. The directory name
is clearly in your `PATH` and can be seen with `echo $PATH`. This smooths over configuration for job submission
at the cost of some flexibility. A work around is to put  your preferred cylc into your `PATH` at login, while
removing the default. In your `~/.bash_profile`:
```
echo "(~/.bash_profile) removing /usr/local/bin from PATH"
echo ""
echo "(~/.bash_profile) PATH was: $PATH"
echo ""
export PATH=$(echo "$PATH" | awk -v RS=: -v ORS=: '$0 != "/usr/local/bin"' | sed 's/:$//')

# now add your preferred cylc to your PATH instead
export PATH=/path/to/your/preferred/cylc/bin:$PATH
echo "(~/.bash_profile) PATH now: $PATH"
```



### terminal and UTF encoding errors <a name="utfencodeerrors"></a>

A workaround is again, to edit your `~/.bash_profile` like above, and add/define `LANG`:
```
echo "(~/.bash_profile) export LANG=C.UTF-8"
export LANG=C.UTF-8
```



### `fre.yamltools` Framework <a name="freyamlframework"></a>

The yaml framework is fully described in `fre-cli`'s `README` and documentation
[on the yaml files](https://noaa-gfdl.readthedocs.io/projects/fre-cli/en/latest/usage.html#yaml-framework).




## Testing locally on PPAN <a name="runtestworkflows"></a>

MUST REVIEW AND EDIT STILL

There are multiple ways of accomplishing this. They are described in order of least to most complex.



### The default local environment setup <a name="deflocalsetup"></a>

MUST REVIEW STILL

Currently, if one is only testing workflow changes against known `fre` tag/versions, it's simplest to use
modulefiles for `cylc` and `fre`. In order to test your `fre-workflows` edits against the known system
```
module load cylc
module load fre/2025.04
```

Developers however will need more flexibility than this to stay ahead of users and develop robust new features.

Generally, edits pertaining to the workflow or fre-cli tool usage in the workflow are code
changes meant to run through the cylc created batch job scripts, submitted by the cylc scheduler.

Even if you are developing and testing a fre-cli tool for use in the workflow in a local conda environment,
the workflow itself, should still be submitted using the modulefiles to eliminate any possible sources of error
in your environment setup.

In this submission process via `fre pp run`, the platform passed on the command line determines the job
runner. For PP/AN platforms, the job scripts are submitted through slurm. On other sites, scripts are
submitted as background jobs.



### Remote environment setup <a name="remotenvsetup"></a>

MUST REVIEW STILL

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



## testing by feature in `fre=cli`

TO REVIEW might remove? might re-engineer? TODO



### Features in fre-cli that are part of a release  <a name="releasefeaturetesting"></a>

TO REVIEW

If the features that you want to include are part of a fre release, you can
load a fre module from the pre-script of your cylc task (if not already specified
in the `[[root]]` section of the site file - this section is "inherited" by all tasks):

```
    [[SPLIT-NETCDF]]
        pre-script = module load fre/{{ VERSION }}; mkdir -p $outputDir
```



### Features in fre-cli that are merged into main <a name="mainmergefeaturetesting"></a>

TO REVIEW

If the features that you want to include are merged into main but not yet part
of a fre release, you can use them by loading fre/test.

```
    [[SPLIT-NETCDF]]
        pre-script = module load fre/test; mkdir -p $outputDir
```



### Features in fre-cli that are in a development branch <a name="howdifffromprevsectiontesting"></a>

TO REVIEW

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

For more information on conda environment setup for fre-cli, see
[fre-cli's README and documentation](https://github.com/NOAA-GFDL/fre-cli/blob/main/README.md).



### Postprocess FMS history files

TO REVIEW

To postprocess FMS history files on GFDL's PP/AN, users can follow fre-cli post-processing steps
[here](https://noaa-gfdl.readthedocs.io/projects/fre-cli/en/latest/usage.html#id1).

NOTE: After the first two steps, `fre pp checkout` and `fre pp configure-yaml`, users can edit the
`ppan.cylc` site file under `~/cylc-src/$your_test_experiment/site/ppan.cylc`, the combined yaml file,
and the rose-suite.conf files. 

If further edits needs to be made for troubleshooting, users can edit files in the
`~/cylc-src/[your_test_experiment_workflow_id]` directory and follow this clean up procedure:
```
# If the experiment needs to be stopped
cylc stop --now [your_test_experiment_workflow_id]

# Removes the cylc-run directory and associated symlinks
cylc clean [your_test_experiment_workflow_id]
```




## `cylc` workflow monitoring <a name="cylcmontips"></a>

TO REVIEW

`cylc` has two workflow viewing interfaces (full GUI and text UI), and a variety of CLI commands that
can expose workflow and task information. The workflow will run and shutdown when all tasks are complete.
If tasks fail, the workflow may stall, in which case it will shutdown in error after a period of time.



### Inspect workflow progress via GUI or TUI interface <a name="guituiprogressmon"></a>

TO REVIEW

The text-based GUI can be launched via:
```
cylc tui [workflow_id]
```

The full GUI can be launched on jhan or jhanbigmem (an107 or an201).
```
cylc gui --ip=`hostname -f` --port=`jhp 1` --no-browser
```
Then, navigate to one of the two links printed to screen in your web browser.
If one just wants a quick look at the state of their workflow, the user-interfaces
can be completely avoided



### Inspect workflow progress with a terminal CLI <a name-"cliprogressmon"></a>

TO REVIEW

Various other `cylc` commands are useful for inspecting a running workflow.
Try `cylc help`, and `cylc <command> --help` for more information on how to
use these tools to your advantage!

Try using the `workflow-state` command, two examples of which are:
```
cylc workflow-state -v [workflow_id]                # show all jobs
cylc workflow-state -v [workflow_id] | grep failed  # show only failed ones
```

Try these others in the CLI to assist with monitoring your workflow progress
- `cylc scan` Lists running workflows
- `cylc cat-log [workflow_id]` Show the scheduler log
- `cylc list` Lists all tasks
- `cylc report-timings`

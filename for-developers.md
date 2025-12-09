# PPAN `fre-workflows` Developer Guide

`fre-workflows` can be used across multiple different platforms, but historically has been developed and tested on PPAN.
The following are guidelines for developing/testing on **PPAN**, but does still contain some generally-applicable advice
to using `fre-workflows` elsewhere.




## Contents
1. [`cylc` Configuration](#cylcconfiguration)
    1. [`cylc` Documentation](#cylcdoc)
    2. [Global `cylc` Config](#globalcylcconfig)
	3. [`cylc` platforms and site](#cylcplatformandsite)
	    1. [`site` value specifics](#sitespecifics)
2. [PPAN Specifics](#ppanspecifics)
    1. [Terminal UTF Encoding](#utfencodeerrors)
    2. [PPAN Documentation](#moreppandoc)
3. [Configuring Workflows With `fre`](#freyamlframework)
4. [Running Workflows with `fre` on PPAN](#configrunppanworkflows)
    1. [With LMOD and Modules](#withlmod)
    2. [With Your Own `conda`/`fre-cli` and LMOD `cylc`](#withcondaandcylc)
    3. [With Only Your Own `conda`/`fre-cli`](#withcondaonly)
5. [`cylc` workflow monitoring](#cylcmontips)
    1. [via GUI or TUI](#guituiprogressmon)
    2. [via CLI](#cliprogressmon)
5. [too old?reviewing](#footemp)
    2. [REVIEWING default local env setup](#deflocalsetup)
    3. [REVIEWING default remote env setup](#remotenvsetup)




## `cylc` Configuration <a name="cylcconfiguration"></a>

This section will go over the basics of configuring `cylc` and other PPAN-specific configurations relevant to `cylc`.



### `cylc` Documentation <a name="cylcdoc"></a>

`fre-workflows` developers should be intimately familiar with
[`cylc` documentation](https://cylc.github.io/cylc-doc/stable/html/index.html).



### `global.cylc` Configuration <a name="globalcylcconfig"></a>

If `cylc` is in your `PATH`, the global configuration can be exposed with `cylc config -d`. If desired, one can override
these values and define their own global configuration by putting a configuration file in the expected location. For 
this, it's best to start your own global configuration with the current one. We can do this with:
```
mkdir --parents /home/$USER/.cylc/flow
cylc config -d > /home/$USER/.cylc/flow/global.cylc
# edit the file to your heart's content
```

Sometimes, a configuration value or setting in a specific workflow takes precedent over the global configuration. For
specifics on this, consult the [`cylc` documentation](https://cylc.github.io/cylc-doc/stable/html/index.html).



### `cylc` Platforms and `site/` files <a name="cylcplatformandsite"></a>

`cylc` and `fre` treat the notion of platforms slightly differently, creating the potential for some confusion.

In `fre`, a platform typically refers to a specific environment of a specific system, generally for the purposes of
tracking which compilers and hardware are used where, and what settings are required to make models run. It's used as a
common input argument to many functions, helping uniquely identify workflow configurations and place where they were run
at the same time.

In `cylc` a platform is usually about selecting a specific set global configuration values, and in `fre-workflows`, also
implies which file in `site/` will be included in the primary `flow.cylc` via `Jinja2`. For PPAN, the two relevant
platform values are `ppan` and `ppan_test`, corresponding to template files in `site/` name respectively. One gets
chosen based on a `site` configuration value within a `fre` settings `yaml`.


#### `ppan` v. `ppan_test` <a name="sitevaluespecifics"></a>

These two differ by one key field, the `job runner handler` field. `site/ppan.cylc` will specify that `cylc`'s default
`Slurm` job runner handler will be used. `site/ppan_test.cylc` by contrast, will use a custom version of the `Slurm` job
runner handler, that parses the job script and tags certain operations for tracking via `epmt`. Additionally, `ppan_test`
contains `Jinja2` lines that will be parsed and ultimately render to a string of annotations that help `epmt` track
workflow functionality across different workflow settings.




## PPAN Specifics <a name="ppanspecifics"></a>

This section will minimally describe the PPAN specifics needed to submit workflows via any method described below.
Generally, more information on PPAN can be found under the RDHPCS systems wiki
[here](https://docs.rdhpcs.noaa.gov/systems/ppan_user_guide.html#) and on the GFDL wiki
[here](https://wiki.gfdl.noaa.gov/index.php/Main_Page). 



### Default `PATH` and `cylc` on PPAN <a name="ppancylcdefaults"></a>

On PPAN, your `PATH` has `cylc` by default. This can be seen on login by immediately running `which cylc`, and further
confirmed via `echo $PATH`. This smooths over configuration for managing/running workflows, at the cost of some
flexibility. To avoid the default `cylc`, a work around is to put your preferred `cylc` into your `PATH` at login, while
removing the default. To do this, insert into your shell's login/profile script (`bash`/`~/.bash_profile` used below):
```
# note, this is for bash
echo "(~/.bash_profile) removing /usr/local/bin from PATH"
echo "(~/.bash_profile) PATH was: $PATH"

export PATH=$(echo "$PATH" | awk -v RS=: -v ORS=: '$0 != "/usr/local/bin"' | sed 's/:$//')

# now add your preferred cylc to your PATH instead
export PATH=/path/to/your/preferred/cylc/bin:$PATH
echo "(~/.bash_profile) PATH now: $PATH"
```


### Terminal UTF-encoding Errors <a name="utfencodeerrors"></a>

An annoyance that sometimes pops up, preventung the submission of a workflow. There are two work arounds- one is putting
`LANG=C.UTF-8` in front of any shell calls that spawn the error. Another is, again, to edit your login/profile script
as above, defining `LANG` at login time:
```
# note, this for bash
echo "(~/.bash_profile) export LANG=C.UTF-8"
export LANG=C.UTF-8
```




## Configuring Workflows With `fre` <a name="freyamlframework"></a>

Developers are expected to know how to configure workflows with `fre`'s `yaml` framework, but this is not covered here.
This is considered user functionality under `fre-cli`, and as such, is fully described in `fre-cli`'s documentation,
located [here](https://noaa-gfdl.readthedocs.io/projects/fre-cli/en/latest/usage.html#yaml-framework). One should also
consult the documentation for `fre pp`, located [here](https://github.com/NOAA-GFDL/fre-cli/tree/main/fre/pp#readme).




## Running a Workflow on PPAN <a name="configrunppanworkflows"></a>

There are multiple approaches to setting up and running workflows on PPAN. This section specifically describes how to
locally run a copy of the CI/CD testing workflow in this repository. The approaches are described below in order of
least to most complex. They are also, equivalently, from the developer standpoint, in order of least to most flexible.

**All cases below make the following assumptions**:
- you have access to PPAN and have logged in
- you have adequate disk space for what you're trying to do
- you begin from a terminal with `$CWD` pointing to a clone of `fre-workflows` under `cylc-src` nor `cylc-run`
- you are making changes to the aforementioned clone, and now you need to test them
- you want to use the workflow defined in `for_gh_runner/yaml_workflow` and are OK with "mocking" the checkout step

If these assumptions match your current situation, you are in the right place! These are the assumptions made by the
local workflow running `bash` script, `for_gh_runner/run_pp_locally.sh`. It is similar to `for_gh_runner/runscript.sh`
by design, to keep workflow testing done on PPAN as apples-to-apples with this repository's pipeline as possible.



### Running Using LMOD Modules <a name="withlmod"></a>

This approach closely tracks how users will generally run workflows, and is the simplest/quickest approach. It's the
least flexible, as it forces usage of current releases of `fre-cli` and/or it's current `main` branch. As such, this
approach can only be used to test new changes to the workflow template itself, and cannot be used to evaluate how a
change in `fre-cli` may affect workflow functionality.

Assuming you have a copy of this repository already (see [above](#configrunppanworkflows) section), then to run a
workflow in this approach, all that is needed is-
```
# load fre, the current version may be updated or different than 2025.04
module load fre/2025.04

## if instead, you want the current main branch of noaa-gfdl/fre-cli
#module load fre/2025.test

# configure, install, validate, and run installed/configured workflow
source for_gh_runner/run_pp_locally.sh
```

You may run into some basic error messages at the `fre pp validate` step complaining about certain directories not
existing. As long as the complaints are about *output* directories, simply create the directories with `mkdir --parents`
and re-run `source for_gh_runner/run_pp_locally.sh`. The script will clean up after itself from previous run attempts,
mock the code checkout again, and re-configure/validate/install the workflow.



### Running With Your `conda` Environment and module-loaded `cylc` <a name="withcondaandcylc"></a>

**NOTE** It is highly recommended by the `cylc` package itself to keep the version consistent across `install`,
`validate`, and `play` steps. Though it's sometimes possible to let them differ and "force" `cylc` to run anyways, we
generally always follow this guideline to avoid any pathological behaviors that could result.

This approach will let you use your own `conda` environment with a custom `fre-cli` install, while leaning on a(n) LMOD
loaded `cylc`. The additional `module load cylc` will guarantee we only use one version of `cylc`, since this is the
`cylc` in one's `PATH` by default. As such, this approach is quite flexible, but requires that all changes are
compatible with a version of `cylc` that possibly differs from what is in the `fre-cli` environment.

If these caveats are acceptable, then begin by activating your `conda` environment, and figuring out where your `fre` is
```
module load miniforge
conda activate your-fre-cli-env

# note this down for the next step
which fre

# to make sure cylc versions don't differ between installed and running workflows
module load cylc
```

Now, open up `site/ppan_test.cylc` with your favorite text editor (or `site/ppan.cylc` to test without `epmt`
annotations/tagging), and under `[runtime]`, within the in the `root` task-family's `init-script` find the following:
```
[runtime]
    [[root]]
        init-script = """
            module load epmt
            module list
            epmt check

            module load fre/{{ FRE_VERSION }}
            module load hsm/1.3.0

            #### if one wants to use their own conda environment, edit the PATH and uncomment below like so:
            #export PATH=/home/$USER/conda/envs/fre-cli/bin:$PATH
        """
```

Uncomment the `export PATH=...` line to point to the folder containing the executable you found with `which fre`. Then,
we can use the `run_pp_locally` script again:
```
# configure, install, validate, and run installed/configured workflow
source for_gh_runner/run_pp_locally.sh
```



### Running With Only Your `conda` Environment <a name="withcondaonly"></a>

This is very similar to the [previous](#withcondaandcylc) approach, but requires you to create your own `global.cylc`
configuration and edit it to comply with system restrictions and enable proper functionality. First, consult the previous
[section](#globalcylcconfig) to create your own `global.cylc` beginning with the global config from the default `cylc`
in your `PATH`.

Next, open the `global.cylc` file and confirm the field `use login shell` is set to `true`, then find the `ssh command`
field and change it to `ssh`. Do this for both the `ppan` and `ppan_test` platform definitions.

Now, we need to remove the default `cylc` from our `PATH`, and additionally include a path to the exact `cylc` within
our conda environment. To accomplish this, follow the instructions in the previous section [here](#ppanspecifics).

Still with me? Now, just like in the [previous section](#withcondaandcylc), edit either `ppan.cylc` or `ppan_test.cylc`
in `site/` to add your `fre-cli` environment executables to `PATH` for your submitted workflow tasks. This should be the
last bit of editing we have to do.

Now, log out, and log back in to PPAN to make sure the new login specifics get picked up, and from the `fre-workflows`
directory do:
```
module load miniforge
conda activate your-fre-cli-env
source for_gh_runner/run_pp_locally.sh
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



### Inspect workflow progress with a terminal CLI <a name="cliprogressmon"></a>

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




## Older stuff still reviewing

### The User/Module Approach <a name="deflocalsetup"></a>

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
app/       environment.yml       etc/       Jinja2Filters/  pytest.ini     README-portability.md    site/
bin/       envs/       flow.cylc       lib/       README-developers.md  README_using_fre-cli.md  tests/
ESM4.5_candidateA.yaml  generic-global-config/  meta/       README.md     rose-suite.conf
> emacs site/ppan.cylc
```

The code that cylc runs from in `~/cylc-run/[your_test_experiment_workflow_id]` is copied from
`~/cylc-src/[your_test_experiment_workflow_id]`, not re-cloned from git. It is not advisable to
put any changes you want to be permanent in `~/cylc-src/[your_test_experiment_workflow_id]`. This
is a little bit risky - it can be hard to keep track of where your edits are taking place, but
allows you to avoid awkward back-and-forth edits in your git history.

How you edit `site/ppan.cylc` for the environment you would like to use might look different
depending on the developmental progress of the features you wish to test:



## testing by feature in `fre-cli`

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



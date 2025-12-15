# PPAN `fre-workflows` Developer Guide

`fre-workflows` can be used across multiple different platforms, but historically has been developed and tested on PPAN.
The following are guidelines for developing/testing on **PPAN**, but still contains some generally-applicable advice
to using `fre-workflows` elsewhere.




## Contents
1. [`cylc` Configuration](#cylcconfiguration)
    1. [`cylc` Documentation](#cylcdoc)
    2. [Global `cylc` Config](#globalcylcconfig)
	3. [`cylc` Platforms and Site](#cylcplatformandsite)
	    1. [`site` Value Specifics](#sitevaluespecifics)
2. [PPAN Specifics](#ppanspecifics)
    1. [PPAN `cylc` Defaults](#ppancylcdefaults)
    2. [Terminal UTF Encoding](#utfencodeerrors)
4. [Configuring Workflows With `fre`](#freyamlframework)
5. [Running Workflows With `fre` on PPAN](#configrunppanworkflows)
    1. [With LMOD and Modules](#withlmod)
    2. [With Your Own `conda`/`fre-cli` and LMOD `cylc`](#withcondaandcylc)
    3. [With Only Your Own `conda`/`fre-cli`](#withcondaonly)
6. [`cylc` Workflow Monitoring](#cylcmontips)
    1. [via GUI or TUI](#guituiprogressmon)
    2. [via CLI](#cliprogressmon)
7. [Testing and Verifying `epmt` Functionality](#epmttesting)
    1. [Verifying `epmt` Annotations and `papiex` Tags](#verifyingepmt)
8. [Further Notes on Workflow Development and Configuration](#notesworkflowdevconfig)
    1. [Workflow Task Environments / Requirements](#workflowtaskenvsreqs)
    2. [Workflow Configuration Hierarchy](#workflowconfighierarchy)
    3. [Workflow Editing Best Practices](#workfloweditingpractices)
        1. [Which Workflow File Should I Edit?](#whichfileedit)
        2. [Can I Edit the Code in `~/cylc-run`?](#editcylcruncode)
        3. [Can I Edit the Code in `~/cylc-src`?](#editcylcsrccode)
        4. [How Do I Test My Changes?](#howtotest)




## `cylc` Configuration <a name="cylcconfiguration"></a>

This section covers the basics of configuring `cylc` and other PPAN-specific configurations relevant to `cylc`.



### `cylc` Documentation <a name="cylcdoc"></a>

`fre-workflows` developers should be intimately familiar with the
[`cylc` documentation](https://cylc.github.io/cylc-doc/stable/html/index.html).



### `global.cylc` Configuration <a name="globalcylcconfig"></a>

If `cylc` is in your `PATH`, you can view the global configuration with `cylc config -d`. If desired, you can override
these values and define your own global configuration by placing a configuration file in the expected location.
To do this, start your global configuration with the current one:
```
mkdir --parents /home/$USER/.cylc/flow
cylc config -d > /home/$USER/.cylc/flow/global.cylc
# edit the file to your heart's content
```

Sometimes a configuration value or setting in a specific workflow takes precedence over the global configuration. For
details, consult the [`cylc` documentation](https://cylc.github.io/cylc-doc/stable/html/index.html).



### `cylc` Platforms and `site/` files <a name="cylcplatformandsite"></a>

`cylc` and `fre` treat the notion of platforms slightly differently, creating the potential for some confusion.

In `fre`, a platform typically refers to a specific environment of a specific system, generally for the purposes of
tracking which compilers and hardware are used, what settings are required to make models run, and where they were run.
It serves as a common input argument to many functions, helping uniquely identify workflow configurations.

In `cylc`, a platform is usually about selecting a specific set of global configuration values. In `fre-workflows`, it also
determines which file in `site/` will be included in the primary `flow.cylc` via `Jinja2`. For PPAN, the two relevant
platform values are `ppan` and `ppan_test`, corresponding to the template files `site/ppan.cylc` and `site/ppan_test.cylc`
respectively. The platform is chosen based on a `site` configuration value within a `fre` settings `yaml`.


#### `ppan` v. `ppan_test` <a name="sitevaluespecifics"></a>

These two platforms differ in one key field: the `job runner handler`. `site/ppan.cylc` specifies that `cylc`'s default
`Slurm` job runner handler will be used. `site/ppan_test.cylc` uses a custom version of the `Slurm` job
runner handler that parses the job script and tags certain operations for tracking via `epmt`. Additionally, `ppan_test`
contains `Jinja2` lines that are parsed and ultimately render to a string of annotations that help `epmt` track
workflow functionality across different workflow settings.




## PPAN Specifics <a name="ppanspecifics"></a>

This section describes the essential PPAN-specific configurations needed to submit workflows via any method described below.
For more comprehensive information on PPAN, consult the RDHPCS systems wiki
[here](https://docs.rdhpcs.noaa.gov/systems/ppan_user_guide.html#) and the GFDL wiki
[here](https://wiki.gfdl.noaa.gov/index.php/Main_Page).



### Default `PATH` and `cylc` on PPAN <a name="ppancylcdefaults"></a>

On PPAN, `cylc` is included in your `PATH` by default. You can verify this by running `which cylc` after login, or by
checking `echo $PATH`. While this simplifies configuration for managing and running workflows, it reduces
flexibility. To use a different version of `cylc`, you can add your preferred `cylc` to your `PATH` at login while
removing the default. To do this, add the following to your shell's login/profile script (`bash`/`~/.bash_profile` shown below):
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

UTF-encoding errors can occasionally prevent workflow submission. There are two workarounds: one is to prefix
`LANG=C.UTF-8` to any shell calls that produce the error. Alternatively, you can edit your login/profile script
as shown above, defining `LANG` at login time:
```
# note, this is for bash
echo "(~/.bash_profile) export LANG=C.UTF-8"
export LANG=C.UTF-8
```




## Configuring Workflows With `fre` <a name="freyamlframework"></a>

Developers are expected to know how to configure workflows with `fre`'s `yaml` framework, but this is not covered here.
This is considered user functionality under `fre-cli` and is fully described in the `fre-cli` documentation
[here](https://noaa-gfdl.readthedocs.io/projects/fre-cli/en/latest/usage.html#yaml-framework). You should also
consult the documentation for `fre pp` [here](https://github.com/NOAA-GFDL/fre-cli/tree/main/fre/pp#readme).




## Running a Workflow on PPAN <a name="configrunppanworkflows"></a>

There are multiple approaches to setting up and running workflows on PPAN. This section specifically describes how to
locally run a copy of the CI/CD testing workflow in this repository. The approaches are described below in order of
least to most complex. They are also, equivalently, from the developer standpoint, in order of least to most flexible.

**All cases below make the following assumptions**:
- you have access to PPAN and have logged in
- you have adequate disk space for what you're trying to do
- you begin from a terminal with `$CWD` pointing to a clone of `fre-workflows` not under `cylc-src` or `cylc-run`
- you are making changes to the aforementioned clone, and now you need to test them
- you want to use the workflow defined in `for_gh_runner/yaml_workflow` and are OK with "mocking" the checkout step

If these assumptions match your current situation, you are in the right place! These are the assumptions made by the
local workflow running `bash` script, `for_gh_runner/run_pp_locally.sh`. It is similar to `for_gh_runner/runscript.sh`
by design, to keep workflow testing done on PPAN as apples-to-apples with this repository's pipeline as possible.



### Running Using LMOD Modules <a name="withlmod"></a>

This approach closely tracks how users will generally run workflows and is the simplest and quickest approach. It is the
least flexible, as it forces usage of current releases of `fre-cli` and/or its current `main` branch. As such, this
approach can only be used to test new changes to the workflow template itself, and cannot be used to evaluate how a
change in `fre-cli` may affect workflow functionality.

Assuming you have a copy of this repository already (see the [above](#configrunppanworkflows) section), run the
workflow with the following:
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

This approach lets you use your own `conda` environment with a custom `fre-cli` install, while relying on an LMOD-
loaded `cylc`. The additional `module load cylc` ensures you only use one version of `cylc`, since this is the
`cylc` in your `PATH` by default. As such, this approach is quite flexible, but requires that all changes are
compatible with a version of `cylc` that possibly differs from what is in the `fre-cli` environment.

If these caveats are acceptable, begin by activating your `conda` environment and determining where your `fre` is located:
```
module load miniforge
conda activate your-fre-cli-env

# note this down for the next step
which fre

# to make sure cylc versions don't differ between installed and running workflows
module load cylc
```

Now, open `site/ppan_test.cylc` with your preferred text editor (or `site/ppan.cylc` to test without `epmt`
annotations/tagging), and under `[runtime]`, within the `root` task-family's `init-script`, find the following:
```
[runtime]
    [[root]]
        init-script = """
            module load epmt
            module list
            epmt check

            #### if you want to use your own conda environment, comment out 'module load fre/...' below
            module load fre/{{ FRE_VERSION }}
            module load gcp/2.3 hsm/1.3.0

            #### if you want to use your own conda environment, edit the PATH and uncomment below like so:
            #export PATH=/home/$USER/conda/envs/fre-cli/bin:$PATH
        """
```

Comment out the line with `module load fre/...`. Uncomment the `export PATH=...` line to point to the folder containing 
the executable you found with `which fre`. Then source the `run_pp_locally` script as before:
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

You will need to remove the default `cylc` from your `PATH` and include a path to the exact `cylc` within
your conda environment. To accomplish this, follow the instructions in the previous section [here](#ppanspecifics).

Next, just like in the [previous section](#withcondaandcylc), edit either `ppan.cylc` or `ppan_test.cylc`
in `site/` to add your `fre-cli` environment executables to `PATH` for your submitted workflow tasks. This should be the
last bit of editing you need to do.

Finally, log out and log back in to PPAN to ensure the new login configuration is applied, then from the `fre-workflows`
directory, run:
```
module load miniforge
conda activate your-fre-cli-env
source for_gh_runner/run_pp_locally.sh
```




## `cylc` workflow monitoring <a name="cylcmontips"></a>

`cylc` has two workflow viewing interfaces; a full graphical interface (GUI), text interface (TUI), and a variety of CLI
commands that can expose workflow and task information. The workflow will run and shut down when all tasks are complete.
If tasks fail, the workflow may stall, in which case it will shut down with an error after a period of time.



### Inspect workflow progress via GUI or TUI interface <a name="guituiprogressmon"></a>

The full GUI can be launched like so:
```
cylc gui --ip=`hostname -f` --port=`jhp 1` --no-browser
```

A text-based interface (TUI) is also available, though occasionally breaks for large workflows. It can be launched via:
```
cylc tui [workflow_id]
```

Then navigate to one of the two links printed to screen in your web browser.



### Inspect workflow progress with a terminal CLI <a name="cliprogressmon"></a>

If you just want a quick look at the state of your workflow, you can avoid the user interfaces and use the CLI instead.
Various `cylc` commands are useful for inspecting a running workflow. Run `cylc help`, `cylc help all`, and
`cylc <command> --help` for more information on how to use these tools.

The `workflow-state` command is particularly useful, for example:
```
cylc workflow-state -v [workflow_id]                # show all jobs
cylc workflow-state -v [workflow_id] | grep failed  # show only failed ones
```

Other useful CLI commands for monitoring your workflow progress:
- `cylc scan` - Lists running workflows
- `cylc cat-log [workflow_id]` - Shows the scheduler log
- `cylc list` - Lists all tasks
- `cylc report-timings` - Reports timing information




## Testing and Verifying `epmt` Functionality <a name="epmttesting"></a>

The `site` variable in `for_gh_runner/yaml_workflow/local_settings.yaml` controls which site configuration is loaded.
Setting `site='ppan'` runs without `epmt` integration. Setting `site='ppan_test'` enables `epmt` functionality. Namely,
these are per-task metadata annotations, and `papiex` tag insertion for shell calls and processes. The way these two
functionalities work is slightly different.

The metadata annotations are generated via Jinja2 within `site/ppan_test.cylc`, using available environment variables
and/or Jinja2 variables to pull and render the tag at runtime. The `papiex` tag insertion is more complex, requiring 
the use of a custom Slurm `job_runner_handler`. `job_runner_handler`s in `cylc` are classes that manage submission of
workflow tasks to a batch workload system. See
[here](https://cylc.github.io/cylc-doc/stable/html/user-guide/task-implementation/job-submission.html#supported-job-submission-methods) 
for more information on this concept.

The custom `handler` for `fre-workflows` is called `PPANHandler`, and the code for it is in `lib/python/ppan_handler.py`.
At job-submission time, `PPANHandler` inserts tags into the batch job script by calling `lib/python/tag_ops_w_papiex.py`, 
which parses the script line-by-line right before submission. It also saves a copy of the un-tagged job script for 
debugging purposes. The code for `PPANHandler` is thoroughly documented and commented. For more information, please see 
the docstrings and comments within the code.



### Verifying `epmt` Annotations and `papiex` Tags <a name="verifyingepmt"></a>

Running workflows with `epmt` enabled follows the same procedures described in section [4](#configrunppanworkflows), 
using `ppan_test` instead of `ppan`. After a workflow has at least partially completed, verify that `epmt` data was 
captured. Job success is irrelevant- `epmt` should retrieve the data successfully for near any degree of success/failure. 
From a workstation, do `module load epmt`, then `epmt python` to open a python shell with `epmt`. You can query job 
information below by replacing `your_user_here` with your username:
```python
>>>
>>> # setup, fill in your username, import epmt_query from epmt's built-in python shell
>>> my_user = 'your_user_here'
>>> import epmt_query as eq
>>>
>>> # query for jobs assoc with your username, show as list of job IDs
>>> my_jobs = eq.get_jobs(fltr=( eq.Job.user_id == my_user ), fmt='terse')
>>> my_jobs
>>> 
>>> # detailed job info with epmt annotations
>>> one_job_dict = eq.get_jobs(jobs=[my_jobs[-1]], fmt='dict')
>>> import pprint
>>> pprint.pprint(one_job_dict[0])
>>> 
>>> # if you know the value of $CYLC_WORKFLOW_UUID, you can get data for all of the workflow's jobs completed so far
>>> workflow_uuid = one_job_dict[0]['tags']['exp_run_uuid']
>>> one_workflows_worth_of_jobs = eq.get_jobs(tags=f'exp_run_uuid:{workflow_uuid}', fmt='terse')
>>> one_workflows_worth_of_jobs
>>>
```

The workflow UUID in the job tags allows retrieval of all jobs associated with a specific workflow run. This works for 
all workflow tasks regardless of success or failure, as `epmt` captures data in nearly all circumstances.




## Further Notes on Workflow Development and Configuration <a name="notesworkflowdevconfig"></a>



### Workflow Task Environments / Requirements <a name="workflowtaskenvsreqs"></a>

Each Slurm job that `cylc` submits runs from a bare environment. For example, if you submitted the workflow from a local
conda environment, that environment will not be automatically available, or activated, within the workflow tasks.
Therefore, if you want to invoke `fre-cli` (or any) tools from within `fre-workflows` tasks, you need to add `fre-cli`
to the batch task environment.

`cylc` provides several ways to specify the requirements of your tasks. One way is to set up environments and tools within
`init-script` or `pre-script` sections defined for each task. A simple example of a `pre-script` in `flow.cylc` looks like:
```
    [[RENAME-SPLIT-TO-PP]]
        pre-script = mkdir -p $outputDir
        script = rose task-run --verbose --app-key rename-split-to-pp
```



### Workflow Configuration Hierarchy <a name="workflowconfighierarchy"></a>

`cylc` workflow configuration is hierarchical, with site-specific configurations from (`site/`), layered on top of a 
central workflow configuration (`flow.cylc`), all of which is layered on top of a global `cylc` scheduler configuration 
(see section [1.2](#globalcylcconfig)). I.e., the global scheduler configuration is included first, then the central 
workflow template (`flow.cylc`) with basic task-parameters/task-family definitions, and then a site-specific configuration 
is appended and parsed from the `site/` directory.

As a developer, it is important to understand this, because it allows settings to be defined in multiple places. At first
this may seem redundant, but done intentionally, this can greatly increase the flexibility of a workflow template. If
done unintentionally, we can easily create nasty, hard-to-understand runtime bugs in our workflows. Note that when 
things are defined multiple times, the configuration value/setting/definition that takes precedence is the one closest
to the bottom of the workflow template.



### Workflow Editing Best Practices <a name="workfloweditingpractices"></a>


#### Which Workflow File Should I Edit? <a name="whichfileedit"></a>

**If you are trying to make changes to a workflow template, first consider where the changes should live**, given the
hierarchy described above. For example, if your changes are so specific to PPAN that the workflow will break everywhere
else, then those changes belong in both `site/ppan.cylc` and `site/ppan_test.cylc`. If the changes were specific to 
Gaea, they would go in `site/gaea.cylc`, etc. If the changes are truly platform independent, and must be propagated
to all sites, then the changes should go in `flow.cylc`.


#### Can I Edit the Code in `~/cylc-run`? <a name="editcylcruncode"></a>

**No, do not edit code in `~/cylc-run`**. The workflow templates get placed there at `install` time, and certain files being
tracked by `git` are edited in order to configure the workflow. The code in this folder is the code that gets used at 
run-time, and it should be managed by `cylc` only.

In any case, tracking changes on edited code in `cylc-run` becomes complicated very quickly, as `cylc` will edit the files
directly.


#### Can I Edit the Code in `~/cylc-src`? <a name="editcylcsrccode"></a>

**Technically yes, but we do not recommend this**. This goes against the "spirit" of what `cylc-src` is for within `fre`.
Code under `cylc-src` is supposed to be code which was checked out by `fre`, under a specific tag and/or branch on NOAA-GFDL
github repositories. Furthermore, the local test workflow defined `for_gh_runner/run_pp_locally.sh` assumes you are NOT 
editing the copy under `cylc-src`, and instead assumes you are developing a local clone of `fre-workflows`, with your
`$PWD` being the repository folder. 

This will ultimately mean you have three copies of the code lying around, with one being your local development copy, 
another being the mock-checked-out code under `cylc-src`, and the fully-configured code installed and run from `cylc-run`.
It's this "bloat" that tempts some `fre` developers to edit the code under `~/cylc-src` to develop changes. Some have 
done this without issue successfully, and some have regrettably forgotten to include details/changes critical to 
workflow functioning that were not easy to recall or re-engineer.


#### How Do I Test My Changes? <a name="howtotest"></a>

There are multiple routes, most of them are described in this document. Local testing on PPAN (see section 
[4](#configrunppanworkflows)) is highly recommended, as it gives developers options to test things out given the level
of flexibility required for testing the changes. 

In the case of PRs, testing success in current pipeline routines is expected, and required. The `create_test_conda_env` 
workflow must successfully build an environment and run all unit tests within the environment successfully. Additionally,
a manual run of the `test_cloud_runner` workflow is required, as it tests the postprocessing workflow in a fully integrated,
end-to-end manner. The success of the `test_cloud_runner` workflow must be unconditionally improved from the current version
of the `main` branch.





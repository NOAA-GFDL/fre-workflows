#fre-workflows

This repository holds code for defining tasks, applications, tools, workflows, and other aspects of the next-generation FRE postprocessing
ecosystem. 


<!-- ______________________________________________________________________________________________________________________ -->
# Instructions to postprocess FMS history files on GFDL's PP/AN
These instructions are targeted at workflow developers. If you are a user simply looking to run a specific workflow, see 
[`fre-cli`](https://github.com/NOAA-GFDL/fre-cli). 



<!-- ______________________________________________________________________________________________________________________ -->
## 1. Clone `fre-workflows` repository
```
git clone https://github.com/NOAA-GFDL/fre-workflows.git
cd fre-workflows
```
**Do not clone to a temporary directory** - the directory must be readable by slurm from all nodes. Directories on local 
`\vftmp` are not, while those on `/home`, `/work`, and `/xtmp` are.



<!-- ______________________________________________________________________________________________________________________ -->
## 2. Load Cylc, the backend workflow engine used by FRE
[`cylc`](https://cylc.github.io/cylc-doc/stable/html/) lets us parse workflow template files (`*.cylc`) and their 
configurations into modular, interdependent batch jobs. Tools used by those jobs (e.g. `fre-nctools` or `xarray`) should 
be loaded by those jobs as part of their requirements and do not need to be loaded at this time unless desired.

To run this repository's code, we need `cylc` accessible and somewhere in out `PATH` environment variable. One way is to activate
a conda environment with `cylc-flow`, `cylc-rose`, and `metomi-rose` installed. At GFDL's PP/AN, it is sufficient to do
```
module load cylc
```


<!-- ______________________________________________________________________________________________________________________ -->
## 3. Fill in rose-suite configuration fields
With your favorite text editor, open up `rose-suite.conf` and set variables to desired values. These values will be passed to
task definitions within `flow.cylc` and taken as configuration settings to instruct task execution.

Key values include:
- `SITE` set to "ppan" to submit jobs to PP/AN cluster
- `HISTORY_DIR` directory path to your raw model output
- `HISTORY_SEGMENT` amount of time covered by a single history file (ISO8601 datetime)
- `PP_CHUNK_A` amount of time covered by a single postprocessed file (ISO8601 datetime)
- `PP_CHUNK_B` secondary chunk size for postprocessed files, if desired (ISO8601 datetime)
- `PP_START` start of the desired postprocessing (ISO8601 datetime)
- `PP_STOP` end of the desired postprocessing (ISO8601 datetime)
- `PP_COMPONENTS` space-separated list of user-defined components, discussed in more detail below
- `PP_GRID_SPEC` path to FMS grid definition tarfile
- `PP_DEFAULT_XYINTERP` default target resolution for regridding, if the resolution is not specified elsewhere
- `FRE_ANALYSIS_HOME` For locating shared analysis scripts (only define if `DO_ANALYSIS=True`)

It is common to not know exactly what to set `PP_COMPONENTS` to when configuring a new workflow from scratch. Later
steps in this guide can help inform how to adjust these settings. The Rose configuation file format is described in full 
[elsewhere](https://metomi.github.io/rose/doc/html/api/configuration/rose-configuration-format.html)

If one is looking to hit the ground running at GFDL's PP/AN, copy/paste the code block here into your `rose-suite.conf`, replacing
`YOUR.USERNAME` with your own where applicable:
```
SITE="ppan"
EXPERIMENT='FOO'
PLATFORM='BAR'
TARGET='BAZ'

DO_STATICS=True
DO_TIMEAVGS=True
DO_ATMOS_PLEVEL_MASKING=True
DO_MDTF=False

DO_REFINEDIAG=False
REFINEDIAG_SCRIPTS="\$CYLC_WORKFLOW_RUN_DIR/etc/refineDiag/refineDiag_atmos_cmip6.csh"

DO_PREANALYSIS=False
PREANALYSIS_SCRIPT="\$CYLC_WORKFLOW_RUN_DIR/etc/refineDiag/refineDiag_data_stager_globalAve.csh"

DO_ANALYSIS=False
DO_ANALYSIS_ONLY=False
FRE_ANALYSIS_HOME="/home/fms/local/opt/fre-analysis/test"
ANALYSIS_DIR='/nbhome/YOUR.USERNAME/fre/FMS2023.04_om5_20240410/ESM4.2JpiC_om5b04r1'

CLEAN_WORK=True

PTMP_DIR='/xtmp/$USER/ptmp'

HISTORY_DIR='/archive/Ian.Laflotte/fre/FMS2023.04_om5_20240410/ESM4.2JpiC_om5b04r1/gfdl.ncrc5-intel23-prod-openmp/history'
HISTORY_SEGMENT='P1Y'

PP_DIR='/archive/YOUR.USERNAME/fre/FMS2023.04_om5_20240410/ESM4.2JpiC_om5b04r1/gfdl.ncrc5-intel23-prod-openmp/pp'
PP_CHUNK_A='P2Y'
PP_COMPONENTS='atmos atmos_scalar land land_static'
PP_START="00010101"
PP_STOP="00020101"
PP_DEFAULT_XYINTERP="360,180"
PP_GRID_SPEC='/work/Ian.Laflotte/mosaic_generation/exchange_grid_toolset/workdir/mosaic_c96om5b04v20240410.20240423.an105/mosaic_c96om5b04v20240410.20240423.an105.tar'
```



<!-- ______________________________________________________________________________________________________________________ -->
## 4. Create history file manifest (optional but highly recommended)
For more complete validation of workflow settings, we create a manifest for our history file archives with
```
tar -tf /path/to/history/YYYYMMDD.nc.tar | grep -v "tile[2-6]" | sort > history-manifest
```

The `history-manifest` contains a list of source files contained within the targeted history files. This can be 
helpful for validating settings on a component-by-component basis in the next step(s).



<!-- ______________________________________________________________________________________________________________________ -->
## 5. Define your desired postprocessing components for `remap-pp-components`
Users define their own postprocessing components for their workflow, which represent a group of source files to be postprocessed 
together. This grouping is typically united by a common gridding, which may be the current "native" gridding of the source files, 
or a desired target gridding to achieve via regridding. If `history-manifest` was created, it will be used to check that the
source files specified in the components are actually present in the history files. 

User-defined components are configured within `app/remap-pp-components/rose-app.conf`. An example set of components could be:
```
[command]
default=remap-pp-components

[atmos]
sources=atmos_month
grid=regrid-xy/default

[atmos_scalar]
sources=atmos_scalar atmos_global_cmip
grid=native

[land]
sources=land_month_cmip
grid=regrid-xy/288_180.conserve_order1

[land_static]
sources=land_static
grid=regrid-xy/288_180.conserve_order1
freq=P0Y
```

Here we've defined the `atmos` component as being a set of one source file, `atmos_month`. The `grid` field shows we wish to 
have these two source files regridded to the default resolution specified in `rose-suite.conf`. By contrast, the `atmos_scalar` 
component contains two source files, and specifies a `native` grid. This indicates that `atmos_scalar` and `atmos_global_cmip` 
source files will not be regridded when processing them for the `atmos_scalar` component. 

Note- it is not uncommon for a specific component to be named after a source file contained in it's `sources` field, but it 
does not imply anything special about the relationship between the source file and the component.

The third component is `land`, and will be regridded to a resolution corresponding to a 180x288 lat/lon grid, using an
interpolation scheme which is conservative to a first-order approximation. The last is the `land_static` component, and will 
be similarly handled to `land`. Since `land_static` is time-independent, it will require `freq=P0Y`, as the name is not used 
to determine if a component involves static data. Statics will only be processed if `DO_STATICS=True` in `rose-suite.conf`.

The setting for `PP_COMPONENTS` should reflect information in `app/remap-pp-components/rose-app.conf`. From our example, a
good list that passes validation would be `PP_COMPONENTS=atmos atmos_scalar land land_static`. 


<!-- ______________________________________________________________________________________________________________________ -->
## 6. Provide more specifics for `regrid-xy`
Any component specified in `app/remap-pp-components/rose-app.conf` requesting regridding requires a corresponding entry in 
`app/regrid-xy/rose-app.conf`, providing further information. A full set of options one can specify in this configuration 
can be found in `app/regrid-xy/README.md`. 

Following up on our example in the previous step, we would not have an extry in `app/regrid-xy/rose-app.conf` for 
`atmos_scalar`, but we will for `atmos`, `land` and `land_static` components:
```
[command]
default=regrid-xy

[atmos]
inputGrid=cubedsphere
inputRealm=atmos
interpMethod=conserve_order2
outputGridLat=180
outputGridLon=288
outputGridType=default
sources=atmos_month

[land]
inputGrid=cubedsphere
inputRealm=land
interpMethod=conserve_order1
outputGridLat=180
outputGridLon=288
outputGridType=288_180.conserve_order1
sources=land_month_cmip

[land_static]
inputGrid=cubedsphere
inputRealm=land
interpMethod=conserve_order1
outputGridLat=180
outputGridLon=288
outputGridType=288_180.conserve_order1
sources=land_static
```
Note that the `atmos_scalar` component does not have an entry here, as we requested a `native` regridding for source files in
that component. Full documentation on the available input configuration fields is available in the 
[`app/regrid-xy` directory](https://github.com/NOAA-GFDL/fre-workflows/tree/update.README/app/regrid-xy), but some things worth 
noting above:
- `inputGrid` can be `cubedsphere` or `tripolar`.
- `inputRealm` attribute is used for identifying the `land`, `atmos`, or `ocean` grid mosaic file.
- The `interpMethod` should be `conserve_order1`, `conserve_order2`, or `bilinear`.
- `OutputGridType` is the grid label referenced in the `app/remap-pp-components/rose-app.conf` file.
- `OutputGridLat` and `OutputGridLon` identify the target grid if `OutputGridType` is not specified




<!-- ______________________________________________________________________________________________________________________ -->
## 7. Validate your workflow configuration
Rose can validate the configuration by checking the field values against a list of rules defined by the devlopers of this 
repository. It's crucial to note that while this list of rules is determined by the requirements of th 

One can wait until this step in this guide, or validate as they go along at any point in the previous instructions
```
rose macro --validate
```
Common errors include non-existent directories and time intervals that are not ISO8601 datetimes. It is recommended to address
any/all complaints. If `history-manifest` exists, `rose macro --validate` will report on source files referenced by components 
that are not present in the history tar file archives. Whether a missing file is a show-stopper or a toothless complaint is
at the discretion of the user. If a source file is missing, consider reconfiguring the component definition(s), remove the 
source file from the component, or simply removing the component altogether.








<!-- ______________________________________________________________________________________________________________________ -->
## 8. Validate/Install/Run the configured workflow templates with `cylc`
Validate the workflow with `cylc` by entering: 
```
cylc validate .
```
If the Cylc validation fails but the Rose validation passes, please raise an issue on this repository, as it is better to 
catch configuration issues at the `rose macro --validate` step, and the validation rules can be updated to match the task
definition requirements.

We install the workflow with:
```
cylc install .
```
This creates a workflow directory in `~/cylc-run`. 

After successful installation, the workflow is launched with:
```
cylc play fre-workflows/run1
```
If on PP/AN, cylc launches a scheduler daemon on a `workflow1` server, via `ssh`, triggering the login banner to be printed. 
This daemon submits and runs jobs based on the task dependencies defined in `flow.cylc`. 






<!-- ______________________________________________________________________________________________________________________ -->
## 9. Inspect workflow progress with an interface (GUI or TUI)
The workflow will run and shutdown when all tasks are complete. If tasks fail, the workflow may stall, in which case
it will shutdown in error after a period of time.

`cylc` has two workflow viewing interfaces (full GUI and text UI), and a variety of CLI commands that can expose workflow
and task information. The text-based GUI can be launched via:
```
cylc tui fre-workflows/run1
```

The full GUI can be launched on jhan or jhanbigmem (an107 or an201).
```
cylc gui --ip=`hostname -f` --port=`jhp 1` --no-browser
```
Then, navigate to one of the two links printed to screen in your web browser. If one just wants a quick look at the state of
their workflow, the user-interfaces can be completely avoided by using the `workflow-state` command, two examples of which are:
```
cylc workflow-state -v fre-workflows/run1                # show all jobs
cylc workflow-state -v fre-workflows/run1 | grep failed  # show only failed ones
```



<!-- ______________________________________________________________________________________________________________________ -->
## 10. Inspect workflow progress with a terminal CLI
Various other `cylc` commands are useful for inspecting a running workflow. Try `cylc help`, and `cylc <command> --help` for
more information on how to use these tools to your advantage!

- `cylc scan` Lists running workflows
- `cylc cat-log fre-workflows/run1` Show the scheduler log
- `cylc list` Lists all tasks
- `cylc report-timings`







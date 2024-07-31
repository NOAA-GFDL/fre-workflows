<!-- 
based on: https://gitlab.gfdl.noaa.gov/fre2/workflows/postprocessing/-/raw/d51df76e537222a3c78405b5749fe59306e6d2bd/README.md
-->
This repository holds code for defining tasks, applications, tools, workflows, and other aspects of the FRE2 postprocessing
ecosystem. 



<!-- ______________________________________________________________________________________________________________________ -->
# Instructions to postprocess FMS history files on GFDL's PP/AN
These instructions are targeted at workflow developers. If you are a user simply looking to run a specific workflow, see 
[`fre-cli`](https://github.com/NOAA-GFDL/fre-cli). 



<!-- ______________________________________________________________________________________________________________________ -->
### 1. Clone `fre-workflows` repository
```
git clone https://github.com/NOAA-GFDL/fre-workflows.git
cd fre-workflows
```
**Do not clone to a temporary directory** - the directory must be readable by slurm from all nodes. Directories on local 
`\vftmp` are not, while those on `/home`, `/work`, and `/xtmp` are.



<!-- ______________________________________________________________________________________________________________________ -->
### 2. Load Cylc, the backend workflow engine used by FRE2
```
module load cylc
```
[`cylc`](https://cylc.github.io/cylc-doc/stable/html/) lets us parse workflow template files (`*.cylc`) and their 
configurations into modular, interdependent batch jobs. Tools used by those jobs (e.g. `fre-nctools` or `xarray`) should 
be loaded by those jobs as part of their requirements and do not need to be loaded at this time unless desired.




<!-- ______________________________________________________________________________________________________________________ -->
### 3. Fill in rose-suite configuration fields
With your favorite text editor, open up `rose-suite.conf` and set variables to desired values. These values will be passed to
task definitions within `flow.cylc` and taken as configuration settings to instruct task execution.

Key values include:
- `SITE` set to "ppan" to submit jobs to PP/AN cluster
- `HISTORY_DIR` directory path to your raw model output
- `HISTORY_SEGMENT` duration of each history segment (ISO8601)
- `PP_CHUNK_A` duration of your desired timeseries (and timeaverages, optionally)
- `PP_START` start of the desired postprocssing (ISO8601)
- `PP_STOP` end of the desired postprocessing (ISO8601)
- `PP_COMPONENTS` space-separated list of user-defined components
- `PP_GRID_SPEC` filepath to FMS grid definition tarfile
- `DEFAULT_XY_INTERP` e.g. `"288,180"`, default target resolution for regridded data.
- `FRE_ANALYSIS_HOME` For locating shared analysis scripts (only define if `DO_ANALYSIS=True`)

It is common to not know exactly what to set `PP_COMPONENTS` to when configuring a new workflow from scratch. Later
steps in this guide can help inform how to adjust these settings.

The Rose configuation file format is described (here)[https://metomi.github.io/rose/doc/html/api/configuration/rose-configuration-format.html]

<!-- ______________________________________________________________________________________________________________________ -->
### 4. Create history file manifest (optional but highly recommended)
For more complete validation of workflow settings, we create a manifest for our history file archives with
```
tar -tf /path/to/history/YYYYMMDD.nc.tar | grep -v "tile[2-6]" | sort > history-manifest
```

The `history-manifest` contains a list of source files contained within the targeted history files. This can be 
helpful for validating settings on a component-by-component basis in the next step.



<!-- ______________________________________________________________________________________________________________________ -->
### 5. Define your desired postprocessing components for `remap-pp-components`
Users define their own postprocessing components for their workflow, which represent a group of source files (listed in your 
`history-manifest`) to be post-processed together. This grouping is typically united by a common gridding, which may be the 
current "native" gridding of the source files, or a desired target gridding to achieve via regridding.

User-defined components are configured within `app/remap-pp-components/rose-app.conf`. A possible set of components for example,
could be:
```
[atmos]
sources=atmos_month
        atmos_daily
grid=regrid-xy/default

[atmos_scalar]
sources=atmos_scalar
        atmos_global_cmip
grid=native

[land]
sources=land_month_cmip
        land_daily_cmip
grid=regrid-xy/2deg

[land.static]
sources=land_static
grid=regrid-xy/default
freq=P0Y


```

Above, we've defined the `atmos` component as being a set of two source files, `atmos_month` and `atmos_daily`. The `grid`
field shows we wish to have these two source files regridded to the default resolution specified in `rose-suite.conf`. By
contrast, the `atmos_scalar` component specifies a `native` grid, indicating that `atmos_scalar` and `atmos_global_cmip` 
source files will not be regridded when processing them for the `atmos_scalar` component. 

Note- it is not uncommon for a specific component to be named after a source file contained in it's `sources` field, 
but it does not imply anything special about the relationship between the source file and the component.

The `land.static` component defined above gets interpreted as part of the `land` component, as any text after a `.` is 
ignored in component names. Here, we want `land` to contain `land_month`, `land_daily`, and `land_static`, and we want all 
all of them to be regridded to a 2-degree resolution gridding. The `freq=P0Y` field implies that `land_static` as a source 
file is time-independent, and will only be processed if `DO_STATICS=True` in `rose-suite.conf`.

The setting for `PP_COMPONENTS` should reflect information in `app/remap-pp-components/rose-app.conf`. From our example, a
good list that passes validation would be `PP_COMPONENTS=atmos atmos_scalar land`. 


<!-- ______________________________________________________________________________________________________________________ -->
### 6. Provide more specifics for `regrid-xy`
Add more-specific regridding instructions to `app/regrid-xy/rose-app.conf`:
```
[atmos]
inputGrid=cubedsphere
inputRealm=atmos
interpMethod=conserve_order2
outputGridType=default
sources=atmos_month
        atmos_daily

[land]
inputGrid=cubedsphere
inputRealm=land
interpMethod=conserve_order1
outputGridLon=144
outputGridLat=90
outputGridType=2deg
sources=land_month_cmip
        land_daily_cmip
        land_static
```

Note that the `atmos_scalar` component does not have an entry here, as we requested a `native` regridding for source files in
that component. 


- The `inputGrid` attribute should be `cubedsphere` or `tripolar`.
- The `inputRealm` attribute is used for identifying the land or atmos grid mosaic file: should be `atmos`, `land`, or `ocean`.
- The `interpMethod` should be `conserve_order1`, `conserve_order2`, or `bilinear`.
- `OutputGridType` is the grid label referenced in the `app/remap-pp-components/rose-app.conf` file.
- If `OutputGridType` is `default`, then the `DEFAULT_XY_INTERP` setting is used. Otherwise, `OutputGridLat` and `OutputGridLon` identify the target grid.


<!-- ______________________________________________________________________________________________________________________ -->
### 7. UPDATEME Optionally, report on history files that may be missing
Generate a "history manifest" file by listing the contents of a history tarfile to a file called 'history-manifest'.
```
tar -tf /path/to/history/YYYYMMDD.nc.tar | grep -v "tile[2-6]" | sort > history-manifest
```

If `history-manifest` exists, `rose macro --validate` will report on history files referenced but not present.

Probably, you should remove components that specify non-existent history files, reconfigure the component definition,
or trust that the missing history files will be created by a refineDiag script.




<!-- ______________________________________________________________________________________________________________________ -->
### 4. Validate your workflow configuration
When you are ready, you can have rose validate your configuration to catch common problems:
```
rose macro --validate
```
If there are any errors, try to address them. Common errors include non-existent directories and time intervals that
do not follow ISO8601 specifications. Iterate between editing your configuration and validating with rose until
all complaints are addressed. 











<!-- ______________________________________________________________________________________________________________________ -->
### 8. UPDATEME Validate/Install/Run the configured workflow templates with `cylc`
Validate the workflow configuation with `cylc validate .`

Please complain (to a Canopy developer) or take a note if if the Cylc validation fails but the Rose validation passes,
as this may expose some internal problems or quoting issues.



<!-- ______________________________________________________________________________________________________________________ -->
### 9. UPDATEME Install the workflow
```
cylc install .
```
This installs the workflow run directory in `~/cylc-run/<exp-name>/runN`, where `N` is an incrementing number (like `FRE --unique`). 
The various `cylc` commands act on the most recent `runN` by default.


<!-- ______________________________________________________________________________________________________________________ -->
### 10. UPDATEME Run the workflow
```
cylc play .
```
The workflow runs a daemon on the `workflow1` server (via `ssh`, so you see the login banner).

















<!-- ______________________________________________________________________________________________________________________ -->
### 11. UPDATEME Inspect workflow progress with an interface (GUI or TUI)
The workflow will run and shutdown when all tasks are complete. If tasks fail, the workflow may stall, in which case
it will shutdown in error after a period of time.

`cylc` has two workflow viewing interfaces (full GUI and text UI), and a variety of CLI commands that can expose workflow
and task information. The text-based GUI can be launched via:
```
cylc tui EXPNAME
```

The full GUI can be launched on jhan or jhanbigmem (an107 or an201).
```
cylc gui --ip=`hostname -f` --port=`jhp 1` --no-browser
```
Then, navigate to one of the two links printed to screen in your web browser


<!-- ______________________________________________________________________________________________________________________ -->
### 12. UPDATEME Inspect workflow progress with a terminal CLI
Various other `cylc` commands are useful for inspecting a running workflow. Try `cylc help`.

- `cylc scan` Lists running workflows
- `cylc workflow-state EXPNAME` Lists all task states
- `cylc cat-log EXPNAME` Show the scheduler log
- `cylc list EXPNAME` Lists all tasks
- `cylc report-timings EXPNAME`







If `history-manifest` exists, `rose macro --validate` will check for source files referenced within `PP_COMPONENTS` but
not present in the history files. 

It's recommended to remove components that specify non-existent history files, reconfigure the component definition,
or trust that the missing history files will be created by a refineDiag script.

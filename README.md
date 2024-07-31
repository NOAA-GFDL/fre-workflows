<!-- 
based on: https://gitlab.gfdl.noaa.gov/fre2/workflows/postprocessing/-/raw/d51df76e537222a3c78405b5749fe59306e6d2bd/README.md
-->


# Instructions to postprocess FMS history files on GFDL's PP/AN

### 1. Clone `fre-workflows` repository
```
git clone https://github.com/NOAA-GFDL/fre-workflows.git
cd fre-workflows
```
**Do not clone to a temporary directory** - the directory in question needs to be available for slurm to read from all nodes, 
and local `/vftmp` is not. `/home`, `/work`, and `/xtmp` are.


### 2. Load Cylc, the backend workflow engine used by Canopy
```
module load cylc
```
[`cylc`](https://cylc.github.io/cylc-doc/stable/html/) lets us parse workflow template files (`*.cylc`) and their 
configurations into modular, interdependent batch jobs. Tools used by those jobs (e.g. `fre-nctools` or `xarray`) should be 
loaded by those jobs as part of their requirements and do not need to be loaded at this time unless desired.


### 3. UPDATEME Create new configuration from empty template, where EXPNAME is the name of your new configuration/experiment
this step should be updated i think
```
cp opt/TEMPLATE.conf opt/rose-suite-EXPNAME.conf
```


### 4. UPDATEMEAdd required configuration items, led by schema prompting
while we're still slightly dependent on rose
```
rose macro --validate
```


### 5. UPDATEME Add configuration items to rose-suite.conf or opt/rose-suite-EXPNAME.conf.
```
vi rose-suite.conf              # Configuration for all experiments
vi opt/rose-suite-EXPNAME.conf  # Configuration for EXPNAME; can override default settings
```
Continue to add/uncomment required configuration items, until there are no schema violations.
Use double-quotes in the values!

Key values include:
- `HISTORY_DIR` directory path to your raw model output
- `HISTORY_SEGMENT` duration of each history segment (ISO8601)
- `PP_CHUNK_A` duration of your desired timeseries (and timeaverages, optionally)
- `PP_COMPONENTS` string-separated list of user-defined components
- `PP_START` start of the desired postprocssing (ISO8601)
- `PP_STOP` end of the desired postprocessing (ISO8601)

Other currently required values include:
- `DEFAULT_XY_INTERP` e.g. `"288,180"`. This is the default regridded grid.
- `FRE_ANALYSIS_HOME` For locating shared analysis scripts. (Should not be required unless `DO_ANALYSIS`, however)
- `PP_GRID_SPEC` filepath to FMS grid definition tarfile
- `SITE` set to "ppan" to submit jobs to PP/AN cluster


### 6. UPDATEME Configure your postprocessing components

A postprocessed component, originally defined in FRE Bronx and used in Canopy, is a user-defined label that has two main 
qualities:
- a single target horizontal grid: i.e. native atmosphere; native ocean; or regridded spherical (lat/lon)
- history files that should be included in the component

FMS history files are limited to a single time dimension, so commonly, multiple history files are mapped to
a single postprocess component. In the following examples, we will create an `atmos` component as a 1x1-degree regridded 
grid composed of the history files `atmos_month` and `atmos_daily`; a `land` component is regridded to a reduced 2-degree 
grid, and should contain `land_month`, `land_daily`, and `land_static`. Finally, a `atmos_scalar` component should be left 
on the native grid, and should contain `atmos_scalar` and `atmos_global_cmip`.

The steps for postprocess component configuration are:
1. Set the PP components you wish to process in the `PP_COMPONENTS` in the rose-suite file(s) described above.
2. Define the history file mapping in `app/remap-pp-components/rose-app.conf` and the regridding details in
`app/regrid-xy/rose-app.conf`.
3. Use `rose macro --validate` throughout for configuration validation.

For example, to postprocess the 3 components `atmos`, `land`, and `atmos_scalar`, set in your `opt/rose-suite-LABEL.conf` file:

```
PP_COMPONENTS="atmos land atmos_scalar"
```

Then, let `rose macro --validate` advise your edits. When the validation errors go away, your configuration is valid and 
consistent. After setting the `PP_COMPONENTS` above, the configuration validation will ensure configuration consistency and 
completeness.

```
rose macro --validate

[V] components.ComponentChecker: issues: 3
    (opts=TEMPLATE)template variables=PP_COMPONENTS=atmos land atmos_scalar
            Requested component 'atmos' is not defined in /nbhome/c2b/git/fre2/workflows/postprocessing/meta/lib/python/macros/../../../../app/remap-pp-components/rose-app.conf
    (opts=TEMPLATE)template variables=PP_COMPONENTS=atmos land atmos_scalar
            Requested component 'land' is not defined in /nbhome/c2b/git/fre2/workflows/postprocessing/meta/lib/python/macros/../../../../app/remap-pp-components/rose-app.conf
    (opts=TEMPLATE)template variables=PP_COMPONENTS=atmos land atmos_scalar
            Requested component 'atmos_scalar' is not defined in /nbhome/c2b/git/fre2/workflows/postprocessing/meta/lib/python/macros/../../../../app/remap-pp-components/rose-app.conf
```

To create your desired history file to postprocess component remapping, it's helpful (i.e. until history file manifests exist) to 
list the contents of the history tarfile in order to create your postprocessing configuration.

```
tar -tf /path/to/history/YYYYMMDD.nc.tar | grep -v "tile[2-6]" | sort
```

Each history file reported above may be included in your postprocess components. For example, here is an 
`app/remap-pp-components/rose-app.conf` file:
```
[atmos]
sources=atmos_month
        atmos_daily
grid=regrid-xy/default

[land]
sources=land_month_cmip
        land_daily_cmip
grid=regrid-xy/2deg

[land.static]
sources=land_static
grid=regrid-xy/default
freq=P0Y

[atmos_scalar]
sources=atmos_scalar
        atmos_global_cmip
grid=native
```

Explanation / discussion:
- The Rose configuation file format is described (here)[https://metomi.github.io/rose/doc/html/api/configuration/rose-configuration-format.html]
- The header sections identify the PP components. PP components may not contain periods! Any text after a period is optional, and merely serves to allow another section for remapping. (e.g. `land` and `land.static` identify the `land` component)
- - The `grid` attribute should be either "native", "regrid-xy/default", or "regrid-xy/LABEL". The regrid-xy label (default or user-defined) are defined in the `app/regrid-xy/rose-app.conf` file, described next.
- The `freq` attribute has special meaning and is needed for static processing. If `freq` is set to `0PY`, only the static
variables will be remapped. If `freq` is unset, then all temporal frequencies are included.

After adding your entries to `app/remap-pp-components/rose-app.conf`, run `rose macro --validate` again:

```
rose macro --validate

(opts=TEMPLATE)template variables=PP_COMPONENTS=atmos land atmos_scalar
Requested component 'atmos' uses history file 'atmos_daily' with regridding label 'regrid-xy/default', but this was not found in app/regrid-xy/rose-app.conf
(opts=TEMPLATE)template variables=PP_COMPONENTS=atmos land atmos_scalar
Requested component 'atmos' uses history file 'atmos_month' with regridding label 'regrid-xy/default', but this was not found in app/regrid-xy/rose-app.conf
(opts=TEMPLATE)template variables=PP_COMPONENTS=atmos land atmos_scalar
Requested component 'land' uses history file 'land_daily_cmip' with regridding label 'regrid-xy/2deg', but this was not found in app/regrid-xy/rose-app.conf
(opts=TEMPLATE)template variables=PP_COMPONENTS=atmos land atmos_scalar
Requested component 'land' uses history file 'land_month_cmip' with regridding label 'regrid-xy/2deg', but this was not found in app/regrid-xy/rose-app.conf
(opts=TEMPLATE)template variables=PP_COMPONENTS=atmos land atmos_scalar
Requested component 'land' uses history file 'land_static' with regridding label 'regrid-xy/2deg', but this was not found in app/regrid-xy/rose-app.conf
```

Now add corresponding regridding instructions for the regridding labels. This can be added to `app/regrid-xy/rose-app.conf`:

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

Explanation / discussion:
- The header sections identify the regridding instructions for a list of history files, and do not have meaning other than being unique.
- The `inputGrid` attribute should be `cubedsphere` or `tripolar`.
- The `inputRealm` attribute is used for identifying the land or atmos grid mosaic file: should be `atmos`, `land`, or `ocean`.
- The `interpMethod` should be `conserve_order1`, `conserve_order2`, or `bilinear`.
- `OutputGridType` is the grid label referenced in the `app/remap-pp-components/rose-app.conf` file.
- If `OutputGridType` is `default`, then the `DEFAULT_XY_INTERP` setting is used. Otherwise, `OutputGridLat` and `OutputGridLon` identify the target grid.


### 7. UPDATEME Optionally, report on history files that may be missing
Generate a "history manifest" file by listing the contents of a history tarfile to a file called 'history-manifest'.
```
tar -tf /path/to/history/YYYYMMDD.nc.tar | grep -v "tile[2-6]" | sort > history-manifest
```

If `history-manifest` exists, `rose macro --validate` will report on history files referenced but not present.

Probably, you should remove components that specify non-existent history files, reconfigure the component definition,
or trust that the missing history files will be created by a refineDiag script.


### 8. UPDATEME Validate the configuration
`rose macro --validate` should report no errors.

Then, validate the Cylc configuration:
`bin/validate-exp EXPNAME`

Please complain (to a Canopy developer) or take a note if if the Cylc validation fails but the Rose validation passes,
as this may expose some internal problems or quoting issues.


### 9. UPDATEME Install the workflow
```
bin/install-exp EXPNAME
```
This installs the workflow run directory in `~/cylc-run/<exp-name>/runN`, where `N` is an incrementing number (like `FRE --unique`). 
The various `cylc` commands act on the most recent `runN` by default.


### 10. UPDATEME Run the workflow
```
cylc play EXPNAME
```
The workflow runs a daemon on the `workflow1` server (via `ssh`, so you see the login banner).


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


### 12. UPDATEME Inspect workflow progress with a terminal CLI
Various other `cylc` commands are useful for inspecting a running workflow. Try `cylc help`.

- `cylc scan` Lists running workflows
- `cylc workflow-state EXPNAME` Lists all task states
- `cylc cat-log EXPNAME` Show the scheduler log
- `cylc list EXPNAME` Lists all tasks
- `cylc report-timings EXPNAME`

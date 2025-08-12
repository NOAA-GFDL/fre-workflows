# FRE Workflows
FRE Workflows is a climate model postprocessing system built on Cylc workflow engine and Rose configuration management. It provides automated postprocessing of climate model output from FMS (Flexible Modeling System) including regridding, time averaging, and analysis workflows.

Always reference these instructions first and fallback to search or bash commands only when you encounter unexpected information that does not match the info here.

## Working Effectively
- Bootstrap and set up the repository:
  - `conda env create -f environment.yml --name fre-workflows` -- takes 3 minutes to complete. NEVER CANCEL. Set timeout to 10+ minutes.
  - `source ~/.bashrc && conda activate fre-workflows`
  - Verify tools: `which cylc && which rose && which fre && which python`
- Validate workflow configuration:
  - `cylc lint -v` -- takes <1 second. Shows style issues but should complete successfully.
  - `rose macro --validate` -- takes <1 second. Shows required configuration variables and filesystem checks.
  - `cylc validate .` -- **WARNING: May hang with complex configurations. Use with caution or timeout after 30 seconds.**
- Run test suites:
  - `pytest -v ./tests` -- takes <2 seconds. Some test failures are expected in development environment.
  - Component-specific tests:
    - `cd app/remap-pp-components && pytest -v ./t` -- takes <2 seconds. Most tests should pass.
    - `cd app/make-timeseries && pytest -v ./test` -- takes <2 seconds. May have shell script syntax errors.
    - `cd Jinja2Filters && pytest -v ./tests` -- takes <1 second. Should pass completely.
    - `cd data_lineage && python -m unittest discover -s test -v` -- takes 3 seconds. Should pass completely.
- Code quality checks:
  - `pylint -v` (in specific app directories like app/make-timeseries)

## Validation
- ALWAYS run `rose macro --validate` before attempting workflow validation to catch configuration issues early.
- **CRITICAL**: `cylc validate .` may hang indefinitely with complex configurations due to Jinja2 processing. Use `timeout 30 cylc validate .` or avoid in CI environments.
- ALWAYS test configuration changes with minimal rose-suite.conf first before full workflow deployment.
- Configuration requirements are STRICT - all required variables must be defined or validation will fail.
- Filesystem validation warnings are normal in development environments (missing directories).

## Required Configuration for Workflow Validation
To validate a workflow with `rose macro --validate`, you MUST have:

1. **rose-suite.conf** with ALL required variables:
   - `SITE` (must be one of: 'ppan', 'generic', 'gfdl-ws', 'gaea' - use single quotes)
   - `EXPERIMENT` (name of your experiment, must match YAML filename)
   - `HISTORY_DIR` (path to model history files)
   - `PP_DIR` (postprocessing output directory)
   - `PP_GRID_SPEC` (path to grid specification file)
   - `PP_DEFAULT_XYINTERP` (default regridding resolution, e.g., "180,288")
   - `PTMP_DIR` (temporary directory path)
   - `TARGET` (target configuration name)
   - `PP_COMPONENTS` (space-separated list of components to process)
   - `PP_CHUNKS` (time chunk specification, e.g., "P1M")
   - Boolean switches: `DO_ANALYSIS`, `DO_ANALYSIS_ONLY`, `DO_STATICS`, `DO_TIMEAVGS`, `DO_ATMOS_PLEVEL_MASKING`, `DO_REFINEDIAG`, `DO_PREANALYSIS`, `DO_MDTF`, `CLEAN_WORK`
   - Time configuration: `HISTORY_SEGMENT`, `PP_CHUNK_A`, `PP_START`, `PP_STOP`

2. **Experiment YAML file** (named {EXPERIMENT}.yaml) defining postprocessing components:
   ```yaml
   postprocess:
     components:
       - type: "atmos"
         sources:
           - history_file: "atmos_month"
         sourceGrid: "cubedsphere"
         xyInterp: "180, 288"
         interpMethod: "conserve_order2"
         inputRealm: "atmos"
         postprocess_on: True
   ```

3. **Component configurations** in app/ directories:
   - `app/remap-pp-components/rose-app.conf` must define each component listed in PP_COMPONENTS
   - `app/regrid-xy/rose-app.conf` must define regridding parameters for components using regridding

## Workflow Operations
- Install workflow: `cylc install .` (creates workflow in ~/cylc-run)
- Run workflow: `cylc play {workflow-name}`
- Monitor workflow: `cylc tui {workflow-name}` or `cylc workflow-state -v {workflow-name}`
- NEVER attempt to run workflows in CI/development environments - they require GFDL-specific infrastructure.

## Common Tasks
The following are validated commands and their expected outputs:

### Environment Setup
```bash
# Create environment (3 minutes, NEVER CANCEL)
conda env create -f environment.yml --name fre-workflows

# Activate environment
source ~/.bashrc && conda activate fre-workflows

# Verify installation
which cylc     # /usr/share/miniconda/envs/fre-workflows/bin/cylc
which rose     # /usr/share/miniconda/envs/fre-workflows/bin/rose
which fre      # /usr/share/miniconda/envs/fre-workflows/bin/fre
which python   # /usr/share/miniconda/envs/fre-workflows/bin/python
```

### Testing Commands
```bash
# Root directory tests (<2 seconds)
pytest -v ./tests

# Component tests
cd app/remap-pp-components && pytest -v ./t           # <2 seconds, mostly passing
cd app/make-timeseries && pytest -v ./test            # <2 seconds, shell syntax errors expected
cd Jinja2Filters && pytest -v ./tests                 # <1 second, should all pass
cd data_lineage && python -m unittest discover -s test -v  # 3 seconds, should all pass

# Linting
cylc lint -v                    # <1 second, style issues expected
```

### Validation Commands  
```bash
# Configuration validation (<1 second)
rose macro --validate

# Workflow validation (<1 second if works, may hang - use with caution)
timeout 30 cylc validate .
```

## Example Working Configuration

### rose-suite.conf
```ini
[template variables]
SITE='generic'
EXPERIMENT="example"
HISTORY_DIR="/archive/example/history"
PP_DIR="/archive/example/pp" 
PTMP_DIR="/tmp/example/ptmp"
PP_GRID_SPEC="/work/example/grid_spec.tar"
TARGET="example-target"
HISTORY_SEGMENT="P1M"
PP_CHUNK_A="P1M" 
PP_CHUNKS="P1M"
PP_START="00010101"
PP_STOP="00010201"
PP_DEFAULT_XYINTERP="180,288"
PP_COMPONENTS="atmos"
DO_ANALYSIS_ONLY=False
DO_ANALYSIS=False
DO_STATICS=False
DO_TIMEAVGS=False
DO_ATMOS_PLEVEL_MASKING=False
DO_REFINEDIAG=False
DO_PREANALYSIS=False
DO_MDTF=False
CLEAN_WORK=False
```

### app/remap-pp-components/rose-app.conf
```ini
[command]
default=remap-pp-components

[atmos]
sources=atmos_month
grid=regrid-xy/default
```

### app/regrid-xy/rose-app.conf
```ini
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
```

## Repository Structure
- `flow.cylc` - Main Cylc workflow definition (Jinja2 template)
- `rose-suite.conf` - Rose configuration file (mostly commented template)
- `environment.yml` - Conda environment specification
- `app/` - Individual workflow applications (8 components)
- `site/` - Site-specific Cylc configurations (ppan, gaea, generic, gfdl-ws)
- `Jinja2Filters/` - Custom Jinja2 filters for workflow generation
- `data_lineage/` - Data lineage tracking utilities
- `tests/` - Root-level test suite
- `bin/` - Utility scripts
- `etc/` - Configuration and resource files

## Development Notes
- Configuration is hierarchical: site/*.cylc > flow.cylc in priority
- Boolean switches control workflow behavior (statics, timeavgs, analysis, etc.)
- Components are user-defined groups of source files for postprocessing
- Regridding configurations are specified in app/regrid-xy/rose-app.conf
- Test failures in development environment are normal and expected
- Shell script syntax errors in make-timeseries are known issues (line 46)
- Use CLEAN_WORK=False for development to preserve intermediate files for debugging
- `cylc validate .` may hang with complex Jinja2 templates - use `rose macro --validate` instead for configuration checking

## Time Expectations
- Environment creation: 3 minutes (NEVER CANCEL, set 10+ minute timeout)
- All validation commands: <1 second each (except cylc validate which may hang)
- All test suites: <3 seconds each (NEVER CANCEL, set 5+ minute timeout for safety)
- Workflow installation: <10 seconds
- Actual workflow execution: varies by data size and configuration (hours to days)

## Manual Validation Scenarios
After making changes to workflow configuration:
1. **Basic validation**: Run `rose macro --validate` and verify only filesystem warnings remain
2. **Component validation**: Ensure all PP_COMPONENTS are defined in app/remap-pp-components/rose-app.conf
3. **Regridding validation**: Verify regridded components have corresponding entries in app/regrid-xy/rose-app.conf
4. **Test execution**: Run component-specific test suites to verify functionality
5. **Lint checking**: Run `cylc lint -v` to check workflow syntax and style
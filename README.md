# Checkout PP suite and app templates
1. git clone --recursive git@gitlab.gfdl.noaa.gov:fre2/workflows/postprocessing.git 
1. cd postprocessing

# Bronx XML converter available
- bin/fre-bronx-to-canopy.py --help
- bin/fre-bronx-to-canopy.py -x XML -p PLATFORM -t TARGET -e EXP
- Takes a long time. module load FRE for frelist first
- After running, set PP_START and PP_STOP in rose-suite.conf, which are the only vars not set
- Double-check the history and PP directories
- "git status" to see the converter output

# Edit PP configurations
1. vi rose-suite.conf
1. vi app/regrid-xy/rose-app.conf
1. vi app/remap-pp-components/rose-app.conf

# Load Cylc
1. module load cylc/test

# Install workflow (on PP/AN)
1. ssh analysis
1. cylc validate .
1. cylc install --no-run-name (`--no-run-name avoids creating runN directories`)

# Start workflow (on PP/AN)
1. ssh analysis
1. cylc play postprocessing

# Monitoring
```
# GUI
1. ssh analysis, and choose 'jhan' at the PP/AN load balancer
2. cylc gui --ip=`hostname -f` --port=`jhp 1` --no-browser
3. Paste the http location given into your web browser

# Terminal GUI
# Note: on PP/AN, there is a python utf error that is resolved by
- setenv PYTHONUTF8 1
- cylc tui postprocessing

# Running jobs
- watch squeue -u $USER --sort=-M --state=r

# Workflow log
- cylc cat-log postprocessing

# Job scripts, stdout, and stderr (respectively)
- cylc cat-log postprocessing//<CYCLE-POINT>/<task-name> -f j
- cylc cat-log postprocessing//<CYCLE-POINT>/<task-name> -f o
- cylc cat-log postprocessing//<CYCLE-POINT>/<task-name> -f e

# Running, submitted, or failed tasks (jobs)
- cylc workflow-state postprocessing | grep -v succeeded
# Report of workflow timings
- cylc report-timings postprocessing
```

# Workflow and global configuration (respectively)
- cylc config postprocessing (`workflow configuration`)
- cylc config (`global configuration`)

# Workflow control
```
# Pause suite
- cylc stop postprocessing
# Stop a workflow and abandon any jobs
- cylc stop postprocessing --now
# Clean up run dir, log dir, share dir
- cylc clean postprocessing
# Reinstall flow.cylc updates but not rose app updates
- cylc play postprocessing
# to start a particular task
- cylc trigger postprocessing//<CYCLE-POINT>/<task-name>
```

# Graphing task dependencies
It's often helpful to visually see the task dependencies, and Cylc provides excellent graphing capability. A introduction is on the Cylc webpage (https://cylc.github.io/cylc-doc/8.0b3/html/tutorial/scheduling/graphing.html)

To see all the currently configured date (cycle point) range,

    cylc graph .

If you have trouble displaying the graphs through your X11 forwarding,
try saving the png file to disk and then viewing from the workstation:

    cylc graph . -o ~/cylc-graph.png
    display ~/cylc-graph.png

You may be overwhelmed by the task graph, especially a large range of dates or many history files. Reducing the time range is an option; e.g. to show just one segment,

    cylc graph . 1979 1979

Aside from reducing the time range, limiting the task parameters (history files and pp component lists) is a good approach. If you are only interested in graphing, simply edit the `flow.cylc` to replace the task paramaters with one each (any name will do). This won't run, but will make an easier graph to read. For example, change this (line 25ish):

    regrid =        {{ "regrid-xy" | form_task_parameters('temporal', PP_COMPONENTS) }}
    regrid_static = {{ "regrid-xy" | form_task_parameters('static', PP_COMPONENTS) }}
    native =        {{ "native" | form_task_parameters('temporal', PP_COMPONENTS) }}
    native_static = {{ "native" | form_task_parameters('static', PP_COMPONENTS) }}
    component  =    {{ PP_COMPONENTS | replace(' ', ', ') }}

to

    regrid =        regrid-history-file
    regrid_static = regrid-static-history-file
    native =        native-history-file
    native_static = native-static-history-file
    component  =    one-component

and then rerun the `cylc graph`

# Many more useful Cylc commands
- cylc help all

# What is happening?
- All files in ~/cylc-run/postprocessing: workflow logs, job logs, job scripts, work directories
- share and work directories are symlinked to /xtmp

# Other notes
- Useful Cylc examples from a Cylc developer (https://github.com/oliver-sanders/cylc-examples)
- data.gov recurrance examples on ISO8601 (https://resources.data.gov/schemas/dcat-us/v1.1/iso8601_guidance/)

# How to run on workstation (may need updating)
# Also, need corresponding settings in rose-suite.conf
- cylc validate .
- cylc install --symlink-dirs="work=/local2/home, share=/local2/home" --no-run-name
- cylc play postprocessing

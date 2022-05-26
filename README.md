# Checkout PP suite and app templates
1. git clone --recursive git@gitlab.gfdl.noaa.gov:fre2/workflows/postprocessing.git 
1. cd postprocessing

# Try Bronx XML converter
- bin/fre-bronx-to-canopy.py --help
- bin/fre-bronx-to-canopy.py -x XML -p PLATFORM -t TARGET -e EXP
- Takes a long time. module load FRE for frelist first
- After running, set PP_START and PP_STOP in rose-suite.conf, which are the only vars not set
- Double-check the history and PP directories
- There may be bug in work-dir cleaning. Turn off to be safe for now
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
1. cylc install --no-run-name (--debug) (`--no-run-name avoids creating runN directories`)

# Start workflow (on PP/AN)
1. ssh analysis
1. cylc play postprocessing (--debug)

# Monitoring
```
# GUI
1. Choose 'jhan' at the PP/AN load balancer
1. cylc gui --ip=`hostname -f` --port=`jhp 1` --no-browser
1. Paste the http location given into your web browser
# Terminal GUI
# Note: on PP/AN, there is a python utf error that is resolved by
# setenv PYTHONUTF8 1
- cylc tui postprocessing
# Running jobs
- watch squeue -u $USER --sort=-M --state=r
# Workflow log
- cylc cat-log postprocessing
- tail -f ~/cylc-run/postprocessing/log/workflow/log
# Job scripts, stdout, and stderr
- ls ~/cylc-run/postprocessing/log/job
# Running, submitted, or failed tasks (jobs)
- cylc workflow-state postprocessing | grep -v succeeded
# Report of workflow timings
- cylc report-timings postprocessing
```

# Retrieving configuration
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
- cylc trigger postprocessing pp-starter.20030101T0000Z
```

# Many more useful Cylc commands
- cylc help all

# What is happening?
- All files in ~/cylc-run/postprocessing: workflow logs, job logs, job scripts, work directories
- share and work directories are symlinked to /xtmp

# Other notes
- Useful Cylc examples from a Cylc developer (https://github.com/oliver-sanders/cylc-examples)
- data.gov recurrance examples on ISO8601 (https://resources.data.gov/schemas/dcat-us/v1.1/iso8601_guidance/)

# Running on workstation
# Need corresponding settings in rose-suite.conf also
- cylc validate .
- cylc install --symlink-dirs="work=/local2/home, share=/local2/home" --no-run-name
- cylc play postprocessing

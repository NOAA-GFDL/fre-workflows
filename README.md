# Checkout PP suite and apps
- git clone --recursive git@gitlab.gfdl.noaa.gov:fre2/workflows/postprocessing.git 
- cd postprocessing

# Running (on PP/AN)
- cylc validate .
# --no-run-name avoids creating runN directories
- cylc install --no-run-name
- cylc play postprocessing

# Running on workstation
# Need corresponding settings in rose-suite.conf also
- cylc validate .
- cylc install --symlink-dirs="work=/local2/home, share=/local2/home" --no-run-name
- cylc play postprocessing

# Retrieving configuration
# Configuration for this workflow
- cylc config postprocessing
# Global configuration (to be set GFDL admins in the future)
- cylc config

# Observing
# Terminal GUI
# Note: on PP/AN, there is a python utf error that is resolved by
# setenv PYTHONUTF8 1
- cylc tui postprocessing
# Running jobs
- watch squeue -u $USER --sort=-M --state=r
# Workflow log
- tail -f ~/cylc-run/postprocessing/log/workflow/log
# Job scripts, stdout, and stderr
- ls ~/cylc-run/postprocessing/log/job
# Running, submitted, or failed tasks (jobs)
- cylc workflow-state postprocessing | grep -v succeeded
# Report of workflow timings
- cylc report-timings postprocessing

# More usage notes
# Pause suite
- cylc stop postprocessing
# Stop a workflow and abandon any jobs
- cylc stop postprocessing --now
# Clean up run dir, log dir, share dir
- cylc clean postprocessing
# Many more useful Cylc commands
- cylc help all

# What is happening?
- All files in ~/cylc-run/postprocessing: workflow logs, job logs, job scripts, work directories
- share and work directories are symlinked to /xtmp

# More usage notes
# Reinstall flow.cylc updates but not rose app updates
- cylc reinstall postprocessing
- cylc play postprocessing
# to start a particular task
- cylc trigger postprocessing pp-starter.20030101T0000Z

# Other notes
- Useful Cylc examples from a Cylc developer (https://github.com/oliver-sanders/cylc-examples)
- data.gov recurrance examples on ISO8601 (https://resources.data.gov/schemas/dcat-us/v1.1/iso8601_guidance/)

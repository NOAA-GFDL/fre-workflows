# Environment instructions, recommended
- Add the below to the top of your ~/.cshrc
setenv PATH ${PATH}:/home/oar.gfdl.sw/conda/miniconda3/envs/cylc/bin
setenv CYLC_CONF_PATH /home/c2b/git/fre2/system-settings

# Environment instructions, alternate
- source /home/oar.gfdl.sw/conda/modulefiles
- conda activate cylc
- Still need to set CYLC_CONF_PATH somehow for batch jobs

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

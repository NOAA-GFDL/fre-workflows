# Instructions
- mkdir -p ~/.cylc/flow && cp /home/c2b/.cylc/flow/global.cylc ~/.cylc/flow (one-time only)
- source /nbhome/c2b/miniconda3/etc/profile.d/conda.csh
- conda activate cylc

# Running
- cylc validate .
- cylc install --no-run-name
- cylc play postprocessing

# Running on workstation (this almost works...)
- cylc validate . --opt-conf-key gfdl-ws
- cylc install --opt-conf-key gfdl-ws --symlink-dirs="work=/local2/home, share=/local2/home" --no-run-name

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
# Clean up run dir, log dir, share dir
- cylc clean postprocessing
# Many more useful Cylc commands
- cylc help all

# What is happening?
- All files in ~/cylc-run/postprocessing: workflow logs, job logs, job scripts, work directories

# More usage notes
# to avoid creating the many runN variations
- cylc install --no-run-name
# to reinstall any updates
- cylc stop postprocessing
- cylc reinstall postprocessing
- cylc play postprocessing
# to start a particular task
- cylc trigger postprocessing pp-starter.20030101T0000Z

# TODOs, ideas
- task dependency related
  - separate TS and TA, add 
  - Separate tasks where sensible (more granularity the better)
    - e.g. refineDiag tasks could be user-script specific in parallel

# Other notes
- Useful Cylc examples from a Cylc developer (https://github.com/oliver-sanders/cylc-examples)
- data.gov recurrance examples on ISO8601 (https://resources.data.gov/schemas/dcat-us/v1.1/iso8601_guidance/)

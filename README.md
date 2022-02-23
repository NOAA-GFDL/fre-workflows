# Instructions
- mkdir -p ~/.cylc/flow && cp /home/c2b/.cylc/flow/global.cylc ~/.cylc/flow (one-time only)
- source /nbhome/c2b/miniconda3/etc/profile.d/conda.csh
- conda activate cylc

# for PPAN:
- cylc validate .
- cylc install --no-run-name
- cylc play postprocessing

# What is happening?
- All files in ~/cylc-run/postprocessing/run1: workflow logs, job logs, job scripts, work directories
- cylc tui postprocessing/run1

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

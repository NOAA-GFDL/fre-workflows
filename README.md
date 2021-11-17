# Instructions
- mkdir -p ~/.cylc/flow && cp /home/c2b/.cylc/flow/global.cylc ~/.cylc/flow (one-time only)
- source /home/c2b/miniconda3/etc/profile.d/conda.csh
- conda activate cylc
# for PPAN:
- cylc validate .
- cylc install
- cylc play postprocessing/run1
# for workstations
- cylc validate . -O gfdl-ws
- cylc install -O gfdl-ws --symlink-dirs="work=/local2/home, share=/local2/home"
- cylc play postprocessing/run1

# What is happening?
- All files in ~/cylc-run/postprocessing/run1: workflow logs, job logs, job scripts, work directories
- cylc tui postprocessing/run1

# TODOs, ideas
- task dependency related
  - separate TS and TA, add 
  - Separate tasks where sensible (more granularity the better)
    - e.g. refineDiag tasks could be user-script specific in parallel

# Other notes
- Useful Cylc examples from a Cylc developer (https://github.com/oliver-sanders/cylc-examples)

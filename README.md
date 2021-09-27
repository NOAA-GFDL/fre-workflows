# Instructions
- source /home/c2b/miniconda3/etc/profile.d/conda.csh
- conda activate cylc
- cylc validate .
- cylc install
- cylc play postprocessing/run1

# TODOs, ideas
- task dependency related
  - separate TS and TA, add 
  - use families to group tasks sensibly
  - Separate tasks where sensible (more granularity the better)
    - e.g. refineDiag tasks could be user-script specific in parallel
  - Find good example for Jinja usage

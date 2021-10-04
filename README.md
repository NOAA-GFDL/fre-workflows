# Instructions
- source /home/c2b/miniconda3/etc/profile.d/conda.csh
- conda activate cylc
# for the default configuration (PPAN)
- cylc validate .
- cylc install
# for optional configurations, e.g. GFDL-WS
- cylc validate . -O gfdl-ws
- cylc install -O gfdl-ws --symlink-dirs="work=/local2/home, share=/local2/home"
- cylc play postprocessing/run1

# TODOs, ideas
- task dependency related
  - separate TS and TA, add 
  - use families to group tasks sensibly
  - Separate tasks where sensible (more granularity the better)
    - e.g. refineDiag tasks could be user-script specific in parallel
  - Find good example for Jinja usage

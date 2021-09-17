# Cylc usage notes:
- Does not work on workstations (background submit fails)
- `module load python/2.7.3 slurm`
- Add cylc to PATH

`setenv PATH ${PATH}:/home/c2b/opt/cylc/bin`

# Run suite

    rose suite-run

# Graph task dependencies
Graph 20 years of tasks

    cylc graph pp . 0001 0020

# TODOs, ideas
- task dependency related
  - separate TS and TA, add 
  - use families to group tasks sensibly
  - Separate tasks where sensible (more granularity the better)
    - e.g. refineDiag tasks could be user-script specific in parallel
  - Find good example for Jinja usage
- task runtime
  - Implement stager using Tom's Rose app
- configuration hooks and Rose
  - Configure experiment-specific items outside of suite.rc, in rose-suite.conf if sensible

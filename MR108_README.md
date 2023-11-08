#### ------------- testing the custom job runner branch 59.papiex_op_tags -------------
note- this is PPAN/GFDL specific while EPMT is still specific to the lab. this has
not been tested anywhere else.


### ------ set-up
this should largely follow the current README.md instructions. with two exceptions.

1 USE CORRECT BRANCH: check out branch `59.papiex_op_tags` after cloning.

2 EDIT CYLC GLOBAL CONFIG:  create the file `~/.cylc/flow/global.cylc` if you need to. 
To fill it with your current defaults: `cylc config | ~/.cylc/flow/global.cylc`

Then, all you should need to do is change the `job runner` field
under the `[[ppan]]` platform. using `sed -i` this can be done like:
```
sed -i 's/job runner = slurm/job runner = ppan_handler/' ~/.cylc/flow/global.cylc
```

make sure the settings get picked up- do `module load cylc` (`conda activate cylc`).
`unload`/`deactivate` first and re-`load`/`activate` if you need to. to confirm the 
change was picked up, the output of `cylc config  | grep -A 1 -B 2 ppan_handler`
should look like
```
[platforms]
    [[ppan]]
		job runner = ppan_handler
        hosts = localhost
```


### ------ running test cases with pytest
first, be in the root directory for this repo. and either
`module load cylc` or `conda activate /app/conda/miniconda/envs/cylc`.

then, you need a `pytest` module somewhere that can work with the cylc conda env
on PPAN. pip-install pytest into your `~/.local` (not allowed to do it in the env).
then. export `~/.local` to `PATH`.
```
pip install pytest
export PATH=$PATH:/home/$USER/.local/bin
```

if you did `module load ...`, then to run `pytest` for `ppan_handler`, you still
need to use the python within the cylc env. so target the `miniconda` env's
`python3`
```
export __CONDA_CYLC_PYTHON=/app/conda/miniconda/envs/cylc/bin/python
$__CONDA_CYLC_PYTHON -m pytest tests/test_PPANHandler.py tests/test_papiex_tooler.py
```

if you did `conda activate ...`, you can just call python in the usual way:
```
python -m pytest tests/test_PPANHandler.py tests/test_papiex_tooler.py
```

omit the target scripts to run all tests. not all tests pass at this time,
the failures are not related to the code in this MR (to Ian's knowledge at least).


### ------ testing the runner with a real workflow. 
after following the README.md instructions, you should have a experiment with a
full `opt/rose-suite-EXPNAME.conf` to work with. the workflow can be submitted
in the usual way from the repo's root directory- 
`bin/install-exp EXPNAME && cylc play EXPNAME/run1`

### ------ assessing runner functionality in a workflow
There is a somewhat annoying problem here- if we're using a custom
job runner like `lib/python/ppan_handler.py`, it's `STDOUT` and `STDERR` get
filtered at different points by the cylc.flow.job_runner_mgr, which creates
and manages a cylc-user's handler of choice. this means that if there's
e.g. a syntax/import error in `lib/python/ppan_handler.py`, the error message
is often silenced or not output to screen in the way one expects.

I've attempted to rig the class output `out` and `err` s.t. this is a less 
frustrating experience, but one should know it can still happen. 

### ------ to verify functionality:

## -- 1) (verbose)x2 + no-detach mode: `cylc play -v -v -N EXPNAME/runN`
this typically shows you the exit code of `ppan_handler.submit()`,
which is 0 upon successful submission (and confirmation via parsing
the STDOUT/ERR).

## -- 2) cat pp-starter job-activity immediately after submission:
`cat ~/cylc-run/EXPNAME/runN/log/job/YYYYMMDDT0000Z/pp-starter/NN/job-activity.log`
essentially tracks job-submission success/failure.

## -- 3) monitor total-workflow activity:
`watch -n "cylc workflow-state -v EXPNAME/runN | grep -v succeeded"`
omit the grep to view tasks in all different states

## -- 4) verify that the papiex-tooler did something:
not every task has ops-of-interest to the papiex tooler (e.g `pp-starter`).
`stage-history` is an early task in the workflow that typically reflects both
initial submission success. It also shows the functionality of `tool_ops_w_papiex`.
to easily compare the parsed job script with the original, do:
```
diff ~/cylc-run/EXPNAME/runN/log/job/YYYYMMDDT0000Z/stage-history/NN/job ~/cylc-run/EXPNAME/runN/log/job/YYYYMMDDT0000Z/stage-history/NN/job.notags
```
where YYYYMMDDT0000Z represents a cycle point (e.g. `19800101T0000Z`). you should 
see only one line of difference having to do with an `hsmget` call within a bash 
`if` statement. 



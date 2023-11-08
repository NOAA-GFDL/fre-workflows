#### ------------- testing the custom job runner branch 59.papiex_op_tags -------------
note- this is PPAN/GFDL specific while EPMT is still specific to the lab. this has
not been tested anywhere else.



### ------ check your env
test using the default `global.cylc` settings on PP/AN. if `.cylc/flow/global.cylc`
already exists, rename/backup/delete it as needed. to get the default settings in
there if they don't exist, `mkdir` as needed and:
```
module load cylc
cylc config | ~/.cylc/flow/global.cylc
```

change the `job runner` field under the `[[ppan]]` platform. this can be done and
verified with:
```
sed -i 's/job runner = slurm/job runner = ppan_handler/' ~/.cylc/flow/global.cylc
module unload cylc && module load cylc
cylc config  | grep -A 1 -B 2 ppan_handler
```

if the change was picked up, the output at the end should look like
```
[platforms]
    [[ppan]]
		job runner = ppan_handler
        hosts = localhost
```

if you don't see that output, talk to Ian. hopefully you shouldn't have to talk
to Ian at this point though.




### ------ set-up for success with pytest
clone the code into a fresh directory, `cd` and `checkout`:
```
git clone --recursive https://gitlab.gfdl.noaa.gov/fre2/workflows/postprocessing.git pp_MR108rev
cd pp_MR108rev && git checkout 59.papiex_op_tags
```

then, you need a `pytest` module somewhere that can work with the cylc conda env
on PPAN. you can't install the package into the cylc conda env with simple user
privileges.

to take my approach, we will pip-install pytest into your `~/.local`. be aware of
potential clashes with any currently installed packages. once you've pondered that
and decided in a pythonic (ad-hoc) spirit that it's likely fine, you can proceed.

unload cylc and load cylc from the `pp_MR108rev` dir. export `~/.local` to `PATH`.
```
module unload cylc && module load cylc
pip install pytest
export PATH=$PATH:/home/$USER/.local/bin
```

when running the tests via `pytest`, target the `cylc` `miniconda` env `python3`
```
export __CONDA_CYLC_PYTHON=/app/conda/miniconda/envs/cylc/bin/python
```

now run the tests:
```
$__CONDA_CYLC_PYTHON -m pytest tests/test_PPANHandler.py tests/test_papiex_tooler.py tests/tests_analysis_validator.py
```
the targeted tests above should succeed and not be based on any rose configuraiton
steps. not every test in `tests/` succeeds at this time, but the ones above should.

while you're here, run the bash tests to make sure i'm not losing my mind. make
sure you only see `VERY GOOD`s and no `VERY BAD`s.
```
source tests/test_papiex_tags_with_bash_if.bash
```


### ------ insert a real workflow configuration and real-workflow test
if you've gotten this far, congrats! our environments are the same more or less,
and we're ready to conifigure the workflow.

first, uncomment the configuartion fields in `rose-suite.conf`. then, use this
`rose-suite` optional configuration i use for `am5`:
```
mv opt/MR108_TEMPLATE.conf opt/rose-suite-am5_c96L33_amip.conf
```

now, we need to configure `regrid-xy` and `remap-pp-components`. i put the ones
i've used in the base directory of this repo.
```
cp MR108_regrid_rose_app app/regrid-xy/rose-app.conf
cp MR108_remap_pp_rose_app app/remap_pp_components/rose-app.conf
```

i think it's worthwhile to create the `history-manifest` for validation's sake.
look at your `HISTORY_DIR` value in `opt/rose-suite-am5_c96L33_amip.conf`, peek
at the location and
```
tar -tf <some history file in HISTORY_DIR> | grep -v "tile[2-6]" | sort >> history-manifest
```

now `rose macro --validate` and squash complaints. mostly the ones you need to
worry about to test the job runner are the ones regarding directories not existing.

the workflow can then be submitted in the usual way from the repo's root directory-
```
bin/install-exp am5_c96L33_amip && cylc play am5_c96L33_amip/run1
```
now you need to assess the functioning of the job runner. 

### REFINING TESTING ABOVE FIRST
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



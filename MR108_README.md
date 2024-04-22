#### ------------- testing the custom job runner branch 59.papiex_op_tags -------------
note- this is PPAN/GFDL specific while EPMT is still specific to the lab. this has
not been tested anywhere else. 


### ------ check your env
test using the default `global.cylc` settings on PP/AN. if `~/.cylc/flow/global.cylc`
already exists, rename/backup/delete it as needed. to get the default settings in
there if they don't exist, `mkdir` as needed and:
```
module load cylc
cylc config >> ~/.cylc/flow/global.cylc
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

from the repo's root dir `pp_MR108rev/`, we will use the cylc conda env. the pip install
will generate a warning that's addressed by the `export` statement. 
```
module unload cylc && module load conda && conda activate cylc
pip install pytest
export PATH=$PATH:/home/$USER/.local/bin
```

now run the tests:
```
python -m pytest tests/test_PPANHandler.py tests/test_papiex_tooler.py tests/test_analysis_validator.py
```
the targeted tests above should succeed and not be based on any rose configuraiton
steps. not every test in `tests/` succeeds at this time, but the ones above should.

while you're here, run the bash tests to make sure i'm not losing my mind. make
sure you only see `VERY GOOD`s and no `VERY BAD`s.
```
source tests/test_papiex_tags_with_bash_if.bash
```

now we do this because we can't submit jobs from the conda env. we do it this way to get
`pytest` interacting with the cylc env. which is terrible. so now do the following even
though it tastes bad.
```
conda deactivate && module unload conda && module load cylc
export __CONDA_CYLC_PYTHON=/app/conda/miniconda/envs/cylc/bin/python
$__CONDA_CYLC_PYTHON -m pytest tests/test_PPANHandler.py tests/test_papiex_tooler.py tests/test_analysis_validator.py
```
you should see all successful tests again. 



### ------ insert a real workflow configuration and real-workflow test
if you've gotten this far, congrats! our environments are the same more or less,
and we're ready to conifigure the workflow.

first, uncomment the configuration fields in `rose-suite.conf`.

then, copy the stock config made for this MR. it basically follows the `main` branch `am5`
configuration examples, minus the `atmos_daily` source file in the component sources list. 
```
cp opt/MR108_TEMPLATE.conf opt/rose-suite-am5_c96L33_amip.conf
cp MR108_regrid_rose_app app/regrid-xy/rose-app.conf
cp MR108_remap_pp_rose_app app/remap_pp_components/rose-app.conf
```

i think it's worthwhile to create the `history-manifest` for validation's sake.
```
tar -tf /archive/inl/am5/2022.01/c96L33_am5a0_cmip6Diag/gfdl.ncrc5-intel22-classic-prod-openmp/history/19800101.nc.tar | grep -v "tile[2-6]" | sort >> history-manifest & cat history-manifest
```

make sure you see output like this after this step:
```
...
./19800101.atmos_level_cmip.tile1.nc
./19800101.atmos_level_daily_cmip.tile1.nc
./19800101.atmos_month_aer.tile1.nc
./19800101.atmos_month_cmip.tile1.nc
./19800101.atmos_month.tile1.nc
./19800101.atmos_scalar.nc
...
```

now `rose macro --validate` and squash complaints about directories yet to be
created, simply by creating them. others are irrelevant to testing `ppan_handler`.

the workflow can then be submitted in the usual way from the repo's root directory-
```
bin/install-exp am5_c96L33_amip && cylc play am5_c96L33_amip/run1
```

do `watch -n 5 "cylc workflow-state -v am5_c96L33_amip/run1"`, wait a few minutes, and
you should see something like the following after a bit
```
connecting to workflow db for /home/Ian.Laflotte/cylc-run/am5_c96L33_amip/run1
pp-starter, 19800101T0000Z, succeeded
pp-starter, 19810101T0000Z, succeeded
stage-history, 19800101T0000Z, succeeded
stage-history-refined, 19800101T0000Z, running
stage-history, 19810101T0000Z, running
stage-history-refined, 19810101T0000Z, running
regrid-xy_land_daily_cmip, 19800101T0000Z, waiting
mask-atmos-plevel_atmos_month, 19800101T0000Z, waiting
regrid-xy_land_month_cmip, 19800101T0000Z, waiting
split-netcdf-native_atmos_global_cmip, 19800101T0000Z, waiting
regrid-xy_atmos_month, 19800101T0000Z, waiting
...
```

successes are a good sign. we can assess the job runner's functioning in other
ways too.

### ------ GENERAL NOTES ON THE CYLC JOB RUNNER MANAGER AND CUSTOM JOB RUNNERS
There is a somewhat annoying problem here- if we're using a custom
job runner like `lib/python/ppan_handler.py`, it's `STDOUT` and `STDERR` get
filtered at different points by the `cylc.flow.job_runner_mgr`, which creates
and manages a cylc-user's handler of choice. this means that if there's
e.g. a syntax/import error in `lib/python/ppan_handler.py`, the error message
is often silenced or not output to screen in the way one expects.

I've attempted to rig the class output `out` and `err` s.t. this is a less 
frustrating experience, but one should know it can still happen. if you
at some point suspect silent failure, you have options. `pytest` should catch
the most frequent causes of these silent errors, minor syntax issues.

## -- 1) (verbose)x2 + no-detach mode: `cylc play -v -v -N EXPNAME/runN`
this typically shows you the exit code of `ppan_handler.submit()`,
which is 0 upon successful submission (and confirmation via parsing
the STDOUT/ERR).

## -- 2) cat pp-starter job-activity immediately after submission:
`cat ~/cylc-run/EXPNAME/runN/log/job/YYYYMMDDT0000Z/pp-starter/NN/job-activity.log`
essentially tracks job-submission success/failure. 

## -- 3) continuously monitor total-workflow activity:
`watch -n "cylc workflow-state -v EXPNAME/runN | grep -v succeeded"`
omit the grep to view tasks in all different states. generally when `ppan_handler`
was not working, the problem shows up first in `pp-starter`, preventing the workflow
from kicking off, or causing the cylc scheduler to exhaust all possible retries,
both execution+submission retries. 

## -- 4) verify that the papiex-tooler did something:
not every task has ops-of-interest to the papiex tooler (e.g `pp-starter`).
`stage-history` is an early task in the workflow that typically reflects both
initial submission success. It also shows the functionality of `tool_ops_w_papiex`.
to easily compare the parsed job script with the original, do:
```
diff ~/cylc-run/am5_c96L33_amip/runN/log/job/19800101T0000Z/stage-history/NN/job ~/cylc-run/am5_c96L33_amip/runN/log/job/19800101T0000Z/stage-history/NN/job.notags
```
where 19800101T0000Z represents a cycle point. you should see only one line of
difference having to do with an `hsmget` call within a bash `if` statement.
```
< if { export PAPIEX_TAGS="op:hsmget;op_instance:1"; hsmget -v -t -a $historyDir -p $ptmpDir$historyDir -w $TMPDIR$historyDir $(basename -s .tar $file)/dummy\*; export SUCCESS=$?; unset PAPIEX_TAGS; } && [ $SUCCESS -eq 0 ]; then
---
> if hsmget -v -t -a $historyDir -p $ptmpDir$historyDir -w $TMPDIR$historyDir $(basename -s .tar $file)/dummy\*; then
```


## -- 5) verify that epmt got the data
in a separate analysis node login
```
module load epmt
epmt shell
```

in the ipython shell:
```
import os
username=os.environ['USER']

import epmt_query as eq
my_jobs=eq.get_jobs(tags='pp_is_canopy:YES;exp_name:am5_c96L33_amip',fltr=(eq.Job.user_id == username),after=-1, fmt='terse')

len(my_jobs)
```
this should grab some of the jobs you just ran, and the length of the jobid list should be 0.

convert the jobs to dict format and filter them for `stage-history` tasks
```
my_jobs=eq.get_jobs(jobs=my_jobs,tags='exp_component:stage-history',fmt='dict')
len(my_jobs)==4
```
the last statement should evaluate to true, assuming you didn't have to resubmit the workflow more than once when using this guide.

now check that the scraped `hsmget` call  in the tooled `stage-history` script was put in the dicitonary:
```
hsmget_proc=my_jobs[0].get('all_proc_tags')
if hsmget_proc is not None: print('yay')
```
I hope you see a "yay"!

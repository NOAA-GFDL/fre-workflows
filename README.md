# Instructions to post-process AM5 history files

Note: There is another, more detailed set of instructions available as a Google Doc here,
https://docs.google.com/document/d/1ACq9o8vBGUzAnV2vkrSoNKW2ogkF9oK7AS98-lm-w2g/edit?usp=sharing,
which may be slightly ahead, but this one will eventaully be synchronized.

0. Clone/checkout workflow and apps

```
git clone --recursive https://gitlab.gfdl.noaa.gov/fre2/workflows/postprocessing.git pp.am5
cd pp.am5
```

1. Load Cylc

```
module load cylc
```

2. List available postprocess configurations

Experiments with already created pp configurations are in the `opt/` directory, in the form `rose-suite-<exp-name>.conf`

```
bin/list-exps
am5_c96L33_amip     # 1 year and 6 year ouput
am5_c96L65_amip     # 8-day output
am5_c384L33_amip    # 8-day output
```

Pick one of the experiments, to replace in `<exp-name>` usage in later steps.

3. Convert the Variable Group files to the regrid and remap Rose app config files

```
bin/write-rose-configs opt/variable-groups/*
```

4. Validate the configuration

```
rose macro --validate
```

All warnings or errors should be fixed. If the fix is in the Variable Group files, then
rerun the previous step. The validation scripts check for experiment and Rose app
configurations only.

5. Validate and install the configuration

```
bin/install-exp <exp-name>      # cylc validate and install steps
```

This installs the workflow run directory in `~/cylc-run/<exp-name>/runN`, where N is an incrementing number (like FRE --unique). The various `cylc` commands act on the most recent `runN` by default.

6. Start the workflow

```
cylc play <exp-name>
...
2022-08-19T16:55:52Z INFO - Extracting job.sh to /home/Chris.Blanton/cylc-run/c96L33_am4p0/run1/.service/etc/job.sh
c96L33_am4p0/run1: workflow1.princeton.rdhpcs.noaa.gov PID=13280
```

The workflow runs a daemon on the `workflow1` server (via `ssh`, so you see the login banner).

7. Start the GUI (optional)

```
ssh analysis            # choose "jhan" (or "jhanbigmem") at the load balancer promp
cd /path/to/your/pp.am5 # dir created in the initial clone step
bin/start-gui           # cylc gui --ip=`hostname -f` --port=`jhp 1` --no-browser
```

Navigate to one of the two links printed to screen in your web browser

6. Examine workflow tasks and timings

Show the state of all tasks with the `workflow-state` command.
```
cylc workflow-state <exp-name>
```

If multiple workflows exist under the same `<exp-name>`, a specific run dir can be specified like e.g. `<exp-name>/run2` to limit the ouput to only `run2` tasks.

Show the current state of the workflow:
```
cylc scan -t rich --colour-blind
```

Report task timings:
```
cylc report-timings <exp-name>
```

Print job log to screen:
```
cylc cat-log <exp-name>//<cycle-point>/<task-name>
```

Print job error log to screen:
```
cylc cat-log -f e <exp-name>//<cycle-point>/<task-name>
```

7. More on validation

The Rose validation scripts act on all experiments.

```
rose macro --validate --suite-only
```

Try changing something to a nonsense value and see if the validator barks.

8. Manually trigger some tasks to see 8-day pp output (c96L65_am4p0_cmip6Diag)

Currently, for the first recurrence, more components are grouped together in unnecessary dependence for statics.
This could be improved, but for now the remap-pp-component tasks that write to /archive will not start until all
slow or doomed tasks finish.

Try triggering via the GUI or command line. For the GUI, click the X next to the color icon, then select Trigger.
For the command line,

```
cylc trigger <exp-name>//<cycle-point>/<task-name>
```

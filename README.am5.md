# Instructions to post-process AM5 history files

0. Clone/checkout workflow and apps

```
git clone --recursive https://gitlab.gfdl.noaa.gov/fre2/workflows/postprocessing.git pp.am5
```

1. Load Cylc

```
module load cylc
```

2. List available postprocess configurations

Experiments with already created pp configurations are in the `opt/` directory, in the form `rose-suite-<exp-name>.conf`

```
>bin/list-exps
c192L33_am4p0_cmip6Diag     # 4-day regression output
c96L65_am4p0_cmip6Diag      # 8-day regression output
c96L33_am4p0                # 2 years
c96L33_am4p0_cmip6Diag      # 2 years
```

Pick one of the experiments, to replace in `<exp-name>` usage in the following steps.

3. Validate and install the configuration

```
>bin/install-exp <exp>      # cylc validate -O $1 && cylc install -O $1 --workflow-name $1

```
This installs the workflow run directory in `~/cylc-run/<exp-name>/runN`, where N is an incrementing number (like FRE --unique).
The `--no-run-name` option simplifies the behavior at the cost of no future unique runs (it would install to `~/cylc-run/<exp-name>`). The various `cylc` commands act on the most recent `runN` by default, so in practice the usage is similar.


4. Start the workflow

```
>cylc play <exp-name>
...
2022-08-19T16:55:52Z INFO - Extracting job.sh to /home/Chris.Blanton/cylc-run/c96L33_am4p0/run1/.service/etc/job.sh
c96L33_am4p0/run1: workflow1.princeton.rdhpcs.noaa.gov PID=13280
```

The workflow runs a daemon on the `workflow1` server (via `ssh`, so you see the login banner).


5. Start the GUI (optional)
```
>ssh analysis

# choose "jhan" at the load balancer prompt. Please note that this connects you to an107 node. 
#CD into your pp.am5 directory where you cloned postprocessing repository initially.

>bin/start-gui              # cylc gui --ip=`hostname -f` --port=`jhp 1` --no-browser
```

Enter the given https location in your web browser


6. Examine workflow tasks and timings

Show the state of all tasks:
```
cylc workflow-state <exp-name>
```

Show the current state of the workflow:
```
cylc scan -t rich --colour-blind
```
Report task timings:
```
cylc report-timings <exp-name>
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
cylc trigger <exp-name>//cycle-point/task-name
```

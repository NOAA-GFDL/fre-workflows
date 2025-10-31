# fre-workflows

The fre-workflows repository holds GFDL's next-generation FRE (FMS Runtime Environment) workflow configuratiion template. This template utilizes cylc, a general purpose workflow engine that is very efficient for cyclic systems. In this workflow, tasks are defined, along with a task graph to determine task dependencies and when they run in the post-proceesing workflow.

For more information, see [cylc's user guide here](https://cylc.github.io/cylc-doc/stable/html/user-guide/index.html). Currently, this repository only contains one post-processing workflow template, however the team plans to expand and add more templates. 

Through the use of fre-cli tools ([`fre-cli repo`](https://github.com/NOAA-GFDL/fre-cli)), the fre-workflows repository is checked out under and experiment name in `~/cylc-src/`, configurations needed for the workflow are created and validated, and the experiment is installed and run by cylc. Once run, cylc automates batch job submission to system resources and produces post-processing model output.

This documentation will be updated when more workflows are added to this repository.

## Repository Table of Contents

The top level directory structure groups source code and input files as follow:

| File/directory                    | Purpose |
| --------------                    | ------- |
| ```Jinja2Filters```               | Collection of Python modules that preprocess the `flow.cylc` jinja template |
| ```app/```                        | Collection of workflow applications that are called from `flow.cylc`  NOTE: These will become `fre-cli` tools in the future |
| ```bin/```                        | Collection of scripts that are called from `flow.cylc`.  These scripts wrap calls to `fre-cli` and keep the `flow.cylc` file easy to read |
| ```envs/```                       | Directory containing Conda environment yaml file for installing cylc |
| ```for_gh_runner/```              | Directory containing YAML file configurations and the runscript used by the Portable Post-Processing (PPP) container in the test_cloud_runner pipeline |
| ```lib/python/```                 | Collection of Python modules used to implement EPMT |
| ```meta/```                       | Unused scripts.  To be removed in a future release. |
| ```site/```                       | Directory containing site specific cylc tasks defined in <site>.cylc files which are included in `flow.cylc` |
| ```tests/```                      | Test scripts used in GitHub Actions CI workflows |
| ```.cylcignore```                 | Files and directories to exclude during cylc-run installation  |
| ```README.md```                   | This project's README file with documentation |
| ```environment.yml```             | Conda environment yaml file for installing `fre-workflows` |
| ```flow.cylc```                   | Cylc workflow definition file containing configuration for FRE Postprocessing |
| ```for-developers.md```           | Documentation providing steps to run the postprocessing workflow for developers |
| ```portability-instructions.md``` | Documentation describing the portable workflow |
| ```pytest.ini```                  | Configuration file used by `pytest` |
| ```rose-suite.conf```             | Configuration file defining changeable parameters |

## `fre-cli` Postprocessing Instructions

Please see [FRE-cli](https://github.com/NOAA-GFDL/fre-cli/tree/main/fre/pp#readme) for instructions on how to run the
postprocessing using `fre-cli` commands at GFDL.

## Developer Instructions

Please see [for-developers.md](https://github.com/NOAA-GFDL/fre-workflows/blob/main/for-developers.md) for instructions
on how to run the postprocessing workflow as a workflow developer.

## Containerized Post-Processing Instructions

Please see
[portability-instructions.md](https://github.com/NOAA-GFDL/fre-workflows/blob/main/portability-instructions.md) for
information regarding how to run a containerized post-processing workflow.

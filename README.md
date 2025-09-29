# fre-workflows

FRE-workflows is GFDL's next-generation FRE (FMS Runtime Environment) workflow engine with a cylc backend ([see
cylc's user guide here](https://cylc.github.io/cylc-doc/stable/html/user-guide/index.html)).  FRE-workflows automates
the process of cloning model code, model compilation, batch job submission to system resources, and post-processing
model output. This new workflow relies on [`fre-cli`](https://github.com/NOAA-GFDL/fre-cli), the new FRE command-line
interface.  Currently, this repository only contains the `fre-cli` postprocessing workflow.  This documentation will be
updated when more workflows are added to this repository.

## Repository Table of Contents

The top level directory structure groups source code and input files as follow:

| File/directory                    | Purpose |
| --------------                    | ------- |
| ```Jinja2Filters```               | Collection of Python modules that preprocess the `flow.cylc` jinja template |
| ```app/```                        | Collection of workflow applications that are called from `flow.cylc`  NOTE: These will become `fre-cli` tools in the future |
| ```bin/```                        | Collection of scripts that are called from `flow.cylc`.  These scripts wrap calls to `fre-cli` and keep the `flow.cylc` file easy to read |
| ```envs/```                       | Directory containing Conda environment yaml file for installing cylc |
| ```lib/python/```                 | Collection of Python modules used to implement EPMT |
| ```meta/```                       | Unused scripts.  To be removed in a future release. |
| ```site/```                       | Directory containing site specific cylc tasks defined in <site>.cylc files which are included in `flow.cylc` |
| ```tests/```                      | Test scripts used in GitHub Actions CI workflows |
| ```.cylcignore```                 | Files and directories to exclude during cylc-run installation  |
| ```README.md```                   | This project's README file with documentation |
| ```environment.yml```             | Conda environment yaml file for installing `fre-workflows` |
| ```flow.cylc```                   | Cylc workflow definition file containing configuration for FRE Postprocessing |
| ```for-developers.md```           | Documentation providing steps to run the postprocessing workflow for developers |
| ```frecli-instructions.md```      | Documentation providing steps to trigger postprocesing via `fre-cli` commands |
| ```portability-instructions.md``` | Documentation describing the portable workflow |
| ```pytest.ini```                  | Configuration file used by `pytest` |
| ```rose-suite.conf```             | Configuration file defining changeable parameters |
| ```user-instructions.md```        | Documentation providing steps to run the postprocessing workflow |

## User Instructions

Please see [user-instructions.md](https://github.com/NOAA-GFDL/fre-workflows/blob/main/user-instructions.md) for
instructions on how to run the postprocessing workflow as a general user at GFDL.

## `fre-cli` Postprocessing Instructions

Please see [FRE-cli](https://github.com/NOAA-GFDL/fre-cli/tree/main/fre/pp#readme) for instructions on how to run the
postprocessing using `fre-cli` commands at GFDL.

## How to Install

Please see
[portability-instructions.md](https://github.com/NOAA-GFDL/fre-workflows/blob/main/portability-instructions.md) for
information regarding how to install the postprocessing workflow.

## Developer Instructions

Please see [for-developers.md](https://github.com/NOAA-GFDL/fre-workflows/blob/main/for-developers.md) for instructions
on how to run the postprocessing workflow as a workflow developer.







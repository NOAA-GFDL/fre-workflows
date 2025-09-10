# fre-workflows

This repository holds code for defining GFDL's next-generation FRE (FMS Runtime Environment) cylc workflows.
Currently, this repository only contains the `fre-cli` postprocessing workflow.  This documentation will be updated
when more workflows are added to this repository.

For more information on cylc workflows please refer to
[cylc's User Guide](https://cylc.github.io/cylc-doc/stable/html/user-guide/index.html)

## Where to find information

For more information on cylc workflows please refer to
[cylc's User Guide](https://cylc.github.io/cylc-doc/stable/html/user-guide/index.html)

For more information regarding `fre pp` please refer to documentaton in the
[`fre-cli` repository](https://github.com/NOAA-GFDL/fre-cli)

## What the files are what

| File/directory                    | Purpose |
| --------------                    | ------- |
| ```Jinja2Filters```               | Scripts that preprocess the `flow.cylc` file. |
| ```app/```                        | Tools that are referenced in `flow.cylc` tasks.  These will all be ported to
`fre-cli` in the future. |
| ```bin/```                        | Contains scripts that are referenced in `flow.cylc` tasks.  These scripts wrap
calls to `fre-cli` and keep the `flow.cylc` file easy to read. |
| ```envs/```                       | Contains a Conda environment yaml file for installing cylc |
| ```etc/refineDiag/```             |  |
| ```generic-global-config/```      |  |
| ```lib/python/```                 | Scripts used to implement EPMT |
| ```meta/```                       | Unused scripts.  To be removed in a future release. |
| ```site/```                       | Contains site specific cylc tasks defined in <site>.cylc files. These files are
included in `flow.cylc`|
| ```tests/```                      | Test scripts used in GitHub Actions workflows. |
| ```.cylcignore```                 | Files that `cylc install` will ignore when transferring files to the workflow
directory.  |
| ```README.md```                   | This project's README file with documentation. |
| ```environment.yml```             | A Conda environment yaml file for installing `fre-workflows`. |
| ```flow.cylc```                   | Defines a cylc workflow configuration for FRE Postprocessing. |
| ```for-developers.md```           | Provides steps to run the postprocessing workflow for developers. |
| ```frecli-instructions.md```      | Provides steps to trigger postprocesing via `fre-cli` commands. |
| ```portability-instructions.md``` | 
| ```pytest.ini```                  | The configuration file used by `pytest`. |
| ```rose-suite.conf```             | A configuration file defining changeable parameters. |
| ```user-instructions.md```        | Provides steps to run the postprocessing workflow. |

## User Instructions

Please see [user-instructions.md](https://github.com/NOAA-GFDL/fre-workflows/blob/main/user-instructions.md) for instructions on how to run the postprocessing workflow as a general user at GFDL.

## `fre-cli` Postprocessing Instructions

Please see [frecli-instructions.md](https://github.com/NOAA-GFDL/fre-workflows/blob/main/frecli-instructions.md) for instructions on how to run the postprocessing using `fre-cli` commands at GFDL.

## Instructions for Porting this Workflow Anywhere

Please see [portability-instructions.md](https://github.com/NOAA-GFDL/fre-workflows/blob/main/portability-instructions.md) for information regarding how to install the postprocessing workflow anywhere.

## Developer Instructions

Please see [for-developers.md](https://github.com/NOAA-GFDL/fre-workflows/blob/main/for-developers.md) for instructions on how to run the postprocessing workflow as a workflow developer.







# Portable Post-Processing
Post-processing workflows are normally run on PP/AN, hence packaages and modules used to run the workflow are specific to the PP/AN system. In order to extend post-processing capabilities to other systems, cylc, GFDL's fre-cli, and a few other packages were containerized.

The team uses podman, in conjunction with the Dockerfile, to build the container image and save it as a local tar image, and apptainer to convert the tar image to a singularity image file (sif). This container uses a conda environment that includes everything needed for the post-processing workflow to run which can be activated in a runscript. The runscript then proceeds to follow the fre-cli post-processing steps. 

For more information on the container build, workflow requirements, and running, see [here](https://github.com/NOAA-GFDL/HPC-ME/blob/main/ppp/README.md).

## Workflow Configuration
For the portable post-processing workflow, the same configuration files are used: 

1. workflow definition file (flow.cylc): defines the workflow, what scripts to use throughout the workfow, and task dependencies.
2. global.cylc: defines default cylc flow settings, including the job runner and platform information (further used in user site configurations).
3. site configurations: define the platform to be used and other site specific user settings, such as site specific tools
4. rose-suite.conf: defines specific info for the workflow such as environment variables for the cylc scheduler 

To help follow the workflow configuration, the following diagram was created.

```mermaid
flowchart LR
 subgraph s1["Cylc-Workflow-Definition"]
        f["flow.cylc"]
        FF["Sections of the workflow definition"]
        S("1.site: 
            - set user site
            - can be gfdl-ws, gaea, ppp-container, or ppan")
        f1("2.meta:
            - information about the workflow")
        f2("3.schedule:
            - settings for the scheduler
            - non-task-specific workflow configuration")
        f3("4.task parameters:
            - define task parameters values and parameter templates")
        f4("5.scheduling:
            - allows cylc to determine when tasks are ready to run
            - define families
            - defines qualifiers")
        f5("6.runtime:
            - determines how, where, and what to execute when tasks are ready
            - can specify what script to execute, what compute resources to use, and how to run a task")
  end
    f --> FF
    FF --> S & f1 & f2 & f3 & f4 & f5

    FF@{ shape: braces}
    style S text-align:left
    style f1 text-align:left
    style f2 text-align:left
    style f3 text-align:left
    style f4 text-align:left
    style f5 text-align:left
``` 

For the portable post-processing workflow, the site file, `ppp-container.cylc` is defined. As exhibited in the diagram below, the `ppan-container.cylc` file defines the platform as `localhost`, which references information in the `global.cylc` to run jobs in the background rather than submitted on slurm as usual. Additionally, it uses the conda environment created in the container (through the dockerfile) and activated in the runscript.

```mermaid
---
config:
  flowchart:
     wrappingWidth: '600'
  theme: redux-dark
---

flowchart TD
subgraph GFDL/GAEA Site files
s1[**gfdl-ws.cylc**:
    - uses platform=localhost]
s2[**gaea.cylc**: 
    - uses platform = localhost
    - loads FRE_VERSION]
s3[**ppan.cylc**:
    - uses platform = ppan
    - includes gfdl/ppan specific tools
    - loads FRE_VERSION]
end

subgraph Non-GFDL
s4[**ppp-container.cylc**:
    - uses platform = localhost
    - activates fre-cli and cylc conda environment in container]
end

G["***global.cylc***:
    - located in ***~/.cylc/flow/***
    - includes information for each platform used in the site configs
    - platforms include: **localhost (jobs run in background), ppan (jobs run on slurm)**
    - defines platform groups: ppan_background nodes
    - includes install directories for symlink locations: share, work"]

DG[***default global.cylc***:
    - platform = localhost
    - jobs run in background]

%% Flow
s1 -.-> G 
s2 -.-> G
s3 -.-> G
s4 -.-> DG

style s1 text-align:left
style s2 text-align:left
style s3 text-align:left
style s4 text-align:left                                                                                                                                               style f4 text-align:left
style G  text-align:left                                                                                                                                               style f4 text-align:left
style DG text-align:left 
```
As long as required data files are accessible and there is ample storage for the post-processing workflow output, the container can be used to run post-processing.

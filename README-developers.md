
Batch environment setup and fre-cli

The slurm jobs that cylc submits are run from a bare environment, not a copy of
the local environment you submitted the jobs from. This means that if you want to
invoke fre-cli tools from within fre-workflows, you need to add fre-cli to the 
batch environment. How you do this depends on how far along the development 
pipeline the features that you want to include in fre-cli are.  

To do this, you use the pre-script defined for each task: 

```
    [[RENAME-SPLIT-TO-PP]]
        pre-script = mkdir -p $outputDir
        script = rose task-run --verbose --app-key rename-split-to-pp
```


Features in fre-cli are part of a release

If the features that you want to include are part of a fre release, you can 
load a fre module from the pre-script of your cylc task: 

```
    [[SPLIT-NETCDF]]
        pre-script = module load fre/2025.03; mkdir -p $outputDir
```

Features in fre-cli are merged into main

If the features that you want to include are merged into main but not yet part 
of a fre release, you can use them by loading fre/test. 

```
    [[SPLIT-NETCDF]]
        pre-script = module load fre/test; mkdir -p $outputDir
```


Features in fre-cli are in a development branch

If you wish to work with changes that are not yet merged into main, the
setup-script needs to set up your conda environment for the fre-cli repo that 
you are working with. Remember: the slurm job scripts are executed as you, and 
have access to your conda environments.

```
    [[SPLIT-NETCDF]]
        pre-script = module load miniforge; conda activate fre-cli; mkdir -p $outputDir
```

For more information on conda environment setup for fre-cli, see: 

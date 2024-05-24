# Remap-pp-components
The remap-pp-components python script works to remap the diagnostics from one convention (i.e. history files) to another (i.e. PP components). It imports the `metomi`, os, subprocess, glob, and pathlib python modules, accessible through `module load fre/canopy`. 

The main remap-pp-components function uses 8 arguments that are defined as environment variables in the `flow.cylc` for the remap task:

```
if __name__ == '__main__':
   remap(inputDir,outputDir,begin,currentChunk,components,product,dirTSWorkaround,ens_mem)
```

Where: 

- `inputDir`: input directory where files are found
- `outputDir`: output directory where files are copied to
- `begin`: date to begin post-processing
- `currentChunk`: current chunk to post-process
- `components`: components to be post-processed
- `product`: variable to define time series or time averaging
- `dirTSWorkaround`: time series workaround variable
- `ens_mem`: the ensemble member number

As of right now, the rewrite utilizes the `rose-app.conf` file in order to extrapolate information about the components to be post-processed. This information includes:

- `grid`: refers to a single target grid, such as "native" or "regrid-xy"
- `sources`: refers to history files that are mapped to, or should be included in, a defined component

The `rose-app.conf` is created via the `configure-yaml` tool in the fre-cli. For more information on where the remap-pp-components rose-app configuration gets its component, one can look to the command:

```
tar -tf /path/to/history/YYYYMMDD.nc.tar | grep -v "tile[2-6]" | sort
```

This command will list the contents of the history tarfile given. Each history file listed can be included in pp components and components to be remapped.

### Testing suite
_________________________________________________________________________
Pytest was used for the remap-pp-components testing-suite in the file `t/test_remap-pp-components.py`. This file includes:

- *ncgen_remap_pp_components*: creates a netCdf file from a cdl file using the test data provided 
- *ncgen_output*: links the output netCdf file to an output location 
- *original_remap_pp_components*: remaps diagnostics using the original remap-pp-components script (will be removed with the replcaement of its python counterpart)
- *rewrite_remap_pp_components*: remaps diagnostics using the rewritten remap-pp-components script
- *nccmp_ncgen_origremap*: compares the output from the ncgen test and the original remap script
- *nccmp_ncgen_rewriteremap*: compares output from the ncgen test the the remap rewrite script
- *nccmp_origremap_rewriteremap*: compares output from the original remap script and the remap rewrite script

In order to use the test script, `pytest` and `nccmp` are required. 

- `nccmp` is available through `module load fre/canopy` 
- For pytest, the user can either,
   1) create a conda environment and install pytest
         
      ```
      conda create --name remap-rewrite
      conda activate remap-rewrite
      conda install conda-forge::nccmp
      ```

   2) put pytest in the user's local packages

      ```
      pip install --user pytest
      export PATH=/home/$USER/.local/bin:$PATH   # make it callable
      ```

From the `/app/remap-pp-component-python/` directory, run:
   ```
   python -m pytest t/test_remap-pp-components
   ```

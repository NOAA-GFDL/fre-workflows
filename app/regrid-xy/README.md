# ABOUT

`regrid-xy` remaps scalar and/or vector fields. It is capable of remapping from a spherical grid onto a different (spherical, or tripolar) grid.
By default, it does so using a conservative scheme. Additional, alternative schemes can be defined and used as well.
_#TODO check this_

# ASSUMPTIONS

The app requires an input file name, pointing to a netCDF file holding scalar or vector data, with or without `.nc` extension. The `#tile` suffix
should be absent in the case of multi-tile files. The file path should not be included
_#TODO also check this_

The number of files required for regridding scalar data is one. While in the case of vector data, it can be one or two files
_#TODO check this, why?_

# ARGUMENTS

The `input_mosaic` argument specifies the input mosaic file, which contains list of tile files that specify grid information for each tile.
_#TODO mosaic v grid? is jargon of choice here correct? _

The `output_mosaic` argument specifies the output mosaic file.
This file contains list of tile files which specify the grid information for each tile. When `output_mosaic` is not specified, the number of
longitudinal and latitudinal divisions (`nlon`, `nlat` respectively) must be specified.
_#TODO check subcases_

The `remap_file` argument specifies the output file name to saves remapping information to. If `remap_file` is specified but the file does not exist,
remapping information will be calculated and stored in `remap_file`.
If `remap_file` is specified and the file exists, remapping information will be read from `remap_file`.
_#TODO awkward I/O, no? check and reconsider perhaps..._

# ROSE CONFIGURATION

**OUTDATED?***

`rose-app.conf` is where configuration info is placed, and defines input/output files, grids, etc. `regrid-xy` uses this to execute the desired
regridding of data. This configuration is user-defined and specified.

Below, `gridSpec` is a given location for the grid specification dataset. The first and second components run by `regrid-xy` would be e.g.:
```
[atmos] 
sources=aerosol_hourly_cmip aerosol_month_cmip atmos_co2_month atmos_diurnal atmos_diurnal_cmip atmos_global_cmip atmos_hourly atmos_level_cmip atmos_month atmos_month_aer atmos_month_cmip atmos_static_cmip atmos_tracer
inputGrid=cubedsphere
inputRealm=atmos
outputGridLon=288
outputGridLat=180
gridSpec=/archive/../../, 

[land] 
sources=fire_month land_dust land_month land_month_cmip land_month_inst land_static land_static_cmip land_static_sg lumip_Lmon_crp lumip_Lmon_psl lumip_Lmon_pst lumip_Lyr lumip_Lyr_crp lumip_Lyr_psl lumip_Lyr_pst river_daily river_month river_month_inst river_static river_static_cmip
inputGrid=cubedsphere
inputRealm=land
outputGridLon=288
outputGridLat=180
gridSpec= archive/../../, which is  a given location for the grid specification dataset
```
Then execute:
`rose app-run`

# REGRID_XY PYTESTS INLINE DOC SAYS
The purpose of the code is to recreate a *.nc file(s) based on the timesteps within that file which it could be days, 
months or years.  It is a pytest collection of routines.  all test_* routines will be called in the order defined. 
First is to test and check for the creation of required directories and a *.nc file from *.cdl text file.

FRE Canopy app regrid_xy tests by successfully regridding and remapping files with rose app as the valid definitions
are being called by the environment.

Usage on runnung this app test for regrid_xy is as follows: 
```
module load fre/test cylc cdo python
cd regrid_xy 
pytest t/test_regrid_xy.py
```

***regarding the above module combo...***
```
an203:~/Working/postprocessing> module load cylc python cdo fre/test
Loading python/3.9
  Loading requirement: conda

Loading cdo/2.1.1
  Loading requirement: hdf5/1.14.1-2 netcdf-c/4.9.2 proj/9.2.0 udunits/2.2.28

Loading perlbrew/5.38.0
  ERROR: Conflicting perlbrew is loaded

Loading gcp/test
  ERROR: Requirement perlbrew/5.38.0 is not loaded

Loading fre/test
  ERROR: Load of requirement perlbrew/5.38.0 failed
  ERROR: Load of requirement gcp/test failed
```

***regarding status of tests***
`fre/test` not loading as a module... using `fre/bronx-20` instead...
test 1 test_regrid_xy failure:
```
ncgen: NetCDF: Not a valid data type or _FillValue type mismatch
	(/home/conda/feedstock_root/build_artifacts/libnetcdf_1660350760069/work/ncgen/genbin.c:genbin_netcdf:130)
...
Error from pe 0: mpp_io(mpp_open): error in opening file /vftmp/Ian.Laflotte/pid182978/pytest-of-Ian.Laflotte/pytest-2/test_regrid_xy0/20030101.nc/C96_grid.tile1.nc: NetCDF: Unknown file format
...
...
...
>       assert sp.returncode == 0
E       AssertionError: assert 1 == 0
E        +  where 1 = CompletedProcess(args=['rose', 'app-run', '-D', '[env]inputDir=/vftmp/Ian.Laflotte/pid182978/pytest-of-Ian.Laflotte/py...ridLat=180', '-D', '[atmos_static_cmip]gridSpec=/archive/gold/datasets/OM4_05/mosaic_c96.v20180227.tar'], returncode=1).returncode
```


test 2 failure: gridSpec unbound variable NO ITS NOT
```
+ echo Arguments:
+ echo '    input dir: /vftmp/Ian.Laflotte/pid182978/pytest-of-Ian.Laflotte/pytest-2/test_regrid_xy0/20030101.nc'
+ echo '    output dir: /vftmp/Ian.Laflotte/pid182978/pytest-of-Ian.Laflotte/pytest-2/test_success_regrid_xy0/out-dir'
+ echo '    begin: 20030101T000000'
+ echo '    TMPDIR: /vftmp/Ian.Laflotte/pid182978'
+ echo '    fregrid mapfile dir: /vftmp/Ian.Laflotte/pid182978/pytest-of-Ian.Laflotte/pytest-2/test_success_regrid_xy0/remap-dir'
+ echo '    component(s): atmos_static_cmip'
/home/Ian.Laflotte/Working/postprocessing/app/regrid-xy/bin/regrid-xy: line 25: gridSpec: unbound variable
[FAIL] regrid-xy # return-code=1
```
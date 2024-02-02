**ABOUT**

This app remaps from a spherical grid or (scalar or vector) data onto any grid (spherical or tripolar) using conservative scheme.  Alternative schemes can be added if needed.


**APP ASSUMPTIONS**

The program expects to read data from a netcdf file, which specifies the input file name. The suffix '.nc' can be omitted.
 The suffix 'tile#' should not present for multiple-tile files.
The number of files must be 1 for scalar regridding and can be 1 or 2 for vector regridding. File path should not be includes.

The input_mosaic specifies the input mosaic information. This file contains list of tile files which specify the grid information for each tile.

The output_mosaic file specifies the output mosaic information.
This file contains list of tile files which specify the grid information for each tile.
If output_mosaic is not specified, nlon and nlat must be specified.

A remap_file  specifies the file name that saves remapping information.
If remap_file is specified and the file does not exist remapping information will be calculated ans stored in remap_file.
If remap_file is specified and the file exists, remapping information will be read from remap_file.

**ROSE CONFIGURATION**

Rose Regrid configuration will execute defined commands or behaviours.
-The user will update the variables accordingly

[atmos] first command of regrid to run
sources=aerosol_hourly_cmip aerosol_month_cmip atmos_co2_month atmos_diurnal atmos_diurnal_cmip atmos_global_cmip atmos_hourly atmos_level_cmip atmos_month atmos_month_aer atmos_month_cmip atmos_static_cmip atmos_tracer
inputGrid=cubedsphere
inputRealm=atmos
outputGridLon=288
outputGridLat=180
gridSpec=/archive/../../, which is  a given location for the grid specification dataset

[land] second command of regrid to run
sources=fire_month land_dust land_month land_month_cmip land_month_inst land_static land_static_cmip land_static_sg lumip_Lmon_crp lumip_Lmon_psl lumip_Lmon_pst lumip_Lyr lumip_Lyr_crp lumip_Lyr_psl lumip_Lyr_pst river_daily river_month river_month_inst river_static river_static_cmip
inputGrid=cubedsphere
inputRealm=land
outputGridLon=288
outputGridLat=180
gridSpec= archive/../../, which is  a given location for the grid specification dataset

Then execute:
rose app-run





#!/bin/csh -f
#------------------------------------
#PBS -N tk_atmos_av_mon
#PBS -l size=1
#PBS -l walltime=04:00:00
#PBS -r y
#PBS -j oe
#PBS -o
#PBS -q batch
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# Script: tk_atmos_av_mon.csh
# Author: Tom Knutson
# Source data: pp/atmos/av/monthly_Xyr
# Output: Creates figures in $out_dir/atmos_${yr1}_${yr2}/Knutson.oht
#
# Sample frepp usage (http://www.gfdl.noaa.gov/fms/fre/#analysis):
# <component type="atmos">
#    <timeAverage ... >
#       <analysis script="script_name [options]"/>
#    </timeAverage>
# </component>

# variables set by frepp
 set in_data_dir
 set in_data_file
 set descriptor
 set out_dir
 set yr1 
 set yr2 
 set fremodule

# make sure valid platform and required modules are loaded
if (`gfdl_platform` == "hpcs-csc") then
   source $MODULESHOME/init/csh
   module purge
   module use -a /home/fms/local/modulefiles
   module load $fremodule
   module load ferret
   module load git
else
   echo "ERROR: invalid platform"
   exit 1
endif

# check again?
if (! $?FRE_ANALYSIS_GIT_URL) then
   echo "ERROR: environment variable FRE_ANALYSIS_GIT_URL not set."
   exit 1
endif

# clone the source code from the repository

set GIT_REPOSITORY = $FRE_ANALYSIS_GIT_URL/bw
set FRE_CODE_TAG = master
set PACKAGE_NAME = tk_atmos_monthly_av
set FRE_CODE_BASE = $TMPDIR/fre-analysis

if (! -e $FRE_CODE_BASE/$PACKAGE_NAME) then
   if (! -e $FRE_CODE_BASE) mkdir $FRE_CODE_BASE
   cd $FRE_CODE_BASE
   git clone -b $FRE_CODE_TAG --recursive $GIT_REPOSITORY/$PACKAGE_NAME.git
endif

##################
# run the script
##################

set options = "-i $in_data_dir -d $descriptor -y $yr1,$yr2 -o $out_dir"

$FRE_CODE_BASE/$PACKAGE_NAME/tk_atmos_clim_driver.csh $options $in_data_file


#!/bin/csh -f
#------------------------------------
#PBS -N bw_atmos_regress
#PBS -l size=1
#PBS -l walltime=04:00:00
#PBS -r y
#PBS -j oe
#PBS -o
#PBS -q batch
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# Script: bw_atmos_regress.csh
# Author: Bruce Wyman
# Source data: pp/atmos/ts/monthly/Xyr
# Output: Creates figures in $out_dir/atmos_${yr1}_${yr2}
#
# Sample frepp usage (http://www.gfdl.noaa.gov/fms/fre/#analysis):
# <component type="atmos">
#    <timeSeries ... >
#       <analysis script="script_name [options]"/>
#    </timeSeries>
# </component>

# variables set by frepp
 set in_data_dir
 set out_dir
 set descriptor
 set yr1
 set yr2
 set databegyr
 set dataendyr
 set datachunk
 set fremodule

# make sure valid platform and required modules are loaded
if (`gfdl_platform` == "hpcs-csc") then
   source $MODULESHOME/init/csh
   module purge
   module use -a /home/fms/local/modulefiles
   module load $fremodule
   module load ncl/6.6.2
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

# clone the source code from the repository if it does not exist

set GIT_REPOSITORY = $FRE_ANALYSIS_GIT_URL/bw
set FRE_CODE_TAG = master
set PACKAGE_NAME = bw_atmos_regress
set FRE_CODE_BASE = $TMPDIR/fre-analysis

if (! -e $FRE_CODE_BASE/$PACKAGE_NAME) then
   if (! -e $FRE_CODE_BASE) mkdir $FRE_CODE_BASE
   cd $FRE_CODE_BASE
   git clone -b $FRE_CODE_TAG --recursive $GIT_REPOSITORY/$PACKAGE_NAME.git
endif

##################
# run the script
##################

set runscript = $FRE_CODE_BASE/bw_atmos_regress/regression.pl
set options = "-i $in_data_dir -d $descriptor -o $out_dir -y $yr1,$yr2 -c $databegyr,$dataendyr,$datachunk"

# lat-lon projection
$runscript $options -v psl,tas,uas,pr -s merra,ecmwf,gpcp

# polar stereographic (NH & SH)
$runscript $options -v h500 -s merra,ecmwf -P


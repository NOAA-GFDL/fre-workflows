#!/bin/csh -f
#------------------------------------
#PBS -N bw_atmos_monthly_timeseries
#PBS -l size=1
#PBS -l walltime=12:00:00
#PBS -r y
#PBS -j oe
#PBS -o
#PBS -q batch
#----------------------------------
# Script: bw_atmos_monthly_timeseries.csh
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
 set staticfile
 set fremodule

# make sure valid platform and required modules are loaded
if (`gfdl_platform` == "hpcs-csc") then
   source $MODULESHOME/init/csh
   module purge
   module use -a /home/fms/local/modulefiles
   module load $fremodule
   module load ncl/6.6.2
   module load intel_compilers/2021.3.0
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
set PACKAGE_NAME = bw_atmos_monthly_ts
set FRE_CODE_BASE = $TMPDIR/fre-analysis

if (! -e $FRE_CODE_BASE/$PACKAGE_NAME) then
   if (! -e $FRE_CODE_BASE) mkdir $FRE_CODE_BASE
   cd $FRE_CODE_BASE
   git clone -b $FRE_CODE_TAG --recursive $GIT_REPOSITORY/$PACKAGE_NAME.git
endif

##################
# run the script
##################

set options = "-i $in_data_dir -d $descriptor -o $out_dir -y $yr1,$yr2 -c $databegyr,$dataendyr,$datachunk --statsfile"
set datasets = merra,ecmwf   # ncep,ncep2,ecmwf,merra (or all)

#####################################
# pressure-latitude zonal mean plots
#####################################

# linear pressure axis
 $FRE_CODE_BASE/$PACKAGE_NAME/zonalmean.pl $options -t mean -v all -s $datasets

# log pressure axis (ucomp & temp) - also std deviation
 $FRE_CODE_BASE/$PACKAGE_NAME/zonalmean.pl $options -L -t mean,stdev -v ucomp,temp -s $datasets

##########################
# pressure level plots
##########################

# lat-lon projection
$FRE_CODE_BASE/$PACKAGE_NAME/preslevel.pl $options -t mean -v ucomp,vcomp,temp,omega,sphum,rh -s $datasets

# polar stereographic (NH & SH)
$FRE_CODE_BASE/$PACKAGE_NAME/preslevel.pl $options -P -t mean -v hght,slp -s $datasets



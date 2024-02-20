#!/bin/csh -f
#------------------------------------
#PBS -N atmos_eddies
#PBS -l size=1
#PBS -l walltime=12:00:00
#PBS -r y
#PBS -j oe
#PBS -o
#PBS -q batch
#------------------------------------
# Source data: pp/atmos_cimp/ts/daily/XXyr

# variables set by frepp
 set in_data_dir
 set descriptor
 set out_dir
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
if (! $?FRE_ANALYSIS_HOME) then
   echo "ERROR: environment variable FRE_ANALYSIS_HOME not set."
   exit 1
endif

# clone the source code from the repository if it does not exist

set GIT_REPOSITORY = $FRE_ANALYSIS_GIT_URL/bw
set FRE_CODE_TAG = testing_20171201
set PACKAGE_NAME = bw_atmos_eddies
set FRE_CODE_BASE = $TMPDIR/fre-analysis

if (! -e $FRE_CODE_BASE/$PACKAGE_NAME) then
   if (! -e $FRE_CODE_BASE) mkdir $FRE_CODE_BASE
   cd $FRE_CODE_BASE
   git clone -b $FRE_CODE_TAG --recursive $GIT_REPOSITORY/$PACKAGE_NAME.git
endif

##################
# run the script
##################

set options = "-i $in_data_dir -d $descriptor -o $out_dir -y $yr1,$yr2 -c $databegyr,$dataendyr,$datachunk -s $staticfile"
set filter = 2   # 0 = no filter, 1 = filtered, 2 = both

# available plots
#   variables: u, v, w, t, z, q
#   levels: 1000, 850, 700, 500, 250, 100, 50, 10

set plots = "uu10,tt10,uu250,vv250,tt250,vt250,uv250,ww500,wt500,zz500,vv850,uv850,tt850,vt850,vq850"

$FRE_CODE_BASE/$PACKAGE_NAME/run_eddies.pl $options -f $filter -p $plots -D merra


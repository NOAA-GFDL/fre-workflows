#!/bin/sh
#generate_test_data.bash
#makes the test files for the rename-split-to-pp tests
set -x

# #timeseries case (need all 6 tiles)
# #also uncomment line 42
# indir=/work/cew/scratch/
# infiles=00010101.atmos_daily.*.nc
# history_source="atmos_daily"
# ncks_outdir=/work/cew/scratch/atmos_subset/raw/
# 
# split_nc_outdir=/work/cew/scratch/atmos_subset/split-netcdf/
# split_nc_vars=("pr" "ps" "pv350K" "temp")
# split_nc_filter=/work/cew/scratch/atmos_subset/split-netcdf-filter/
# rename_outdir=/work/cew/scratch/atmos_subset/atmos-ts
# rename_regrid_outdir=/work/cew/scratch/atmos_subset/atmos-ts-regrid/regrid/
#/home/Carolyn.Whitlock/Code/fre-workflows/app/rename-split-to-pp/tests/test-data/input/atmos-ts

#static case (only one tile)
#also uncomment line 44
indir=/work/cew/scratch/
infiles=00010101.ocean_static.nc
history_source="ocean_static"
ncks_outdir=/work/cew/scratch/ocean_subset/raw/

split_nc_outdir=/work/cew/scratch/ocean_subset/split-netcdf/
split_nc_vars=("Coriolis" "hfgeou" "wet" "wet_u" "wet_v")
split_nc_filter=/work/cew/scratch/ocean_subset/split-netcdf-filter/

rename_indir=/home/Carolyn.Whitlock/Code/fre-workflows/app/rename-split-to-pp/tests/test-data/input/ocean-static
rename_outdir=/work/cew/scratch/ocean_subset/ocean-static
#rename_regrid_outdir=/work/cew/scratch/ocean_subset/ocean-static-regrid/regrid/
rename_test_outdir=/home/Carolyn.Whitlock/Code/fre-workflows/app/rename-split-to-pp/tests/test-data/ocean-static

test_dir=/home/Carolyn.Whitlock/Code/fre-workflows/app/rename-split-to-pp/tests/test-data
test_indir=$test_dir/input/
test_orig_outdir=$test_dir/orig-output/

#Cut down to a 14x9x6-month grid
ncks_infiles=$(ls $indir/$infiles)
for ncksi in ${ncks_infiles[@]}; do
  echo $ncksi
  ncks_outfile=$(basename $ncksi)
  #timeseries slice
  #ncks -d grid_xt,0,14 -d grid_yt,0,9 -d time,0,181 $ncksi -O $ncks_outdir/$ncks_outfile
  ##static slice (ocean coords can't be over antarctica)
  ncks -d xh,532,546 -d yh,526,535 -d xq,532,546 -d yq,526,535 $ncksi -O $ncks_outdir/$ncks_outfile
  #the ocean static files also need a bounds dim + time bounds
  #ncap2 -s 'defdim("bnds",2); time_bnds=make_bounds(time,$bnds,"time_bnds");' $ncks_outdir/$ncks_outfile -O $ncks_outdir/$ncks_outfile
  #for the record: I tried to edit the bounds down to an appropriate dim by editing them from 0,0 to 0,1 . time value is 0 btw
done

#call split-netcdf on the output directory; save a couple of the files for later
fre pp split-netcdf-wrapper -i $ncks_outdir -o $split_nc_outdir -s $history_source --split-all-vars
for var in ${split_nc_vars[@]}; do 
  cp $split_nc_outdir/*.${var}.nc $split_nc_filter
  nc_filename=$(ls $split_nc_outdir/*.${var}.nc)
  nc_basename=$(basename $nc_filename)
  cdl_filename=$(echo $nc_basename | sed -e s:.nc:.cdl:g)
  ncdump $split_nc_outdir/*.${var}.nc > $rename_indir/$cdl_filename
done

#call rename-split-to-pp on the split-netcdf output; dump all files to cdl
python /home/cew/Code/fre-workflows/app/rename-split-to-pp/bin/rename_split_to_pp_wrapper.py $split_nc_filter $rename_outdir $history_source do_regrid=FALSE
for f in $(find $rename_outdir | grep ".nc"); do
  #$f has the directory structure of the output; remove $rename_output to get what the tool wrote
  nc_basename = $(echo $f | sed -e s:$rename_outdir::g)
  cdl_filename=$(echo $nc_basename | sed -e s:.nc:.cdl:g)
  ncdump $f > $rename_outdir/$cdl_filename
done

#finally, copy cdl files + directory structure to final resting location.
#test-data has a dir structure that looks like this for a given $example:
#
# input/ - where the input files for the test are located
#   $example/
#     input.nc (built from cdl files)
#   $example-regrid/
#     regrid/ - symlinked to input/example/ to avoid duplicating the regrid file structure
# output/ - where the tests write the output files
# orig-output/
#   $example/
#     $example-frequency/
#       $example-duration/
#         output.nc (built from cdl files)
#   $example-regrid/
#     regrid/ - symlinked to orig-output/example/ to avoid duplicating the regrid file structure

cdl_input=$(find $rename_indir | grep ".cdl")
for f in $cdl_input; do
  #replace source dir with dest dir
  dest=$(echo $f | sed -e s:$rename_indir:$test_indir:g)
  dest_dir=$(dirname $dest)
  mkdir -p $dest_dir
  cp $f $dest_dir
done

mkdir -p $test_indir/${history_source}-regrid/regrid/
ln -s $test_indir/$history_source $test_indir/${history_source}-regrid/regrid/

cdl_output=$(find $rename_outdir | grep ".cdl")
for f in $cdl_output; do
  #replace source dir with dest dir
  dest=$(echo $f | sed -e s:$rename_outdir:$test_outdir:g)
  dest_dir=$(dirname $dest)
  mkdir -p $dest_dir
  cp $f $dest_dir
done

mkdir -p $test_outdir/${history_source}-regrid/regrid/
ln -s $test_outdir/$history_source $test_outdir/${history_source}-regrid/regrid/



exit 0



#select a few files from split-netcdf-wrapper to go to tests/test-data/atmos-ts
#focus on weird edge cases (small vars, large vars), common use cases (3-d vars)

#run that directory through rename-split-to-pp - which currently takes a godawful melange of environment vars

#rename-split-to-pp-wrapper inputDir outputDir history_source do_regrid=FALSE
#dump the contents of your output directory to cdl; delete netcdf files


#and dump your input files to cdl; delete netcdf files




#Ocean files need a slightly different set of coords so as not to select Antarctica
infile=/home/cew/Code/cmip7-sprint/testfiles/input/00010101.ocean_static.nc
outfile=/home/cew/Code/cmip7-sprint/testfiles/00010101.ocean_static.nc
ncks -d xh,532,546 -d yh,526,535 -d xq,532,546 -d yq,526,535 $infile -O $outfile

#cdl file for regression test output
ncdump $outfile > /home/cew/Code/cmip7-sprint/testfiles/00010101.ocean_static.cdl

split_nc_outdir=/home/cew/Code/cmip7-sprint/testfiles/ocean_static/

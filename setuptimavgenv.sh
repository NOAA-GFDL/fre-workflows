#!/bin/sh -e -x

# this script is to setup the generate-time-average python module within fre_python_tools
# it might change a bunch since we're about to overhaul the app/submodule structure
# it is not intended to be part of the final dev product of this branch, it is a development "bootstrap"
# use at own risk if you're not Ian L.
# usage: source setuptimavgenv.sh from pp.am5/ directory

CURRENT=$PWD
BASENAME=$(basename $CURRENT)
if [[ $BASENAME != "pp.am5" ]] ;
then
	echo "PROBLEM!!!"
	return
fi

# get the fre-python-tools
cd $PWD/app
git clone -b gen.time.avgs git@github.com:NOAA-GFDL/fre-python-tools.git fre-python-tools
cd fre-python-tools/

# cleanup stuff i don't need for now. 
rm ./*
rm -rf ./tests/

# grab the app i need- my gen.time.avgs, and put it where i can likely use the structure
# of other apps as a guiding principle
mv ./fre_python_tools/generate_time_averages ./..
cd ..
rm -rf ./fre-python-tools/

# b.c. -e -x directives near shebang, if this part doesn't work, i'll get a complaint
# good.
pwd
ls generate_time_averages/
echo "generate_time_averages/ is ready to go!"

cd ..
return

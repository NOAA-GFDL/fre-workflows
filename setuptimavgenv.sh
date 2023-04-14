#!/bin/sh -e

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
	echo "source me from the cloned git repo's base directory."
	return
fi

# get the fre-python-tools
cd $PWD/app/generate-time-averages
git clone -b gen.time.avgs git@github.com:NOAA-GFDL/fre-python-tools.git fre-python-tools
mv ./fre-python-tools/fre_python_tools/generate_time_averages/ .

# cleanup stuff i don't need for now. 
rm -rf ./fre-python-tools/
rm -rf ./generate_time_averages/testfiles/

# b.c. -e -x directives near shebang, if this part doesn't work, i'll get a complaint
pwd
if ls generate_time_averages/; then
	echo "generate_time_averages/ is ready to go!"
else
	echo "something wrong! generate_time_averages dir not found."
fi

cd $CURRENT
return

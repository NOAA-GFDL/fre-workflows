#!/bin/sh -e -x

# to clean up messes i make via setuptimavgenv.sh
# usage: source cleanuptimavgenv.sh from pp.am5/

CURRENT=$PWD
BASENAME=$(basename $CURRENT)
if [[ $BASENAME != "pp.am5" ]] ;
then
	echo "PROBLEM!!!"
	return
fi

if [[ -d $PWD/app/fre-python-tools ]] ;
then
	echo "cleaning up $PWD/app/fre-python-tools"
	rm -rf $PWD/app/fre-python-tools
fi

if [[ -d $PWD/app/generate_time_averages ]] ;
then
	echo "cleaning up $PWD/app/generate_time_averages"
	rm -r $PWD/app/generate_time_averages
fi

echo "done cleaning up."
return

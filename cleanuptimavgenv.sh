#!/bin/sh -e -x

# to clean up messes i make via setuptimavgenv.sh
# usage: source cleanuptimavgenv.sh from pp.am5/

CURRENT=$PWD
BASENAME=$(basename $CURRENT)
if [[ $BASENAME != "pp.am5" ]] ;
then
	echo "PROBLEM!!!"
	echo "source me from the cloned git repo's base directory."
	return
fi

TARG=$PWD/app/generate-time-averages/fre-python-tools
if [[ -d $TARG ]] ;
then
	echo "cleaning up $TARG"
	rm -rf $TARG
fi

TARG=$PWD/app/generate-time-averages/generate_time_averages
if [[ -d $TARG ]] ;
then
	echo "cleaning up $TARG"
	rm -rf $TARG
fi

echo "done cleaning up."
return

#!/bin/bash
set -eou pipefail


#echo "------------------------------"
if mv DNE_file DNE2_file; then
	 # This line should not fire because the file does not exist
	 # the TAGS approach is prob. touching the exit status. BAD.
	#return $?
	#return 1
	exit 1
else
	#return $?
	#return 0
	exit 0
fi
#echo "------------------------------"

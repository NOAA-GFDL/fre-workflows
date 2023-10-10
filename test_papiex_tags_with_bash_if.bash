#!/bin/bash

set -euo pipefail
if [ ! -f some_file ] ; then touch some_file ; fi 
if [ -f yet_another_file ] ; then rm -f yet_another_file ; fi
if [ -f some_other_file ] ; then rm -f some_other_file ; fi

#canonical case in cylc, guarding against a non-zero exit status.
# mv here stands in for some kind of command where a non-zero 
# exit status doesn't necessarily insinuate failure


# this should succeed, we've created some_file
if mv some_file some_other_file; then
	echo "i succeed! yay!"
else
	echo "i failed and i should not have because i am the base-case! BOO! whats wrong?!?!"
fi

# this seems to succeed and not fail unexpectedly. great!
if export SOME_DUMMY_VAR=foo && mv some_other_file yet_another_file; then
	echo "i succeed! yay! test a few more variations Ian."
	echo "the value of SOME_DUMMY_VAR=${SOME_DUMMY_VAR}"
else
	echo "i failed and this disappoints me quite a bit. boo."
fi
unset SOME_DUMMY_VAR


# this seems to succeed and not fail unexpectedly. great!
if export SOME_DUMMY_VAR=foo && mv yet_another_file yet_another_another_file && unset SOME_DUMMY_VAR; then
	echo "i succeed! yay! test a few more variations Ian."
	echo "the value of SOME_DUMMY_VAR=${SOME_DUMMY_VAR}"
else
	echo "i failed and this disappoints me quite a bit. boo."
fi
unset SOME_DUMMY_VAR














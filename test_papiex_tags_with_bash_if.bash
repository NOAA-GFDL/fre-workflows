#!/bin/bash

set -euo pipefail
if [ ! -f some_file ] ; then touch some_file ; fi
if [ -f another_file ] ; then rm -f another_file ; fi
if [ -f yet_another_file ] ; then rm -f yet_another_file ; fi
if [ -f some_other_file ] ; then rm -f some_other_file ; fi

#canonical case in cylc, guarding against a non-zero exit status.
# mv here stands in for some kind of command where a non-zero 
# exit status doesn't necessarily insinuate failure


# here, SOME_DUMMY_VAR steps in for PAPIEX_TAGS, which when set, signals what op+related stuff
# to search for in the process streams. so these tests are about making sure that we can do
# this around a command sensibly and the bash syntax permits it. this is important, because
# if the env var isnt set or unset, we may not scrape the data we want, or too much, or none
# at all.

### this should succeed, we've created some_file
##------------------------------------------------
#if mv some_file some_other_file; then
#	echo "i succeed! yay!"
#else
#	echo "i failed and i should not have because i am the base-case! BOO! whats wrong?!?!"
#fi

## this seems to succeed and not fail unexpectedly. great!
##------------------------------------------------
#if export SOME_DUMMY_VAR=foo && mv some_other_file yet_another_file; then
#	echo "i succeed! yay! test a few more variations Ian."
#else
#	echo "i failed and this disappoints me quite a bit. boo."
#fi
#echo "the value of SOME_DUMMY_VAR=${SOME_DUMMY_VAR}"
#unset SOME_DUMMY_VAR

## this seems to succeed and not fail unexpectedly. great!
##------------------------------------------------
#if export SOME_DUMMY_VAR=foo && mv some_other_file yet_another_file; then
#	echo "i succeed! yay! test a few more variations Ian."
#else
#	echo "i failed and this disappoints me quite a bit. boo."
#fi
#echo "the value of SOME_DUMMY_VAR=${SOME_DUMMY_VAR}"
#unset SOME_DUMMY_VAR


## this seems to succeed and not fail unexpectedly. great!
##------------------------------------------------
#if export SOME_DUMMY_VAR=foo && mv yet_another_file yet_another_another_file && unset SOME_DUMMY_VAR; then
#	echo "i succeed! yay! test a few more variations Ian."
#else
#	echo "i failed and this disappoints me quite a bit. boo."
#fi
#echo "the value of SOME_DUMMY_VAR=${SOME_DUMMY_VAR}"
#unset SOME_DUMMY_VAR


### what if the file doesn't exist
## this seems to result in SOME_DUMMY_VAR keeping it's value - this could be problematic! FATAL FLAW IN && CHAINED COMMANDS
##------------------------------------------------
#if export SOME_DUMMY_VAR=foo && mv DOEXNT_EXISTyet_another_file yet_another_another_file && unset SOME_DUMMY_VAR; then
#	echo "i succeed! ... wait that should not be happening what's going on???"
#else
#	echo "i failed as expected. i'm worried SOME_DUMM_VAR still has a value of foo and what that means for tooling..."
#fi
#echo "the value of SOME_DUMMY_VAR=${SOME_DUMMY_VAR}"
#unset SOME_DUMMY_VAR



### what about a multi-line statement after the if?
# if the file exists this is fine.
##------------------------------------------------
#if export SOME_DUMMY_VAR=foo ; mv some_file another_file ; unset SOME_DUMMY_VAR; then
#	echo "i succeed! this is good"
#else
#	echo "i failed! this bad."
#fi
#echo "the value of SOME_DUMMY_VAR=${SOME_DUMMY_VAR}"
#unset SOME_DUMMY_VAR


### what about a multi-line statement after the if?
## if the file doesn't exist... no bueno, FATAL FLAW
##------------------------------------------------
#if export SOME_DUMMY_VAR=foo ; mv DOESNTEXISTsome_file another_file ; unset SOME_DUMMY_VAR; then
#	echo "i succeed! this is NOT good. the last unset SOME_DUMMY_VAR succeeds"
#	echo "... and so if mv fails, whatever assumes success after me will run"
#else
#	echo "i failed! this bad."
#fi
#echo "the value of SOME_DUMMY_VAR=${SOME_DUMMY_VAR}"
#unset SOME_DUMMY_VAR




## what about using logical OR statement for the "unset" step?
# if the file does exist...
echo ""
echo ""
cmd_return_code=0
if export SOME_DUMMY_VAR="value" && { mv some_file another_file; export success=$?; unset SOME_DUMMY_VAR; } && [ $success ] ; then
	echo "i succeeded, as i should!"
	set +u ;	echo "i hope SOME_DUMMY_VAR has no value!!! SOME_DUMMY_VAR=$SOME_DUMMY_VAR" ;	set -u
else
	echo "PROBLEMPROBLEMPROBLEMPROBLEMPROBLEMPROBLEMPROBLEMPROBLEM"
	echo "i failed AND I SHOULD NOT HAVE"
	echo "PROBLEMPROBLEMPROBLEMPROBLEMPROBLEMPROBLEMPROBLEMPROBLEM"
fi
set +u ; echo "the value of SOME_DUMMY_VAR=${SOME_DUMMY_VAR}"
unset SOME_DUMMY_VAR ; set -u



echo ""
echo ""
cmd_return_code=0
if export SOME_DUMMY_VAR="value" && { mv some_file another_file; export success=$?; unset SOME_DUMMY_VAR; } && [ $success ] ; then
	echo "PROBLEMPROBLEMPROBLEMPROBLEMPROBLEMPROBLEMPROBLEMPROBLEM"
	echo "i succeeded AND I SHOULD NOT HAVE"
	echo "PROBLEMPROBLEMPROBLEMPROBLEMPROBLEMPROBLEMPROBLEMPROBLEM"
else
	echo "i failed, as i should!"
	set +u ; echo "i hope SOME_DUMMY_VAR has no value!!! SOME_DUMMY_VAR=$SOME_DUMMY_VAR" ; set -u
fi
set +u; echo "the value of SOME_DUMMY_VAR=${SOME_DUMMY_VAR}"
unset SOME_DUMMY_VAR ; set -u

echo ""
echo ""


#
##structure: for some command in an if-block
#if some_command_success_or_error ; then
#	echo "positive result"
#else
#	echo "negative result"
#fi
#
#
#
##becfomes
#if export FAKE_PAPIEX_TAGS="FOO" && (some_command_success_or_error && unset FAKE_PAPIEX_TAGS) || unset FAKE_PAPIEX_TAGS; then
#	echo "positive result"
#else
#	echo "negative result"
#fi


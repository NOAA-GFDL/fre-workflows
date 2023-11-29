#!/bin/bash
set -eou pipefail


# as expected.
echo "------------------------------"
if mv DNE DNE2; then
	echo "EXP #1 : succeeded, why? BOO! VERY BAD"
else
	echo "EXP #1 : failed, yay! VERY GOOD"
fi
echo "------------------------------"


# works as expected upon failure, great!
echo "------------------------------"
if { export FAKE_PAPI_TAGS=FOO; mv DNE DNE2; export SUCCESS=$?; unset FAKE_PAPI_TAGS; } && [ $SUCCESS -eq 0 ]; then
	echo "EXP #2 : succeeded, why? BOO! VERY BAD"
else
	echo "EXP #2 : failed, yay! VERY GOOD"
	set +u; echo "EXP #2 : checking: FAKE_PAPI_TAGS=${FAKE_PAPI_TAGS} and SUCCESS=${SUCCESS}"; set -u;
fi
set +u; echo "EXP #2 : out of if/else block, checking: FAKE_PAPI_TAGS=${FAKE_PAPI_TAGS}"; set -u;
echo "------------------------------"


# not an env var test. works as expected upon failure, great!
echo "------------------------------"
if { export FAKE_PAPI_TAGS=FOO; mv DNE DNE2; SUCCESS=$?; unset FAKE_PAPI_TAGS; } && [ $SUCCESS -eq 0 ]; then
	echo "EXP #3 : succeeded, why? BOO! VERY BAD"
else
	echo "EXP #3 : failed, yay! VERY GOOD"
	set +u; echo "EXP #3 : checking: FAKE_PAPI_TAGS=${FAKE_PAPI_TAGS} and SUCCESS=${SUCCESS}"; set -u;
fi
set +u; echo "EXP #3 : out of if/else block, checking: FAKE_PAPI_TAGS=${FAKE_PAPI_TAGS}"; set -u;
echo "------------------------------"


#!/bin/bash

set -eou pipefail


if [ ! -f a_file ]; then touch a_file; fi

# as expected.
echo "------------------------------"
if mv a_file diff_file; then
	echo "EXP #1 : moved a_file to diff_file, yay! VERY GOOD"
else
	echo "EXP #1 : failed, why? BOO! VERY BAD"
fi
echo "------------------------------"


# works like above, great!
echo "------------------------------"
if { mv diff_file diff_file2; export SUCCESS=$?; } && [ $SUCCESS -eq 0 ]; then
	echo "EXP #2 : moved diff_file to diff_file2, yay! VERY GOOD"
else
	echo "EXP #2 : failed, why? BOO! VERY BAD"
fi
echo "------------------------------"




# works as expected upon success, great!
echo "------------------------------"
if { export FAKE_PAPI_TAGS=FOO; mv diff_file2 final_file; export SUCCESS=$?; unset FAKE_PAPI_TAGS; } && [ $SUCCESS -eq 0 ]; then
	echo "EXP #3 : i succeeded! that's a good thing! I should succeed! VERY GOOD"
	set +u; echo "EXP # : checking: FAKE_PAPI_TAGS=${FAKE_PAPI_TAGS}"; set -u;
else
	echo "EXP #3 : i SHOULD NOT FAIL. WHY DO I FAIL? VERY BAD"
fi
set +u; echo "EXP #3 : out of if/else block, checking: FAKE_PAPI_TAGS=${FAKE_PAPI_TAGS}"; set -u;
echo "------------------------------"

# works as expected upon failure, great!
echo "------------------------------"
if { export FAKE_PAPI_TAGS=FOO; mv diff_file666 diff_file777; export SUCCESS=$?; unset FAKE_PAPI_TAGS; } && [ $SUCCESS -eq 0 ]; then
	echo "EXP #4 : i SHOULD NOT SUCCEED. WHY DO I SUCCEED? VERY BAD"
else
	echo "EXP #4 : i failed! that's a good thing! I should fail! VERY GOOD"
	set +u; echo "EXP # : checking: FAKE_PAPI_TAGS=${FAKE_PAPI_TAGS}"; set -u;
fi
set +u; echo "EXP #4 : out of if/else block, checking: FAKE_PAPI_TAGS=${FAKE_PAPI_TAGS}"; set -u;
echo "------------------------------"



echo $SUCCESS && unset SUCESS
mv final_file diff_file2


# not using an env var test. works as expected upon failure, great!
echo "------------------------------"
if { export FAKE_PAPI_TAGS=FOO; mv diff_file2 final_file; SUCCESS=$?; unset FAKE_PAPI_TAGS; } && [ $SUCCESS -eq 0 ]; then
	echo "EXP #5 : i succeeded! that's a good thing! I should succeed! VERY GOOD"
	set +u; echo "EXP # : checking: FAKE_PAPI_TAGS=${FAKE_PAPI_TAGS}"; set -u;
else
	echo "EXP #5 : i SHOULD NOT FAIL. WHY DO I FAIL? VERY BAD"
fi
set +u; echo "EXP #5 : out of if/else block, checking: FAKE_PAPI_TAGS=${FAKE_PAPI_TAGS}"; set -u;
echo "------------------------------"


# not an env var test. works as expected upon failure, great!
echo "------------------------------"
if { export FAKE_PAPI_TAGS=FOO; mv diff_file666 diff_file777; SUCCESS=$?; unset FAKE_PAPI_TAGS; } && [ $SUCCESS -eq 0 ]; then
	echo "EXP #6 : i SHOULD NOT SUCCEED. WHY DO I SUCCEED? VERY BAD"
else
	echo "EXP #6 : i failed! that's a good thing! I should fail! VERY GOOD"
	set +u; echo "EXP # : checking: FAKE_PAPI_TAGS=${FAKE_PAPI_TAGS}"; set -u;
fi
set +u; echo "EXP #6 : out of if/else block, checking: FAKE_PAPI_TAGS=${FAKE_PAPI_TAGS}"; set -u;
echo "------------------------------"


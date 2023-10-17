#!/bin/bash

set -eou pipefail


if [ ! -f a_file ]; then touch a_file; fi

# as expected.
if mv a_file diff_file; then
	echo "moved a_file to diff_file, yay! VERY GOOD"
else
	echo "failed, why? BOO! VERY BAD"
fi


# works like above, great!
if { mv diff_file diff_file2; export SUCCESS=$?; } && [ $SUCCESS -eq 0 ]; then
	echo "moved diff_file to diff_file2, yay! VERY GOOD"
else
	echo "failed, why? BOO! VERY BAD"
fi

## works as expected upon failure, great!
#if { mv diff_file666 diff_file777; export SUCCESS=$?; } && [ $SUCCESS -eq 0 ]; then
#	echo "i SHOULD NOT SUCCEED. WHY DO I SUCCEED? VERY BAD"
#else
#	echo "i failed! that's a good thing! I should fail! VERY GOOD"
#fi


# works as expected upon success, great!
if { export FAKE_PAPI_TAGS=FOO; mv diff_file2 final_file; export SUCCESS=$?; unset FAKE_PAPI_TAGS; } && [ $SUCCESS -eq 0 ]; then
	echo "i succeeded! that's a good thing! I should succeed! VERY GOOD"
	set +u; echo "checking: FAKE_PAPI_TAGS=${FAKE_PAPI_TAGS}"; set -u;
else
	echo "i SHOULD NOT FAIL. WHY DO I FAIL? VERY BAD"
fi
set +u; echo "out of if/else block, checking: FAKE_PAPI_TAGS=${FAKE_PAPI_TAGS}"; set -u;


# works as expected upon failure, great!
if { export FAKE_PAPI_TAGS=FOO; mv diff_file666 diff_file777; export SUCCESS=$?; unset FAKE_PAPI_TAGS; } && [ $SUCCESS -eq 0 ]; then
	echo "i SHOULD NOT SUCCEED. WHY DO I SUCCEED? VERY BAD"
else
	echo "i failed! that's a good thing! I should fail! VERY GOOD"
	set +u; echo "checking: FAKE_PAPI_TAGS=${FAKE_PAPI_TAGS}"; set -u;
fi
set +u; echo "out of if/else block, checking: FAKE_PAPI_TAGS=${FAKE_PAPI_TAGS}"; set -u;


#echo $SUCCESS

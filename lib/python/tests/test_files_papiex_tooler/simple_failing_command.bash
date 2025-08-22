#!/bin/bash
set -eou pipefail

if mv DNE_file DNE2_file; then
	 # This line should not fire because the file does not exist
	exit 1
else
	 # This line should fire as expected, before and after tags
	exit 0
fi

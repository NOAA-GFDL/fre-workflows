#!/bin/csh

## RefineDiag scripts reads raw history files and generates new, refined history files
# Script copies test history file to another history file
set input_dir = `pwd`

if ( $?refineDiagDir ) then
    set output_dir = $refineDiagDir
else
    echo "ERROR: refineDiagDir environment variable is not set."
    exit 1
endif

if ( -d "$input_dir" ) then
    #ls -aF
    echo "Input directory found: $input_dir"
    echo "good to go"
    foreach INFILE (*atmos_month*.nc)
        set OUTFILE = ${INFILE:r}_refined.${INFILE:e}
        echo "OUTFILE $OUTFILE"
        cp "$INFILE" "$output_dir/$OUTFILE"
    end
else
    echo "Error: Input directory $input_dir does not exist."
    exit 1
endif

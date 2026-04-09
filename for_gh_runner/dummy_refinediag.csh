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
    ls -aF
    echo "Input directory found: $input_dir"
    echo "good to gio"
    for each INFILE (`\bin\ls *atmos_daily*cmip*.nc`)
        set OUTFILE = `echo $INFILE | sed -e 's/_cmip/_refined/'`
        cp $INFILE $refineDiagDir/$OUTFILE
    end
else
    echo "Error: Input directory $input_dir does not exist."
    exit 1
endif

#cd $input_dir
#if ($?refineDiagDir) then  #(and input_dir exists and is non-empty)
#    #copy nc file to another file
#    for f in ls $input_dir do
#        cp $f 
#    endfor 
#else
#    echo "Error"
#    exit 1
#endif

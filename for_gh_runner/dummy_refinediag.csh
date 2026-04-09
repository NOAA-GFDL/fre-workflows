#!/bin/csh

## RefineDiag scripts reads raw history files and generates new, refined history files
# Script copies test history file to another history file
 
# what's in here
ls 

# define outfile
input_dir=$pwd
output_dir= $refineDiagDir

if ls $input_dir then
    echo "good to go"
else
    echo "Nothing in here"
    exit 1

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

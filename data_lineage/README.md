To create a DAG, modify the routines in `/app` to export the i/o files and their hashes with an epmt annotation.

The general skeleton for this is below, the same must be done for output, but with modified var names and file locations:

```shell
# Initialize the list
export input_file_list=
    
...

# Iterate through input files
for input_file in $(ls $inputDir); do
    # Determine hash for file, include absolute path so the hash maintains uniqueness
    hash_val=$(/home/Cole.Harvey/.conda/envs/bloom-filter-env/bin/python /home/Cole.Harvey/postprocessing/data_lineage/bloomfilter/HashGen.py $inputDir/$input_file)
    export input_file_list="${input_file_list}$input_file  $hash_val,"
    echo -e "\nadded $input_file to input list with hash_val: $hash_val"
done 
    
...

# At the end of the script, make the annotation to epmt
if [[ -n "$input_file_list" ]]; then
    echo -e "\n---input---"
    echo -e "DATA_LINEAGE_IN = \n${input_file_list%*,}"
    epmt annotate EPMT_DATA_LINEAGE_IN="${input_file_list%*,}"
fi
```

Once this has been finished for the apps you would like to track, run a workflow and take note of the run number. Then, use this command to grab the `$CYLC_WORKFLOW_UUID`
for the current workflow:

`cylc cat-log -f o am5_c96L33_amip/run<RUN_NUMBER>//19800101T0000Z/pp-starter | grep CYLC_WORKFLOW_UUID= | sed 's/CYLC_WORKFLOW_UUID=//'`

Don't forget to replace `<RUN_NUMBER>` in the command above with this workflow's run number.

Finally, replace the `fp` variable in `postprocessing/data_lineage/dag/test.py/main` with the `$CYLC_WORKFLOW_UUID`.

You can now run `test.py` using this interpreter: `/home/Cole.Harvey/.conda/envs/coles_py2/bin/python`

# Useful Links

[Summary](https://docs.google.com/document/d/1pB1VXthywjqaz-Kr4dmDMZzZbgrmDAyYeBlIw0VOD7U/edit?usp=sharing)

[Project Outline](https://docs.google.com/document/d/1DzLZVOazFiqG-vPx0pF9hKLh4jnHssCk-xOjEBjBED4/edit?usp=sharing)

[Step-By-Step Run Guide](https://docs.google.com/document/d/1MnFjArk466TciaZ6j8PNHyljHr3cWM_tkmlzWwxj9Bo/edit?usp=sharing)

# Usage Instructions

This tool is still in development. Follow the instructions below to use it effectively.

---

## 1. Creating a DAG
To create a DAG, modify the routines in `app/` to export the input/output
files and their hashes with an epmt annotation. Follow the general skeleton below:

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
    # Annotate the shared path between all input files to save annotation space
    epmt annotate EPMT_DATA_LINEAGE_IN_PATH="$inputDir/"
    echo -e  "\nannotated $inputDir/ to EPMT_DATA_LINEAGE_IN_PATH"

    echo -e "\n---input---\n"
    epmt annotate EPMT_DATA_LINEAGE_IN="${input_file_list%*,}"
    echo -e "annotated \n${input_file_list%*,} to EPMT_DATA_LINEAGE_IN"
fi
```
## 2. Adding the CYLC_WORKFLOW_UUID to epmt_tags
Add the `$CYLC_WORKFLOW_UUID` to the epmt_tags for each routine in `app/`. 
The epmt_tags are located in `site/ppan.cylc`, and the syntax is `EPMT_EXP_UUID:$CYLC_WORKFLOW_UUID`.


## 3. Run the workflow
Once this has been finished for the apps you would like to track, run a workflow and take note of the run number.


## 4. Obtain the CYLC_WORKFLOW_UUID
Use this command to grab the `$CYLC_WORKFLOW_UUID` for the current workflow:

```shell
cylc cat-log -f o am5_c96L33_amip/run<RUN_NUMBER>//19800101T0000Z/pp-starter | grep CYLC_WORKFLOW_UUID= | sed 's/CYLC_WORKFLOW_UUID=//'
```

**IMPORTANT:** Don't forget to replace `<RUN_NUMBER>` in the command above with this workflow's run number.

## 5. Calibrate test.py
Replace the `fp` variable in `postprocessing/data_lineage/dag/test.py/main` with the `$CYLC_WORKFLOW_UUID`.

## 6. Run test.py 
You can now run `test.py` using this interpreter: 
```shell
/home/Cole.Harvey/.conda/envs/coles_py2/bin/python SerialDag.py
```

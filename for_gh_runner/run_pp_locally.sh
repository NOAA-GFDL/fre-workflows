#!/bin/bash

### see markdown instructions on usage in for-developers.md

if [ $(basename $PWD) != 'fre-workflows' ]; then
    echo "ERROR: source me from a fre-workflows directory or i won't work"
    return 1
fi

# 0 to run the workflow. non-zero to do everything except run it, i.e. "dry-run".
dry_run=0
echo "dry_run=$dry_run"

# there shouldn't be a strong need to change any of this
yaml="for_gh_runner/yaml_workflow/model.yaml"
expt="test_pp_locally"
platform="ptest"
target="ttest"
workflow_dir_name="${expt}__${platform}__${target}"
echo "workflow_dir_name = $workflow_dir_name"

# if this doesn't exist, the mock check out won't work
if [ ! -d /home/$USER/cylc-src ]; then
    mkdir --parents /home/$USER/cylc-src
fi

cylc_src_dir_name=/home/$USER/cylc-src/$workflow_dir_name
echo "cylc_src_dir_name = $cylc_src_dir_name"

cylc_run_dir_name=/home/$USER/cylc-run/$workflow_dir_name
echo "cylc_run_dir_name = $cylc_run_dir_name"

ept_arg_string="-e $expt -p $platform -t $target"
echo "e/p/t arg string is $ept_arg_string"


echo ""
echo ""
echo "*****************"
echo "CLEANING UP PREV RUN DIR, IF FOUND"
if [ -d $cylc_run_dir_name ]; then
    echo "run dir found, cylc stop first, we may have recently ran a previous version"
    cylc stop --now --now ${workflow_dir_name}

    echo "cylc clean to remove the run directory products correctly. sleep for 10s after."
    cylc clean $workflow_dir_name
    sleep 10s
fi


echo ""
echo ""
echo "*****************"
echo "CLEANING UP PREV SRC DIR, IF FOUND"
if [ -d $cylc_src_dir_name ]; then
    echo "src dir found, REMOVING OLD cylc-src. sleep for 10s after."
    rm -rf $cylc_src_dir_name
    sleep 10s
fi

# if you want this, comment on https://github.com/NOAA-GFDL/fre-cli/issues/673
#echo ""
#echo ""
#echo "*****************"
#echo "CHECKING OUT LOCAL REPO COPY"
#fre -vv pp checkout $ept_arg_string --local .
#if [ $? -ne 0 ] ; then
#    echo "ERROR CHECKING OUT"
#fi


echo ""
echo ""
echo "*****************"
echo "MOCK CHECKING OUT"
mock_checkout_targ=$(pwd)
echo "cd .. && cp -rf $mock_checkout_targ $cylc_src_dir_name && cd -"
cd .. && cp -rf $mock_checkout_targ $cylc_src_dir_name && cd -
if [ $? -ne 0 ] ; then
    echo "ERROR MOCK CHECKING OUT"
    return 1
fi


echo ""
echo ""
echo "*****************"
echo "CONFIGURING YAML"
echo "fre -vv pp configure-yaml -y $yaml $ept_arg_string"
fre -vv pp configure-yaml -y $yaml $ept_arg_string
if [ $? -ne 0 ] ; then
    echo "*****************"
    echo "ERROR CONFIGURING YAML"
    return 1
fi


echo ""
echo ""
echo "*****************"
echo "VALIDATING"
echo "fre -vv pp validate $ept_arg_string"
fre -vv pp validate $ept_arg_string
if [ $? -ne 0 ] ; then
    echo "*****************"
    echo "ERROR VALIDATING"
    return 1
fi


echo ""
echo ""
echo "*****************"
echo "INSTALLING"
echo "fre -vv pp install $ept_arg_string"
fre -vv pp install $ept_arg_string
if [ $? -ne 0 ] ; then
    echo "*****************"
    echo "ERROR INSTALLING"
    return 1
fi


if [ ! $dry_run -eq 0 ] ; then
	echo ""
	echo ""
	echo "*****************"
	echo "DRY-RUNNING"
    echo "dry_run, no cylc play!"
    echo "would have run: cylc play --no-detach --debug -s 'STALL_TIMEOUT=\"PT0S\"' $workflow_dir_name"
    return 0
fi


echo ""
echo ""
echo "*****************"
echo "RUNNING"
echo "cylc play --no-detach --debug -s 'STALL_TIMEOUT=\"PT0S\"' $workflow_dir_name"
cylc play --no-detach --debug -s 'STALL_TIMEOUT="PT10S"' $workflow_dir_name
#echo "fre -vv pp run $ept_arg_string"
#fre -vv pp run $ept_arg_string
if [ $? -ne 0 ] ; then
    echo "*****************"
    echo "ERROR RUNNING"
    return 1
fi

#echo ""
#echo ""
#echo "*****************"
#echo "WORKFLOW-STATE"
#echo "watch -n 5 'cylc workflow-state -v $workflow_dir_name'"
#watch -n 5 'cylc workflow-state -v test_pp_locally__ptest__ttest'


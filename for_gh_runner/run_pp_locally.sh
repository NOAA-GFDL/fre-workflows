#!/bin/bash

if [ $(basename $PWD) != 'fre-workflows' ]; then
    echo "ERROR: source me from a fre-workflows directory or i won't work"
    return 1
fi

## preamble, i needed to make sure my global.cylc was more in-line with the cylc in /usr/local/bin
## i did that be doing the following:
# cylc config -d > /home/$USER/.cylc/flow/global.cylc

## then, within that global.cylc i had to change the ssh command field from gsissh to ssh
## for the future, we should use 'cylc path', but it doesn't do anything if use login shell = True

## i needed the following in my ~/.bash_profile
#echo "(~/.bash_profile) export LANG=C.UTF-8"
#export LANG=C.UTF-8
#echo "(~/.bash_profile) PATH was: $PATH"
#export PATH=$(echo "$PATH" | awk -v RS=: -v ORS=: '$0 != "/usr/local/bin"' | sed 's/:$//')
#export PATH=/home/inl/conda/envs/fre-cli/bin:$PATH
#echo "(~/.bash_profile) PATH now: $PATH"

# 0 to run the workflow. 1 to do everything except run it.
dry_run=0
echo "dry_run=$dry_run"

expt="test_pp_locally"
platform="ptest"
target="ttest"
yaml="for_gh_runner/yaml_workflow/model.yaml"

workflow_dir_name="${expt}__${platform}__${target}"
echo "workflow_dir_name = $workflow_dir_name"

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

#echo ""
#echo ""
#echo "*****************"
#echo "CHECKING OUT"
#fre -vv pp checkout $ept_arg_string
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

if [ $dry_run -eq 1 ] ; then
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


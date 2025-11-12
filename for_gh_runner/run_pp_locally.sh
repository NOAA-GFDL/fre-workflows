#!/bin/bash

if [ $(basename $PWD) != 'fre-workflows' ]; then
	echo "ERROR: source me from a fre-workflows directory or i won't work"
	return 1
fi

## preammble, i needed to make sure my global.cylc was more in-line with the cylc in /usr/local/bin
## i did that be doing the following:
# cylc config -d > /home/$USER/.cylc/flow/global.cylc

## then, within that global.cylc i had to change the ssh command field from gsissh to ssh
## i also commented out 'cylc path', but it doesn't do anything in the first place since use login shell = True


## i needed these in my ~/.bash_profile
#echo "(~/.bash_profile) export LANG=C.UTF-8"
#export LANG=C.UTF-8
#export PATH=$(echo "$PATH" | awk -v RS=: -v ORS=: '$0 != "/usr/local/bin"' | sed 's/:$//')

## path to my virtual env fre-cli was necessary too
#export PATH=/home/inl/conda/envs/fre-cli/bin:$PATH
#echo "PATH is now: $PATH"


expt="test_pp_locally"
platform="ptest"
target="ttest"
yaml="for_gh_runner/yaml_workflow/model.yaml"

workflow_dir_name="${expt}__${platform}__${target}"
echo "workflow_dir_name = $workflow_dir_name"

string="-e $expt -p $platform -t $target"


echo ""
echo ""
echo "*****************"
echo "CLEANING UP OLD SOURCE CODE IF FOUND"
if [ -d /home/$USER/cylc-src/$workflow_dir_name ]; then
	echo "source code found, REMOVING OLD cylc-src"
	rm -rf /home/$USER/cylc-src/$workflow_dir_name
fi

echo ""
echo ""
echo "*****************"
echo "CLEANING UP OLD RUN DIR IF FOUND"
if [ -d /home/$USER/cylc-run/$workflow_dir_name ]; then
	echo "run dir found, cylc stop first"
	cylc stop --now --now ${workflow_dir_name}
	
	echo "cylc clean next"
	cylc clean $workflow_dir_name

	echo "src dir found, REMOVING OLD cylc-src"
	rm -rf /home/$USER/cylc-src/$workflow_dir_name
fi

sleep 30s

#echo ""
#echo ""
#echo "*****************"
#echo "CHECKING OUT"
#fre -vv pp checkout $string
#if [ $? -ne 0 ] ; then
#    echo "ERROR CHECKING OUT"
#fi

echo ""
echo ""
echo "*****************"
echo "MOCK CHECKING OUT"
mock_checkout_targ=$(pwd)
echo "cd .. && cp -rf $mock_checkout_targ /home/$USER/cylc-src/$workflow_dir_name && cd -"
cd .. && cp -rf $mock_checkout_targ /home/$USER/cylc-src/$workflow_dir_name && cd -
if [ $? -ne 0 ] ; then
    echo "ERROR MOCK CHECKING OUT"
	return 1
fi

echo ""
echo ""
echo "*****************"
echo "CONFIGURING YAML"
echo "fre -vv pp configure-yaml -y $yaml $string"
fre -vv pp configure-yaml -y $yaml $string
if [ $? -ne 0 ] ; then
    echo "*****************"
    echo "ERROR CONFIGURING YAML"
	return 1
fi

echo ""
echo ""
echo "*****************"
echo "VALIDATING"
echo "fre -vv pp validate $string"
fre -vv pp validate $string
if [ $? -ne 0 ] ; then
    echo "*****************"
    echo "ERROR VALIDATING"
	return 1
fi

echo ""
echo ""
echo "*****************"
echo "INSTALLING"
echo "fre -vv pp install $string"
fre -vv pp install $string
if [ $? -ne 0 ] ; then
    echo "*****************"
    echo "ERROR INSTALLING"
	return 1
fi

echo ""
echo ""
echo "*****************"
echo "RUNNING"
echo "cylc play --no-detach --debug -s 'STALL_TIMEOUT=\"PT0S\"' $name"
cylc play --no-detach --debug -s 'STALL_TIMEOUT="PT10S"' $workflow_dir_name
#echo "fre -vv pp run $string"
#fre -vv pp run $string
if [ $? -ne 0 ] ; then
    echo "*****************"
    echo "ERROR RUNNING"
	return 1
fi

#@echo ""
#@echo ""
#@echo "*****************"
#@echo "cylc workflow-state every 5 seconds"
#@watch -n 5 'cylc workflow-state -v test_pp_locally__ptest__ttest'


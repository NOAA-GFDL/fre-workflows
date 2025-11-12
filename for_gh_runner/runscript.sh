#!/bin/bash

# stops script if a command fails
# set -e 

## TO-DO: 
##    - automate rebuilding container when there is an update in fre-cli
##    - checks for the status of the workflow (before installation step)

# Initialize ppp-setup
# Set environment variables 
export TMPDIR=/mnt/temp
export HOME=/mnt

#Not sure if needed
#export CYLC_CONF_PATH=/mnt

### WHAT IS NEEDED ON THE CLOUD VS NOT for conda set-up
# Initializations for conda environment in container
conda init --all
source /opt/conda/etc/profile.d/conda.sh
conda deactivate
conda activate /app/cylc-flow-tools

# update fre-cli env with specific branch development
cd fre-cli
git checkout add-climo-wrapper
pip install .
export PATH=/mnt/.local/bin:$PATH
cd -

get_user_input () {
    # User input
    echo Please Enter Experiment Name:
    echo "Experiment name: test_pp"

    echo Please Enter Platform:
#    read -r plat
    echo "Platform: ptest"

    echo Please Enter Target:
#    read -r targ
    echo "Target: ttest"

    echo Please Enter Path to model yaml file:
#    read -r yamlfile
    echo "Model yaml: ./for_gh_runner/yaml_workflow/model.yaml"

    expname="test_pp"
    plat="ptest"
    targ="ttest"
    yamlfile="./for_gh_runner/yaml_workflow/model.yaml"

    name=${expname}__${plat}__${targ}
}

create_dirs () {
    # Create necessary paths used in workflow
    paths=("${HOME}/pp" "${HOME}/ptmp" "${HOME}/temp")

    for p in ${paths[@]}; do
        if [ -d $p ]; then
            echo -e "Path $p previously created. Removing..."
            rm -rf $p
            echo -e "   Creating new $p\n"
            mkdir -p $p
        else
            mkdir -p $p
        fi
    done
}

check_exit_status () {
    if [ $? -ne 0 ]; then
        echo "$1 failed"
        exit 1
    fi
}

fre_pp_steps () {
    set -x

    # experiment cleaned if previously installed
    if [ -d /mnt/cylc-run/${name} ]; then
        echo -e "\n${name} previously installed"
        echo "   Removing ${name}..."
        cylc clean ${name}
    fi

    ## Checkout
    echo -e "\nCreating $name directory in ${HOME}/cylc-src/${name} ..."
    rm -rf /mnt/cylc-src/${name}
    mkdir -p /mnt/cylc-src/${name}

    echo -e "\nCopying fre-workflows directory in ${HOME}/cylc-src/${name} ..."
    cp -r ./* /mnt/cylc-src/${name}
    check_exit_status "MOCK CHECKOUT (cp)"

    #Not sure if needed because if no global.cylc found, cylc uses default, which utilizes background jobs anyway ...
    #export CYLC_CONF_PATH=/mnt/cylc-src/${name}/generic-global-config/

    ## Configure the rose-suite and rose-app files for the workflow
    echo -e "\nRunning fre pp configure-yaml, combining separate yaml configs into one, then writing rose-suite/app config files ..."
    fre -vv pp configure-yaml -e ${expname} -p ${plat} -t ${targ} -y ${yamlfile}
    check_exit_status "CONFIGURE-YAML"

    ## Validate the configuration files
    echo -e "\nRunning fre pp validate, validating rose-suite/app config files ..."
    fre -vv pp validate -e ${expname} -p ${plat} -t ${targ} || echo "validation didn't work, guarding against exit"
    check_exit_status "VALIDATE"

    # Install
    echo -e "\nRunning fre pp install, installing workflow in ${HOME}/cylc-run/${name} ..."
    fre -vv pp install -e ${expname} -p ${plat} -t ${targ}
    check_exit_status "INSTALL"

    ## RUN
    echo -e "\nRunning the workflow with cylc play ..."
    cylc play --no-detach --debug -s 'STALL_TIMEOUT="PT0S"' ${name}
    #check_exit_status "PLAY" # if cylc play fails and this is not commented, log uploading does not work

    ## SUMMARY
    echo -e "\nWorkflow ended, final task states from workflow-state are ..."
    cylc workflow-state -v ${name}
}

main () {
    # Run set-up and fre-cli post-processing steps #

    # Set user-input
    get_user_input

    #Create directories needed for post-processing
    create_dirs

    # Run the post-processing steps
    fre_pp_steps
}

# Run main function
main

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

# update fre-cli env with specific branch development
cd fre-cli
pip install .
export PATH=/mnt/.local/bin:$PATH
cd -

get_user_input () {
    echo Please Enter Experiment Name:
    echo "Experiment name: test_pp"

    echo Please Enter Platform:
    echo "Platform: ptest"

    echo Please Enter Target:
    echo "Target: ttest"

    echo Please Enter Path to model yaml file:
    echo "Model yaml: ./for_gh_runner/yaml_workflow/model.yaml"

    expname="test_pp"
    plat="ptest"
    targ="ttest"
    yamlfile="./for_gh_runner/yaml_workflow/model.yaml"

    name=${expname}__${plat}__${targ}
}

create_dirs () {
    

    echo "Creating necessary paths used in workflow"
    paths=("${HOME}/pp" "${HOME}/ptmp" "${HOME}/temp")

    ## check if path exists or if there are any broken symlinks
    ## in refinediag task, there is a point in which symlinks are being made, 
    ## which caused an issue when re-running and copying files to locations
    ## that existed already (from the broken symlinks)
    for p in "${paths[@]}"; do
        if [ -e "$p" ] || [ -L "$p" ]; then
            readlink $p
            echo -e "Path $p previously created. Removing..."
            rm -rf "$p"
            echo -e "   Creating new $p\n"
            mkdir -p "$p"
        else
            mkdir -p "$p"
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

    ## Clean previous experiment
    echo "experiment cleaning, if it was previously installed"
    if [ -d ${HOME}/cylc-run/${name} ]; then
        echo -e "\n${name} previously installed"
        echo "   Removing ${name}..."
        cylc clean ${name}
    fi

    ## More cleaning needed for refineDiag output
    if [ -d ${HOME}/$USER/refined_history ]; then
        echo -e "Refine Diag scripts previously run, removing ..."
        rm -rf ${HOME}/$USER/refined_history
    fi 

    ## Checkout
    echo -e "\nCreating $name directory in ${HOME}/cylc-src/${name} ..."
    rm -rf ${HOME}/cylc-src/${name}
    mkdir -p ${HOME}/cylc-src/${name}

    echo -e "\nCopying fre-workflows directory in ${HOME}/cylc-src/${name} ..."
    cp -r ./* ${HOME}/cylc-src/${name}
    check_exit_status "MOCK CHECKOUT (cp)"

    #Not sure if needed because if no global.cylc found, cylc uses default, which utilizes background jobs anyway ...
    #export CYLC_CONF_PATH=/mnt/cylc-src/${name}/generic-global-config/

    ## Configure the rose-suite file for the workflow
    echo -e "\nRunning fre pp configure-yaml, combining separate yaml configs into one, then writing rose-suite config file ..."
    fre -vv pp configure-yaml -e ${expname} -p ${plat} -t ${targ} -y ${yamlfile}
    check_exit_status "CONFIGURE-YAML"

    ## Validate the configuration files
    echo -e "\nRunning fre pp validate, validating rose-suite config file ..."
    fre -vv pp validate -e ${expname} -p ${plat} -t ${targ}
    check_exit_status "VALIDATE"

    # Install
    echo -e "\nRunning fre pp install, installing workflow in ${HOME}/cylc-run/${name} ..."
    fre -vv pp install -e ${expname} -p ${plat} -t ${targ}
    check_exit_status "INSTALL"

    ## RUN
    echo -e "\nRunning the workflow with cylc play ..."
    # set these two jinja variables to disable task retries and set the stall timer to zero
    cylc play --no-detach --debug -s 'STALL_TIMEOUT="PT0S"' -s 'DEFAULT_RETRIES=""' ${name}
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

#!/bin/bash 
set -eox

#make sure RUN is defined first. source me. 

cylc stop am5_c96L33_amip/run${RUN}
export RUN=$(($RUN+1)) 
bin/install-exp am5_c96L33_amip && cylc play -v -v am5_c96L33_amip/run${RUN} 
sleep 5s 
echo "" 
cat ~/cylc-run/am5_c96L33_amip/run${RUN}/log/job/19800101T0000Z/pp-starter/01/job-activity.log

set +eox

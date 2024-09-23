python3 -m venv $CYLC_WORKFLOW_SHARE_DIR/analysis-envs/clouds
source $CYLC_WORKFLOW_SHARE_DIR/analysis-envs/clouds/bin/activate
pip install --upgrade pip
cd $CYLC_TASK_WORK_DIR
git clone https://github.com/NOAA-GFDL/analysis-scripts.git
cd analysis-scripts
cd analysis-scripts && pip install . && cd ..
cd figure_tools && pip install . && cd ..
cd freanalysis && pip install . && cd ..
cd freanalysis_clouds && pip install . && cd ..

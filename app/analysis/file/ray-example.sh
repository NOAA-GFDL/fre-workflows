#!/bin/bash

# set path to catalog and output directory
catalog=
out_dir=

# Load modules.
source /usr/local/Modules/5.1.1/init/bash
module load python/3.9

# Run the analysis script.
source /net2/rlm/analysis-scripts/example/env/bin/activate
python3 -c "from freanalysis_clouds import CloudAnalysisScript; CloudAnalysisScript().run_analysis('$catalog', '$output_dir')"

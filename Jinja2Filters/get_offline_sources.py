#/usr/bin/env /net2/Dana.Singh/envs/fre-cli/bin/python
"""
Create a dictionary of the offline static diagnostic
paths associated with a pp component.
"""

import os
from pathlib import Path
import logging
import yaml

# set up logging
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def get_offline_sources(temporal_type, pp_components_str, yamlfile):
    """
    Arguments:
        grid_type (str): One of: native or regrid-xy
        temporal_type (str): One of: temporal or static
        pp_component (str): all, or a space-separated list
    """
    logger.debug("Desired pp components: %s", pp_components_str)
    pp_components = pp_components_str.split()

    # Path to yaml configuration
    exp_dir = Path(__file__).resolve().parents[1]
    path_to_yamlconfig = os.path.join(exp_dir, yamlfile)
    # Load and read yaml configuration
    with open(path_to_yamlconfig,'r') as yml:
        yml_info = yaml.safe_load(yml)

    for comp_info in yml_info["postprocess"]["components"]:
        comp = comp_info.get("type")
        # Check that pp_components defined matches those in the yaml file
        # Skip component if they don't match
        # skip if pp component not desired
        if comp not in pp_components:
            continue

        # Assess offline diagnostics
        # Dictionary for {component: [list of offline diagnostic paths]}
        results = {}
        if temporal_type == "offline_static":
            if "static" not in comp_info.keys():
                logger.debug("Skipping static as there are no static sources defined")
                continue

            offline_src=[]
            for static_info in comp_info["static"]:
                if static_info.get("offline_source") is None:
                    continue

                # Append offline source paths for component to list
                off_src.append(static_info.get("offline_source"))

            # Update dictionary with offline source paths
            results.update({comp_info["type"]: offline_src})

        else:
            raise Exception(f"Temporal type, {temporal_type}, not offline_static")

    return results

## TESTING ##
#print(form_task_parameters('offline_static', 'atmos_scalar', 'c96_climo_cmip6_postprocess_ATMOS.yaml'))

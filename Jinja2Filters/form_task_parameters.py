import os
from pathlib import Path 
import yaml

# set up logging
import logging
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def form_task_parameters(grid_type, temporal_type, pp_components_str, yamlfile):
    """Form the task parameter list based on the grid type, the temporal type,
    and the desired pp component(s)

    Arguments:
        grid_type (str): One of: native or regrid-xy
        temporal_type (str): One of: temporal or static
        pp_component (str): all, or a space-separated list
    """
    logger.debug(f"Desired pp components: {pp_components_str}")
    pp_components = pp_components_str.split()

    # Path to yaml configuration
    exp_dir = Path(__file__).resolve().parents[1]
    path_to_yamlconfig = os.path.join(exp_dir, yamlfile)
    # Load and read yaml configuration 
    with open(path_to_yamlconfig,'r') as yml:
        yml_info = yaml.safe_load(yml)

    #
    results = []
    for comp_info in yml_info["postprocess"]["components"]:
        comp = comp_info.get("type")

        # Check that pp_components defined matches those in the yaml file
        # Skip component if they don't match
        # skip if pp component not desired
        if comp in pp_components: 
            pass
        else:
            continue

        # Set grid type if component has xyInterp defined or not
        if "xyInterp" not in comp_info.keys():
            candidate_grid_type = "native"
        else:
            candidate_grid_type = "regrid-xy"

        # Check that candidate_grid_type matches grid type passed in function
        # If not, skip post-processing of component
        if candidate_grid_type != grid_type:
            logger.debug(f"Skipping as not right grid; got '{candidate_grid_type}' and wanted '{grid_type}'")
            continue

        # Filter static and temporal
        if temporal_type == "static":
            #print(comp_info["static"]["freq"])
            if "static" not in comp_info.keys():
                logger.debug("Skipping static as there are no static sources defined")
                continue

            for static_info in comp_info["static"]:
                if static_info.get("source") is not None:
                    results.append(static_info.get("source"))
## to-do: assess offline diagnostics
#                elif:
#                    results = results + static_info.get("offline_sources")

        elif temporal_type == "temporal":
            for hist_file in comp_info["sources"]:
                results.append(hist_file.get("history_file"))
            #results = results + comp_info.get("sources")

        else:
            raise Exception(f"Unknown temporal type: {temporal_type}")
            
    # results list --> set --> list: checks for repetitive sources listed
    answer = sorted(list(set(results)))

    # Returns a comma separated list of sources
    logger.debug("Returning string" + ', '.join(answer))
    return(', '.join(answer))

## OWN TESTING ##
#print(form_task_parameters('regrid-xy', 'temporal', 'ocean_cobalt_sfc ocean_cobalt_btm', 'COBALT_postprocess.yaml')))
#print(form_task_parameters('regrid-xy', 'static', 'ocean_cobalt_sfc ocean_cobalt_btm', 'COBALT_postprocess.yaml'))
#print(form_task_parameters('native', 'temporal', 'ocean_cobalt_sfc ocean_cobalt_btm', 'COBALT_postprocess.yaml'))
#print(form_task_parameters('native', 'static', 'ocean_cobalt_sfc ocean_cobalt_btm', 'COBALT_postprocess.yaml'))

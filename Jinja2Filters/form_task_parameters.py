import re
import os
import metomi.rose.config
import ast
from pathlib import Path
import yaml

# set up logging
import logging
logging.basicConfig(level=logging.INFO)
fre_logger = logging.getLogger(__name__)

def form_task_parameters(grid_type, temporal_type, pp_components_str, yamlfile):
    """Form the task parameter list based on the grid type, the temporal type,
    and the desired pp component(s)

    Arguments:
        grid_type (str): One of: native or regrid-xy
        temporal_type (str): One of: temporal or static
        pp_component (str): all, or a space-separated list
"""
    fre_logger.debug(f"Desired pp components: {pp_components_str}")
    pp_components = pp_components_str.split()
    path_to_conf = os.path.dirname(os.path.abspath(__file__)) + '/../app/remap-pp-components/rose-app.conf'
    node = metomi.rose.config.load(path_to_conf)

    # Path to yaml configuration
    exp_dir = Path(__file__).resolve().parents[1]
    path_to_yamlconfig = os.path.join(exp_dir, yamlfile)
    # Load and read yaml configuration 
    with open(path_to_yamlconfig,'r') as yml:
        yml_info = yaml.safe_load(yml)

    results = []
    regex_pp_comp = re.compile('^\w+')
    for keys, sub_node in node.walk():
        # only target the keys
        if len(keys) != 1:
            continue

        # skip env and command keys
        item = keys[0]
        if item == "env" or item == "command":
            continue
        comp = regex_pp_comp.match(item).group()

        # skip if pp component not desired
        if comp in pp_components: 
            pass
        else:
            continue
        fre_logger.debug(f"Examining item '{item}' and component '{comp}'")

        # skip if grid type is not desired
        # some grid types (i.e. regrid-xy) have subtypes (i.e. 1deg, 2deg)
        # in remap-pp-components/rose-app.conf the grid type and subgrid is specified as "regrid-xy/1deg" (e.g.).
        # So we will strip off after the slash and the remainder is the grid type
        candidate_grid_type = re.sub('\/.*', '', node.get_value(keys=[item, 'grid']))
        if candidate_grid_type != grid_type:
            fre_logger.debug(f"Skipping as not right grid; got '{candidate_grid_type}' and wanted '{grid_type}'")
            continue

        # filter static and temporal
        # if freq is not set             => temporal
        # if freq includes "P0Y"         => static
        # if freq does not include "P0Y" => temporal
        freq = node.get_value(keys=[item, 'freq'])
        if freq is not None and 'P0Y' in freq and temporal_type == 'temporal':
            fre_logger.debug("Skipping static when temporal is requested")
            continue
        if temporal_type == "static":
            if freq is not None and 'P0Y' not in freq:
                fre_logger.debug("Skipping as static is requested, no P0Y here")
                continue
        elif (temporal_type == "temporal"):
            if freq is not None and 'P0Y' in freq:
                fre_logger.debug("Skipping as temporal is requested, P0Y here")
                continue
        else:
            raise Exception("Unknown temporal type:", temporal_type)

        # convert array in string form to array
        sources = ast.literal_eval(node.get_value(keys=[item, 'sources']))
        for source in sources:
            results.append(source['history_file'])
        fre_logger.debug(f"Results so far: {results}")

    answer = sorted(list(set(results)))
    fre_logger.debug(f"Returning string: {', '.join(answer)}")
    return(', '.join(answer))

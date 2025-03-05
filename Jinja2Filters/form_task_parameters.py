import re
import os
import metomi.rose.config
import ast
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
        logger.debug(f"Examining item '{item}' comp '{comp}'")

        # skip if pp component not desired
        logger.debug(f"Is {comp} in {pp_components}?")
        if comp in pp_components: 
            logger.debug('Yes')
        else:
            logger.debug('No')
            continue

        # skip if grid type is not desired
        # some grid types (i.e. regrid-xy) have subtypes (i.e. 1deg, 2deg)
        # in remap-pp-components/rose-app.conf the grid type and subgrid is specified as "regrid-xy/1deg" (e.g.).
        # So we will strip off after the slash and the remainder is the grid type
        candidate_grid_type = re.sub('\/.*', '', node.get_value(keys=[item, 'grid']))
        if candidate_grid_type != grid_type:
            logger.debug(f"Skipping as not right grid; got '{candidate_grid_type}' and wanted '{grid_type}'")
            continue

        # filter static and temporal
        # if freq is not set             => temporal
        # if freq includes "P0Y"         => static
        # if freq does not include "P0Y" => temporal
        freq = node.get_value(keys=[item, 'freq'])
        if freq is not None and 'P0Y' in freq and temporal_type == 'temporal':
            logger.debug("Skipping static when temporal is requested")
            continue
        if temporal_type == "static":
            if freq is not None and 'P0Y' not in freq:
                logger.debug("Skipping as static is requested, no P0Y here", freq)
                continue
        elif (temporal_type == "temporal"):
            if freq is not None and 'P0Y' in freq:
                logger.debug("Skipping as temporal is requested, P0Y here", freq)
                continue
        else:
            raise Exception("Unknown temporal type:", temporal_type)

        # convert array in string form to array
        sources = ast.literal_eval(node.get_value(keys=[item, 'sources']))
        results.extend(sources)

    answer = sorted(list(set(results)))
    logger.debug("Returning string" + ', '.join(answer))
    return(', '.join(answer))

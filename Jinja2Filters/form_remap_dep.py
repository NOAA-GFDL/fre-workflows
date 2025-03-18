import re
import os
import metomi.rose.config
import ast

# set up logging
import logging
logging.basicConfig(level=logging.INFO)
fre_logger = logging.getLogger(__name__)

"""! form_remap_dep parses the remap_pp_components rose-app.conf and uses input from rose-suite.conf in the form of
env variables and returns the pp component and source name dependencies for remap_pp_components task execution. For 
instance, for an atmos PP component that requires the regridded atmos_month and regridded atmos_daily history 
files, this JinjaFilter when called within flow.cylc helps identify this dependency to complete the corresponding 
task graph. This JinjaFilter ensures a remap-pp-component only waits for the dependent make-timeseries tasks such 
that the succeeded components output are made available in the final destination. 
See form_remap_dep invocations from flow.cylc
"""
# @file form_remap_dep.py
# Author(s)
# Created by A.Radhakrishnan on 06/27/2022
# Credit MSD workflow team
 
# Function parameter type hints, PEP 484
 
def form_remap_dep(grid_type: str, temporal_type: str, chunk: str, pp_components_str: str, output_type: str, history_segment: str=None) -> str:

    """ Form the task parameter list based on the grid type, the temporal type, and the desired pp component(s)

    Arguments:
       @param grid_type (str): One of: native or regrid-xy
       @param temporal_type (str): One of: temporal or static
       @param chunk (str): e.g P5Y for 5-year time series 
       @param pp_component (str): all, or a space-separated list
       @param output_type (str): ts or av
       @param history_segment (str): if given, handle special case where history segment equals pp-chunk-a

       @return remap_dep (multiline str) with Jinja formatting listing source-pp dependencies  
    """
    pp_components = pp_components_str.split(' ')
    if(grid_type == "regrid-xy"):
      grid = "regrid"
    else:
      grid = grid_type 

    # Determine the task needed to run before remap-pp-components
    # Note: history_segment should be specified for primary chunk generation,
    # and omitted for secondary chunk generation.
    if output_type == "ts":
        if history_segment == chunk:
            prereq_task = "rename-split-to-pp"
        else:
            prereq_task = "make-timeseries"
    elif output_type== "av":
        prereq_task = "make-timeavgs"
    else:
        raise Exception("output type not supported")

    ########################
    dict_group_source={}
    remap_comp = None 
    fre_logger.debug(f"Passed args: grid_type='{grid_type}', temporal_type='{temporal_type}', chunk='{chunk}', pp_components_str='{pp_components_str}'")
    remap_dep = "" 
    path_to_conf = os.path.dirname(os.path.abspath(__file__)) + '/../app/remap-pp-components/rose-app.conf'
    node = metomi.rose.config.load(path_to_conf)
    results = []
    makets_stmt = ""
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
        if comp not in pp_components:
            continue
        fre_logger.debug(f"Examining item '{item}' and component '{comp}'")

        # skip if grid type is not desired
        # some grid types (i.e. regrid-xy) have subtypes (i.e. 1deg, 2deg)
        # in remap-pp-components/rose-app.conf the grid type and subgrid is specified as "regrid-xy/1deg" (e.g.).
        # So we will strip off after the slash and the remainder is the grid type
        candidate_grid_type = re.sub('\/.*', '', node.get_value(keys=[item, 'grid']))
        if candidate_grid_type != grid_type:
            fre_logger.debug(f"Skipping as not right grid; got '{candidate_grid_type}' but wanted '{grid_type}'")
            continue

        # skip if temporal type is not desired
        # freq is optional, so if it does not exist then continue on
        freq = node.get_value(keys=[item, 'freq'])
        if temporal_type == "static":
            if freq and 'P0Y' not in freq:
                fre_logger.debug("Skipping as static is requested, no P0Y here")
                continue
        elif (temporal_type == "temporal"):
            if freq and 'P0Y' in freq:
                fre_logger.debug("Skipping as temporal is requested, P0Y here")
                continue
        else:
            raise Exception("Unknown temporal type:", temporal_type)
        # chunk is optional, so if it does not exist then continue on
        chunk_from_config = node.get_value(keys=[item, 'chunk'])
        if chunk_from_config and chunk not in chunk_from_config:
            fre_logger.debug("Skipping as chunk '{chunk}' is requested, but not in configuration {chunk_from_config}")
            continue

        results = ast.literal_eval(node.get_value(keys=[item, 'sources']))
        remap_comp = comp
        answer = sorted(list(set(results)))
        if remap_comp is not None:
           #If the same PP component is mapped to several sources per rose-app.conf, we make it a list and append values so we don't replace the key's value 
         if remap_comp in dict_group_source.keys():
              dict_group_source[remap_comp].append(answer[0])    
         else:
              dict_group_source[remap_comp] = answer 
    if dict_group_source:
          for key, value in dict_group_source.items():
              makets_stmt = ""
              for src in value:
                  if(makets_stmt != ''): 
                      # make-timeseries and make-timeavgs tasks have the chunksize in the task name,
                      # but rename-split-to-pp does not
                      if prereq_task == 'rename-split-to-pp':
                          makets_stmt = f"{makets_stmt} & {prereq_task}-{grid}_{src}"
                      else:
                          makets_stmt = f"{makets_stmt} & {prereq_task}-{grid}-{chunk}_{src}"
                  else:
                      if prereq_task == 'rename-split-to-pp':
                          makets_stmt = f"{prereq_task}-{grid}_{src}"
                      else:
                          makets_stmt = f"{prereq_task}-{grid}-{chunk}_{src}"
 
              remap_stmt = f"remap-pp-components-{output_type}-{chunk}_{key}"
              remap_dep_stmt = f"{makets_stmt} => {remap_stmt}"
              remap_dep += f"{remap_dep_stmt}\n"
    # Possibly, no tasks are needed for the given request (grid type, temporal/static, chunk, components).
    # When that happens just exit with an empty string and exit normally.
    return(remap_dep)

#print(form_remap_dep('regrid-xy', 'temporal', 'P4D', 'land atmos land_cubic'))

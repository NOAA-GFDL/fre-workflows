""" 
form_remap_dep:
- parses the remap_pp_components rose-app.conf
- uses input from rose-suite.conf in the form of env variables
- returns the pp component and source name dependencies for
  remap_pp_components task execution. 

For instance, for an atmos PP component that requires the regridded
atmos_month and regridded atmos_daily history files, this JinjaFilter
when called within flow.cylc helps identify this dependency to
complete the corresponding task graph. 

This JinjaFilter ensures a remap-pp-component only waits for the
dependent make-timeseries tasks such that the succeeded components
output are made available in the final destination. 

See form_remap_dep invocations from flow.cylc
"""
# Function parameter type hints, PEP 484

import os
from pathlib import Path
import yaml

def form_remap_dep(grid_type: str,
                   temporal_type: str,
                   chunk: str,
                   pp_components_str: str,
                   output_type: str,
                   yamlfile: str,
                   history_segment: str=None) -> str:
    """ 
    Form the task parameter list based on the grid type,
    the temporal type, and the desired pp component(s)

    Arguments:
       @param grid_type (str): One of: native or regrid-xy
       @param temporal_type (str): One of: temporal or static
       @param chunk (str): e.g P5Y for 5-year time series 
       @param pp_component (str): all, or a space-separated list
       @param output_type (str): ts or av
       @param yamlfile (str): yaml configuration file passed through workflow
       @param history_segment (str): if given, handle special case where history
                                     segment equals pp-chunk-a

       @return remap_dep (multiline str) with Jinja formatting listing source-pp
               dependencies  
    """
    pp_components = pp_components_str.split(' ')
    if grid_type == "regrid-xy":
        grid = "regrid"
    else:
        grid = grid_type

    # Determine the task needed to run before remap-pp-components
    # Note: history_segment should be specified for primary chunk generation,
    # and omitted for secondary chunk generation.
    if output_type == "ts":
        if str(history_segment) == str(chunk):
            prereq_task = "rename-split-to-pp"
        else:
            prereq_task = "make-timeseries"
    elif output_type== "av":
        prereq_task = "make-timeavgs"
    else:
        raise Exception("output type not supported")

    #print(pp_components)
    #print(chunk)
    ########################
    dict_group_source={}
    remap_comp = None
    #print("DEBUG: Passed args ",grid_type, temporal_type, chunk, pp_components_str)
    remap_dep = ""
    #print("DEBUG: desired pp components:", pp_components)

    # Path to yaml configuration
    exp_dir = Path(__file__).resolve().parents[1]
    path_to_yamlconfig = os.path.join(exp_dir, yamlfile)

    # Load and read yaml configuration
    with open(path_to_yamlconfig,'r') as yml:
        yml_info = yaml.safe_load(yml)

    makets_stmt = ""
    # Loop through pp components; check components passd in script are defined in yaml config
    for comp_info in yml_info["postprocess"]["components"]:
        comp = comp_info.get("type")

        #print("DEBUG: Examining", item, comp)
        if comp not in pp_components:
            #print(comp, " not in", pp_components)
            continue

        # skip if grid type is not desired
        # Set grid type if component has xyInterp defined or not
        if "xyInterp" not in comp_info.keys():
            candidate_grid_type = "native"
        else:
            candidate_grid_type = "regrid-xy"

        if candidate_grid_type != grid_type:
            #print("DEBUG: Skipping as not right grid; got", candidate_grid_type, "and wanted", grid_type)
            continue

##########NOT SURE YET
#        # skip if temporal type is not desired
#        # freq is optional, so if it does not exist then continue on
#        freq = node.get_value(keys=[item, 'freq'])
        freq = comp_info.get("freq")
        if temporal_type == "static":
            if freq is not None and 'P0Y' not in freq:
                #print("DEBUG: Skipping as static is requested, no P0Y here", freq)
                continue
        elif temporal_type == "temporal":
            if freq is not None and 'P0Y' in freq:
                #print("DEBUG: Skipping as temporal is requested, P0Y here", freq)
                continue
        else:
            raise Exception(f"Unknown temporal type: {temporal_type}")
#########
#        # chunk is optional, so if it does not exist then continue on
        chunk_from_config = comp_info.get("chunk")
        if chunk_from_config is not None and chunk not in chunk_from_config:
            #print("DEBUG: Skipping as {} is requested, but not in rose-app config {}:".format(chunk, comp_info["chunk"]))
            continue
##########
        results=[]

        # Get source list; append to results
        for hist_file in comp_info["sources"]:
            results.append(hist_file.get("history_file"))

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
                if makets_stmt != '':
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
    return remap_dep

# Testing #
#print(form_remap_dep('regrid-xy', 'temporal', 'P4D', 'atmos_cmip atmos', 'ts', 'c96L65_am5f7b12r1_amip_TEST_GRAPH.yaml'))

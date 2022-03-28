import re
import os
import metomi.rose.config

def form_task_parameters(grid_type, temporal_type, pp_components):
    """Form the task parameter list based on the grid type, the temporal type,
    and the desired pp component(s)

    Arguments:
        grid_type (str): One of: native or regrid-xy
        temporal_type (str): One of: temporal or static
        pp_component (str): all, or a comma-separated list
"""
    path_to_conf = os.path.dirname(os.path.abspath(__file__)) + '/../app/remap-pp-components/rose-app.conf'
    node = metomi.rose.config.load(path_to_conf)
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
        #print("DEBUG: Examining", item, comp)

        # skip if pp component not desired
        if "all" not in pp_components:
            #print("DEBUG: PP COMP", pp_components, "COMP is", comp)
            if comp not in pp_components:
                #print("DEBUG2: comp is not in pp_components", pp_components, "and", comp)
                continue
        #print("DEBUG: Examining", item, comp)

        # skip if grid type is not desired
        if node.get_value(keys=[item, 'grid']) != grid_type:
            #print("DEBUG: Skipping as not right grid")
            continue

        # skip if temporal type is not desired
        freq = node.get_value(keys=[item, 'freq'])
        if temporal_type == "static":
            if 'P0Y' not in freq:
                #print("DEBUG: Skipping as static is requested, no P0Y here", freq)
                continue
        elif (temporal_type == "temporal"):
            if 'P0Y' in freq:
                #print("DEBUG: Skipping as temporal is requested, P0Y here", freq)
                continue
        else:
            raise Exception("Unknown temporal type:", temporal_type)

        results = results + node.get_value(keys=[item, 'source']).split()

    answer = sorted(list(set(results)))
    return(', '.join(answer))

#print(form_task_parameters('native', 'temporal', 'land atmos land_cubic'))
import re
import os
import metomi.rose.config

def form_task_parameter_components(grid_type, temporal_type, pp_components_str):
    """Form a dictionary with task-parameters as keys and their corresponding 
    component(s) as a list. The dict is based on the grid type (regrid or native), 
    time dependence (static or temporal) and the desired/requested components. 

    it also depends on configuration information within app/remap-pp-componenets/rose-suite.conf
    which defines what source files (task parameters) are desired given specific componenets. 

    Arguments:
        grid_type (str): One of: native or regrid-xy
        temporal_type (str): One of: temporal or static
        pp_component (list of str): all, or a space-separated list
    """
    
    pp_components = pp_components_str.split()
    
    path_to_conf = os.path.dirname(os.path.abspath(__file__)) + '/../app/remap-pp-components/rose-app.conf'
    node = metomi.rose.config.load(path_to_conf)
    
    results = {}
    regex_pp_comp = re.compile('^\w+')

    for key, sub_node in node.walk():

        # key should be a list with 1 string entry, always.
        if len(key) != 1:
            continue

        # skip env and command key
        item = key[0]
        if item == "env" or item == "command":
            continue
        comp = regex_pp_comp.match(item).group()

        # skip if pp component not desired
        if "all" not in pp_components and comp not in pp_components:
            continue

        # skip if grid type is not desired
        # some grid types (i.e. regrid-xy) have subtypes (i.e. 1deg, 2deg)
        # in remap-pp-components/rose-app.conf the grid type and subgrid is specified as "regrid-xy/1deg" (e.g.).
        # So we will strip off after the slash and the remainder is the grid type
        candidate_grid_type = re.sub('\/.*', '', node.get_value(keys=[item, 'grid']))
        if candidate_grid_type != grid_type:
            continue

        # filter static and temporal
        # if freq is not set             => temporal
        # if freq includes "P0Y"         => static
        # if freq does not include "P0Y" => temporal
        freq = node.get_value(keys=[item, 'freq'])

        if freq is not None and 'P0Y' in freq and temporal_type == 'temporal':
            continue

        if temporal_type == "static":
            if freq is not None and 'P0Y' not in freq:
                continue
        elif (temporal_type == "temporal"):
            if freq is not None and 'P0Y' in freq:
                continue
        else:
            raise Exception("Unknown temporal type:", temporal_type)

        relevant_comps=[]
        relevant_comps.append(key[0])
        sources = node.get_value(keys=[item, 'sources']).split()
        for source in sources:
            if source not in results:
                results[source] = relevant_comps[0]
            else:
                other_comps=results[source].split(' ')
                if __name__=="__main__":
                    print(f'other_comps={other_comps}')

                other_comps.append(relevant_comps[0])
                results[source] = ' '.join(other_comps)
                if __name__=="__main__":
                    print(f'results[{source}]={results[source]}')
                
    return results


##### local debug/testing
### requires some kind of configuration present in app/remap_pp_components/rose-app.conf
### *AND* within app/regridy-xy/rose-app.conf
grid_type='regrid-xy'
temporal_type='temporal'
pp_components_str="atmos atmos_cmip"
print(f"\nform_task_parameter_components({grid_type}, {temporal_type}, {pp_components_str}) \n yields...")
print(form_task_parameter_components(grid_type=grid_type, temporal_type=temporal_type, pp_components_str=pp_components_str))


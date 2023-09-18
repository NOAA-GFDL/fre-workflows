import re
import os
import metomi.rose.config

def form_task_parameters_2(grid_type, temporal_type, pp_components_str):
    """Form the task parameter list based on the grid type, the temporal type,
    and the desired pp component(s)

    Arguments:
        grid_type (str): One of: native or regrid-xy
        temporal_type (str): One of: temporal or static
        pp_component (str): all, or a space-separated list
    """
    print(f'\n ------_______ form_task_parameters_2( {grid_type}, {temporal_type}, {pp_components_str}) ______------ \n')    
    pp_components = pp_components_str.split()
    #print("DEBUG: desired pp components:", pp_components)
    path_to_conf = os.path.dirname(os.path.abspath(__file__)) + '/../app/remap-pp-components/rose-app.conf'
    node = metomi.rose.config.load(path_to_conf)
    #results = []
    results = {}
    regex_pp_comp = re.compile('^\w+')
    #print(f'node={node}')
    for key, sub_node in node.walk():

        # key should be a list with 1 string entry, always.
        # only target the keys
        if len(key) != 1:
            continue

        print(f'key={key}')
        #print(f'sub_node={sub_node}')
        

        # skip env and command key
        item = key[0]
        print(f'item type is: {type(item)}')
        if item == "env" or item == "command":
            continue
        comp = regex_pp_comp.match(item).group()
        print(f'comp type is {type(comp)}')
        print(f'comp is {comp}')
        #print("DEBUG: Examining", item, comp)

        # skip if pp component not desired
        if "all" not in pp_components:
            #print("DEBUG: PP COMP", pp_components, "COMP is", comp)
            if comp not in pp_components: 
       		#print("DEBUG2: comp not in pp_components", pp_components, "and", comp)
                continue
        #print("DEBUG: Examining", item, comp)

        # skip if grid type is not desired
        # some grid types (i.e. regrid-xy) have subtypes (i.e. 1deg, 2deg)
        # in remap-pp-components/rose-app.conf the grid type and subgrid is specified as "regrid-xy/1deg" (e.g.).
        # So we will strip off after the slash and the remainder is the grid type
        candidate_grid_type = re.sub('\/.*', '', node.get_value(keys=[item, 'grid']))
        if candidate_grid_type != grid_type:
            #print("DEBUG: Skipping as not right grid; got", candidate_grid_type, "and wanted", grid_type)
            continue

        # filter static and temporal
        # if freq is not set             => temporal
        # if freq includes "P0Y"         => static
        # if freq does not include "P0Y" => temporal
        freq = node.get_value(keys=[item, 'freq'])

        if freq is not None and 'P0Y' in freq and temporal_type == 'temporal':
            #print("DEBUG: Skipping static when temporal is requested")
            continue

        if temporal_type == "static":
            if freq is not None and 'P0Y' not in freq:
                #print("DEBUG: Skipping as static is requested, no P0Y here", freq)
                continue
        elif (temporal_type == "temporal"):
            if freq is not None and 'P0Y' in freq:
                #print("DEBUG: Skipping as temporal is requested, P0Y here", freq)
                continue
        else:
            raise Exception("Unknown temporal type:", temporal_type)

        component_list=[]
        component_list.append(key[0])
        sources = node.get_value(keys=[item, 'sources']).split()
        for source in sources:
            if source not in results:
                results[source] = component_list
            else:
                #curr_component = str(results[source])
                #curr_component += " " + str(component)
                for other_comp in results[source]: component_list.append(other_comp)
                results[source] = component_list
                

        print(f'key,sources={key},{sources}')        
        #results = results + node.get_value(keys=[item, 'sources']).split()

    #print(f'results=\n{results}\n')
    #answer = sorted(list(set(results)))
    #return(', '.join(answer))
    return results




#print("\nform_task_parameters('native', 'temporal', 'totally_arbitrary_component atmos_scalar') \n yields...")
#print(form_task_parameters('native', 'temporal', 'totally_arbitrary_component atmos_scalar'))

#print("\nform_task_parameters('native', 'temporal', 'atmos_scalar') \n yields...")
#print(form_task_parameters('native', 'temporal', 'atmos_scalar'))
#
#print("\nform_task_parameters('native', 'temporal', 'totally_arbitrary_component') \n yields...")
#print(form_task_parameters('native', 'temporal', 'totally_arbitrary_component'))
#
#print("\nform_task_parameters('native', 'temporal', 'totally_arbitrary_component atmos_scalar') \n yields...")
#print(form_task_parameters('native', 'temporal', 'totally_arbitrary_component atmos_scalar'))


#print(form_task_parameters('native', 'temporal', 'atmos'))


import re
import os
import metomi.rose.config

def strtobool(val): 
    """Convert string true/false to boolean"""
    if val.lower().startswith("t") or val.lower().startswith("y"): 
        return True 
    elif val.lower().startswith("f") or val.lower().startswith("n"): 
        return False 
    raise Exception("invalid boolean value: {!r}".format(val))

def form_analysis_tasks(pp_components_str, pp_dir, start_year, default_chunk1, default_chunk2):
    """Form the analysis tasks from app/analysis/rose-app.conf

    Arguments:
        pp_components_str (str): all, or a space-separated list
                            analysis scripts depending on others will be skipped
        pp_dir (str): absolute filepath root (up to component, not including)
        start_year (str): will use at yr1 if cumulative mode on
        default_chunk[12] (str): default chunks to use if analysis script does not care
"""
    pp_components = pp_components_str.split()
    path_to_conf = os.path.dirname(os.path.abspath(__file__)) + '/../app/analysis/rose-app.conf'
    node = metomi.rose.config.load(path_to_conf)
    results = ""
    for keys, sub_node in node.walk():
        # only target the keys
        if len(keys) != 1:
            continue

        # skip env and command keys
        item = keys[0]
        if item == "env" or item == "command":
            continue

        # get the required pp components for the analysis script
        item_comps = node.get_value(keys=[item, 'components']).split()

        # skip this analysis script if pp component not requested
        #print("DEBUG: Examining", item, item_comps)
        if "all" not in pp_components:
            for comp in item_comps:
                if comp not in pp_components:
                    continue
        #print("DEBUG: Still examining", item)

        # get the mandatory options: script path and frequency
        item_script = os.path.basename(node.get_value(keys=[item, 'script']))
        item_freq = node.get_value(keys=[item, 'freq'])

        # get the optional option chunksize
        # if not set, use the main pp chunks
        item_chunks_str = node.get_value(keys=[item, 'chunk'])
        if item_chunks_str:
            item_chunks = item_chunks_str.split()
        else:
            item_chunks = [default_chunk1, default_chunk2]

        # get the optional cumulative option
        # cumulative option is the entire pp range, not just this chunk
        # default is off
        item_cumulative_str = node.get_value(keys=[item, 'cumulative'])
        if item_cumulative_str:
            item_cumulative = strtobool(item_cumulative_str)
        else:
            item_cumulative = False

        # write the task family
        results += """
            [[{item}]]
                script = '''
                    chmod +x $CYLC_WORKFLOW_SHARE_DIR/analysis-scripts/{item_script}.$yr1-$yr2
                    $CYLC_WORKFLOW_SHARE_DIR/analysis-scripts/{item_script}.$yr1-$yr2
                '''
                [[[environment]]]
                    component = {comp}
                    freq = {freq}
                    staticfile = {pp_dir}/{comp}/{comp}.static.nc
                    scriptLabel = {item}
            """.format(item=item, item_script=item_script, comp=item_comps[0], freq=item_freq, pp_dir=pp_dir)

        # write the tasks
        for chunk in item_chunks:
            # only write the tasks if the chunk is one of the Cylc PP chunks
            if chunk == default_chunk1 or chunk == default_chunk2:
                results += """
            [[{item}-{chunk}]]
                inherit = ANALYSIS-{chunk}, {item}
                [[[environment]]]
                    in_data_dir = {pp_dir}/{comp}/ts/{freq}/{chunk}
            """.format(item=item, chunk=chunk, comp=item_comps[0], freq=item_freq, pp_dir=pp_dir)

        # if cumulative, then set yr1 to the pp start
        if item_cumulative:
            results += """
                        yr1 = {yr1}
            """.format(yr1=start_year)

    #print("DEBUG: returning", results)
    return(results)

#print(form_analysis_tasks('all', '/archive/Chris.Blanton/am5/2022.01/c96L33_am4p0_cmip6Diag/gfdl.ncrc4-intel21-prod-openmp/pp', '2000', 'P1Y', 'P4Y'))

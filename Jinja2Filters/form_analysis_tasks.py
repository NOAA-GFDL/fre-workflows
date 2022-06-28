import re
import os
import metomi.rose.config

def form_analysis_tasks(pp_components, pp_dir, default_chunk1, default_chunk2):
    """Form the analysis tasks from app/analysis/rose-app.conf

    Arguments:
        pp_component (str): all, or a space-separated list
                            analysis scripts depending on others will be skipped
        pp_dir (str): absolute filepath root (up to component, not including)
        default_chunk[12] (str): default chunks to use if analysis script does not care
"""
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

        item_comps = node.get_value(keys=[item, 'components']).split()
        #print("DEBUG: Examining", item, item_comps)

        # skip if pp component not desired
        if "all" not in pp_components:
            #print("DEBUG: PP COMP", pp_components, "COMP is", item_comps)
            for comp in item_comps:
                if comp not in pp_components:
                    #print("DEBUG2: comp is not in pp_components", pp_components, "and", comp)
                    continue
        #print("DEBUG: Still examining", item)

        item_freq = node.get_value(keys=[item, 'freq'])
        item_chunks_str = node.get_value(keys=[item, 'chunk'])
        if item_chunks_str:
            item_chunks = item_chunks_str.split()
        else:
            item_chunks = [default_chunk1, default_chunk2]

        # write the tasks
        for chunk in item_chunks:
            results += """
                [[{item}]]
                    inherit = ANALYSIS-{chunk}
                    script = '''
                        chmod +x $CYLC_WORKFLOW_SHARE_DIR/analysis-scripts/{item}.$yr1-$yr2
                        $CYLC_WORKFLOW_SHARE_DIR/analysis-scripts/{item}.$yr1-$yr2
                    '''
                    [[[environment]]]
                        component = {comp}
                        frequency = {freq}
                        chunksize = {chunk}
                        in_data_dir = {pp_dir}/{comp}/ts/{freq}/{chunk}
                        staticfile = {pp_dir}/{comp}/{comp}.static.nc
            """.format(item=item, chunk=chunk, comp=item_comps[0], freq=item_freq, pp_dir=pp_dir)

    return(results)

#print(form_analysis_tasks('all', '/archive/Chris.Blanton/am5/2022.01/c96L33_am4p0_cmip6Diag/gfdl.ncrc4-intel21-prod-openmp/pp', 'P2Y', 'P4Y'))

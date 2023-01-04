import re
import os
import metomi.rose.config
import metomi.isodatetime.parsers
import metomi.isodatetime.dumpers

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

        # consider adding analysis script to workflow
        # if not adding, write a note why
        print(f"NOTE: Considering adding '{item}' to workflow")

        # get the required pp components for the analysis script
        item_comps = node.get_value(keys=[item, 'components']).split()

        # skip this analysis script if pp component not requested
        if "all" not in pp_components:
            skip_item = 0
            for comp in item_comps:
                if comp not in pp_components:
                    print(f"NOTE: Skipping package '{item}' as it requests a component not available: '{comp}'")
                    skip_item = 1
                    continue
            if skip_item:
                continue

        # get the mandatory options: script path and frequency
        item_script = os.path.basename(node.get_value(keys=[item, 'script']))
        assert item_script
        item_freq = node.get_value(keys=[item, 'freq'])
        assert item_freq
        #print("DEBUG: script and frequency:", item_script, item_freq)

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
        if item_cumulative:
            start_time = metomi.isodatetime.parsers.TimePointParser().parse(start_year + '-01-01')
            print("NOTE: Using cumulative range, starting from:", start_time)

        # get the optional start/end options
        item_start_str = node.get_value(keys=[item, 'start'])
        item_end_str = node.get_value(keys=[item,'end'])
        #print("DEBUG:", item_start_str, item_end_str)
        if item_start_str:
            item_start = metomi.isodatetime.parsers.TimePointParser().parse(item_start_str)
        else:
            item_start = None
        if item_end_str:
            item_end = metomi.isodatetime.parsers.TimePointParser().parse(item_end_str)
        else:
            item_end = None
        if item_start and item_end:
            print("NOTE: Using defined date range:", item_start, item_end)

        # write the analysis script task(s), one for each chunk
        # each analysis script inherits from an analysis script family
        # and a scheduler family
        # the scheduler family looks like ANALYSIS-XXX, where XXX is a defined date request
        # that sets yr1 and inherits from ANALYSIS. ANALYSIS-CHUNK-A/B are in flow.cylc already
        added_a_chunk = 0
        for chunk in item_chunks:
            # in all cases, need to add in suitable in_data_dir corresponding to the PP output
            header = f"[[{item}-{chunk}]]"
            tail = """
        [[[environment]]]
            in_data_dir = {pp_dir}/{comp}/ts/{freq}/{chunk}
            """.format(item=item, chunk=chunk, comp=item_comps[0], freq=item_freq, pp_dir=pp_dir)

            # skip the chunk if it's not available as TS chunks
            if chunk != default_chunk1 and chunk != default_chunk2:
                print("NOTE: Skipping chunk", chunk)
                continue

            # 3 main cases: defined year range, cumulative, and every-chunk
            # defined year range
            if item_start and item_end:
                added_a_chunk = 1
                this_range = metomi.isodatetime.dumpers.TimePointDumper().strftime(item_start, '%Y%m%d') + '_' + metomi.isodatetime.dumpers.TimePointDumper().strftime(item_end, '%Y%m%d')
                print("NOTE: Using defined year range for chunk", chunk)
                results += f"""
    {header}
        inherit = ANALYSIS-{this_range}, {item}
        {tail}
                """
                yr1 = metomi.isodatetime.dumpers.TimePointDumper().strftime(item_start, '%Y')
                yr2 = metomi.isodatetime.dumpers.TimePointDumper().strftime(item_end, '%Y')
                results += f"""
    [[ANALYSIS-{this_range}]]
        inherit = ANALYSIS
        [[[environment]]]
            yr1 = {yr1}
            yr2 = {yr2}
                """

            # cumulative
            elif item_cumulative:
                added_a_chunk = 1
                print("NOTE: Using cumulative for chunk", chunk)
                results += """
    {header}
        inherit = ANALYSIS-CUMULATIVE-{date2}, {item}
        {tail}
                """.format(item=item, header=header, tail=tail, date2=metomi.isodatetime.dumpers.TimePointDumper().strftime(start_time, '%Y%m%d'))

            # every chunk
            else:
                added_a_chunk = 1
                print("NOTE: Using regular chunks for chunk", chunk)
                results += f"""
    {header}
        inherit = ANALYSIS-{chunk}, {item}
        {tail}
                """

        # chunk not available: skip with a message
        if not added_a_chunk:
            print(f"NOTE: Skipping package '{item}' as it requests pp chunks not available")
            continue
        
        # write the analysis script family
        print(f"NOTE: Adding analysis script task family for '{item}'")
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

        print(f"NOTE: Ending processing of '{item}'\n")

    #print("DEBUG: returning", results)
    return(results)

#print(form_analysis_tasks('atmos', '/archive/Chris.Blanton/am5/2022.01/c96L33_am4p0_cmip6Diag/gfdl.ncrc4-intel21-prod-openmp/pp', '2000', 'P1Y', 'P4Y'))

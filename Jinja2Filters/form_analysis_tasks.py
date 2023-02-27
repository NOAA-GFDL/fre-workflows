import os
import re
import sys
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

def get_analysis_info(pp_components_str, pp_dir, start_str, stop_str, default_chunk1_str, default_chunk2_str=None):
    """Form the analysis tasks from app/analysis/rose-app.conf

    Arguments:
        pp_components_str (str): all, or a space-separated list
                            analysis scripts depending on others will be skipped
        pp_dir (str): absolute filepath root (up to component, not including)
        start_str (str): will use at yr1 if cumulative mode on
        stop_str (str): last cycle point to process
        default_chunk[12] (str): default chunks to use if analysis script does not care
"""
    # convert strings to date objects
    start = metomi.isodatetime.parsers.TimePointParser().parse(start_str)
    stop = metomi.isodatetime.parsers.TimePointParser().parse(stop_str)
    sys.stderr.write(f"ANALYSIS: from {start} to {stop}\n")
    default_chunk1 = metomi.isodatetime.parsers.DurationParser().parse(default_chunk1_str)
    sys.stderr.write(f"ANALYSIS: default chunk1 is {default_chunk1}\n")
    if default_chunk2_str:
        default_chunk2 = metomi.isodatetime.parsers.DurationParser().parse(default_chunk2_str)
        sys.stderr.write(f"ANALYSIS: default chunk2 is {default_chunk2}\n")

    pp_components = pp_components_str.split()
    path_to_conf = os.path.dirname(os.path.abspath(__file__)) + '/../app/analysis/rose-app.conf'
    node = metomi.rose.config.load(path_to_conf)

    # build up the results multiline string that will contain the analysis task
    results = ""

    # loop over the analysis scripts listed in the config file
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
        sys.stderr.write(f"ANALYSIS: Considering '{item}'\n")

        # get the required pp components for the analysis script
        item_comps = node.get_value(keys=[item, 'components']).split()

        # skip this analysis script if pp component not requested
        if "all" not in pp_components:
            skip_item = 0
            for comp in item_comps:
                if comp not in pp_components:
                    sys.stderr.write(f"ANALYSIS: Skipping '{item}' as it requests a component not available: '{comp}'\n")
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
        elif default_chunk2_str:
            item_chunks = [default_chunk1, default_chunk2]
        else:
        item_start_str = node.get_value(keys=[item, 'start'])
        item_end_str = node.get_value(keys=[item,'end'])
        #print("DEBUG:", item_start_str, item_end_str)
        if item_start_str:
            try:
                item_start = metomi.isodatetime.parsers.TimePointParser().parse(item_start_str)
            except:
                sys.stderr.write(f"WARNING: Could not parse ISO8601 start date {item_start_str}")
                item_start = None
        else:
            item_start = None
        if item_end_str:
            try:
                item_end = metomi.isodatetime.parsers.TimePointParser().parse(item_end_str)
            except:
                sys.stderr.write(f"WARNING: Could not parse ISO8601 end date {item_end_str}")
                item_end = None
        else:
            item_end = None
        if item_start and item_end:
            sys.stderr.write(f"NOTE: Using defined date range: {item_start} to {item_end}")

        # write the analysis script task(s), one for each chunk
        # each analysis script inherits from an analysis script family
        # and a scheduler family
        # the scheduler family looks like ANALYSIS-XXX, where XXX is a defined date request
        # that sets yr1 and inherits from ANALYSIS. ANALYSIS-CHUNK-A/B are in flow.cylc already
        added_a_chunk = 0
        for chunk in item_chunks:
            # in all cases, need to add in suitable in_data_dir corresponding to the PP output
            header = f"[[analysis-{item}-{chunk}]]"
            tail = """
        [[[environment]]]
            in_data_dir = {pp_dir}/{comp}/ts/{freq}/{chunk}
            """.format(chunk=chunk, comp=item_comps[0], freq=item_freq, pp_dir=pp_dir)

            # skip the chunk if it's not available as TS chunks
            if chunk != default_chunk1 and chunk != default_chunk2:
                sys.stderr.write(f"NOTE: Skipping chunk {chunk}\n")
                continue

            # 3 main cases: defined year range, cumulative, and every-chunk
            # defined year range
            if item_start and item_end:
                added_a_chunk = 1
                this_range = metomi.isodatetime.dumpers.TimePointDumper().strftime(item_start, '%Y%m%d') + '_' + metomi.isodatetime.dumpers.TimePointDumper().strftime(item_end, '%Y%m%d')
                sys.stderr.write(f"NOTE: Using defined year range for chunk {chunk}\n")
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
                sys.stderr.write(f"NOTE: Using cumulative for chunk {chunk}\n")
                results += """
    {header}
        inherit = ANALYSIS-CUMULATIVE-{chunk}-{date2}, analysis-{item}
        {tail}
                """.format(item=item, header=header, tail=tail, chunk=chunk, date2=metomi.isodatetime.dumpers.TimePointDumper().strftime(start_time, '%Y%m%d'))

            # every chunk
            else:
                added_a_chunk = 1
                sys.stderr.write(f"NOTE: Using regular chunks for chunk {chunk}\n")
                results += f"""
    {header}
        inherit = ANALYSIS-{chunk}, analysis-{item}
        {tail}
                sys.stderr.write(f"NOTE: Using cumulative for chunk {chunk}\n")

                # loop over the dates
                date = start
                while date <= stop:
                    date_str = metomi.isodatetime.dumpers.TimePointDumper().strftime(date, '%Y%m%d')
                    header = f"[[analysis-{item}-{chunk}-{date_str}]]"
                    date += chunk
                    results += f"""
    {header}
        inherit = ANALYSIS-CUMULATIVE-{chunk}-{date_str}, analysis-{item}
        {tail}
                """

            # every chunk
            else:
                added_a_chunk = 1
                sys.stderr.write(f"NOTE: Using regular chunks for chunk {chunk}\n")
                results += f"""
    {header}
        inherit = ANALYSIS-{chunk}, analysis-{item}
        {tail}
                """

        # chunk not available: skip with a message
        if not added_a_chunk:
            sys.stderr.write(f"NOTE: Skipping package '{item}' as it requests pp chunks not available")
            continue
        
        # write the analysis script family
        sys.stderr.write(f"NOTE: Adding analysis script task family for '{item}'\n")
        results += """
    [[analysis-{item}]]
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

        sys.stderr.write(f"NOTE: Ending processing of '{item}'\n\n")

    #print("DEBUG: returning", results)
    return(results)

#print(form_analysis_tasks('atmos', '/archive/Chris.Blanton/am5/2022.01/c96L33_am4p0_cmip6Diag/gfdl.ncrc4-intel21-prod-openmp/pp', '2000', 'P1Y', 'P4Y'))

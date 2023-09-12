import os
import re
import sys
import metomi.rose.config
import metomi.isodatetime.parsers
import metomi.isodatetime.dumpers
from legacy_date_conversions import *

def str_to_bool(val): 
    """Convert string true/false to boolean."""
    if val.lower().startswith("t") or val.lower().startswith("y"): 
        return True 
    elif val.lower().startswith("f") or val.lower().startswith("n"): 
        return False 
    raise Exception("invalid boolean value: {!r}".format(val))

def check_components(list1, list2):
    """Utility method to check pp component suitability.

    If each item in list1 is in list2, return True.
    If "all" is one of the items in list2, return True.
    Otherwise, return False.
    """
    if "all" in list2:
        return(True)
    else:
        for item in list1:
            if item not in list2:
                return(False)
    return(True)

def get_item_info(node, keys, pp_components, ana_start=None, ana_stop=None, print_stderr=False):
    """Utility method to retrieve config information about an analysis script.

    Accepts 3 arguments:
        node                    Rose ConfigNode object
        keys                    iterated structure of the node, as walked over with "walk"
        pp_components           PP components that the workflow is using

    If the name of the configuration item is "env" or "command", or
    if the keys includes more than the item name, return False.

    Otherwise, return this list of information about the analysis script:
        item, item_comps, item_script, item_freq, item_start, item_end, item_cumulative
    """
    # only target the keys
    if len(keys) != 1:
        return(False)

    # skip env and command keys
    item = keys[0]
    if item == "env" or item == "command":
        return(False)

    # consider adding analysis script to workflow
    # if not adding, write a note why
    #sys.stderr.write(f"DEBUG: Considering '{item}'\n")

    # skip this analysis script if pp component not requested
    item_comps = node.get_value(keys=[item, 'components']).split()
    if not check_components(item_comps, pp_components):
        if print_stderr:
            sys.stderr.write(f"ANALYSIS: {item}: Skipping as it requests component(s) not available ({item_comps})\n")
        return(False)

    # get the mandatory options: script path, frequency, and product (ts or av)
    item_script = os.path.basename(node.get_value(keys=[item, 'script']))
    assert item_script
    item_freq = node.get_value(keys=[item, 'freq'])
    assert item_freq
    item_product = node.get_value(keys=[item, 'product'])
    assert item_product
    #print(f"DEBUG: script '{item_script}' and frequency {item_freq}")

    # The first "word" of item_script will be the script, but there could be more command-line args.
    if " " in item_script:
        split = item_script.split()
        item_script_file = split.pop(0)
        item_script_extras = ' '.join(split)
    else:
        item_script_file = item_script
        item_script_extras = ""

    # Expand the script arguments if they are needed. cvdp at least includes $ANALYSIS_START
    if ana_start is not None:
        item_script_extras = item_script_extras.replace('$ANALYSIS_START', metomi.isodatetime.dumpers.TimePointDumper().strftime(ana_start, '%Y'))

    # get the optional start and stop
    item_start_str = node.get_value(keys=[item, 'start'])
    item_end_str = node.get_value(keys=[item,'end'])
    # expand $ANALYSIS_START and $ANALYSIS_STOP if they exist, replacing with ana_start and ana_stop
    if item_start_str:
        if item_start_str == '$ANALYSIS_START' and ana_start is not None:
            item_start = ana_start
        else:
            try:
                item_start = metomi.isodatetime.parsers.TimePointParser().parse(item_start_str)
            except:
                if print_stderr:
                    sys.stderr.write(f"ANALYSIS: WARNING: Skipping '{item}' as the start date '{item_start_str}' is invalid\n")
                return(False)
    else:
        item_start = None
    if item_end_str:
        if item_end_str == '$ANALYSIS_STOP' and ana_stop is not None:
            item_end = ana_stop
        else:
            try:
                item_end = metomi.isodatetime.parsers.TimePointParser().parse(item_end_str)
            except:
                sys.stderr.write(f"ANALYSIS: WARNING: Skipping '{item}' as the stop date '{item_end_str}' is invalid\n")
                return(False)
    else:
        item_end = None
    #if item_start and item_end:
        #sys.stderr.write(f"DEBUG: {item}: defined date range: {item_start} to {item_end}\n")

    # get the optional cumulative option
    item_cumulative = node.get_value(keys=[item, 'cumulative'])
    if item_cumulative:
        item_cumulative = str_to_bool(item_cumulative)
    else:
        item_cumulative = False
    #print("DEBUG: Start, end, cumulative:", item_start_str, item_end_str, item_cumulative)

    return(item, item_comps, item_script_file, item_script_extras, item_freq, item_start, item_end, item_cumulative, item_product)

def get_cumulative_info(node, pp_components, pp_dir, chunk, start, stop, analysis_only=False, print_stderr=False):
    """Return the task definitions and task graph for all cumulative-mode analysis scripts.

    Accepts 7 arguments:
        node                    Rose ConfigNode object
        pp_components           PP components that the workflow is using
        pp_dir                  PP directory to be used for setting in_data_dir template variable
        chunk                   ISO8601 duration used by the workflow
        start                   date object of the beginning of PP
        stop                    date object of the end of PP
        analysis_only           optional boolean to indicate no pre-requisites needed
    """
    defs = ""
    graph = ""

    for keys, sub_node in node.walk():
        # retrieve information about the script
        item_info = get_item_info(node, keys, pp_components)
        if item_info:
            item, item_comps, item_script_file, item_script_extras, item_freq, item_start, item_end, item_cumulative, item_product = item_info
        else:
            continue

        # skip if the analysis type (interval, cumulative, defined) isn't what we're looking for
        if item_start and item_end:
            #sys.stderr.write(f"DEBUG: Skipping {item} as it is defined interval\n")
            continue
        elif item_cumulative:
            start_str = metomi.isodatetime.dumpers.TimePointDumper().strftime(start, '%Y')
            if print_stderr:
                sys.stderr.write(f"ANALYSIS: {item}: Will run from {start_str} to current available (cumulative mode)\n")
        else:
            #sys.stderr.write(f"DEBUG: Skipping {item} as it is every chunk\n")
            continue

        bronx_freq = convert_iso_duration_to_bronx_freq(item_freq)
        bronx_chunk = convert_iso_duration_to_bronx_chunk(chunk)

        # ts and av distinction
        if item_product == "ts":
            in_data_dir = f"{pp_dir}/{item_comps[0]}/ts/{bronx_freq}/{bronx_chunk}"
        else:
            in_data_dir = f"{pp_dir}/{item_comps[0]}/av/{bronx_freq}_{bronx_chunk}"

        # add the analysis script details that don't depend on time
        defs += f"""
    [[analysis-{item}]]
        script = '''
            chmod +x $CYLC_WORKFLOW_SHARE_DIR/analysis-scripts/{item_script_file}.$yr1-$yr2
            $CYLC_WORKFLOW_SHARE_DIR/analysis-scripts/{item_script_file}.$yr1-$yr2 {item_script_extras}
        '''
        [[[environment]]]
            in_data_dir = {in_data_dir}
            freq = {item_freq}
            staticfile = {pp_dir}/{item_comps[0]}/{item_comps[0]}.static.nc
            scriptLabel = {item}
            datachunk = {chunk.years}
        """

        # loop over the dates
        oneyear = metomi.isodatetime.parsers.DurationParser().parse('P1Y')
        date = start + chunk - oneyear
        #print(f"DEBUG: start {start} and stop {stop}")
        while date <= stop:
            date_str = metomi.isodatetime.dumpers.TimePointDumper().strftime(date, '%Y')

            # add the task definition for each ending time
            defs += f"""
    [[analysis-{item}-{date_str}]]
        inherit = ANALYSIS-CUMULATIVE-{date_str}, analysis-{item}
            """

            # add the task definition family for each ending time
            defs += f"""
    [[ANALYSIS-CUMULATIVE-{date_str}]]
        inherit = ANALYSIS
        [[[environment]]]
            yr1 = {metomi.isodatetime.dumpers.TimePointDumper().strftime(start, '%Y')}
            yr2 = {metomi.isodatetime.dumpers.TimePointDumper().strftime(date, '%Y')}
            """

            date += chunk

        # now set the task graphs
        date = start + chunk - oneyear
        while date <= stop:
            graph += f"        R1/{metomi.isodatetime.dumpers.TimePointDumper().strftime(date, '%Y-%m-%dT00:00:00Z')} = \"\"\"\n"
            if not analysis_only:
                graph += f"            REMAP-PP-COMPONENTS-{chunk}:succeed-all\n"
            d = date
            i = -1
            while d > start + chunk:
                if not analysis_only:
                    graph += f"            & REMAP-PP-COMPONENTS-{chunk}[{i*chunk}]:succeed-all\n"
                i -= 1
                d -= chunk
            if analysis_only:
                graph += f"            ANALYSIS-CUMULATIVE-{metomi.isodatetime.dumpers.TimePointDumper().strftime(date, '%Y')}\n"
            else:
                graph += f"            => ANALYSIS-CUMULATIVE-{metomi.isodatetime.dumpers.TimePointDumper().strftime(date, '%Y')}\n"
            graph += f"        \"\"\"\n"
            date += chunk

    return(defs, graph)

def get_per_interval_info(node, pp_components, pp_dir, chunk, analysis_only=False, print_stderr=False):
    """Return the task definitions and task graph for all every-interval-mode analysis scripts.

    Accepts 5 arguments:
        node                    Rose ConfigNode object
        pp_components           PP components that the workflow is using
        pp_dir                  PP directory to be used for setting in_data_dir template variable
        chunk                   ISO8601 duration used by the workflow
        analysis_only           optional boolean to indicate no pre-requisites needed
        print_stderr            print analysis script information
    """
    defs = ""
    graph = ""
    oneyear = metomi.isodatetime.parsers.DurationParser().parse('P1Y')

    for keys, sub_node in node.walk():
        # retrieve information about the script
        item_info = get_item_info(node, keys, pp_components)
        if item_info:
            item, item_comps, item_script_file, item_script_extras, item_freq, item_start, item_end, item_cumulative, item_product = item_info
        else:
            continue

        # skip if the analysis type (interval, cumulative, defined) isn't what we're looking for
        if item_start and item_end:
            #sys.stderr.write(f"DEBUG: Skipping {item} as it is defined interval\n")
            continue
        elif item_cumulative:
            #sys.stderr.write(f"DEBUG: Skipping {item} as it is cumulative\n")
            continue
        else:
            if print_stderr:
                sys.stderr.write(f"ANALYSIS: {item}: Will run every chunk {chunk}\n")

        # add the task definitions
        bronx_freq = convert_iso_duration_to_bronx_freq(item_freq)
        bronx_chunk = convert_iso_duration_to_bronx_chunk(chunk)
        defs += f"""
    [[analysis-{item}]]
        inherit = ANALYSIS-{chunk}
        script = '''
            chmod +x $CYLC_WORKFLOW_SHARE_DIR/analysis-scripts/{item_script_file}.$yr1-$yr2
            $CYLC_WORKFLOW_SHARE_DIR/analysis-scripts/{item_script_file}.$yr1-$yr2 {item_script_extras}
        '''
        [[[environment]]]
            in_data_dir = {pp_dir}/{item_comps[0]}/ts/{bronx_freq}/{bronx_chunk}
            freq = {item_freq}
            staticfile = {pp_dir}/{item_comps[0]}/{item_comps[0]}.static.nc
            scriptLabel = {item}
    [[ANALYSIS-{chunk}]]
        inherit = ANALYSIS
        [[[environment]]]
            yr1 = $(cylc cycle-point --template=CCYY --offset=-{chunk - oneyear})
            datachunk = {chunk.years}
        """

        # now add the task graphs
        graph += f"        +{chunk - oneyear}/{chunk} = \"\"\"\n"
        if analysis_only:
            graph += f"            ANALYSIS-{chunk}\n"
        else:
            graph += f"            REMAP-PP-COMPONENTS-{chunk}:succeed-all => ANALYSIS-{chunk}\n"
        graph += f"        \"\"\"\n"

        #sys.stderr.write(f"DEBUG: Ending processing of '{item}'\n")

    return(defs, graph)

def get_defined_interval_info(node, pp_components, pp_dir, chunk, pp_start, pp_stop, ana_start, ana_stop, analysis_only=False, print_stderr=False):
    """Return the task definitions and task graph for all user-defined range analysis scripts.

    Accepts 7 arguments:
        node                    Rose ConfigNode object
        pp_components           PP components that the workflow is using
        pp_dir                  PP directory to be used for setting in_data_dir template variable
        chunk                   ISO8601 duration used by the workflow
        start                   date object of the beginning of PP
        stop                    date object of the end of PP
        analysis_only           optional boolean to indicate no pre-requisites needed
        print_stderr            print analysis script information to screen
    """
    defs = ""
    graph = ""

    for keys, sub_node in node.walk():
        # retrieve information about the script
        item_info = get_item_info(node, keys, pp_components, ana_start, ana_stop, print_stderr)
        if item_info:
            item, item_comps, item_script_file, item_script_extras, item_freq, item_start, item_end, item_cumulative, item_product = item_info
        else:
            continue

        # skip if the analysis type (interval, cumulative, defined) isn't what we're looking for
        if item_start and item_end:
            pass
        elif item_cumulative:
            #sys.stderr.write(f"DEBUG: Skipping {item} as it is cumulative\n")
            continue
        else:
            #sys.stderr.write(f"DEBUG: Skipping {item} as it is every chunk\n")
            continue

        # if requested year range is outside the workflow range, then skip
        item_start_str = metomi.isodatetime.dumpers.TimePointDumper().strftime(item_start, '%Y')
        item_end_str = metomi.isodatetime.dumpers.TimePointDumper().strftime(item_end, '%Y')
        start_str = metomi.isodatetime.dumpers.TimePointDumper().strftime(pp_start, '%Y')
        stop_str = metomi.isodatetime.dumpers.TimePointDumper().strftime(pp_stop, '%Y')
        if item_start < pp_start or item_end > pp_stop:
            if print_stderr:
                sys.stderr.write(f"ANALYSIS: {item}: Defined-interval ({item_start_str}-{item_end_str}) outside workflow range ({start_str}-{stop_str}), skipping\n")
            continue

        # locate the nearest enclosing chunks
        d1 = pp_start
        while d1 <= item_start - chunk:
            d1 += chunk
        d2 = pp_stop
        while d2 >= item_end + chunk:
            d2 -= chunk
        d1_str = metomi.isodatetime.dumpers.TimePointDumper().strftime(d1, '%Y')
        d2_str = metomi.isodatetime.dumpers.TimePointDumper().strftime(d2, '%Y')
        if print_stderr:
            sys.stderr.write(f"ANALYSIS: {item}: Will run once for time period {item_start_str} to {item_end_str} (chunks {d1_str} to {d2_str})\n")

        # set the task definitions`
        bronx_freq = convert_iso_duration_to_bronx_freq(item_freq)
        bronx_chunk = convert_iso_duration_to_bronx_chunk(chunk)
        defs += f"""
    [[analysis-{item}]]
        inherit = ANALYSIS-{item_start_str}_{item_end_str}
        script = '''
            chmod +x $CYLC_WORKFLOW_SHARE_DIR/analysis-scripts/{item_script_file}.$yr1-$yr2
            $CYLC_WORKFLOW_SHARE_DIR/analysis-scripts/{item_script_file}.$yr1-$yr2 {item_script_extras}
        '''
        [[[environment]]]
            in_data_dir = {pp_dir}/{item_comps[0]}/ts/{bronx_freq}/{bronx_chunk}
            freq = {item_freq}
            staticfile = {pp_dir}/{item_comps[0]}/{item_comps[0]}.static.nc
            scriptLabel = {item}
            datachunk = {chunk.years}
    [[ANALYSIS-{item_start_str}_{item_end_str}]]
        inherit = ANALYSIS
        [[[environment]]]
            yr1 = {item_start_str}
            yr2 = {item_end_str}
        """

        # set the graph definitions
        oneyear = metomi.isodatetime.parsers.DurationParser().parse('P1Y')
        graph += f"        R1/{metomi.isodatetime.dumpers.TimePointDumper().strftime(d2, '%Y-%m-%dT00:00:00Z')} = \"\"\"\n"
        if not analysis_only:
            graph += f"            REMAP-PP-COMPONENTS-{chunk}:succeed-all\n"
        d = d2
        i = -1
        while d > pp_start + chunk:
            if not analysis_only:
                graph += f"            & REMAP-PP-COMPONENTS-{chunk}[{i*chunk}]:succeed-all\n"
            i -= 1
            d -= chunk
        if analysis_only:
            graph += f"            ANALYSIS-{item_start_str}_{item_end_str}\n"
        else:
            graph += f"            => ANALYSIS-{item_start_str}_{item_end_str}\n"
        graph += f"        \"\"\"\n"

    return(defs, graph)

def get_analysis_info(info_type, pp_components_str, pp_dir, pp_start_str, pp_stop_str, ana_start_str, ana_stop_str, chunk, analysis_only=False, print_stderr=False):
    """Return requested analysis-related information from app/analysis/rose-app.conf

    Accepts 7 arguments:
        info_type: one of these types
            per-interval-task-definitions           Returns task environments for every-chunk analysis scripts
            per-interval-task-graph                 Returns task graph for every-chunk analysis scripts
            cumulative-task-definitions             Returns task environments for cumulative-mode analysis scripts
            cumulative-task-graph                   Returns task graph for cumulative-mode analysis scripts
            defined-task-definitions                Returns task environments for user-defined year range analysis scripts
            defined-task-graph                      Returns task graph for user-defined year range analysis scripts
        pp_components_str (str): all, or a space-separated list
                                 analysis scripts depending on others will be skipped
        pp_dir (str): absolute filepath root (up to component, not including)
        start_str (str): will use at yr1 if cumulative mode on
        stop_str (str): last cycle point to process
        chunk (str): chunk to use for task graphs at least
        analysis_only (bool): make task graphs not depend on REMAP-PP-COMPONENTS
        print_stderr (bool): print a summary of analysis scripts that would be run
"""
    # convert strings to date objects
    #sys.stderr.write(f"DEBUG: {pp_start_str} to {pp_stop_str}, and chunk {chunk}, and {ana_start_str} to {ana_stop_str}\n")
    pp_start = metomi.isodatetime.parsers.TimePointParser(assumed_time_zone=(0,0)).parse(pp_start_str)
    pp_stop = metomi.isodatetime.parsers.TimePointParser(assumed_time_zone=(0,0)).parse(pp_stop_str)
    chunk = metomi.isodatetime.parsers.DurationParser().parse(chunk)
    ana_start = metomi.isodatetime.parsers.TimePointParser(assumed_time_zone=(0,0)).parse(ana_start_str)
    ana_stop = metomi.isodatetime.parsers.TimePointParser(assumed_time_zone=(0,0)).parse(ana_stop_str)
    #sys.stderr.write(f"DEBUG: {pp_start} to {pp_stop}, and chunk {chunk}, and {ana_start} to {ana_stop}\n")

    # split the pp_components into a list
    pp_components = pp_components_str.split()

    # locate the analysis Rose configuration
    path_to_conf = os.path.dirname(os.path.abspath(__file__)) + '/../app/analysis/rose-app.conf'
    node = metomi.rose.config.load(path_to_conf)

    # return the requested information
    if info_type == 'per-interval-task-definitions':
        #sys.stderr.write(f"DEBUG: Will return per-interval task definitions only\n")
        return(get_per_interval_info(node, pp_components, pp_dir, chunk, analysis_only, print_stderr)[0])
    elif info_type == 'per-interval-task-graph':
        #sys.stderr.write(f"DEBUG: Will return per-interval task graph only\n")
        return(get_per_interval_info(node, pp_components, pp_dir, chunk, analysis_only, False)[1])
    elif info_type == 'cumulative-task-graph':
        #sys.stderr.write(f"DEBUG: Will return cumulative task graph only\n")
        return(get_cumulative_info(node, pp_components, pp_dir, chunk, pp_start, pp_stop, analysis_only, print_stderr)[1])
    elif info_type == 'cumulative-task-definitions':
        #sys.stderr.write(f"DEBUG: Will return cumulative task definitions only\n")
        return(get_cumulative_info(node, pp_components, pp_dir, chunk, pp_start, pp_stop, analysis_only, print_stderr)[0])
    elif info_type == 'defined-interval-task-graph':
        #sys.stderr.write(f"DEBUG: Will return defined-interval task graph only\n")
        return(get_defined_interval_info(node, pp_components, pp_dir, chunk, pp_start, pp_stop, ana_start, ana_stop, analysis_only, print_stderr)[1])
    elif info_type == 'defined-interval-task-definitions':
        #sys.stderr.write(f"DEBUG: Will return defined-interval task definitions only\n")
        return(get_defined_interval_info(node, pp_components, pp_dir, chunk, pp_start, pp_stop, ana_start, ana_stop, analysis_only, print_stderr)[0])
    else:
        raise Exception(f"Invalid information type: {info_type}")

# for interactive debugging use below
#print(get_analysis_info('per-interval-task-definitions', 'all', '/archive/Chris.Blanton/am5/2022.01/c96L33_am4p0_cmip6Diag/gfdl.ncrc4-intel21-prod-openmp/pp', '1979', '1988', 'P2Y'))
#print(get_analysis_info('per-interval-task-graph', 'all', '/archive/Chris.Blanton/am5/2022.01/c96L33_am4p0_cmip6Diag/gfdl.ncrc4-intel21-prod-openmp/pp', '1979', '1988', 'P3Y', True))
#print(get_analysis_info('cumulative-task-definitions', 'all', '/archive/Chris.Blanton/am5/2022.01/c96L33_am4p0_cmip6Diag/gfdl.ncrc4-intel21-prod-openmp/pp', '1979', '1988', 'P2Y'))
#print(get_analysis_info('cumulative-task-graph', 'all', '/archive/Chris.Blanton/am5/2022.01/c96L33_am4p0_cmip6Diag/gfdl.ncrc4-intel21-prod-openmp/pp', '1979', '1988', 'P2Y', False))
#print(get_analysis_info('defined-interval-task-definitions', 'all', '/archive/Chris.Blanton/am5/2022.01/c96L33_am4p0_cmip6Diag/gfdl.ncrc4-intel21-prod-openmp/pp', '1979', '2020', 'P6Y', False))
#print(get_analysis_info('defined-interval-task-graph', 'all', '/archive/Chris.Blanton/am5/2022.01/c96L33_am4p0_cmip6Diag/gfdl.ncrc4-intel21-prod-openmp/pp', '1979', '2020', 'P12Y', True))

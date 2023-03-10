import os
import re
import sys
import metomi.rose.config
import metomi.isodatetime.parsers
import metomi.isodatetime.dumpers

def str_to_bool(val): 
    """Convert string true/false to boolean"""
    if val.lower().startswith("t") or val.lower().startswith("y"): 
        return True 
    elif val.lower().startswith("f") or val.lower().startswith("n"): 
        return False 
    raise Exception("invalid boolean value: {!r}".format(val))

def check_components(item_comps, pp_components):
    if "all" in pp_components:
        return(True)
    else:
        for comp in item_comps:
            if comp not in pp_components:
                return(False)

def get_item_info(node, keys, pp_components):
    # only target the keys
    if len(keys) != 1:
        return(False)

    # skip env and command keys
    item = keys[0]
    if item == "env" or item == "command":
        return(False)

    # consider adding analysis script to workflow
    # if not adding, write a note why
    sys.stderr.write(f"DEBUG: Considering '{item}'\n")

    # skip this analysis script if pp component not requested
    item_comps = node.get_value(keys=[item, 'components']).split()
    if not check_components(item_comps, pp_components):
        sys.stderr.write(f"DEBUG: Skipping '{item}' as it requests a component not available: '{comp}'\n")
        return(False)

    # get the mandatory options: script path and frequency
    item_script = os.path.basename(node.get_value(keys=[item, 'script']))
    assert item_script
    item_freq = node.get_value(keys=[item, 'freq'])
    assert item_freq
    print(f"DEBUG: script '{item_script}' and frequency {item_freq}")

    # get the optional start and stop
    item_start_str = node.get_value(keys=[item, 'start'])
    item_end_str = node.get_value(keys=[item,'end'])
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
        sys.stderr.write(f"DEBUG: {item}: defined date range: {item_start} to {item_end}\n")

    # get the optional cumulative option
    item_cumulative = node.get_value(keys=[item, 'cumulative'])
    if item_cumulative:
        item_cumulative = str_to_bool(item_cumulative)
    else:
        item_cumulative = False
    print("DEBUG: Start, end, cumulative:", item_start_str, item_end_str, item_cumulative)

    return(item, item_comps, item_script, item_freq, item_start, item_end, item_cumulative)

def get_cumulative_definitions(node, pp_components, pp_dir, chunk, start, stop):
    """
    loop over the analysis scripts listed in the config file
    build up the task graph or task definition results multiline string that will be returned
    """
    results = ""

    for keys, sub_node in node.walk():
        # retrieve information about the script
        item_info = get_item_info(node, keys, pp_components)
        if item_info:
            item, item_comps, item_script, item_freq, item_start, item_end, item_cumulative = item_info
        else:
            continue

        # skip if the analysis type (interval, cumulative, defined) isn't what we're looking for
        if item_start and item_end:
            sys.stderr.write(f"DEBUG: Skipping {item} as it is defined interval")
            continue
        elif item_cumulative:
            sys.stderr.write(f"ANALYSIS: {item}: Will run from {start} (cumulative)\n")
        else:
            sys.stderr.write(f"DEBUG: Skipping {item} as it is every chunk\n")
            continue

        # add the analysis script details that don't depend on time
        results += f"""
    [[analysis-{item}]]
        script = '''
            chmod +x $CYLC_WORKFLOW_SHARE_DIR/analysis-scripts/{item_script}.$yr1-$yr2
            $CYLC_WORKFLOW_SHARE_DIR/analysis-scripts/{item_script}.$yr1-$yr2
        '''
        [[[environment]]]
            in_data_dir = {pp_dir}/{item_comps[0]}/ts/{item_freq}/{chunk}
            component = {item_comps[0]}
            freq = {item_freq}
            staticfile = {pp_dir}/{item_comps[0]}/{item_comps[0]}.static.nc
            scriptLabel = {item}
            datachunk = {chunk.years}
        """

        # loop over the dates
        oneyear = metomi.isodatetime.parsers.DurationParser().parse('P1Y')
        date = start + chunk - oneyear
        print(f"DEBUG: start {start} and stop {stop}")
        while date <= stop:
            date_str = metomi.isodatetime.dumpers.TimePointDumper().strftime(date, '%Y')

            # add the task definition for each ending time
            results += f"""
    [[analysis-{item}-{date_str}]]
        inherit = ANALYSIS-CUMULATIVE-{date_str}, analysis-{item}
            """

            # add the task definition family for each ending time
            results += f"""
    [[ANALYSIS-CUMULATIVE-{date_str}]]
        inherit = ANALYSIS
        [[[environment]]]
            yr1 = {metomi.isodatetime.dumpers.TimePointDumper().strftime(start, '%Y')}
            yr2 = {metomi.isodatetime.dumpers.TimePointDumper().strftime(date, '%Y')}
            """

            date += chunk

    return(results)

def get_cumulative_graph(node, pp_components, pp_dir, chunk, start, stop, analysis_only):
    """
    loop over the analysis scripts listed in the config file
    build up the task graph or task definition results multiline string that will be returned
    """
    results = ""

    for keys, sub_node in node.walk():
        # retrieve information about the script
        item_info = get_item_info(node, keys, pp_components)
        if item_info:
            item, item_comps, item_script, item_freq, item_start, item_end, item_cumulative = item_info
        else:
            continue

        # skip if the analysis type (interval, cumulative, defined) isn't what we're looking for
        if item_start and item_end:
            sys.stderr.write(f"DEBUG: Skipping {item} as it is defined interval")
            continue
        elif item_cumulative:
            sys.stderr.write(f"ANALYSIS: {item}: Will run from {start} (cumulative)\n")
        else:
            sys.stderr.write(f"DEBUG: Skipping {item} as it is every chunk\n")
            continue

        # loop over the dates
        oneyear = metomi.isodatetime.parsers.DurationParser().parse('P1Y')
        date = start + chunk - oneyear
        while date <= stop:
            results += f"        R1/{metomi.isodatetime.dumpers.TimePointDumper().strftime(date, '%Y-%m-%dT00:00:00Z')} = \"\"\"\n"
            if not analysis_only:
                results += f"            REMAP-PP-COMPONENTS-{chunk}:succeed-all\n"
            d = date
            i = -1
            while d > start + chunk:
                if not analysis_only:
                    results += f"            & REMAP-PP-COMPONENTS-{chunk}[{i*chunk}]:succeed-all\n"
                i -= 1
                d -= chunk
            if analysis_only:
                results += f"            ANALYSIS-CUMULATIVE-{chunk}-{metomi.isodatetime.dumpers.TimePointDumper().strftime(date, '%Y')}\n"
            else:
                results += f"            => ANALYSIS-CUMULATIVE-{chunk}-{metomi.isodatetime.dumpers.TimePointDumper().strftime(date, '%Y')}\n"
            results += f"        \"\"\"\n"
            date += chunk

    return(results)

def get_interval_definitions(node, pp_components, pp_dir, chunk):
    """
    loop over the analysis scripts listed in the config file
    build up the task graph or task definition results multiline string that will be returned
    """
    results = ""

    for keys, sub_node in node.walk():
        # retrieve information about the script
        item_info = get_item_info(node, keys, pp_components)
        if item_info:
            item, item_comps, item_script, item_freq, item_start, item_end, item_cumulative = item_info
        else:
            continue

        # skip if the analysis type (interval, cumulative, defined) isn't what we're looking for
        if item_start and item_end:
            sys.stderr.write(f"DEBUG: Skipping {item} as it is defined interval")
            continue
        elif item_cumulative:
            sys.stderr.write(f"DEBUG: Skipping {item} as it is cumulative")
            continue
        else:
            sys.stderr.write(f"ANALYSIS: {item}: Will run every chunk {chunk}\n")

        # add the stuff
        results += f"""
    [[analysis-{item}]]
        inherit = ANALYSIS-{chunk}
        script = '''
            chmod +x $CYLC_WORKFLOW_SHARE_DIR/analysis-scripts/{item_script}.$yr1-$yr2
            $CYLC_WORKFLOW_SHARE_DIR/analysis-scripts/{item_script}.$yr1-$yr2
        '''
        [[[environment]]]
            in_data_dir = {pp_dir}/{item_comps[0]}/ts/{item_freq}/{chunk}
            component = {item_comps[0]}
            freq = {item_freq}
            staticfile = {pp_dir}/{item_comps[0]}/{item_comps[0]}.static.nc
            scriptLabel = {item}
        """

        sys.stderr.write(f"NOTE: Ending processing of '{item}'\n")

    return(results)

def get_analysis_info(info_type, pp_components_str, pp_dir, start_str, stop_str, chunk, analysis_only=False):
    """Return analysis-related information from app/analysis/rose-app.conf

    Arguments:
        info_type:
            are-there-per-interval-tasks            Returns true or false
            per-interval-task-definitions           Returns task environments for per-interval tasks
            cumulative-task-graph                   Returns task graph for cumulative tasks
            cumulative-task-definitions             Returns task environments for cumulaive tasks
            defined-task-graph                      Returns task graph for defined-interval tasks
            defined-task-definitions                REturns task environments for defined-interval tasks
        pp_components_str (str): all, or a space-separated list
                            analysis scripts depending on others will be skipped
        pp_dir (str): absolute filepath root (up to component, not including)
        start_str (str): will use at yr1 if cumulative mode on
        stop_str (str): last cycle point to process
        chunk (str): chunk to use for task graphs at least
        analysis_only (bool): make task graphs not depend on REMAP-PP-COMPONENTS

        # retrieve the needed information, one of
        #   per-interval-task-definitions
        #       Includes analysis script family and the tasks. Scheduler family is in flow.cylc
        #   cumulative-task-graph
        #       Write related task graph strings for cumulative tasks
        #   cumulative-task-definitions
        #       Includes analysis script family, scheduler family, and the tasks
        #   are-there-per-interval-tasks
        #       Returns True or False if 'per-interval-task-definitions' is non-empty or empty
"""
    # convert strings to date objects
    start = metomi.isodatetime.parsers.TimePointParser().parse(start_str)
    stop = metomi.isodatetime.parsers.TimePointParser().parse(stop_str)
    chunk = metomi.isodatetime.parsers.DurationParser().parse(chunk)
    sys.stderr.write(f"DEBUG: {start} to {stop}, and chunk {chunk}\n")

    # split the pp_components into a list
    pp_components = pp_components_str.split()

    # locate the analysis Rose configuration
    path_to_conf = os.path.dirname(os.path.abspath(__file__)) + '/../app/analysis/rose-app.conf'
    node = metomi.rose.config.load(path_to_conf)

    # return the requested information
    if info_type == 'per-interval-task-definitions':
        sys.stderr.write(f"ANALYSIS: Will return per-interval task definitions only\n")
        return(get_interval_definitions(node, pp_components, pp_dir, chunk))
    elif info_type == 'are-there-per-interval-tasks':
        sys.stderr.write(f"ANALYSIS: Will check if there are per-interval tasks and return True or False\n")
        return(bool(get_interval_definitions(node, pp_components, pp_dir, chunk)))
    elif info_type == 'cumulative-task-graph':
        sys.stderr.write(f"ANALYSIS: Will return cumulative task graph only\n")
        return(get_cumulative_graph(node, pp_components, pp_dir, chunk, start, stop, analysis_only))
    elif info_type == 'cumulative-task-definitions':
        sys.stderr.write(f"ANALYSIS: Will return cumulative task definitions only\n")
        return(get_cumulative_definitions(node, pp_components, pp_dir, chunk, start, stop))
    elif info_type == 'defined-interval-task-graph':
        sys.stderr.write(f"ANALYSIS: Will return defined-interval task graph only\n")
    elif info_type == 'defined-interval-task-definitions':
        sys.stderr.write(f"ANALYSIS: Will return defined-interval task definitions only\n")
    else:
        raise Exception(f"Invalid information type: {info_type}")

#print(get_analysis_info('per-interval-task-definitions', 'all', '/archive/Chris.Blanton/am5/2022.01/c96L33_am4p0_cmip6Diag/gfdl.ncrc4-intel21-prod-openmp/pp', '1979', '1988', 'P2Y'))
#print(get_analysis_info('are-there-per-interval-tasks', 'all', '/archive/Chris.Blanton/am5/2022.01/c96L33_am4p0_cmip6Diag/gfdl.ncrc4-intel21-prod-openmp/pp', '1979', '1988', 'P2Y'))
#print(get_analysis_info('cumulative-task-definitions', 'all', '/archive/Chris.Blanton/am5/2022.01/c96L33_am4p0_cmip6Diag/gfdl.ncrc4-intel21-prod-openmp/pp', '1979', '1988', 'P2Y'))

#print(get_analysis_info('cumulative-task-graph', 'all', '/archive/Chris.Blanton/am5/2022.01/c96L33_am4p0_cmip6Diag/gfdl.ncrc4-intel21-prod-openmp/pp', '1979', '1988', 'P2Y', True))
#print(get_analysis_info('cumulative-task-graph', 'all', '/archive/Chris.Blanton/am5/2022.01/c96L33_am4p0_cmip6Diag/gfdl.ncrc4-intel21-prod-openmp/pp', '1979', '1988', 'P2Y', False))

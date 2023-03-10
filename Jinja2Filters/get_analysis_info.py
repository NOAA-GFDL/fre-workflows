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

    # check which information is requested
    if info_type == 'are-there-per-interval-tasks':
        sys.stderr.write(f"ANALYSIS: Will check if there are per-interval tasks and return True or False\n")
    elif info_type == 'per-interval-task-definitions':
        sys.stderr.write(f"ANALYSIS: Will return per-interval task definitions only\n")
    elif info_type == 'cumulative-task-graph':
        sys.stderr.write(f"ANALYSIS: Will return cumulative task graph only\n")
    elif info_type == 'cumulative-task-definitions':
        sys.stderr.write(f"ANALYSIS: Will return cumulative task definitions only\n")
    elif info_type == 'defined-interval-task-graph':
        sys.stderr.write(f"ANALYSIS: Will return defined-interval task graph only\n")
    elif info_type == 'defined-interval-task-definitions':
        sys.stderr.write(f"ANALYSIS: Will return defined-interval task definitions only\n")
    else:
        raise Exception(f"Invalid information type: {info_type}")
    sys.stderr.write(f"\n")

    # build up the task graph and task definition results multiline string that will be returned
    results_interval_definition = ""
    results_cumulative_definition = ""
    results_cumulative_graph = ""
    results_defined_definition = ""
    results_defined_graph = ""

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
        sys.stderr.write(f"DEBUG: Considering '{item}'\n")

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
            sys.stderr.write(f"ANALYSIS: {item}: defined date range: {item_start} to {item_end}\n")

        # get the optional cumulative option
        item_cumulative = node.get_value(keys=[item, 'cumulative'])
        if item_cumulative:
            item_cumulative = str_to_bool(item_cumulative)
        else:
            item_cumulative = False
        print("DEBUG: Start, end, cumulative:", item_start_str, item_end_str, item_cumulative)

        # retrieve the needed information, one of
        #   per-interval-task-definitions
        #       Includes analysis script family and the tasks. Scheduler family is in flow.cylc
        #   cumulative-task-graph
        #       Write related task graph strings for cumulative tasks
        #   cumulative-task-definitions
        #       Includes analysis script family, scheduler family, and the tasks
        #   are-there-per-interval-tasks
        #       Returns True or False if 'per-interval-task-definitions' is non-empty or empty

        # set added_a_task variable if a task definition is used.
        # if so, the analysis script task family will be created later also
        added_a_task = 0

        # in all cases, need to add in suitable in_data_dir corresponding to the PP output
        header = f"[[analysis-{item}-{chunk}]]"
        tail = """
        [[[environment]]]
            in_data_dir = {pp_dir}/{comp}/ts/{freq}/{chunk}
        """.format(chunk=chunk, comp=item_comps[0], freq=item_freq, pp_dir=pp_dir)

        # cumulative
        if item_cumulative:
            sys.stderr.write(f"NOTE: Using cumulative mode\n")

        elif item_start and item_end:
            sys.stderr.write(f"NOTE: Using defined interval\n")

        # every chunk
        else:
            added_a_task = 1
            sys.stderr.write(f"NOTE: Using every interval\n")
            results_interval_definition += f"""
    {header}
        inherit = ANALYSIS-{chunk}, analysis-{item}
        {tail}
            """

        # if cumulative, add the scheduler family
        # loop over the dates
        if item_cumulative:
            oneyear = metomi.isodatetime.parsers.DurationParser().parse('P1Y')
            date = start + chunk - oneyear
            #print(f"DEBUG: start {start} and stop {stop}")
            while date <= stop:
                date_str = metomi.isodatetime.dumpers.TimePointDumper().strftime(date, '%Y')

                # add the task definition
                header = f"[[analysis-{item}-{chunk}-{date_str}]]"
                added_a_task = 1
                results_cumulative_definition += f"""
    {header}
        inherit = ANALYSIS-CUMULATIVE-{chunk}-{date_str}, analysis-{item}
        {tail}
                    """

                # add the scheduler family
                results_cumulative_definition += f"""
    [[ANALYSIS-CUMULATIVE-{chunk}-{date_str}]]
        inherit = ANALYSIS
        [[[environment]]]
            yr1 = {metomi.isodatetime.dumpers.TimePointDumper().strftime(start, '%Y')}
            yr2 = {metomi.isodatetime.dumpers.TimePointDumper().strftime(date, '%Y')}
            datachunk = {chunk.years}
                    """

                # finally add the task graph
                #print("ok date is", date)
                results_cumulative_graph += f"        R1/{metomi.isodatetime.dumpers.TimePointDumper().strftime(date, '%Y-%m-%dT00:00:00Z')} = \"\"\"\n"
                if not analysis_only:
                    results_cumulative_graph += f"            REMAP-PP-COMPONENTS-{chunk}:succeed-all\n"
                d = date
                i = -1
                while d > start + chunk:
                    if not analysis_only:
                        results_cumulative_graph += f"            & REMAP-PP-COMPONENTS-{chunk}[{i*chunk}]:succeed-all\n"
                    i -= 1
                    d -= chunk
                if analysis_only:
                    results_cumulative_graph += f"            ANALYSIS-CUMULATIVE-{chunk}-{metomi.isodatetime.dumpers.TimePointDumper().strftime(date, '%Y')}\n"
                else:
                    results_cumulative_graph += f"            => ANALYSIS-CUMULATIVE-{chunk}-{metomi.isodatetime.dumpers.TimePointDumper().strftime(date, '%Y')}\n"
                results_cumulative_graph += f"        \"\"\"\n"

                date += chunk
                #print("now date is", date)
                #print(f"is {date} less than or equal to {stop}")

        # write the analysis script family
        if added_a_task:
            analysis_family = """
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
        if item_cumulative:
            results_cumulative_definition += analysis_family
        else:
            results_interval_definition += analysis_family

        sys.stderr.write(f"NOTE: Ending processing of '{item}'\n")

    if info_type == 'are-there-per-interval-tasks':
        if results_interval_definition:
            return True
        else:
            return False
    elif info_type == 'per-interval-task-definitions':
        return results_interval_definition
    elif info_type == 'cumulative-task-graph':
        return results_cumulative_graph
    elif info_type == 'cumulative-task-definitions':
        return results_cumulative_definition

print(get_analysis_info('defined-interval-task-definitions', 'all', '/archive/Chris.Blanton/am5/2022.01/c96L33_am4p0_cmip6Diag/gfdl.ncrc4-intel21-prod-openmp/pp', '1979', '1988', 'P2Y'))

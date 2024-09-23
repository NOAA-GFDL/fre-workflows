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
        return True
    else:
        for item in list1:
            if item not in list2:
                return False
    return True

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
        return False

    # skip env and command keys
    item = keys[0]
    if item == "env" or item == "command":
        return False

    # consider adding analysis script to workflow
    # if not adding, write a note why

    # get the mandatory options: script path, frequency, product (ts or av), and switch
    item_script = os.path.basename(node.get_value(keys=[item, 'script']))
    if item_script is None:
        raise Exception(f"Jinja2Filters/get_analysis_info.py \n get_value([{item},'script']) is None!")
    
    item_freq = node.get_value(keys=[item, 'freq'])
    if item_freq is None:
        raise Exception(f"Jinja2Filters/get_analysis_info.py \n get_value([{item},'freq']) is None!")

    item_product = node.get_value(keys=[item, 'product'])
    if item_product is None:
        raise Exception(f"Jinja2Filters/get_analysis_info.py \n get_value([{item},'product']) is None!")

    item_switch = node.get_value(keys=[item, 'switch'])
    if item_switch is None:
        raise Exception(f"Jinja2Filters/get_analysis_info.py \n get_value([{item},'switch']) is None!")

    # skip if switch is off
    if item_switch == "off":
        return False

    # skip this analysis script if pp component not requested
    item_comps = node.get_value(keys=[item, 'components']).split()
    if not check_components(item_comps, pp_components):
        if print_stderr:
            sys.stderr.write(f"ANALYSIS: {item}: Skipping as it requests component(s) not available ({item_comps})\n")
        return False

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

    # get the optional cumulative option
    item_cumulative = node.get_value(keys=[item, 'cumulative'])
    if item_cumulative:
        item_cumulative = str_to_bool(item_cumulative)
    else:
        item_cumulative = False

    # get the optional install and publish scripts
    item_install_script = node.get_value(keys=[item, 'install'])
    item_publish_script = node.get_value(keys=[item, 'publish'])

    return(item, item_comps, item_script_file, item_script_extras, item_freq, item_start, item_end, item_cumulative, item_product, item_install_script, item_publish_script)

def get_cumulative_info(node, pp_components, pp_dir, chunk, pp_start, pp_stop, analysis_only=False, print_stderr=False):
    """Return the task definitions and task graph for all cumulative-mode analysis scripts.

    Accepts 8 arguments, last 2 optional:
        node                    Rose ConfigNode object
        pp_components           PP components that the workflow is using
        pp_dir                  PP directory to be used for setting in_data_dir template variable
        chunk                   ISO8601 duration used by the workflow
        pp_start                date object of the beginning of PP
        pp_stop                 date object of the end of PP
        analysis_only           optional boolean to indicate no pre-requisites needed
        print_stderr            optional boolean to print analysis scripts that will be launched
    """
    defs = ""
    graph = ""

    for keys, sub_node in node.walk():
        # retrieve information about the script
        # scripts that use pp components that are not being used are skipped
        item_info = get_item_info(node, keys, pp_components)
        if item_info:
            item, item_comps, item_script_file, item_script_extras, item_freq, item_start, item_end, item_cumulative, item_product, item_install, item_publish = item_info
        else:
            continue

        # skip if the analysis type (interval, cumulative, defined) isn't what we're looking for
        if item_start and item_end:
            continue
        elif item_cumulative:
            start_str = metomi.isodatetime.dumpers.TimePointDumper().strftime(pp_start, '%Y')
            if print_stderr:
                sys.stderr.write(f"ANALYSIS: {item}: Will run from {start_str} to current available (cumulative mode)\n")
        else:
            continue

        # form a base task definition for the analysis script
        # to be called "analysis-{item}"
        defs += form_task_definition_string(item_freq, chunk, pp_dir, item_comps, item, item_script_file, item_script_extras, item_product, item_install, item_publish)

        # add task to install the analysis script env
        if item_install:
            graph += f"""
        R1 = \"\"\"
            install-analysis-{item}
        \"\"\"
        """

        # to make the task run, we will create a task family for
        # each chunk/interval, starting from the beginning of pp data
        # then we create an analysis script task for each of these task families
        oneyear = metomi.isodatetime.parsers.DurationParser().parse('P1Y')
        date = pp_start + chunk - oneyear
        while date <= pp_stop:
            date_str = metomi.isodatetime.dumpers.TimePointDumper().strftime(date, '%Y')

            # add the task definition for each ending time
            defs += f"""
    [[analysis-{item}-{date_str}]]
        inherit = ANALYSIS-CUMULATIVE-{date_str}, analysis-{item}
            """

            # add the publish task definition for each ending time
            if item_publish:
                defs += f"""
    [[publish-analysis-{item}-{date_str}]]
        inherit = publish-analysis-{item}
                """

            # add the task definition family for each ending time
            defs += f"""
    [[ANALYSIS-CUMULATIVE-{date_str}]]
        inherit = ANALYSIS
        [[[environment]]]
            yr1 = {metomi.isodatetime.dumpers.TimePointDumper().strftime(pp_start, '%Y')}
            yr2 = {metomi.isodatetime.dumpers.TimePointDumper().strftime(date, '%Y')}
            """

            # add the timeaverage in_data_file
            if item_product == "av":
                if item_freq == "P1M":
                    times = '{01,02,03,04,05,06,07,08,09,10,11,12}'
                else:
                    times = 'ann'
                defs += """
    [[analysis-{}-{}]]
        [[[environment]]]
            in_data_file = {}.{}.{}.nc
                """.format(item, date_str, item_comps[0], '{$(seq -s, -f "%04g" $yr1 $yr2)}', times)

            date += chunk

        # now set the task graphs.
        # We need one recurrence interval for each analysis stop time.
        # In that interval, the ts analysis scripts depend on the remap-pp-component tasks,
        # and the av analysis scripts depend on combine-timeavgs.
        # If "analysis only" option is set, then do not use those prereq dependences
        # and assume the pp data is already there.
        date = pp_start + chunk - oneyear
        while date <= pp_stop:
            graph += f"        R1/{metomi.isodatetime.dumpers.TimePointDumper().strftime(date, '%Y-%m-%dT00:00:00Z')} = \"\"\"\n"
            if item_install:
                graph += f"            install-analysis-{item}[^] => analysis-{item}\n"
            if not analysis_only:
                if item_product == "av":
                    graph += f"            COMBINE-TIMEAVGS-{chunk}:succeed-all\n"
                else:
                    graph += f"            REMAP-PP-COMPONENTS-TS-{chunk}:succeed-all\n"
            d = date
            i = -1
            while d > pp_start + chunk:
                if not analysis_only:
                    if item_product == "av":
                        graph += f"            & COMBINE-TIMEAVGS-{chunk}[{i*chunk}]:succeed-all\n"
                    else:
                        graph += f"            & REMAP-PP-COMPONENTS-TS-{chunk}[{i*chunk}]:succeed-all\n"
                i -= 1
                d -= chunk
            if not analysis_only and item_product == "ts":
                graph += f"            => data-catalog\n"
            if analysis_only:
                graph += f"            data-catalog => ANALYSIS-CUMULATIVE-{metomi.isodatetime.dumpers.TimePointDumper().strftime(date, '%Y')}\n"
            else:
                graph += f"            => ANALYSIS-CUMULATIVE-{metomi.isodatetime.dumpers.TimePointDumper().strftime(date, '%Y')}\n"
            if item_publish:
                graph += f"             analysis-{item}-{date_str} => publish-analysis-{item}-{date_str}\n"
            graph += f"        \"\"\"\n"
            date += chunk

    return(defs, graph)

def get_per_interval_info(node, pp_components, pp_dir, chunk, analysis_only=False, print_stderr=False):
    """Return task definitions and the task graph for all every-interval analysis scripts.

    Accepts 6 arguments, last 2 optional:
        node                    Rose ConfigNode object
        pp_components           PP components that the workflow is using
                                Skip scripts that use components not present
        pp_dir                  PP directory to be used for setting in_data_dir template variable
        chunk                   Launch the analysis scripts every interval of this chunk
        analysis_only           optional boolean to indicate no pre-requisites needed
                                normally, ts scripts depend on remap-pp-components, and
                                av scripts depend on combine-timeavgs
        print_stderr            print analysis script information to screen
                                only for humans to see what analysis scripts will be launched
    """
    defs = ""
    graph = ""
    oneyear = metomi.isodatetime.parsers.DurationParser().parse('P1Y')

    # loop over all analysis scripts
    for keys, sub_node in node.walk():
        # retrieve information about the script
        # if the analysis script uses a component not present, then item_info will be empty
        item_info = get_item_info(node, keys, pp_components)
        if item_info:
            item, item_comps, item_script_file, item_script_extras, item_freq, item_start, item_end, item_cumulative, item_product, item_install, item_publish = item_info
        else:
            continue

        # skip the analysis script if it is cumulative or defined-interval
        # we only care about every-interval ones
        if item_start and item_end:
            continue
        elif item_cumulative:
            continue
        else:
            if print_stderr:
                sys.stderr.write(f"ANALYSIS: {item}: Will run every chunk {chunk}\n")

        # form a base task definition for the analysis script
        # to be called "analysis-{item}"
        defs += form_task_definition_string(item_freq, chunk, pp_dir, item_comps, item, item_script_file, item_script_extras, item_product, item_install, item_publish)

        # to make the task run, we will create a corresponding task graph below
        # corresponding to the interval (chunk), e.g. ANALYSIS-P1Y.
        # Then, the analysis script will inherit from that family, to enable
        # both the task triggering and the yr1 and datachunk template vars.
        defs += f"""
    [[analysis-{item}]]
        inherit = ANALYSIS-{chunk}
        """

        # create the task family for all every-interval analysis scripts
        defs += f"""
    [[ANALYSIS-{chunk}]]
        inherit = ANALYSIS
        [[[environment]]]
            yr1 = $(cylc cycle-point --template=CCYY --offset=-{chunk - oneyear})
            datachunk = {chunk.years}
        """

        # for timeaverages, set the in_data_file variable
        if item_product == "av":
            if item_freq == "P1M":
                times = '{01,02,03,04,05,06,07,08,09,10,11,12}'
            else:
                times = 'ann'
            defs += """
    [[analysis-{}]]
        [[[environment]]]
            in_data_file = {}.{}.{}.nc
            """.format(item, item_comps[0], '$yr1-$yr2', times)

        # now set the task graph
        # The analysis chunk is the recurrence inteval.
        # Normally, the ts scripts depend on remap-pp-components, and the
        # av scripts depend on combine-timeavgs.
        # If "analysis only" option is set, then do not use the prerequisite dependencies
        # and assume the pp data is already there.
        graph += f"        +{chunk - oneyear}/{chunk} = \"\"\"\n"
        if item_install:
            graph += f"            install-analysis-{item}[^] => analysis-{item}\n"
        if analysis_only:
            graph += f"            data-catalog => ANALYSIS-{chunk}?\n"
        else:
            if item_product == "av":
                graph += f"            COMBINE-TIMEAVGS-{chunk}:succeed-all => ANALYSIS-{chunk}?\n"
            else:
                graph += f"            REMAP-PP-COMPONENTS-TS-{chunk}:succeed-all => data-catalog => ANALYSIS-{chunk}?\n"
        if item_publish:
            graph += f"        analysis-{item} => publish-analysis-{item}\n"
        graph += f"        \"\"\"\n"

        # add task to install the analysis script env
        if item_install:
            graph += f"""
        R1 = \"\"\"
            install-analysis-{item}
        \"\"\"
        """

    return(defs, graph)

def form_task_definition_string(freq, chunk, pp_dir, comps, item, script_file, script_extras, product, install, publish):
    """Form the task definition string"""

    bronx_freq = convert_iso_duration_to_bronx_freq(freq)
    bronx_chunk = convert_iso_duration_to_bronx_chunk(chunk)

    # ts and av distinction
    if product == "ts":
        in_data_dir = os.path.join(pp_dir,comps[0],"ts",bronx_freq,bronx_chunk,"")
    else:
        in_data_dir = os.path.join(pp_dir,comps[0],"av",bronx_freq,bronx_chunk,"")

    string = f"""
    [[analysis-{item}]]
        script = '''
            chmod +x $CYLC_WORKFLOW_SHARE_DIR/analysis-scripts/{script_file}.$yr1-$yr2
            $CYLC_WORKFLOW_SHARE_DIR/analysis-scripts/{script_file}.$yr1-$yr2 {script_extras}
        '''
        [[[environment]]]
            in_data_dir = {in_data_dir}
            freq = {freq}
            staticfile = {pp_dir}/{comps[0]}/{comps[0]}.static.nc
            scriptLabel = {item}
            datachunk = {chunk.years}
        """
    if install:
        # If absolute path is specified, use it
        print("DEBUG:", install)
        if os.path.isabs(install):
            install_fullpath = install
        # If relative path is specified and it exists, assume it's in app/analysis/file and refer to the cylc-run location
        elif os.path.exists(install):
            install_fullpath = os.path.join('$CYLC_RUN_DIR', 'app', 'analysis', 'file', os.path.basename(install))
        # Otherwise, just use it, but it probably won't work. (Validation should catch this)
        else:
            install_fullpath = install
        string += f"""
    [[install-analysis-{item}]]
        inherit = BUILD-ANALYSIS
        script = chmod +x {install} && {install}
        """

    if publish:
        string += f"""
    [[publish-analysis-{item}]]
        inherit = PUBLISH-ANALYSIS
        script = {publish}
        """

    return(string)

def get_defined_interval_info(node, pp_components, pp_dir, chunk, pp_start, pp_stop, ana_start, ana_stop, analysis_only=False, print_stderr=False):
    """Return the task definitions and task graph for all user-defined range analysis scripts.

    Accepts 10 arguments, last 2 optional:
        node                    Rose ConfigNode object
        pp_components           PP components that the workflow is using
        pp_dir                  PP directory to be used for setting in_data_dir template variable
        chunk                   ISO8601 duration used by the workflow
        pp_start                date object of the beginning of PP
        pp_stop                 date object of the end of PP
        ana_start               date object of the beginning of analysis request
        ana_stop                date object of the end of analysis request
        analysis_only           optional boolean to indicate no pre-requisites needed
        print_stderr            print analysis script information to screen
    """
    defs = ""
    graph = ""

    for keys, sub_node in node.walk():
        # retrieve information about the script
        item_info = get_item_info(node, keys, pp_components, ana_start, ana_stop, print_stderr)
        if item_info:
            item, item_comps, item_script_file, item_script_extras, item_freq, item_start, item_end, item_cumulative, item_product, item_install, item_publish = item_info
        else:
            continue

        # skip if the analysis type (interval, cumulative, defined) isn't what we're looking for
        if item_start and item_end:
            pass
        elif item_cumulative:
            continue
        else:
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

        # set the task definitions that don't depend on time
        defs += form_task_definition_string(item_freq, chunk, pp_dir, item_comps, item, item_script_file, item_script_extras, item_product, item_install, item_publish)

        # set the task definition above to inherit from the task family below
        defs += f"""
    [[analysis-{item}]]
        inherit = ANALYSIS-{item_start_str}_{item_end_str}
        """

        # set time-varying stuff
        defs += f"""
    [[ANALYSIS-{item_start_str}_{item_end_str}]]
        inherit = ANALYSIS
        [[[environment]]]
            yr1 = {item_start_str}
            yr2 = {item_end_str}
        """

        # now set the in_data_file for av's
        if item_product == "av":
            if item_freq == "P1M":
                times = '{01,02,03,04,05,06,07,08,09,10,11,12}'
            else:
                times = 'ann'
            defs += """
    [[analysis-{}]]
        [[[environment]]]
            in_data_file = {}.{}.{}.nc
            """.format(item, item_comps[0], '{$(seq -s, -f "%04g" $yr1 $yr2)}', times)

        # set the graph definitions
        oneyear = metomi.isodatetime.parsers.DurationParser().parse('P1Y')
        graph += f"        R1/{metomi.isodatetime.dumpers.TimePointDumper().strftime(d2, '%Y-%m-%dT00:00:00Z')} = \"\"\"\n"
        if item_install:
            graph += f"            install-analysis-{item}[^] => analysis-{item}\n"
        if not analysis_only:
            if item_product == "av":
                graph += f"            COMBINE-TIMEAVGS-{chunk}:succeed-all\n"
            else:
                graph += f"            REMAP-PP-COMPONENTS-TS-{chunk}:succeed-all\n"
        d = d2
        i = -1
        while d > pp_start + chunk:
            if not analysis_only:
                if item_product == "av":
                    graph += f"            & COMBINE-TIMEAVGS-{chunk}[{i*chunk}]:succeed-all\n"
                else:
                    graph += f"            & REMAP-PP-COMPONENTS-TS-{chunk}[{i*chunk}]:succeed-all\n"
            i -= 1
            d -= chunk
        if not analysis_only and item_product == "ts":
            graph += f"            => data-catalog\n"
        if analysis_only:
            graph += f"            data-catalog => ANALYSIS-{item_start_str}_{item_end_str}\n"
        else:
            graph += f"            => ANALYSIS-{item_start_str}_{item_end_str}\n"
        if item_publish:
            graph += f"        analysis-{item} => publish-analysis-{item}\n"
        graph += f"        \"\"\"\n"

        # add task to install the analysis script env
        if item_install:
            graph += f"""
        R1 = \"\"\"
            install-analysis-{item}
        \"\"\"
        """

    return(defs, graph)

def get_analysis_info(info_type, pp_components_str, pp_dir, pp_start_str, pp_stop_str, ana_start_str, ana_stop_str, chunk, analysis_only=False, print_stderr=False):
    """Return requested analysis-related information from app/analysis/rose-app.conf

    Accepts 10 arguments, last 2 optional:
        info_type (str): one of these
            per-interval-task-definitions           Returns task environments for every-chunk analysis scripts
            per-interval-task-graph                 Returns task graph for every-chunk analysis scripts
            cumulative-task-definitions             Returns task environments for cumulative-mode analysis scripts
            cumulative-task-graph                   Returns task graph for cumulative-mode analysis scripts
            defined-task-definitions                Returns task environments for user-defined year range analysis scripts
            defined-task-graph                      Returns task graph for user-defined year range analysis scripts
        pp_components_str (str):        all, or a space-separated list of pp components that are being generated
                                        analysis scripts depending on non-present components will be skipped
        pp_dir (str):                   absolute filepath root (up to component, not including)
                                        used for forming the in_data_dir/in_data_file template vars
        pp_start_str (str):             start of pp data availability
                                        Not used for every-interval scripts.
                                        For cumulative scripts, use for yr1
        pp_stop_str (str):              last cycle point to process
        chunk (str):                    chunk to use for task graphs at least
        analysis_only (bool):           make task graphs not depend on REMAP-PP-COMPONENTS
        print_stderr (bool):            print a summary of analysis scripts that would be run
"""
    # convert strings to date objects
    pp_start = metomi.isodatetime.parsers.TimePointParser(assumed_time_zone=(0,0)).parse(pp_start_str)
    pp_stop = metomi.isodatetime.parsers.TimePointParser(assumed_time_zone=(0,0)).parse(pp_stop_str)
    chunk = metomi.isodatetime.parsers.DurationParser().parse(chunk)
    ana_start = metomi.isodatetime.parsers.TimePointParser(assumed_time_zone=(0,0)).parse(ana_start_str)
    ana_stop = metomi.isodatetime.parsers.TimePointParser(assumed_time_zone=(0,0)).parse(ana_stop_str)

    # split the pp_components into a list
    pp_components = pp_components_str.split()

    # locate the analysis Rose configuration
    path_to_conf = os.path.dirname(os.path.abspath(__file__)) + '/../app/analysis/rose-app.conf'
    node = metomi.rose.config.load(path_to_conf)

    # return the requested information
    if info_type == 'per-interval-task-definitions':
        return(get_per_interval_info(node, pp_components, pp_dir, chunk, analysis_only, print_stderr)[0])
    elif info_type == 'per-interval-task-graph':
        return(get_per_interval_info(node, pp_components, pp_dir, chunk, analysis_only, False)[1])
    elif info_type == 'cumulative-task-graph':
        return(get_cumulative_info(node, pp_components, pp_dir, chunk, pp_start, pp_stop, analysis_only, print_stderr)[1])
    elif info_type == 'cumulative-task-definitions':
        return(get_cumulative_info(node, pp_components, pp_dir, chunk, pp_start, pp_stop, analysis_only, print_stderr)[0])
    elif info_type == 'defined-interval-task-graph':
        return(get_defined_interval_info(node, pp_components, pp_dir, chunk, pp_start, pp_stop, ana_start, ana_stop, analysis_only, print_stderr)[1])
    elif info_type == 'defined-interval-task-definitions':
        return(get_defined_interval_info(node, pp_components, pp_dir, chunk, pp_start, pp_stop, ana_start, ana_stop, analysis_only, print_stderr)[0])
    else:
        raise Exception(f"Invalid information type: {info_type}")

# for interactive debugging use, uncomment and modify below
#print(get_analysis_info('per-interval-task-definitions', 'all', '/archive/Chris.Blanton/am5/2022.01/c96L33_am4p0_cmip6Diag/gfdl.ncrc4-intel21-prod-openmp/pp', '1979', '1988', 'P2Y'))

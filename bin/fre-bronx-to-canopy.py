#!/home/oar.gfdl.sw/conda/miniconda3/envs/cylc/bin/python

import argparse
import re
import os
import sys
import subprocess
import logging
import metomi.rose.config
import metomi.isodatetime.parsers

#
# Primary Usage: fre-bronx-to-canopy -x XML -e EXP -p PLATFORM -t TARGET
# 
#
# The Bronx-to-Canopy XML converter overwrites 3 files:
# - opt/rose-suite-EXPNAME.conf
# - app/remap-pp-components/rose-app.conf
# - app/regrid-xy/rose-app.conf
#

LOGGING_FORMAT = '%(asctime)s  %(levelname)s: %(message)s'
FRE_PATH = '/home/fms/local/opt/fre-commands/bronx-20/bin'
FRE_TEST_PATH = '/home/fms/local/opt/fre-commands/test/bin'
CYLC_PATH = '/home/fms/fre-canopy/system-settings/bin'
CYLC_REFINED_SCRIPTS = ["check4ptop.pl", 
                        "module_init_3_1_6.pl",
                        "plevel_mask.ncl", 
                        "refineDiag_atmos.csh",
                        "refine_fields.pl", 
                        "surface_albedo.ncl",
                        "tasminmax.ncl", 
                        "tracer_refine.ncl",
                        "refineDiag_atmos_cmip6.csh"
                       ]
CYLC_REFINED_DIR = "\\$CYLC_WORKFLOW_RUN_DIR/etc/refineDiag"
PREANALYSIS_SCRIPT = "refineDiag_data_stager_globalAve.csh"


def freq_from_legacy(legacy_freq):
    """Return ISO8601 duration given Bronx-style frequencies

    Arguments:
        1. legacy_freq[str]: The Bronx frequency
    """
    lookup = {
        'annual': 'P1Y',
        'monthly': 'P1M',
        'seasonal': 'P3M',
        'daily': 'P1D',
        '120hr': 'P120D',
        '12hr': 'PT12H',
        '8hr': 'PT8H',
        '6hr': 'PT6H',
        '4hr': 'PT4H',
        '3hr': 'PT3H',
        '2hr': 'PT2H',
        '1hr': 'PT1H',
        'hourly': 'PT1H',
        '30min': 'PT30M'
    }
    return lookup[legacy_freq]

def chunk_from_legacy(legacy_chunk):
    """Return ISO8601 duration given Bronx-style chunk

    Arguments:
        1. legacy_chunk[str]: The Bronx chunk
    """
    regex = re.compile('(\d+)(\w+)')
    match = regex.match(legacy_chunk)
    if not match:
        logging.error("Could not convert Bronx chunk to ISO8601 duration: "            \
                      + legacy_chunk)
        raise ValueError

    if match.group(2) == "yr":
        return 'P{}Y'.format(match.group(1))
    elif match.group(2) == 'mo':
        return 'P{}M'.format(match.group(1))
    else:
        logging.error("Unknown time units " + match.group(2))
        raise ValueError

def frelist_xpath(args, xpath):
    """Returns filepaths of FRE XML elements that use X-path notation
       using Bronx's 'frelist' command via Python's 'subprocess' module

    Arguments:
        1. args[str]: Argparse user-input arguments
        2. xpath[str]: X-path (XML) notation required by 'frelist'
    """
    cmd = "frelist -x {} -p {} -t {} {} --evaluate '{}'".format(args.xml,
                                                                args.platform,
                                                                args.target,
                                                                args.experiment,
                                                                xpath)
    logging.info(">> {}".format(xpath))
    process = subprocess.run(cmd,
                             shell=True,
                             check=True,
                             capture_output=True,
                             universal_newlines=True)
    result = process.stdout.strip()
    logging.info(result)
    return(result)

def duration_to_seconds(duration):
    """Returns the conversion of a chunk duration to seconds

    Arguments: 
        1. duration[str]: The original chunk duration
    """
    dur = metomi.isodatetime.parsers.DurationParser().parse(duration)
    return dur.get_seconds()


def main(args):
    """The meat of the converter

       Arguments: 
           1. args[argparse Namespace]: Arguments given at the command line

       Tasks:
           1. Generate key-value pairs for the rose-suite.conf.
           2. Generate content for the regrid-xy app
           3. Generate content for the remap-pp-components app
    """
    xml = args.xml
    expname = args.experiment
    platform = args.platform
    target = args.target

    ##########################################################################
    # Set up default configurations for regrid-xy and remap-pp-components
    ##########################################################################
    rose_remap = metomi.rose.config.ConfigNode()
    rose_remap.set(keys=['command', 'default'], value='remap-pp-components')

    rose_regrid_xy = metomi.rose.config.ConfigNode()
    rose_regrid_xy.set(keys=['command', 'default'], value='regrid-xy')

    ##########################################################################
    # Create the rose-suite config and begin setting up key-value pairs
    # Note: All strings inside the rose-suite configuration MUST be quoted.
    # Note: The exception to the 'quote' rule is boolean values.
    # Note: Addition of quotes will appear as "'" in the code.
    ##########################################################################
    rose_suite = metomi.rose.config.ConfigNode()
    rose_suite.set(keys=['template variables', 'SITE'],              value='"ppan"')
    rose_suite.set(keys=['template variables', 'CLEAN_WORK'],        value='True')
    rose_suite.set(keys=['template variables', 'PTMP_DIR'],          value='"/xtmp/$USER/ptmp"')
    rose_suite.set(keys=['template variables', 'DO_MDTF'],           value='False')
    rose_suite.set(keys=['template variables', 'DO_STATICS'],        value='True')
    rose_suite.set(keys=['template variables', 'DO_TIMEAVGS'],       value='True')
    rose_suite.set(keys=['template variables', 'DO_ANALYSIS_ONLY'],  value='False')
    rose_suite.set(keys=['template variables', 'FRE_ANALYSIS_HOME'], value='"/home/fms/local/opt/fre-analysis/test"')
    
    #if args.pp_start is not None:
    #    rose_suite.set(keys=['template variables', 'PP_START'],
    #                   value="'" + str(args.pp_start) + "'")
    #else:
    #    rose_suite.set(keys=['template variables', 'PP_START'],
    #                   value="'0000'")

    #if args.pp_stop is not None:
    #    rose_suite.set(keys=['template variables', 'PP_STOP'],
    #                   value="'" + str(args.pp_stop) + "'")
    #else:
    #    rose_suite.set(keys=['template variables', 'PP_STOP'],
    #                   value="'0000'")

    #if args.do_refinediag:
    #    rose_suite.set(keys=['template variables', 'DO_REFINEDIAG'],
    #                   value='True')
    #    rose_suite.set(keys=['template variables', 'REFINEDIAG_NAME'],
    #                   value="'atmos'")
    #    rose_suite.set(keys=['template variables', 'DO_PREANALYSIS'],
    #                   value='True')
    #    rose_suite.set(keys=['template variables', 'PREANALYSIS_NAME'],
    #                   value="'vitals'")
    #else:
    rose_suite.set(keys=['template variables', 'DO_REFINEDIAG'], value='False')
    rose_suite.set(keys=['template variables', 'DO_PREANALYSIS'], value='False')

    #rose_suite.set(keys=['template variables', 'DO_ANALYSIS'],
    #               value=args.do_analysis)
    rose_suite.set(keys=['template variables', 'EXPERIMENT'],
                   value="'{}'".format(expname))
    rose_suite.set(keys=['template variables', 'PLATFORM'],
                   value="'{}'".format(platform))
    rose_suite.set(keys=['template variables', 'TARGET'],
                   value="'{}'".format(target))

    regex_fre_property = re.compile('\$\((\w+)')
    all_components = set()

    ##########################################################################
    # Run 'frelist' in the background to fetch the default history directory,
    # the default history_refineDiag directory, and the default PP directory,
    # all of which have been set in the XML. If the custom arguments for these
    # directory variables have not been set by the user at the command line,
    # the XML's default paths will be inserted into rose-suite.conf.
    ##########################################################################
    logging.info("Running frelist for XML parsing...")
    logging.info("If this fails, try running the 'frelist' call manually.\n")
    fetch_history_cmd = "frelist -x {} -p {} -t {} {} -d archive".format(xml,
                                                                         platform,
                                                                         target,
                                                                         expname)
    logging.info(">> {}".format(fetch_history_cmd))
    fetch_history_process = subprocess.run(fetch_history_cmd,
                                           shell=True,
                                           check=True,
                                           capture_output=True,
                                           universal_newlines=True)
    historyDir = fetch_history_process.stdout.strip() + '/history'
    historyDirRefined = historyDir + '_refineDiag'
    logging.info(historyDir)

    fetch_pp_cmd = "frelist -x {} -p {} -t {} {} -d postProcess".format(xml,
                                                                        platform,
                                                                        target,
                                                                        expname)
    logging.info(">> {}".format(fetch_pp_cmd))
    fetch_pp_process = subprocess.run(fetch_pp_cmd,
                                      shell=True,
                                      check=True,
                                      capture_output=True,
                                      universal_newlines=True)
    ppDir = fetch_pp_process.stdout.strip()
    logging.info(ppDir)

    fetch_analysis_dir_cmd = "frelist -x {} -p {} -t {} {} -d analysis".format(xml,
                                                                        platform,
                                                                        target,
                                                                        expname)
    logging.info(">> {}".format(fetch_analysis_dir_cmd))
    fetch_analysis_dir_process = subprocess.run(fetch_analysis_dir_cmd,
                                      shell=True,
                                      check=True,
                                      capture_output=True,
                                      universal_newlines=True)
    analysisDir = fetch_analysis_dir_process.stdout.strip()
    logging.info(analysisDir)

    gridSpec = frelist_xpath(args, 'input/dataFile[@label="gridSpec"]')
    simTime = frelist_xpath(args, 'runtime/production/@simTime')
    simUnits = frelist_xpath(args, 'runtime/production/@units')

    rose_suite.set(keys=['template variables', 'HISTORY_DIR'],
                   value="'{}'".format(historyDir))
    rose_suite.set(keys=['template variables', 'HISTORY_DIR_REFINED'],
                   value="'{}'".format(historyDirRefined))
    rose_suite.set(keys=['template variables', 'PP_DIR'],
                   value="'{}'".format(ppDir))
    rose_suite.set(keys=['template variables', 'ANALYSIS_DIR'],
                   value="'{}'".format(analysisDir))
    rose_suite.set(keys=['template variables', 'GRID_SPEC'],
                   value="'{}'".format(gridSpec))

    ##########################################################################
    # Process the refineDiag scripts into the rose-suite configuration from
    # the <refineDiag> tags in the XML. There is one special <refineDiag>
    # script that contains its own key-value pair: PREANALYSIS. Everything
    # else gets processed into a list of strings under the REFINEDIAG_SCRIPT
    # rose-suite setting. Also, if a script referenced can also be found in
    # Canopy's centralized refineDiag repository, located in the
    # $CYLC_WORKFLOW_DIR/etc/refineDiag, then THOSE references will be used.
    # Otherwise, the reference will be whatever path the XML finds.
    ##########################################################################
    preanalysis_path_xml = None
    preanalysis_path_cylc = "'{}/{}'".format(CYLC_REFINED_DIR,
                                             PREANALYSIS_SCRIPT)

    # Only need to retrieve the refineDiag scripts if the --do_refinediag setting
    # has been enabled on the command line by the user.
    if rose_suite.get_value(keys=['template variables', 'DO_REFINEDIAG']) == "True":
       refineDiag_cmd = ("frelist -x {} -p {} -t {} {} "                               \
                         "--evaluate postProcess/refineDiag/@script".format(xml,
                                                                            platform,
                                                                            target,
                                                                            expname)
                        )
       refineDiag_process = subprocess.run(refineDiag_cmd,
                                           shell=True,
                                           check=True,
                                           capture_output=True,
                                           universal_newlines=True)

       # Place the subprocess output (the retrieved refineDiag scripts) into a
       # comma-separated list of single-quoted strings, deleting unwanted characters
       str_output = "'{}'".format(refineDiag_process.stdout)
       proc_output_list = str_output.replace(",", "','")                               \
                          .replace(" ", "','")                                         \
                          .replace("\n", "")                                           \
                          .split(",")

       # Pop out and retrieve the special 'preanalysis' script from the list of
       # other captured refineDiag script, if it has been found. A list comprehension
       # seems to work well for this case
       try:
           preanalysis_path_xml = proc_output_list.pop(                                \
               [idx for idx, substr in enumerate(proc_output_list)                     \
                if PREANALYSIS_SCRIPT in substr][0])
       except IndexError:
           pass

       # The following nested loop assigns the Cylc workflow directory location 
       # for refineDiag scripts instead of the XML-based one, if it exists.
       # Additionally, there are 2 levels within the Cylc location: 
       # CYLC_WORKFLOW_DIR/etc/refineDiag and
       # CYLC_WORKFLOW_DIR/etc/refineDiag/atmos_refine_scripts. If the script that
       # we've identified is 'refineDiag_atmos_cmip6.csh', we will reference the
       # former location. Otherwise, we will reference the latter location.
       for cylc_refined_script in CYLC_REFINED_SCRIPTS:
           for idx, xml_script_path in enumerate(proc_output_list):
               if cylc_refined_script in xml_script_path:
                   if cylc_refined_script == "refineDiag_atmos_cmip6.csh":
                       proc_output_list[idx] = "'{}/{}'".format(CYLC_REFINED_DIR,
                                                                cylc_refined_script)
                   else:
                       proc_output_list[idx] = "'{}/atmos_refine_scripts/{}'"          \
                                               .format(CYLC_REFINED_DIR,
                                                       cylc_refined_script)
           
       # Write out the final list of refineDiag scripts as a list of comma-separated,
       # single-quoted strings. If there are none found by this point, i.e. the
       # <refineDiag> were commented out in the XML or none exist (yet the user
       # selected --do_refineDiag), then write out an empty string and display 
       # a warning to the user.
       refineDiag_scripts = ",".join(proc_output_list)
       if not refineDiag_scripts:
           refineDiag_scripts = "''"

       rose_suite.set(keys=['template variables', 'REFINEDIAG_SCRIPT'],
                      value=refineDiag_scripts)
       if rose_suite.get_value(keys=['template variables',
                                     'REFINEDIAG_SCRIPT']) == "''":
           if rose_suite.get_value(keys=['template variables',
                                         'DO_PREANALYSIS']) == "True":
               logging.warning("Writing only the preanalysis script...")
           else:
               logging.warning("No refineDiag scripts written. "                       \
                               "Check your XML to see if the "                         \
                               "<refineDiag> tag exists or is commented out.")

    if rose_suite.get_value(keys=['template variables',
                                  'DO_PREANALYSIS']) == "True":
        if preanalysis_path_xml is not None:
            rose_suite.set(keys=['template variables', 'PREANALYSIS_SCRIPT'],
                           value=preanalysis_path_cylc)
        else:
            # Case where there's no preanalysis script in XML 
            # but other refineDiag scripts exist
            rose_suite.unset(keys=['template variables', 'PREANALYSIS_NAME'])
            rose_suite.set(keys=['template variables', 'DO_PREANALYSIS'],
                           value="False")

    # Grab all of the necessary PP component items/elements from the XML
    comps = frelist_xpath(args, 'postProcess/component/@type').split()
    rose_suite.set(keys=['template variables', 'PP_COMPONENTS'],
                   value="'{}'".format(' '.join(comps)))

    segment_time = frelist_xpath(args, 'runtime/production/segment/@simTime')
    segment_units = frelist_xpath(args, 'runtime/production/segment/@units')

    if segment_units == 'years':
        segment = 'P{}Y'.format(segment_time)
    elif segment_units == 'months':
        segment = 'P{}M'.format(segment_time)
    else:
        logging.error("Unknown segment units: {}".format(segment_units))
        raise ValueError

    # P12M is identical to P1Y but the latter looks nicer
    if segment == 'P12M':
        segment = 'P1Y'
    rose_suite.set(keys=['template variables', 'HISTORY_SEGMENT'], value="'{}'".format(segment))

    # Get the namelist current_date as the likely PP_START (unless "start" is used in the PP tags)
    # frelist --namelist may be better, but sometimes may not work
    current_date_str = frelist_xpath(args, 'input/namelist')
    match = re.search(r'current_date\s*=\s*(\d+),(\d+),(\d+)', current_date_str)
    if match:
        try:
            current_date = metomi.isodatetime.data.TimePoint(year=match.group(1), month_of_year=match.group(2), day_of_month=match.group(3))
        except:
            logging.warn("Could not parse date from namelist current_date")
            current_date = None
    else:
        current_date = None
        logging.warn("Could not find current_date in namelists")
    logging.info(f"current_date (from namelists): {current_date}")

    # change this later, but let's put them in now
    if simUnits == "years":
        oneless = int(simTime) - 1
        duration = f"P{oneless}Y"
    elif simUnits == "months":
        duration = f"P{simTime}M"
    else:
        raise Exception("Was thinking simUnits would be years or months")
    dur = metomi.isodatetime.parsers.DurationParser().parse(duration)
    pp_stop = current_date + dur
    rose_suite.set(keys=['template variables', 'PP_START'], value=f'"{current_date}"')
    rose_suite.set(keys=['template variables', 'PP_STOP'], value=f'"{pp_stop}"')

    # Loop over all of the PP components, fetching the sources, xyInterp, 
    # and sourceGrid.
    #comp_count = 0
    #for comp in comps:
    #    comp_count += 1
    #    pp_comp_xpath_header = 'postProcess/component[@type="{}"]'                     \
    #                           .format(comp)
    #    logging.info("Component loop: {} out of {}"                                    \
    #                 .format(comp_count, len(comps)))

#        comp_source = frelist_xpath(args, '{}/@source'                                 \
#                                          .format(pp_comp_xpath_header))
#        xyInterp = frelist_xpath(args, '{}/@xyInterp'                                  \
#                                       .format(pp_comp_xpath_header))
#        sourceGrid = frelist_xpath(args, '{}/@sourceGrid'                              \
#                                         .format(pp_comp_xpath_header))
#        if xyInterp:
#            grid = "regrid-xy"
#        else:
#            grid = "native"

#        sources = set()
#        timeseries_count = 0

        # Get the number of TS nodes
#        results = frelist_xpath(args, '{}/timeSeries/@freq'                            \
#                                      .format(pp_comp_xpath_header)).split()
#        timeseries_count = len(results)

        # Loop over the TS nodes and write out the frequency, chunklength, and
        # grid to the remap-pp-components Rose app configuration
#        for i in range(1, timeseries_count + 1):
#            label = "{}.{}".format(comp, str(i))

#            source = frelist_xpath(args, '{}/timeSeries[{}]/@source'                   \
#                                         .format(pp_comp_xpath_header, i))
#            if source:
#                sources.add(source)
#                rose_remap.set(keys=[label, 'source'], value=source)
#            elif comp_source:
#                sources.add(comp_source)
#                rose_remap.set(keys=[label, 'source'], value=comp_source)
#            else:
#                logging.warning("Skipping a timeSeries with no source "                \
#                                "and no component source for {}"                       \
#                                .format(comp))
#                continue

#            freq = freq_from_legacy(frelist_xpath(args,                                
#                                                  '{}/timeSeries[{}]/@freq'            \
#                                                  .format(pp_comp_xpath_header, i)))
#            chunk = chunk_from_legacy(frelist_xpath(args,                              
#                                                    '{}/timeSeries[{}]/@chunkLength'   \
#                                                    .format(pp_comp_xpath_header, i)))
#            rose_remap.set(keys=[label, 'freq'], value=freq)
#            rose_remap.set(keys=[label, 'chunk'], value=chunk)
#            rose_remap.set(keys=[label, 'grid'], value=grid)

#        rose_remap.set(keys=[comp + '.static', 'source'], value=' '.join(sources))
#        rose_remap.set(keys=[comp + '.static', 'chunk'], value="P0Y")
#        rose_remap.set(keys=[comp + '.static', 'freq'], value="P0Y")
#        rose_remap.set(keys=[comp + '.static', 'grid'], value=grid)
#
#        if grid == "native":
#            continue
#        else:
            # Write out values to the 'regrid-xy' Rose app as well as the
            # 'GRID_SPEC' value to the rose-suite configuration.
#            rose_regrid_xy.set(keys=[comp, 'sources'], value=' '.join(sources))

#            sourcegrid_split = sourceGrid.split('-')
#            rose_regrid_xy.set(keys=[comp, 'inputGrid'], value=sourcegrid_split[1])
#            rose_regrid_xy.set(keys=[comp, 'inputRealm'], value=sourcegrid_split[0])

#            interp_split = xyInterp.split(',')
#            rose_regrid_xy.set(keys=[comp, 'outputGridLon'], value=interp_split[1])
#            rose_regrid_xy.set(keys=[comp, 'outputGridLat'], value=interp_split[0])

#            rose_regrid_xy.set(keys=[comp, 'gridSpec'], value=gridSpec)

    # Process all of the found PP chunks into the rose-suite configuration
    if args.verbose:
        print("")
    logging.info("Setting PP chunks...")

    all_chunks = set()
    for keys, sub_node in rose_remap.walk():
        if len(keys) != 1:
            continue

        item = keys[0]
        if item == "env" or item == "command":
            continue

        chunk = rose_remap.get_value(keys=[item, 'chunk'])
        if chunk == 'P0Y':
            continue
        all_chunks.add(chunk)

    sorted_chunks = list(all_chunks)
    sorted_chunks.sort(key=duration_to_seconds, reverse=False)

    #assert len(all_chunks) >= 1
    #logging.info("  Chunks found: {}".format(', '.join(sorted_chunks)))
    #if len(all_chunks) == 1:
    #    rose_suite.set(['template variables', 'PP_CHUNK_A'],
    #                   "'{}'".format(sorted_chunks[0]))
    #    rose_suite.set(['template variables', 'PP_CHUNK_B'],
    #                   "'{}'".format(sorted_chunks[0]))
    #else:
    #    rose_suite.set(['template variables', 'PP_CHUNK_A'],
    #                   "'{}'".format(sorted_chunks[0]))
    #    rose_suite.set(['template variables', 'PP_CHUNK_B'],
    #                   "'{}'".format(sorted_chunks[1]))
    #logging.info("  Chunks used: {}".format(', '.join(sorted_chunks[0:2])))
   
    # Write out the final configurations.
    if args.verbose:
        print("") 
    logging.info("Writing output files...")

    dumper = metomi.rose.config.ConfigDumper()
    
    outfile = f"opt/rose-suite-{args.experiment}.conf"
    logging.info("  " + outfile)
    dumper(rose_suite, outfile)

    outfile = "app/remap-pp-components/rose-app.conf"
    logging.info("  " + outfile)
    dumper(rose_remap, outfile)

    outfile = "app/regrid-xy/rose-app.conf"
    logging.info("  " + outfile)
    dumper(rose_regrid_xy, outfile)

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="FRE Bronx-to-Canopy converter")
    parser.add_argument('--xml', '-x', required=True, 
                        help="Required. The Bronx XML")
    parser.add_argument('--platform', '-p', required=True, 
                        help="Required. The Bronx XML Platform")
    parser.add_argument('--target', '-t', required=True, 
                        help="Required. The Bronx XML Target")
    parser.add_argument('--experiment', '-e', required=True, 
                        help="Required. The Bronx XML Experiment")
    parser.add_argument('--do_analysis', action='store_true', default=False,
                        help="Optional. Runs the analysis scripts.")
    parser.add_argument('--historydir', 
                        help="Optional. History directory to reference. "              \
                             "If not specified, the XML's default will be used.")
    parser.add_argument('--refinedir',                                                 
                        help="Optional. History refineDiag directory to reference. "   \
                             "If not specified, the XML's default will be used.")
    parser.add_argument('--ppdir', 
                        help="Optional. Postprocessing directory to reference. "       \
                             "If not specified, the XML's default will be used.")
    parser.add_argument('--do_refinediag', action='store_true', default=False,
                        help="Optional. Process refineDiag scripts")
    parser.add_argument('--pp_start',                                                  
                        help="Optional. Starting year of postprocessing. "             \
                             "If not specified, a default value of '0000' "            \
                             "will be set and must be changed in rose-suite.conf")
    parser.add_argument('--pp_stop',                                                   
                        help="Optional. Ending year of postprocessing. "               \
                             "If not specified, a default value of '0000' "            \
                             "will be set and must be changed in rose-suite.conf")
    parser.add_argument('--validate', action='store_true',                             
                        help="Optional. Run the Cylc validator "                       \
                             "immediately after conversion")
    parser.add_argument('--verbose', '-v', action='store_true',
                        help="Optional. Display detailed output")
    parser.add_argument('--quiet', '-q', action='store_true',
                        help="Optional. Display only serious messages and/or errors")

    args = parser.parse_args()

    cylc_loaded = False

    ##########################################################################
    # Check the OS environment. Exit if FRE has not been loaded or Cylc has
    # not been loaded (if using the --validate option).
    ##########################################################################
    if not (FRE_PATH in os.getenv('PATH') or FRE_TEST_PATH in os.getenv('PATH')):
        raise EnvironmentError("Cannot run the XML converter because FRE Bronx "       \
                               "isn't loaded. Please load the latest FRE Bronx "       \
                               "module and try again.")
    
    if args.validate:
        if CYLC_PATH in os.getenv('PATH'):
            cylc_loaded = True
        else:
            raise EnvironmentError("Cannot run the validator tool because "            \
                                   "the Cylc module isn't loaded. Please "             \
                                   "run 'module load cylc/test' and try again.")

    # Logging settings. The default is throwing only warning messages
    if args.verbose:
        logging.basicConfig(level=logging.INFO, format=LOGGING_FORMAT)
    elif args.quiet:
        logging.basicConfig(level=logging.ERROR, format=LOGGING_FORMAT)
    else:
        logging.basicConfig(level=logging.WARNING, format=LOGGING_FORMAT)

    # Alert the user if only 1 or zero PP years are given as an option, and 
    # notify them that a default of '0000' for those years will be set in the
    # rose-suite configuration
    if (args.pp_start is not None and args.pp_stop is None)                            \
        or (args.pp_stop is not None and args.pp_start is None):

        logging.warning("Only 1 PP start/stop year was specified. "                    \
                        "After the converter has run, please edit the "                \
                        "default '0000' values within your rose-suite.conf.")
    if not args.pp_start and not args.pp_stop:
        logging.warning("No PP start/stop year was specified. "                        \
                        "After the converter has run, please edit the "                \
                        "default '0000' values within your rose-suite.conf")

    # These series of conditionals takes into account input from the user 
    # (for the PP_START and PP_STOP year) that is not 4 digits or other
    # nonsensical years. The rose-suite config requires 4 digits for years
    # and if the year is under '1000' (but > 0), then leading zeros must be used.
    if args.pp_start is not None and args.pp_stop is not None:
        if len(args.pp_start) < 4 and int(args.pp_start) > 0:
            args.pp_start = '0' * (4 - len(args.pp_start)) + args.pp_start
        if len(args.pp_stop) < 4 and int(args.pp_stop) > 0:
            args.pp_stop = '0' * (4 - len(args.pp_stop)) + args.pp_stop
        if int(args.pp_start) >= int(args.pp_stop):
            logging.warning("Your PP_START date is equal to or later than "            \
                            "your PP_STOP date. Please revise these values in "        \
                            "your configuration after the converter has run.")         
        if len(args.pp_start) > 4                                                      \
            or len(args.pp_stop) > 4                                                   \
            or int(args.pp_start) <= 0                                                 \
            or int(args.pp_stop) <= 0:

            logging.warning("At least one of your PP_start or PP_stop years "          \
                            "does not make sense. Please revise this value in "        \
                            "your configuration after the converter has run.")

    main(args)

    if args.verbose:
        print("")
    logging.info("XML conversion complete!")

    # Run the Cylc validator tool on the current directory if conditions are met.
    # Note: the user must be running the converter in the parent Cylc Workflow
    # Directory if the validator is run.
    if cylc_loaded:
        if args.verbose:
            print("")
        logging.info("Running the Cylc validator tool...")
        try:
            subprocess.run("cylc validate .", shell=True, check=True)
        except subprocess.CalledProcessError:
            logging.error("Errant values in rose-suite.conf or other Cylc errors. "    \
                          "Please check your configuration and run the validator "     \
                          "again separately.")
        finally:
            logging.info("Validation step complete!")


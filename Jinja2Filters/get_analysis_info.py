from pathlib import Path

from metomi.isodatetime.parsers import DurationParser, TimePointParser
from yaml import safe_load

from legacy_date_conversions import *

# set up logging
import logging
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Global variables just set to reduce typing a little.
duration_parser = DurationParser()
one_year = duration_parser.parse("P1Y")
time_parser = TimePointParser(assumed_time_zone=(0, 0))


def str_to_bool(value): 
    """Converts a string to boolean.

    Args:
        value: String input.

    Returns:
        Bool value for the string.

    Raises:
        ValueError if the string cannot be interpreted.
    """
    if isinstance(value, bool):
        return value
    if value.lower().startswith("t") or value.lower().startswith("y"):
        return True
    if value.lower().startswith("f") or value.lower().startswith("n"):
        return False
    raise ValueError(f"cannot convert string '{value}' to boolean.")


class AnalysisScript(object):
    def __init__(self, name, config, experiment_components, experiment_starting_date,
                 experiment_stopping_date):
        """Initialize the analysis script object.

        Args:
            name: String name of the analysis.
            config: Dictionary of analysis script configuration options.
            experiment_components: List of string experiment component names.
            experiment_starting_date: Starting date for the experiment.
            experiment_stopping_date: Stopping date for the experiment.
        """
        self.name = name
        logger.debug(f"{name}: initializing AnalysisScript instance")

        # Skip if configuration wants to skip it
        self.switch = config["workflow"]["analysis_on"]
        if self.switch == False:
            return

        # Skip if the components are not available
        self.components = [x.strip() for x in config["workflow"]["components"]]
        for component in self.components:
            if component not in experiment_components:
                raise ValueError(f"ERROR: Analysis script '{self.name}' requests postprocessing component '{component}' but is not one of these available components: {experiment_components}. Please add the component or turn the analysis script off.")

        # Parse the pp date range
        self.experiment_date_range = [
            experiment_starting_date,
            experiment_stopping_date
        ]

        # Parse the rest of the 'workflow' config items
        self.product = config["workflow"]["product"]
        if "cumulative" in config["workflow"]:
            self.cumulative = str_to_bool(config["workflow"]["cumulative"])
        else:
            self.cumulative = False
        if config["workflow"]["script_frequency"] == "R1":
            self.script_frequency = "R1"
        else:
            self.script_frequency = duration_parser.parse(config["workflow"]["script_frequency"])

        # Parse the new analysis config items
        if 'legacy' in config:
            self.is_legacy = True
            # the first word of command will be the script, but there could be more command-line args
            stuff = config["legacy"]["script"].split()
            if len(stuff) > 1:
                self.legacy_script = stuff.pop(0)
                self.legacy_script_args = ' '.join(stuff)
            else:
                self.legacy_script = stuff.pop(0)
                self.legacy_script_args = ""
        else:
            self.is_legacy = False

        self.data_frequency = config["required"]["data_frequency"]

        # if dates are years, convert to string or else ISO conversion will fail
        if isinstance(config["required"]["date_range"][0], int):
            one = "{:04d}".format(config["required"]["date_range"][0])
            two = "{:04d}".format(config["required"]["date_range"][1])
        else:
            one = config["required"]["date_range"][0]
            two = config["required"]["date_range"][1]
        self.date_range = [
            time_parser.parse(one),
            time_parser.parse(two)
        ]

        logger.debug(f"{name}: initialized instance")

    def choose_pp_chunk(self, chunks):
        """Choose the most suitable postprocessing chunk size.

        Args:
            chunks: List of ISO8601 durations used by the workflow.

        Returns:
            Most suitable chunk (pp subdirectory) for the script
        """
        analysis_years = self.date_range[1].year - self.date_range[0].year + 1
        chunks_str = ", ".join(chunks)
        chunks = [duration_parser.parse(c) for c in chunks]

        if self.script_frequency == "R1":
            if self.product == 'av':
                if self.cumulative:
                    return max(chunks)
                else:
                    for c in chunks:
                        if c.years == analysis_years:
                            return c

                    raise NotImplementedError(f"ERROR: Non-supported analysis script configuration: {self.name}: " +
                                              f"run-once (R1), timeaverages, and non-accumulative is inconsistent, " +
                                              f"unless one of the chunk sizes ({chunks_str}) represents "
                                              f"{self.date_range[0]} through {self.date_range[1]}, inclusive.")
            else:
                return min(chunks)

        # If any chunk matches the script frequency, return that chunk.
        for c in chunks:
            if c == self.script_frequency:
                return c

        raise NotImplementedError(f"Non-supported analysis script configuration: {self.name}: script frequency " +
                                  f"'{self.script_frequency}' matches none of the pp chunks ({chunks_str})")

    def graph(self, chunk, analysis_only):
        """Generate the cylc task graph string for the analysis script.

        Args:
            chunk: Post-processing chunk size for this analysis script
            analysis_only: Boolean; can we assume pp files are already there?

        Returns:
            String cylc task graph for the analysis.
        """
        if self.switch == False:
            return ""

        graph = ""

        logger.debug(f"script frequency = {self.script_frequency}")
        logger.debug(f"chunk = {chunk}")
        logger.debug(f"analysis date range = {self.date_range}")

        date0, date1 = self.date_range

        if self.script_frequency == chunk and not self.cumulative:
            # Run every chunk (not cumulative)
            graph += f'{self.script_frequency} = """\n'
            if analysis_only:
                graph += f"ANALYSIS-{chunk}?\n"
            else:
                if self.product == "av":
                    dep = f"COMBINE-TIMEAVGS-{chunk}:succeed-all"
                else:
                    dep = f"REMAP-PP-COMPONENTS-TS-{chunk}:succeed-all"

                graph += f"{dep} => ANALYSIS-{chunk}?\n"

            if not self.is_legacy:
                graph += f"install-analysis-{self.name}[^] => analysis-{self.name}"

            graph += f'"""\n'
        elif self.script_frequency == chunk and self.cumulative:
            # Run every chunk (cumulative)
            deps = []
            d = date0
            while d <= date1:
                graph += f'R1/{d} = """\n'
                analysis_task = f"ANALYSIS-CUMULATIVE-{d.year:04}"

                if analysis_only:
                    graph += f"{analysis_task}\n"
                else:
                    if self.product == "av":
                        deps.append(f"COMBINE-TIMEAVGS-{chunk}[{d}]:succeed-all")
                    else:
                        deps.append(f"REMAP-PP-COMPONENTS-TS-{chunk}[{d}]:succeed-all")

                    graph += " & ".join(deps) + f" => {analysis_task}\n"

                if not self.is_legacy:
                    graph += f"install-analysis-{self.name}[^] => analysis-{self.name}-{d.year:04}\n"

                graph += '"""\n'
                d += chunk
        elif self.script_frequency == "R1":
            # Run the analysis once, over a custom date range
            graph += f'R1/{date0} = """\n'

            if not analysis_only:
                deps = []
                d = date0
                while d <= date1:
                    if self.product == "av":
                        deps.append(f"COMBINE-TIMEAVGS-{chunk}[{d}]:succeed-all")
                    else:
                        deps.append(f"REMAP-PP-COMPONENTS-TS-{chunk}[{d}]:succeed-all")
                    d += chunk

                graph += " & ".join(deps) + " => "

            graph += f"ANALYSIS-{date0.year:04}_{date1.year:04}\n"

            if not self.is_legacy:
                graph += f"install-analysis-{self.name}[^] => analysis-{self.name}-{date0.year:04}_{date1.year:04}"

            graph += '"""\n'
        else:
            raise NotImplementedError(f"Non-supported analysis script configuration: {self.name}")

        if not self.is_legacy:
            graph += f'R1 = """install-analysis-{self.name}"""\n'

        return graph

    def definition(self, chunk, pp_dir):
        """Form the task definition string."""
        if self.switch == False:
            return ""

        definitions = ""

        cmip_to_bronx = {
            "yr": "annual",
            "mon": "monthly",
            "day": "daily",
            "3hr": "3hr",
            "6hr": "6hr",
        }
        frequency = cmip_to_bronx[self.data_frequency]
        bronx_chunk = convert_iso_duration_to_bronx_chunk(chunk)

        # ts and av distinction
        if self.product == "ts":
            in_data_dir = Path(pp_dir) / self.components[0] / self.product / frequency / bronx_chunk
            pre_script = "pre-script = rose task-run --verbose --app-key data-catalog\n"
        else:
            in_data_dir = Path(pp_dir) / self.components[0] / self.product / f"{frequency}_{bronx_chunk}"
            pre_script = ""

        legacy_analysis_str = f"""
    [[analysis-{self.name}]]
        {pre_script}
        script = '''
# First, sed-replace the template vars and create a runnable analysis script from the template.
# actually, just sed-replace the undercase environment variables
# need posix mode to output variables in a simple list (not json)
set -o posix
        """

        # quoting madness!
        legacy_analysis_str += '''
vars=$(set | awk -F '=' '{ print $1 }' | grep [a-z])
        '''

        if self.is_legacy:
            script_basename = Path(self.legacy_script).name
            legacy_analysis_str += f"""
# WORKDIR is the exception to include
vars="$vars WORKDIR"

# create the sed script
for var in $vars; do
    eval var2=\$$var
    if [[ -n $var2 ]]; then
        echo "s|set $var\s*$|set $var = $var2|" >> sed-script
        echo "s|^\s*$var=\s*$|$var='$var2'|"    >> sed-script
    fi
done
echo "s|\$FRE_ANALYSIS_HOME|$FRE_ANALYSIS_HOME|" >> sed-script

# write the filled-in script
if [[ $yr1 == $yr2 ]]; then
    scriptOut=$outputDir/{script_basename}.$yr1
else
    scriptOut=$outputDir/{script_basename}.$yr1-$yr2
fi
mkdir -p $outputDir
sed -f sed-script {self.legacy_script} > $scriptOut
echo "Saved script '$scriptOut'"
ls -l $scriptOut
rm sed-script

# Then, run the script
chmod +x $scriptOut
$scriptOut {self.legacy_script_args}
        '''
        [[[environment]]]
            # some analysis scripts expect a trailing slash
            in_data_dir = {in_data_dir}/
            freq = {frequency}
            staticfile = {pp_dir}/{self.components[0]}/{self.components[0]}.static.nc
            scriptLabel = {self.name}
            datachunk = {chunk.years}
            """

        new_analysis_str = f"""
    [[analysis-{self.name}]]
        {pre_script}
        script = '''
fre analysis run \
    --name              freanalysis_{self.name} \
    --catalog           $catalog \
    --output-directory  $out_dir/{self.name} \
    --output-yaml       $out_dir/{self.name}/output.yaml \
    --experiment-yaml   $experiment_yaml \
    --library-directory $CYLC_WORKFLOW_SHARE_DIR/analysis-envs/freanalysis_{self.name}
        '''
        # retry 10 times (due to mysterious intake-esm issue)
        execution retry delays = 10*PT1M
        """

        install_str = f"""
    [[install-analysis-{self.name}]]
        inherit = BUILD-ANALYSIS
        script = '''
fre analysis install \
    --url               $ANALYSIS_URL \
    --name              freanalysis_{self.name} \
    --library-directory $CYLC_WORKFLOW_SHARE_DIR/analysis-envs/freanalysis_{self.name}
        '''
        """

        if self.script_frequency == chunk and self.date_range == self.experiment_date_range \
           and not self.cumulative:
            # to make the task run, we will create a corresponding task graph below
            # corresponding to the interval (chunk), e.g. ANALYSIS-P1Y.
            # Then, the analysis script will inherit from that family, to enable
            # both the task triggering and the yr1 and datachunk template vars.
            logger.info(f"{self.name}: Will run every chunk {chunk}")
            if self.is_legacy:
                definitions += legacy_analysis_str
            else:
                definitions += new_analysis_str

            # create the task family for all every-interval analysis scripts
            definitions += f"""
    [[ANALYSIS-{chunk}]]
        inherit = ANALYSIS
        [[[environment]]]
            yr1 = $(cylc cycle-point --template=CCYY)
            databegyr = $yr1
            dataendyr = $yr2
            datachunk = {chunk.years}
                """

            # inherit from the task family
            definitions += f"""
    [[analysis-{self.name}]]
        inherit = ANALYSIS-{chunk}
            """

            # For time averages, set the in_data_file variable
            if self.product == "av":
                if self.data_frequency == "mon":
                    times = '{01,02,03,04,05,06,07,08,09,10,11,12}'
                else:
                    times = 'ann'
                if chunk == one_year:
                    years = '$yr1'
                else:
                    years = '$yr1-$yr2'
                definitions += f"""
    [[analysis-{self.name}]]
        [[[environment]]]
            in_data_file = {self.components[0]}.{years}.{times}.nc
                """

            # create the install script
            if not self.is_legacy:
                definitions += install_str

            logger.debug(f"{self.name}: Finished determining scripting")
            return definitions

        if self.script_frequency == chunk and self.date_range == self.experiment_date_range \
           and self.cumulative:
            # Case 2: run the analysis every chunk, but depend on all previous chunks too.
            # To make the task run, we will create a task family for
            # each chunk/interval, starting from the beginning of pp data
            # then we create an analysis script task for each of these task families.
            logger.info(f"{self.name}: Will run each chunk {chunk} from beginning {self.experiment_date_range[0]}")
            date = self.experiment_date_range[0]
            while date <= self.experiment_date_range[1]:
                date_str = f"{date.year:04}"

                # Add the task definition for each ending time.
                definitions += f"""
    [[analysis-{self.name}-{date_str}]]
        inherit = ANALYSIS-CUMULATIVE-{date_str}, analysis-{self.name}
                """

                if self.is_legacy:
                    definitions += legacy_analysis_str
                else:
                    definitions += new_analysis_str

                # Add the task definition family for each ending time.
                year1 = f"{self.experiment_date_range[0].year:04}"
                year2 = f"{date.year:04}"
                definitions += f"""
                    [[ANALYSIS-CUMULATIVE-{date_str}]]
                        inherit = ANALYSIS
                        [[[environment]]]
                            yr1 = {year1}
                            yr2 = {year2}
                            databegyr = $yr1
                            dataendyr = $yr2
                """

                # Add the time average in_data_file
                if self.product == "av":
                    if self.data_frequency == "mon":
                        times = '{01,02,03,04,05,06,07,08,09,10,11,12}'
                    else:
                        times = 'ann'
                    if year1 == year2:
                        years = year1
                    else:
                        # loop thru and determine the timeaverage filenames
                        years = ""
                        dd = self.experiment_date_range[0]
                        while dd <= date:
                            y1 = f"{dd.year:04}"
                            y2 = f"{(dd + chunk - one_year).year:04}"
                            if len(years) > 0:
                                years += ','
                            if y1 == y2:
                                years += f"{y1}"
                            else:
                                years += f"{y1}-{y2}"
                            dd += chunk
                    years = "{" + str(years) + "}"
                    definitions += f"""
    [[analysis-{self.name}-{date_str}]]
        [[[environment]]]
            in_data_file = {self.components[0]}.{years}.{times}.nc
                    """
                date += chunk

            # create the install script
            if not self.is_legacy:
                definitions += install_str

            return definitions

        if self.script_frequency == "R1":
            # Locate the nearest enclosing chunks.
            d1 = self.experiment_date_range[0]
            while d1 <= self.date_range[0] - chunk:
                d1 += chunk
            d2 = self.experiment_date_range[1]
            while d2 >= self.date_range[1] + chunk:
                d2 -= chunk
            d1_str = f"{d1.year:04}"
            d2_str = f"{d2.year:04}"
            if self.product == 'av' and not self.cumulative:
                if chunk.years == d2.year - d1.year + 1:
                    pass
                else:
                    raise NotImplementedError(f"ERROR: Non-supported analysis script configuration: {self.name}: run-once (R1), timeaverages, and non-accumulative is inconsistent, unless duration '{chunk}' represents {self.date_range[0]} through {self.date_range[1]} inclusive.")
            logger.info(f"{self.name}: Will run once for time period {self.date_range[0]} to {self.date_range[1]} (chunks {d1_str} to {d2_str})")
            date1_str = f"{self.date_range[0].year:04}"
            date2_str = f"{self.date_range[1].year:04}"

            # Set the task definition above to inherit from the task family below
            definitions += f"""
    [[analysis-{self.name}-{date1_str}_{date2_str}]]
        inherit = ANALYSIS-{date1_str}_{date2_str}, analysis-{self.name}
            """

            # Set time-varying stuff
            definitions += f"""
                [[ANALYSIS-{date1_str}_{date2_str}]]
                    inherit = ANALYSIS
                    [[[environment]]]
                        yr1 = {date1_str}
                        yr2 = {date2_str}
                        databegyr = $yr1
                        dataendyr = $yr2
            """

            # now set the in_data_file for av's
            if self.product == "av":
                if self.data_frequency == "mon":
                    times = '{01,02,03,04,05,06,07,08,09,10,11,12}'
                else:
                    times = 'ann'
                if date1_str == date2_str:
                    years = date1_str
                else:
                    # loop thru and determine the timeaverage filenames
                    years = ""
                    dd = d1
                    while dd <= d2:
                        y1 = f"{dd.year:04}"
                        y2 = f"{(dd + chunk - one_year).year:04}"
                        if len(years) > 0:
                            years += ','
                        if y1 == y2:
                            years += f"{y1}"
                        else:
                            years += f"{y1}-{y2}"
                        dd += chunk
                years = "{" + str(years) + "}"
                definitions += f"""
    [[analysis-{self.name}]]
        [[[environment]]]
            in_data_file = {self.components[0]}.{years}.{times}.nc
                """

            if self.is_legacy:
                definitions += legacy_analysis_str
            else:
                definitions += install_str
                definitions += new_analysis_str

            return definitions
        raise NotImplementedError(f"Non-supported analysis script configuration: {self.name}")


def task_generator(yaml_, experiment_components, experiment_start, experiment_stop):
    for script_name, script_params in yaml_["analysis"].items():
        # Retrieve information about the script
        script_info = AnalysisScript(script_name, script_params, experiment_components,
                                     experiment_start, experiment_stop)
        if script_info.switch == False:
            logger.info(f"{script_name}: Skipping, switch set to off")
            continue
        yield script_info


def task_definitions(yaml_, experiment_components, experiment_start, experiment_stop, chunks, pp_dir):
    """Return the task definitions for all user-defined analysis scripts.

    Args:
        yaml_: Dictionary experiment yaml.
        experiment_components: List of string experiment component names.
        experiment_start: Date that the experiment starts at.
        experiment_stop: Date that the experiment stops at.
        chunks: List of ISO8601 durations used by the workflow.
        pp_dir: postproceessing directory

    Returns:
        String containing the task defintions.
    """
    logger.debug("About to generate all task definitions")
    definitions = ""
    for script_info in task_generator(yaml_, experiment_components, experiment_start, experiment_stop):
        chunk = script_info.choose_pp_chunk(chunks)
        definitions += script_info.definition(chunk, pp_dir)
    logger.debug("Finished generating all task definitions")
    return definitions


def task_graph(yaml_, experiment_components, experiment_start, experiment_stop, chunks, analysis_only):
    """Return the task graphs for all user-defined analysis scripts.

    Args:
        yaml_: Dictionary experiment yaml.
        experiment_components: List of string experiment component names.
        experiment_start: Date that the experiment starts at.
        experiment_stop: Date that the experiment stops at.
        chunks: List of ISO8601 durations used by the workflow.
        analysis_only: Optional boolean to not depend on remap tasks (assume pp files already exist)

    Returns:
        String containing the task graphs.
    """
    graph = ""
    for script_info in task_generator(yaml_, experiment_components, experiment_start, experiment_stop):
        chunk = script_info.choose_pp_chunk(chunks)
        graph += script_info.graph(chunk, analysis_only)
    return graph


def get_analysis_info(experiment_yaml, info_type, experiment_components, pp_dir,
                           experiment_start, experiment_stop, chunks, analysis_only=False):
    """Return requested analysis-related information from app/analysis/rose-app.conf

    Args:
        experiment_yaml: Path to the experiment yaml file.
        info_type: String that tells which kind of output to make (graph or definition).
        pp_components: String pp components that are being generated.
        pp_dir: absolute filepath root (up to component, not including)
                used for forming the in_data_dir/in_data_file template vars
        pp_start_str (str):             start of pp data availability
                                        Not used for every-interval scripts.
                                        For cumulative scripts, use for yr1
        pp_stop_str (str):              last cycle point to process
        chunks: List of ISO8601 durations used by the workflow.
        analysis_only (bool): make task graphs not depend on REMAP-PP-COMPONENTS
    """
    logger.debug("get_analysis_info: starting")
    # Convert strings to date objects.
    experiment_start = time_parser.parse(experiment_start)
    experiment_stop = time_parser.parse(experiment_stop)

    # split the pp_components into a list
    experiment_components = experiment_components.split()

    with open(experiment_yaml) as file_:
        yaml_ = safe_load(file_)
        if info_type == "task-graph":
            logger.debug("get_analysis_info: about to return graph")
            return task_graph(yaml_, experiment_components, experiment_start,
                              experiment_stop, chunks, analysis_only)
        elif info_type == "task-definitions":
            logger.debug("get_analysis_info: about to return definitions")
            return task_definitions(yaml_, experiment_components, experiment_start,
                                   experiment_stop, chunks, pp_dir)
        raise ValueError(f"Invalid information type: {info_type}.")

from logging import getLogger
from pathlib import Path

import metomi.isodatetime.dumpers
import metomi.isodatetime.parsers
from yaml import safe_load

from legacy_date_conversions import *


# Global variables just set to reduce typing a little.
logger = getLogger(__name__)
duration_parser = metomi.isodatetime.parsers.DurationParser()
one_year = duration_parser.parse("P1Y")
time_dumper = metomi.isodatetime.dumpers.TimePointDumper()
time_parser = metomi.isodatetime.parsers.TimePointParser(assumed_time_zone=(0, 0))


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

        # Skip if configuration wants to skip it
        self.switch = config["workflow"]["switch"]
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
        self.date_range = [
            time_parser.parse(config["required"]["date_range"][0]),
            time_parser.parse(config["required"]["date_range"][1])
        ]

    def choose_pp_chunk(self, chunk1, chunk2):
        """Choose the most suitable postprocessing chunk size.

        Args:
            chunk1: Post-processing chunk size for the experiment.
            chunk2: Second pp chunk if available.

        Returns:
            Most suitable chunk (pp subdirectory) for the script
        """
        analysis_years = int(time_dumper.strftime(self.date_range[1], '%Y')) - int(time_dumper.strftime(self.date_range[0], '%Y')) + 1
        if self.script_frequency == "R1":
            if self.product == 'av':
                if self.cumulative:
                    if chunk2 is not None:
                        return(chunk2)
                    else:
                        return(chunk1)
                else:
                    if chunk2.years == analysis_years:
                        return(chunk2)
                    if chunk1.years == analysis_years:
                        return(chunk1)
                    else:
                        raise NotImplementedError(f"ERROR: Non-supported analysis script configuration: {self.name}: run-once (R1), timeaverages, and non-accumulative is inconsistent, unless duration ('{chunk1}' or '{chunk2}') represents {self.date_range[0]} through {self.date_range[1]} inclusive.")
            else:
                return(chunk1)

        if self.product == "ts":
            if chunk1 == self.script_frequency:
                return(chunk1)
            elif chunk2 == self.script_frequency:
                return(chunk2)
            else:
                raise NotImplementedError(f"Non-supported analysis script configuration: {self.name}: script frequency '{self.script_frequency}' matches neither of pp chunks, {chunk1} and {chunk2}")
        elif self.product == "av":
            if chunk2 == self.script_frequency:
                return(chunk2)
            elif chunk1 == self.script_frequency:
                return(chunk1)
            else:
                raise NotImplementedError(f"Non-supported analysis script configuration: {self.name}: script frequency '{self.script_frequency}' matches neither of pp chunks, {chunk1} and {chunk2}")

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

        install_analysis_str = f"""
R1 = \"\"\"
    install-analysis-{self.name}
\"\"\"
        """

        graph = ""

        #print(f"DEBUG: script frequency = {self.script_frequency}")
        #print(f"DEBUG: chunk = {chunk}")
        #print(f"DEBUG: analysis date range = {self.date_range}")
        #print(f"DEBUG: exp date range = {self.experiment_date_range}")

        if self.script_frequency == chunk and self.date_range == self.experiment_date_range \
           and not self.cumulative:
            graph += f"{self.script_frequency} = \"\"\"\n"
            if analysis_only:
                graph += f"data-catalog => ANALYSIS-{chunk}?\n"
            else:
                if self.product == "av":
                    graph += f"COMBINE-TIMEAVGS-{chunk}:succeed-all"
                else:
                    graph += f"REMAP-PP-COMPONENTS-TS-{chunk}:succeed-all => data-catalog"
                graph += f"=> ANALYSIS-{chunk}?\n"
            if not self.is_legacy:
                graph += f"install-analysis-{self.name}[^] => analysis-{self.name}"
            graph += f"\"\"\"\n"
            if not self.is_legacy:
                graph += install_analysis_str
            return graph

        if self.script_frequency == chunk and self.date_range == self.experiment_date_range \
           and self.cumulative:
            date = self.experiment_date_range[0] + chunk - one_year  # Last year of first chunk.
            while date <= self.experiment_date_range[1]:
                graph += f"R1/{time_dumper.strftime(date, '%Y-%m-%dT00:00:00Z')} = \"\"\"\n"
                if not analysis_only:
                    if self.product == "av":
                        graph += f"COMBINE-TIMEAVGS-{chunk}:succeed-all\n"
                    else:
                        graph += f"REMAP-PP-COMPONENTS-TS-{chunk}:succeed-all\n"

                # Looping backwards through all previous chunks.
                d = date
                i = -1
                while d > self.experiment_date_range[0]:
                    if not analysis_only:
                        if self.product == "av":
                            graph += f"& COMBINE-TIMEAVGS-{chunk}[{i*chunk}]:succeed-all\n"
                        else:
                            graph += f"& REMAP-PP-COMPONENTS-TS-{chunk}[{i*chunk}]:succeed-all\n"
                    i -= 1
                    d -= chunk

                if analysis_only:
                    graph += f"data-catalog => ANALYSIS-CUMULATIVE-{time_dumper.strftime(date, '%Y')}\n"
                else:
                    if self.product == "ts":
                        graph += f"=> data-catalog => ANALYSIS-CUMULATIVE-{time_dumper.strftime(date, '%Y')}\n"
                    else:
                        graph += f"=> ANALYSIS-CUMULATIVE-{time_dumper.strftime(date, '%Y')}\n"

                if not self.is_legacy:
                    graph += f"install-analysis-{self.name}[^] => analysis-{self.name}-{time_dumper.strftime(date, '%Y')}\n"
                graph += f"        \"\"\"\n"
                date += chunk
            if not self.is_legacy:
                graph += install_analysis_str
            return graph

        if self.script_frequency == "R1":
            # Run the analysis once over a custom date range (can match experiment).
            date = self.date_range[1]
            graph += f"R1/{time_dumper.strftime(date, '%Y-%m-%dT00:00:00Z')} = \"\"\"\n"
            if not analysis_only:
                if self.product == "av":
                    graph += f"COMBINE-TIMEAVGS-{chunk}:succeed-all\n"
                else:
                    graph += f"REMAP-PP-COMPONENTS-TS-{chunk}:succeed-all\n"

            # Looping backwards through all previous chunks.
            d = date - chunk
            i = -1
            while d >= self.date_range[0]:
                if not analysis_only:
                    if self.product == "av":
                        graph += f"& COMBINE-TIMEAVGS-{chunk}[{i*chunk}]:succeed-all\n"
                    else:
                        graph += f"& REMAP-PP-COMPONENTS-TS-{chunk}[{i*chunk}]:succeed-all\n"
                i -= 1
                d -= chunk
            if not analysis_only:
                graph += "=>\n"
            if self.product == "ts":
                graph += "data-catalog =>\n"
            graph += f"ANALYSIS-{time_dumper.strftime(self.date_range[0], '%Y')}_{time_dumper.strftime(self.date_range[1], '%Y')}\n"
            if not self.is_legacy:
                graph += f"install-analysis-{self.name}[^] => analysis-{self.name}-{time_dumper.strftime(self.date_range[0], '%Y')}_{time_dumper.strftime(self.date_range[1], '%Y')}"
            graph += f"        \"\"\"\n"
            if not self.is_legacy:
                graph += install_analysis_str
            return graph

        raise NotImplementedError(f"Non-supported analysis script configuration: {self.name}")

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
        else:
            in_data_dir = Path(pp_dir) / self.components[0] / self.product / f"{frequency}_{bronx_chunk}"
        

        legacy_analysis_str = f"""
    [[analysis-{self.name}]]
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
            logger.info(f"ANALYSIS: {self.name}: Will run every chunk {chunk}")
            if self.is_legacy:
                definitions += legacy_analysis_str
            else:
                definitions += new_analysis_str

            # create the task family for all every-interval analysis scripts
            definitions += f"""
    [[ANALYSIS-{chunk}]]
        inherit = ANALYSIS
        [[[environment]]]
            yr1 = $(cylc cycle-point --template=CCYY --offset=-{chunk - one_year})
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

            return definitions

        if self.script_frequency == chunk and self.date_range == self.experiment_date_range \
           and self.cumulative:
            # Case 2: run the analysis every chunk, but depend on all previous chunks too.
            # To make the task run, we will create a task family for
            # each chunk/interval, starting from the beginning of pp data
            # then we create an analysis script task for each of these task families.
            logger.info(f"ANALYSIS: {self.name}: Will run each chunk {chunk} from beginning {self.experiment_date_range[0]}")
            date = self.experiment_date_range[0] + chunk - one_year
            while date <= self.experiment_date_range[1]:
                date_str = time_dumper.strftime(date, '%Y')

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
                year1 = time_dumper.strftime(self.experiment_date_range[0], "%Y")
                year2 = time_dumper.strftime(date, "%Y")
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
                            y1 = f"{int(time_dumper.strftime(dd, '%Y')):04d}"
                            y2 = f"{int(time_dumper.strftime(dd + chunk - one_year, '%Y')):04d}"
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
            d1_str = time_dumper.strftime(d1, '%Y')
            d2_str = time_dumper.strftime(d2, '%Y')
            if self.product == 'av' and not self.cumulative:
                if chunk.years == int(time_dumper.strftime(d2, '%Y')) - int(time_dumper.strftime(d1, '%Y')) + 1:
                    pass
                else:
                    raise NotImplementedError(f"ERROR: Non-supported analysis script configuration: {self.name}: run-once (R1), timeaverages, and non-accumulative is inconsistent, unless duration '{chunk}' represents {self.date_range[0]} through {self.date_range[1]} inclusive.")
            logger.info(f"ANALYSIS: {self.name}: Will run once for time period {self.date_range[0]} to {self.date_range[1]} (chunks {d1_str} to {d2_str})\n")
            date1_str = time_dumper.strftime(self.date_range[0], '%Y')
            date2_str = time_dumper.strftime(self.date_range[1], '%Y')

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
                        y1 = f"{int(time_dumper.strftime(dd, '%Y')):04d}"
                        y2 = f"{int(time_dumper.strftime(dd + chunk - one_year, '%Y')):04d}"
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
            logger.info("must skip analysis {script_name}.")
            continue
        yield script_info


def task_definitions(yaml_, experiment_components, experiment_start, experiment_stop, chunk1, chunk2, pp_dir):
    """Return the task definitions for all user-defined analysis scripts.

    Args:
        yaml_: Dictionary experiment yaml.
        experiment_components: List of string experiment component names.
        experiment_start: Date that the experiment starts at.
        experiment_stop: Date that the experiment stops at.
        chunk1: ISO8601 duration used by the workflow.
        chunk2: If used, second pp chunk used by the workflow.
        pp_dir: postproceessing directory

    Returns:
        String containing the task defintions.
    """
    definitions = ""
    for script_info in task_generator(yaml_, experiment_components, experiment_start, experiment_stop):
        chunk = script_info.choose_pp_chunk(chunk1, chunk2)
        definitions += script_info.definition(chunk, pp_dir)
    return definitions


def task_graph(yaml_, experiment_components, experiment_start, experiment_stop, chunk1, chunk2, analysis_only):
    """Return the task graphs for all user-defined analysis scripts.

    Args:
        yaml_: Dictionary experiment yaml.
        experiment_components: List of string experiment component names.
        experiment_start: Date that the experiment starts at.
        experiment_stop: Date that the experiment stops at.
        chunk1: ISO8601 duration used by the workflow.
        chunk2: If used, second pp chunk used by the workflow.
        analysis_only: Optional boolean to not depend on remap tasks (assume pp files already exist)

    Returns:
        String containing the task graphs.
    """
    graph = ""
    for script_info in task_generator(yaml_, experiment_components, experiment_start, experiment_stop):
        chunk = script_info.choose_pp_chunk(chunk1, chunk2)
        graph += script_info.graph(chunk, analysis_only)
    return graph


def get_analysis_info(experiment_yaml, info_type, experiment_components, pp_dir,
                           experiment_start, experiment_stop, chunk1, chunk2=None, analysis_only=False):
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
        chunk1 (str): Smaller chunk size
        chunk2 (str): Larger chunk size (optional)
        analysis_only (bool): make task graphs not depend on REMAP-PP-COMPONENTS
    """
    # Convert strings to date objects.
    experiment_start = time_parser.parse(experiment_start)
    experiment_stop = time_parser.parse(experiment_stop)
    chunk1 = duration_parser.parse(chunk1)
    if chunk2 is not None:
        chunk2 = duration_parser.parse(chunk2)

    # split the pp_components into a list
    experiment_components = experiment_components.split()

    with open(experiment_yaml) as file_:
        yaml_ = safe_load(file_)
        if info_type == "task-graph":
            return task_graph(yaml_, experiment_components, experiment_start,
                              experiment_stop, chunk1, chunk2, analysis_only)
        elif info_type == "task-definitions":
            return task_definitions(yaml_, experiment_components, experiment_start,
                                   experiment_stop, chunk1, chunk2, pp_dir)
        raise ValueError(f"Invalid information type: {info_type}.")

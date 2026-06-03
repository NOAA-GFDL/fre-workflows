import logging
from pathlib import Path

from metomi.isodatetime.parsers import DurationParser, TimePointParser
from yaml import safe_load

from legacy_date_conversions import convert_iso_duration_to_bronx_chunk

# set up logging
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Global variables just set to reduce typing a little.
duration_parser = DurationParser()
one_year = duration_parser.parse("P1Y")
time_parser = TimePointParser(assumed_time_zone=(0, 0))


class AnalysisScript:
    def __init__(self, name, config, experiment_components, experiment_starting_date,
                 experiment_stopping_date, pp_chunks, yaml):
        """Initialize the analysis script object.

        Args:
            name: String name of the analysis.
            config: Dictionary of analysis script configuration options.
            experiment_components: List of available postprocess component names.
            experiment_starting_date: Starting date for the experiment.
            experiment_stopping_date: Stopping date for the experiment.
            pp_chunks: List of ISO8601 durations used by the workflow.
            yaml: Resolved postprocessing yaml
        """
        self.name = name
        logger.debug(f"{name}: initializing AnalysisScript instance")

        # Skip if configuration wants to skip it
        # user_script_on is an optional key that is True (by default)
        # if not defined in the YAML
        if "user_script_on" in config:
            self.switch = config["user_script_on"]
        else:
            self.switch = True
    
        if self.switch is False:
            return

        if config["install"]["method"] not in ("cshell", "pip", "conda"):
            raise ValueError(f"ERROR: install method must be 'cshell', 'pip', or 'conda'")

        # Skip if the requested components are not available
        self.components = [x.strip() for x in config["workflow"]["components"]]
        for component in self.components:
            if component not in experiment_components:
                raise ValueError(f"ERROR: User script '{self.name}' requests postprocessing component '{component}' but is not one of the available components {experiment_components}. Please add the component or turn the script off.")

        # Parse the rest of the 'workflow' config items
        self.script_type = config["install"]["method"]
        self.when_to_run = config["workflow"]["when_to_run"]
        self.chunk = duration_parser.parse(config["workflow"]["interval"])

        if self.script_type == "cshell":
            self.product = config["data"]["type"]
            self.data_frequency = config["data"]["frequency"]
        elif self.script_type in ("pip", "conda"):
            self.product = config.get("data", {}).get("type", "ts")

            # check for needed pp prerequisites
            if self.product not in ['av', 'ts']:
                raise ValueError("ERROR: product type must be 'ts' or 'av'")
            if self.product == "ts":
                if self.chunk not in pp_chunks:
                    raise ValueError(f"ERROR: Analysis script '{self.name}' requests timeseries chunk size '{self.chunk}', but " +
                                     "this chunk size is not declared in 'pp_chunks'")
            else:
                # Confirm the requested climatology chunk exists for each component
                for ana_comp in config["workflow"]["components"]:
                    found_needed_inputs_for_component = False
                    for exp_comp in yaml["postprocess"]["components"]:
                        if exp_comp["type"] == ana_comp:
                            if 'climatology' in exp_comp:
                                for climo_request in exp_comp["climatology"]:
                                    if climo_request["frequency"] == self.data_frequency and climo_request["interval_years"] == self.chunk.years:
                                        found_needed_inputs_for_component = True
                    if not found_needed_inputs_for_component:
                        raise ValueError(f"ERROR: Analysis script '{self.name}' requests climatology chunk size '{self.chunk}', but " +
                                         f"no suitable climatology sections were found in postprocess component '{ana_comp}'")

        # YAGNI? do scripts really want to specify their own start/stop dates?
        self.date_range            = [experiment_starting_date, experiment_stopping_date]
        self.experiment_date_range = [experiment_starting_date, experiment_stopping_date]

        if self.script_type == "cshell":
            self.cshell_script = config["install"]["path"]
        elif self.script_type == "pip":
            package = config["install"]["package"]
            # Convert SCP-style SSH URL (git@host:user/repo.git) to pip VCS format
            if package.startswith("git@") and ":" in package:
                host, path = package.split(":", 1)
                package = f"git+ssh://{host}/{path}"
            if "branch" in config["install"]:
                package = f"{package}@{config['install']['branch']}"
            self.pip_package = package
            self.pip_entry_point = config["install"]["entry_point"]
            self.pip_python = config["install"]["python"]
        elif self.script_type == "conda":
            self.conda_package = config["install"]["package"]
            self.conda_branch = config["install"].get("branch", None)
            self.conda_environment_file = config["install"].get("environment_file", "environment.yaml")
            self.conda_entry_point = config["install"]["entry_point"]
            self.conda_executable = config["install"]["conda_executable"]

        logger.debug(f"{name}: initialized instance")

    def graph(self):
        """Generate the cylc task graph string for the analysis script.

        Returns:
            String cylc task graph for the analysis.
        """
        if self.switch is False:
            return ""

        graph = ""

        logger.debug(f"script type = {self.script_type}")
        logger.debug(f"chunk size = {self.chunk}")
        logger.debug(f"analysis date range = {self.date_range}")

        date0, date1 = self.date_range

        if self.when_to_run == "independent":
            # Run every chunk (not cumulative)
            suffix = f"{self.chunk}"
            graph += f'{self.chunk} = """\n'

            if self.product == "av":
                dep = f"COMBINE-TIMEAVGS-{self.chunk}:succeed-all"
            else:
                dep = f"REMAP-PP-COMPONENTS-TS-{self.chunk}:succeed-all"

            graph += f"{dep} => data-catalog-{suffix} => ANALYSIS-{suffix}?\n"

            if not self.script_type == "cshell":
                graph += f"install-analysis-{self.name}[^] => analysis-{self.name}"

            graph += f'"""\n'
        elif self.when_to_run == "cumulative":
            # Run every chunk (cumulative)
            deps = []
            d = date0
            while d <= date1:
                year_start = f"{date0.year:04}"
                year_end = f"{(d + self.chunk - one_year).year:04}"
                suffix = f"{self.chunk}-{year_start}_{year_end}"
                graph += f'R1/{d} = """\n'

                if self.product == "av":
                    deps.append(f"COMBINE-TIMEAVGS-{self.chunk}[{d}]:succeed-all")
                else:
                    deps.append(f"REMAP-PP-COMPONENTS-TS-{self.chunk}[{d}]:succeed-all")

                graph += " & ".join(deps) + f" => data-catalog-{suffix} => ANALYSIS-{suffix}\n"

                if not self.script_type == "cshell":
                    graph += f"install-analysis-{self.name}[^] => analysis-{self.name}-{year_start}_{year_end}\n"

                graph += '"""\n'
                d += self.chunk
        else:
            raise NotImplementedError(f"Non-supported analysis script configuration: {self.name}")

        if not self.script_type == "cshell":
            graph += f'R1 = """install-analysis-{self.name}"""\n'

        return graph

    def definition(self, pp_dir):
        """Generate the cylc task definition string for the analysis script.

        Args:
            pp_dir: postprocessing directory

        Returns:
            Cylc task definition string for this analysis script
        """
        if self.switch is False:
            return ""

        definitions = ""

        cmip_to_bronx = {
            "yr": "annual",
            "mon": "monthly",
            "day": "daily",
            "3hr": "3hr",
            "6hr": "6hr",
        }
        if self.script_type == "cshell":
            frequency = cmip_to_bronx[self.data_frequency]
            bronx_chunk = convert_iso_duration_to_bronx_chunk(self.chunk)
            if self.product == "ts":
                in_data_dir = Path(pp_dir) / self.components[0] / self.product / frequency / bronx_chunk
            else:
                in_data_dir = Path(pp_dir) / self.components[0] / self.product / f"{frequency}_{bronx_chunk}"

            script_basename = Path(self.cshell_script).name
            cshell_analysis_str = f"""
    [[analysis-{self.name}]]
        script = '''
# sed-replace lowercase environment variables into the cshell script template
set -o posix
vars=$(set | awk -F '=' '{{ print $1 }}' | grep [a-z])
# WORKDIR is the exception to include
vars="$vars WORKDIR"

# create the sed script
for var in $vars; do
    eval var2=\\$$var
    if [[ -n $var2 ]]; then
        echo "s|set $var\\s*$|set $var = $var2|" >> sed-script
        echo "s|^\\s*$var=\\s*$|$var='$var2'|"    >> sed-script
    fi
done
echo "s|\\$FRE_ANALYSIS_HOME|$FRE_ANALYSIS_HOME|" >> sed-script

# write the filled-in script
if [[ $yr1 == $yr2 ]]; then
    scriptOut=$outputDir/{script_basename}.$yr1
else
    scriptOut=$outputDir/{script_basename}.$yr1-$yr2
fi
mkdir -p $outputDir
sed -f sed-script {self.cshell_script} > $scriptOut
echo "Saved script '$scriptOut'"
ls -l $scriptOut
rm sed-script

# Then, run the script
chmod +x $scriptOut
$scriptOut
        '''
        [[[environment]]]
            # some analysis scripts expect a trailing slash
            in_data_dir = {in_data_dir}/
            freq = {frequency}
            staticfile = {pp_dir}/{self.components[0]}/{self.components[0]}.static.nc
            scriptLabel = {self.name}
            datachunk = {self.chunk.years}
            """

        if self.script_type == "pip":
            pip_analysis_str = f"""
    [[analysis-{self.name}]]
        script = '''
source $venv_dir/bin/activate
{self.pip_entry_point} $case_yaml $settings_yaml $output_dir
        '''
        [[[environment]]]
            venv_dir = $CYLC_WORKFLOW_SHARE_DIR/analysis-venvs/{self.name}
        """
            pip_install_str = f"""
    [[install-analysis-{self.name}]]
        script = '''
{self.pip_python} -m venv $venv_dir
$venv_dir/bin/pip install --upgrade pip setuptools wheel
$venv_dir/bin/pip install {self.pip_package}
        '''
        [[[environment]]]
            venv_dir = $CYLC_WORKFLOW_SHARE_DIR/analysis-venvs/{self.name}
        """

        if self.script_type == "conda":
            branch_arg = f"--branch {self.conda_branch} " if self.conda_branch else ""
            conda_analysis_str = f"""
    [[analysis-{self.name}]]
        script = '''
{self.conda_executable} run --prefix $env_prefix --no-capture-output {self.conda_entry_point} $case_yaml $settings_yaml $output_dir
        '''
        [[[environment]]]
            env_prefix = $CYLC_WORKFLOW_SHARE_DIR/analysis-conda-envs/{self.name}
        """
            conda_install_str = f"""
    [[install-analysis-{self.name}]]
        inherit = BUILD-ANALYSIS
        script = '''
clone_dir=$CYLC_WORKFLOW_SHARE_DIR/analysis-conda-clones/{self.name}
rm -rf $clone_dir $env_prefix
git clone {branch_arg}{self.conda_package} $clone_dir
{self.conda_executable} env create -f $clone_dir/{self.conda_environment_file} --prefix $env_prefix
        '''
        [[[environment]]]
            env_prefix = $CYLC_WORKFLOW_SHARE_DIR/analysis-conda-envs/{self.name}
        """

        if self.when_to_run == "independent":
            # to make the task run, we will create a corresponding task graph below
            # corresponding to the interval (chunk), e.g. ANALYSIS-P1Y.
            # Then, the analysis script will inherit from that family, to enable
            # both the task triggering and the yr1 and datachunk template vars.
            logger.debug(f"{self.name}: Will run every chunk {self.chunk}")
            if self.script_type == "cshell":
                definitions += cshell_analysis_str
            elif self.script_type == "pip":
                definitions += pip_analysis_str
            elif self.script_type == "conda":
                definitions += conda_analysis_str

            # create the task family for all every-interval analysis scripts
            interval_years_minus_one = self.chunk - one_year
            definitions += f"""
    [[data-catalog-{self.chunk}]]
        inherit = DATA-CATALOG
    [[ANALYSIS-{self.chunk}]]
        inherit = ANALYSIS
        [[[environment]]]
            yr1 = $(cylc cycle-point --template=CCYY)
            yr2 = $(cylc cycle-point --template=CCYY --offset-years={interval_years_minus_one.years})
            databegyr = $yr1
            dataendyr = $yr2
            datachunk = {self.chunk.years}
                """

            # inherit from the task family
            definitions += f"""
    [[analysis-{self.name}]]
        inherit = ANALYSIS-{self.chunk}
            """

            # For time averages, set the in_data_file variable (cshell only)
            if self.script_type == "cshell" and self.product == "av":
                if self.data_frequency == "mon":
                    times = '{01,02,03,04,05,06,07,08,09,10,11,12}'
                else:
                    times = 'ann'
                if self.chunk == one_year:
                    years = '$yr1'
                else:
                    years = '$yr1-$yr2'
                definitions += f"""
    [[analysis-{self.name}]]
        [[[environment]]]
            in_data_file = {self.components[0]}.{years}.{times}.nc
                """

            if self.script_type == "pip":
                definitions += pip_install_str
            elif self.script_type == "conda":
                definitions += conda_install_str

            logger.debug(f"{self.name}: Finished determining scripting")
            return definitions

        if self.when_to_run == "cumulative":
            # Case 2: run the analysis every chunk, but depend on all previous chunks too.
            # To make the task run, we will create a task family for
            # each chunk/interval, starting from the beginning of pp data
            # then we create an analysis script task for each of these task families.
            logger.debug(f"{self.name}: Will run each chunk {self.chunk} from beginning {self.experiment_date_range[0]}")
            interval_years_minus_one = self.chunk - one_year
            date = self.experiment_date_range[0]
            while date <= self.experiment_date_range[1]:
                year1 = f"{self.experiment_date_range[0].year:04}"
                year2 = f"{(date + interval_years_minus_one).year:04}"
                date_str = f"{year1}_{year2}"

                # Add the task definition for each ending time.
                definitions += f"""
    [[analysis-{self.name}-{date_str}]]
        inherit = ANALYSIS-{self.chunk}-{date_str}, analysis-{self.name}
                """

                if self.script_type == "cshell":
                    definitions += cshell_analysis_str
                elif self.script_type == "pip":
                    definitions += pip_analysis_str
                elif self.script_type == "conda":
                    definitions += conda_analysis_str

                # Add the task definition family for each ending time.
                definitions += f"""
                    [[data-catalog-{self.chunk}-{date_str}]]
                        inherit = DATA-CATALOG
                    [[ANALYSIS-{self.chunk}-{date_str}]]
                        inherit = ANALYSIS
                        [[[environment]]]
                            yr1 = {year1}
                            yr2 = {year2}
                            databegyr = $yr1
                            dataendyr = $yr2
                """

                # Add the time average in_data_file (cshell only)
                if self.script_type == "cshell" and self.product == "av":
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
                            y2 = f"{(dd + self.chunk - one_year).year:04}"
                            if len(years) > 0:
                                years += ','
                            if y1 == y2:
                                years += f"{y1}"
                            else:
                                years += f"{y1}-{y2}"
                            dd += self.chunk
                    years = "{" + str(years) + "}"
                    definitions += f"""
    [[analysis-{self.name}-{date_str}]]
        [[[environment]]]
            in_data_file = {self.components[0]}.{years}.{times}.nc
                    """
                date += self.chunk

            if self.script_type == "pip":
                definitions += pip_install_str
            elif self.script_type == "conda":
                definitions += conda_install_str

            return definitions

        raise NotImplementedError(f"Non-supported analysis script configuration: {self.name}")


def task_generator(yaml_, experiment_components, experiment_start, experiment_stop, pp_chunks):
    for script_name, script_params in yaml_["final-step-user-scripts"].items():
        # Retrieve information about the script
        script_info = AnalysisScript(script_name, script_params, experiment_components,
                                     experiment_start, experiment_stop, pp_chunks, yaml_)
        if script_info.switch is False:
            logger.debug(f"{script_name}: Skipping, switch set to off")
            continue
        yield script_info


def task_definitions(yaml_, experiment_components, experiment_start, experiment_stop, pp_chunks, pp_dir):
    """Return the task definitions for all user-defined analysis scripts.

    Args:
        yaml_: Dictionary experiment yaml.
        experiment_components: List of string experiment component names.
        experiment_start: Date that the experiment starts at.
        experiment_stop: Date that the experiment stops at.
        pp_chunks: List of ISO8601 durations used by the workflow.
        pp_dir: postprocessing directory

    Returns:
        String containing the task defintions.
    """
    logger.debug("About to generate all task definitions")
    definitions = ""
    for script_info in task_generator(yaml_, experiment_components, experiment_start, experiment_stop, pp_chunks):
        definitions += script_info.definition(pp_dir)
    logger.debug("Finished generating all task definitions")
    return definitions


def task_graph(yaml_, experiment_components, experiment_start, experiment_stop, pp_chunks):
    """Return the task graphs for all user-defined analysis scripts.

    Args:
        yaml_: Dictionary experiment yaml.
        experiment_components: List of string experiment component names.
        experiment_start: Date that the experiment starts at.
        experiment_stop: Date that the experiment stops at.
        pp_chunks: List of ISO8601 durations used by the workflow.

    Returns:
        String containing the task graphs.
    """
    graph = ""
    for script_info in task_generator(yaml_, experiment_components, experiment_start, experiment_stop, pp_chunks):
        graph += script_info.graph()
    return graph


def get_analysis_info(experiment_yaml, info_type, experiment_components, pp_dir,
                           experiment_start, experiment_stop, pp_chunks):
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
        pp_chunks: List of ISO8601 durations used by the workflow.
    """
    logger.debug("get_analysis_info: starting")
    # Convert strings to date objects.
    experiment_start = time_parser.parse(experiment_start)
    experiment_stop = time_parser.parse(experiment_stop)
    pp_chunks = [duration_parser.parse(c) for c in pp_chunks]

    # split the pp_components into a list
    experiment_components = experiment_components.split()

    with open(experiment_yaml) as file_:
        yaml_ = safe_load(file_)
        if info_type == "task-graph":
            logger.debug("get_analysis_info: about to return graph")
            return task_graph(yaml_, experiment_components, experiment_start,
                              experiment_stop, pp_chunks)
        if info_type == "task-definitions":
            logger.debug("get_analysis_info: about to return definitions")
            return task_definitions(yaml_, experiment_components, experiment_start,
                                   experiment_stop, pp_chunks, pp_dir)
        raise ValueError(f"Invalid information type: {info_type}.")

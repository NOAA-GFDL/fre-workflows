import logging
import metomi.isodatetime.dumpers
import metomi.isodatetime.parsers
from yaml import safe_load

from legacy_date_conversions import *
from iter_chunks import iter_chunks

# set up logging
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Global variables just set to reduce typing a little.
duration_parser = metomi.isodatetime.parsers.DurationParser()
one_year = duration_parser.parse("P1Y")
time_dumper = metomi.isodatetime.dumpers.TimePointDumper()
time_parser = metomi.isodatetime.parsers.TimePointParser(assumed_time_zone=(0, 0))

def sort_pp_chunks(unsorted_strings):
    """Create descending list of pp chunk durations"""
    durations = []
    for string in unsorted_strings:
        durations.append(duration_parser.parse(string))
    return sorted(durations, reverse=True)

def lookup_source_for_component(yaml_, component):
    """Return list of history files associated with a pp component"""
    sources = []
    for item in yaml_["postprocess"]["components"]:
        if item["type"] == component:
            for source in item["sources"]:
                sources.append(source["history_file"])
    return sources

class Climatology:
    def __init__(self, component, frequency, interval_years, pp_chunk, sources, grid, pp_start, pp_stop):
        """Initialize the climatology object

        Args:
            component: Data source for the climatology
            frequency: 'mon' or 'yr'
            interval_years: Number of years in the averaging window
            pp_chunk: ISO8601 duration available in timeseries to be used as input
            sources: List of history files
            grid: 'native' or 'regrid-xy/lat_lon.conserve_orderX'
            pp_start: Postprocessing start date (string, e.g. '0001')
            pp_stop: Postprocessing stop date (string, e.g. '0020')
        """
        logger.debug(f"Initializing climatology for component '{component}'")

        self.component = component
        self.frequency = frequency
        self.interval_years = interval_years
        self.pp_chunk = pp_chunk
        self.sources = sources
        self.grid = grid
        self.pp_start = pp_start
        self.pp_stop = pp_stop

        logger.debug(f"component='{component}', frequency='{frequency}', interval_years='{interval_years}', pp_chunk='{pp_chunk}', sources={sources}, grid='{grid}'")

    def graph(self, history_segment, clean_work):
        """Generate the cylc task graph string for the climatology.

        The climatology's own cycle point is anchored at the start of
        the LAST contributing pp_chunk (not the start of the whole
        interval), so that every dependency on an earlier chunk can be
        expressed with a backward (negative) cycle point offset.
        Unsigned/forward offsets are unsafe here: cylc resolves the
        inverse relationship (which climatology instance a given chunk
        feeds) by subtracting the raw offset from the chunk's own cycle
        point, which goes out of bounds for chunks near the start of
        the workflow when the interval spans more than one pp_chunk.
        """

        if self.grid == 'native':
            grid = "native"
        else:
            grid = "regrid"

        graph = ""

        chunks_per_interval = self.interval_years / self.pp_chunk.years
        assert chunks_per_interval == int(chunks_per_interval)
        chunks_per_interval = int(chunks_per_interval)
        lead_years = (chunks_per_interval - 1) * self.pp_chunk.years

        # first, make the climo graphs themselves
        graph += f"+P{lead_years}Y/P{self.interval_years}Y = \"\"\"\n"

        for source in self.sources:
            for count in range(chunks_per_interval):
                connector = "" if count == 0 else " & "
                lookback = lead_years - count * self.pp_chunk.years
                if self.pp_chunk == history_segment:
                    task = f"split-netcdf-{grid}_{source}"
                else:
                    task = f"make-timeseries-{grid}-{self.pp_chunk}_{source}"
                if lookback == 0:
                    graph += f"{connector}{task}"
                else:
                    graph += f"{connector}{task}[-P{lookback}Y]"
            graph += "\n"
            graph += f" => climo-{self.frequency}-P{self.interval_years}Y_{self.component}\n"
            graph += f" => remap-climo-{self.frequency}-P{self.interval_years}Y_{self.component}\n"
            graph += f" => combine-climo-{self.frequency}-P{self.interval_years}Y_{self.component}\n"
            if clean_work:
                graph += f"remap-climo-{self.frequency}-P{self.interval_years}Y_{self.component} => clean-shards-av-P{self.interval_years}Y\n"
                graph += f"combine-climo-{self.frequency}-P{self.interval_years}Y_{self.component} => clean-pp-timeavgs-P{self.interval_years}Y\n"

            # The last chunk of every window shares its cycle point with
            # climo itself, so it can safely reuse the same recurring,
            # offset-free rule.
            if clean_work:
                graph += f"climo-{self.frequency}-P{self.interval_years}Y_{self.component} => clean-shards-ts-P{self.pp_chunk.years}Y\n"

        graph += f"\"\"\"\n"

        if clean_work and chunks_per_interval > 1:
            # The earlier chunks of each window are consumed by a climo
            # instance that occurs LATER than they do, so a relative
            # offset can't express the dependency safely: cylc sanity
            # checks every taskdef at the workflow's initial cycle
            # point regardless of whether that point is really valid
            # for it, and subtracting/adding an offset that large from
            # a cycle point near the start of the workflow goes out of
            # bounds. Absolute cycle points sidestep that arithmetic
            # entirely, so enumerate the actual chunk boundaries here
            # instead of using a generic recurring rule.
            chunk_points = [
                chunk['cycle_point']
                for chunk in iter_chunks(
                    [str(self.pp_chunk)], str(history_segment),
                    self.pp_start, self.pp_stop
                )
            ]
            for window_start in range(0, len(chunk_points), chunks_per_interval):
                window = chunk_points[window_start:window_start + chunks_per_interval]
                if len(window) < chunks_per_interval:
                    # Partial trailing window: no climo instance for it.
                    continue
                climo_point = window[-1]
                for chunk_point in window[:-1]:
                    graph += f"R1/{chunk_point} = \"\"\"\n"
                    graph += (
                        f"climo-{self.frequency}-P{self.interval_years}Y_{self.component}"
                        f"[{climo_point}] => clean-shards-ts-P{self.pp_chunk.years}Y\n"
                    )
                    graph += f"\"\"\"\n"

        return graph

    def definition(self, clean_work):
        """Generate the cylc task definitions for the climatology.
        """
        definitions = ""
        sources = ','.join(self.sources)

        definitions += f"""
    [[climo-{self.frequency}-P{self.interval_years}Y_{self.component}]]
        inherit = MAKE-TIMEAVGS
        [[[environment]]]
            sources = {sources}
            output_interval = P{self.interval_years}Y
            input_interval = P{self.pp_chunk.years}Y
            grid = {self.grid}
            frequency = {self.frequency}
            outputDir = $CYLC_WORKFLOW_SHARE_DIR/shards/av/{self.grid}
        """

        # The climatology's cycle point is anchored at the start of the
        # last contributing pp_chunk (see graph(), above), so the data
        # window spans backward by (chunks_per_interval - 1) chunks and
        # forward through the end of that final chunk.
        chunks_per_interval = int(self.interval_years / self.pp_chunk.years)
        lead_years = (chunks_per_interval - 1) * self.pp_chunk.years
        end_offset = self.pp_chunk - one_year

        if lead_years == 0:
            begin = "$(cylc cycle-point)"
        else:
            begin = f"$(cylc cycle-point --offset=-P{lead_years}Y)"

        definitions += f"""
    [[remap-climo-{self.frequency}-P{self.interval_years}Y_{self.component}]]
        inherit = REMAP-PP-COMPONENTS-AV
        [[[environment]]]
            components = {self.component}
            currentChunk = P{self.interval_years}Y
            begin = {begin}
            end = $(cylc cycle-point --print-year --offset={end_offset})
        """

        definitions += f"""
    [[combine-climo-{self.frequency}-P{self.interval_years}Y_{self.component}]]
        inherit = COMBINE-TIMEAVGS-P{self.interval_years}Y
        [[[environment]]]
            component = {self.component}
            frequency = {self.frequency}
            interval = P{self.interval_years}Y
            end = $(cylc cycle-point --print-year --offset={end_offset})
    [[COMBINE-TIMEAVGS-P{self.interval_years}Y]]
        inherit = COMBINE-TIMEAVGS
        """

        if clean_work:
            definitions += f"""
    [[clean-shards-av-P{self.interval_years}Y]]
        inherit = CLEAN-SHARDS-AV
        [[[environment]]]
            duration = P{self.interval_years}Y
    [[clean-pp-timeavgs-P{self.interval_years}Y]]
        inherit = CLEAN-PP-TIMEAVGS
        [[[environment]]]
            duration = P{self.interval_years}Y
            """

        return definitions

def task_generator(yaml_):
    # Retrieve the pp components
    components = []
    for component in yaml_["postprocess"]["components"]:
        if component.get("postprocess_on", True):
            components.append(component["type"])

    # determine pp chunk to use. require the timeaverage interval to be a multiple of pp chunk
    pp_chunks = yaml_["postprocess"]["settings"]["pp_chunks"]
    pp_start = yaml_["postprocess"]["settings"]["pp_start"]
    pp_stop = yaml_["postprocess"]["settings"]["pp_stop"]

    for component in yaml_["postprocess"]["components"]:
        if not component.get('postprocess_on', True):
            continue
        if 'climatology' in component:
            for item in component['climatology']:
                # determine pp chunk to use. require the timeaverage interval to be a multiple of pp chunk
                interval_years=item["interval_years"]
                for chunk in sort_pp_chunks(pp_chunks):
                    if interval_years % chunk.years == 0:
                        pp_chunk = chunk
                        break
                try:
                    pp_chunk
                except UnboundLocalError:
                    raise Exception(f"Unsupported climatology configuration: Interval in years '{interval_years}' is not a multiple of any pp chunk {pp_chunks}")


                if "xyInterp" in component:
                    lat_lon = component['xyInterp'].split(',')
                    grid = 'regrid-xy/' + lat_lon[0] + '_' + lat_lon[1] + '.' + component['interpMethod']
                else:
                    grid = 'native'

                climatology_info = Climatology(
                    component=component["type"],
                    frequency=item["frequency"],
                    interval_years=interval_years,
                    pp_chunk=pp_chunk,
                    sources=lookup_source_for_component(yaml_, component["type"]),
                    grid=grid,
                    pp_start=pp_start,
                    pp_stop=pp_stop
                )
                yield climatology_info

def task_definitions(yaml_, clean_work):
    """Return the task definitions for all requested climatologies.

    Args:
        yaml_: Dictionary experiment yaml.

    Returns:
        String containing the task defintions.
    """
    logger.debug("About to generate all task definitions")
    definitions = ""
    for script_info in task_generator(yaml_):
        definitions += script_info.definition(clean_work)
    logger.debug("Finished generating all task definitions")
    return definitions

def task_graphs(yaml_, history_segment, clean_work):
    """Return the task graphs for all requested climatologies.

    Args:
        yaml_: Dictionary experiment yaml.
        history_segment: ISO duration
        clean_work: Boolean, whether to clean work directories

    Returns:
        String containing the task graphs.
    """
    logger.debug("About to generate all task graphs")
    graph = ""
    for script_info in task_generator(yaml_):
        graph += script_info.graph(history_segment, clean_work)
    logger.debug("Finished generating all task graphs")
    return graph

def get_climatology_info(experiment_yaml, info_type):
    """Return requested climatology information from the experiment yaml

    Args:
        experiment_yaml: Path to the experiment yaml file.
        info_type: String that tells which kind of output to make (graph or definition).
        clean_work: Boolean, whether to clean work directories
    """
    logger.debug("get_climatology_info: starting")

    # define valid info types
    valid_types = ["task-graph", "task-definitions"]
    if info_type not in valid_types:
        raise ValueError(f"Invalid information type: {info_type}. Valid types include task-graph or task-definitions")
 
    with open(experiment_yaml) as file_:
        yaml_ = safe_load(file_)

        clean_work = yaml_["postprocess"]["switches"]["clean_work"]
        history_segment = duration_parser.parse(yaml_["postprocess"]["settings"]["history_segment"])

        if info_type == "task-graph":
            logger.debug("about to return graph")
            return task_graphs(yaml_, history_segment, clean_work)
        if info_type == "task-definitions":
            logger.debug("about to return definitions")
            return task_definitions(yaml_, clean_work)

# example for interactive testing
#print(get_climatology_info('ESM4.5_candidateA.yaml', 'task-definitions'))

from pathlib import Path

import metomi.isodatetime.dumpers
import metomi.isodatetime.parsers
from yaml import safe_load
import pprint

from legacy_date_conversions import *

# set up logging
import logging
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Global variables just set to reduce typing a little.
duration_parser = metomi.isodatetime.parsers.DurationParser()
one_year = duration_parser.parse("P1Y")
time_dumper = metomi.isodatetime.dumpers.TimePointDumper()
time_parser = metomi.isodatetime.parsers.TimePointParser(assumed_time_zone=(0, 0))

def sort_pp_chunks(unsorted_strings):
    """Create descending list of pp chunk durations"""
    durations = []
    for s in unsorted_strings:
        durations.append(duration_parser.parse(s))
    return(sorted(durations, reverse=True))

def lookup_source_for_component(yaml_, component):
    """Return list of history files associated with a pp component"""
    sources = []
    for item in yaml_["postprocess"]["components"]:
        if item["type"] == component:
            for source in item["sources"]:
                sources.append(source["history_file"])
    return(sources)

class Climatology(object):
    def __init__(self, component, frequency, interval_years, pp_chunk, sources, grid):
        """Initialize the climatology object

        Args:
            component: Data source for the climatology
            frequency: 'mon' or 'yr'
            interval_years: Number of years in the averaging window
            pp_chunk: ISO8601 duration available in timeseries to be used as input
            sources: List of history files
            grid: 'native' or 'regrid-xy/lat_lon.conserve_orderX'
        """
        logger.debug(f"Initializing climatology for component '{component}'")

        self.component = component
        self.frequency = frequency
        self.interval_years = interval_years
        self.pp_chunk = pp_chunk
        self.sources = sources
        self.grid = grid

        logger.debug(f"component='{component}', frequency='{frequency}', interval_years='{interval_years}', pp_chunk='{pp_chunk}', sources={sources}, grid='{grid}'")

    def graph(self, history_segment, clean_work):
        """Generate the cylc task graph string for the climatology.
        """

        if self.grid == 'native':
            grid = "native"
        else:
            grid = "regrid"

        # Use pp_chunk recurrence to ensure source tasks exist at all required cycle points
        graph = f"P{self.pp_chunk.years}Y = \"\"\"\n"

        # Calculate how many pp_chunks fit in one interval
        chunks_per_interval = self.interval_years / self.pp_chunk.years
        assert chunks_per_interval == int(chunks_per_interval)
        chunks_per_interval = int(chunks_per_interval)
        
        for index, source in enumerate(self.sources):
            count = 0
            while count < chunks_per_interval:
                if index == 0:
                    connector = ""
                else:
                    connector = " & "
                if count == 0:
                    if self.pp_chunk == history_segment:
                        graph += f"{connector}rename-split-to-pp-{grid}_{source}"
                    else:
                        graph += f"{connector}make-timeseries-{grid}-{self.pp_chunk}_{source}"
                else:
                    offset = count * self.pp_chunk
                    if self.pp_chunk == history_segment:
                        graph += f" & rename-split-to-pp-{grid}_{source}[{offset}]"
                    else:
                        graph += f" & make-timeseries-{grid}-{self.pp_chunk}_{source}[{offset}]"
                count += 1
            graph += "\n"
            #if clean_work:
            #    graph += f"    make-timeavgs-{grid}-P{self.interval_years}Y_{source}"
            #    count = 0
            #    while count < chunks_per_interval:
            #        if count == 0:
            #            graph += f" => clean-shards-{self.pp_chunk}"
            #        else:
            #            offset = count * self.pp_chunk
            #            graph += f" & clean-shards-{self.pp_chunk}[{offset}]"
            #        count += 1
            #    graph += "\n"
        # Climatology tasks run at the same cycle points as the dependencies (no offset)
        # They will naturally run at pp_chunk intervals, processing interval_years of data
        graph += f" => climo-{self.frequency}-P{self.interval_years}Y_{self.component}\n"
        graph += f" => remap-climo-{self.frequency}-P{self.interval_years}Y_{self.component}\n"
        graph += f" => combine-climo-{self.frequency}-P{self.interval_years}Y_{self.component}\n"

        graph += f"\"\"\"\n"

        # Clean tasks should use correct dependency offsets to ensure they wait for the right climo task.
        # For a P2Y interval with P1Y chunks, climo at 1980 processes 1980-1981 data.
        # So clean-shards at both 1980 and 1981 should depend on the climo at 1980.
        # We achieve this by creating separate recurrence patterns for each offset within the interval:
        #   P2Y = "climo => clean-shards"           # 1980, 1982, 1984, ... (no offset)
        #   P2Y/+P1Y = "climo[-P1Y] => clean-shards"  # 1981, 1983, 1985, ... (offset -P1Y)
        if clean_work:
            for offset_index in range(chunks_per_interval):
                # Calculate offset as a duration (metomi.isodatetime duration object)
                # Multiplying an integer by a duration object produces a new duration
                offset = offset_index * self.pp_chunk
                
                # Create recurrence pattern
                if offset_index == 0:
                    # First cycle point in each interval - no offset in recurrence or dependency
                    recurrence = f"P{self.interval_years}Y"
                    offset_str = ""
                else:
                    # Subsequent cycle points - offset recurrence start, and offset dependency backwards
                    recurrence = f"P{self.interval_years}Y/+{offset}"
                    offset_str = f"[-{offset}]"
                
                graph += f"{recurrence} = \"\"\"\n"
                graph += f"climo-{self.frequency}-P{self.interval_years}Y_{self.component}{offset_str}         => clean-shards-ts-P{self.pp_chunk.years}Y\n"
                graph += f"remap-climo-{self.frequency}-P{self.interval_years}Y_{self.component}{offset_str}   => clean-shards-av-P{self.interval_years}Y\n"
                graph += f"combine-climo-{self.frequency}-P{self.interval_years}Y_{self.component}{offset_str} => clean-pp-timeavgs-P{self.interval_years}Y\n"
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

        offset = duration_parser.parse(f"P{self.interval_years}Y") - one_year

        definitions += f"""
    [[remap-climo-{self.frequency}-P{self.interval_years}Y_{self.component}]]
        inherit = REMAP-PP-COMPONENTS-AV
        [[[environment]]]
            components = {self.component}
            currentChunk = P{self.interval_years}Y
            begin = $(cylc cycle-point)
            end = $(cylc cycle-point --print-year --offset={offset})
        """

        definitions += f"""
    [[combine-climo-{self.frequency}-P{self.interval_years}Y_{self.component}]]
        inherit = COMBINE-TIMEAVGS
        [[[environment]]]
            component = {self.component}
            frequency = {self.frequency}
            interval = P{self.interval_years}Y
            end = $(cylc cycle-point --print-year --offset={offset})
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
    history_segment = yaml_["postprocess"]["settings"]["history_segment"]

    # Retrieve the pp components
    components = []
    for component in yaml_["postprocess"]["components"]:
        if component["postprocess_on"] is True:
            components.append(component["type"])

    # determine pp chunk to use. require the timeaverage interval to be a multiple of pp chunk
    pp_chunks = yaml_["postprocess"]["settings"]["pp_chunks"]

    for component in yaml_["postprocess"]["components"]:
        if not component['postprocess_on']:
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
                    grid=grid
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
        elif info_type == "task-definitions":
            logger.debug("about to return definitions")
            return task_definitions(yaml_, clean_work)

# example for interactive testing
#print(get_climatology_info('ESM4.5_candidateA.yaml', 'task-definitions'))

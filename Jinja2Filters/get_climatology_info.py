from pathlib import Path

import metomi.isodatetime.dumpers
import metomi.isodatetime.parsers
from yaml import safe_load

from legacy_date_conversions import *

# set up logging
import logging
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Global variables just set to reduce typing a little.
duration_parser = metomi.isodatetime.parsers.DurationParser()
one_year = duration_parser.parse("P1Y")
time_dumper = metomi.isodatetime.dumpers.TimePointDumper()
time_parser = metomi.isodatetime.parsers.TimePointParser(assumed_time_zone=(0, 0))

class Climatology(object):
    def __init__(self, component, frequency, interval_years):
        """Initialize the climatology object

        Args:
            component: Data source for the climatology
            frequency: 'mon' or 'yr'
            interval_years: Number of years in the averaging window
        """
        logger.debug(f"Initializing climatology for component '{component}'")

        self.component = component
        self.frequency = frequency
        self.interval_years = interval_years

    def graph(self):
        """Generate the cylc task graph string for the climatology.
        """

        return graph

    def definition(self:
        """Generate the cylc task definitions for the climatology.
        """

        return definitions

def task_generator(yaml_):
    for component in yaml_["postprocess"]["components"]:
        if 'climatology' in component:
            for item in array:
                frequency = component["climatology"]["frequency"]
                interval_years = component["climatology"]["interval_years"]
                climatology_info = Climatology(component, frequency, interval_years)
                yield climatology_info

def task_definitions(yaml_):
    """Return the task definitions for all requested climatologies.

    Args:
        yaml_: Dictionary experiment yaml.

    Returns:
        String containing the task defintions.
    """
    logger.debug("About to generate all task definitions")
    definitions = ""
    for script_info in task_generator(yaml_):
        definitions += script_info.definition(chunk)
    logger.debug("Finished generating all task definitions")
    return definitions

def task_graphs(yaml_):
    """Return the task graphs for all requested climatologies.

    Args:
        yaml_: Dictionary experiment yaml.

    Returns:
        String containing the task graphs.
    """
    logger.debug("About to generate all task graphs")
    graph = ""
    for script_info in task_generator(yaml_):
        graph += script_info.graph(chunk)
    logger.debug("Finished generating all task graphs")
    return graph

def get_climatology_info(experiment_yaml, info_type):
    """Return requested climatology information from the experiment yaml

    Args:
        experiment_yaml: Path to the experiment yaml file.
        info_type: String that tells which kind of output to make (graph or definition).
    """
    logger.debug("get_climatology_info: starting")
    
    with open(experiment_yaml) as file_:
        yaml_ = safe_load(file_)

        # Convert strings to date objects.
        experiment_start = time_parser.parse(experiment_start)
        experiment_stop = time_parser.parse(experiment_stop)
        chunk1 = duration_parser.parse(chunk1)
        if chunk2 is not None:
            chunk2 = duration_parser.parse(chunk2)

        # split the pp_components into a list
        experiment_components = experiment_components.split()

        if info_type == "task-graph":
            logger.debug("about to return graph")
            return task_graphs(yaml_)
        elif info_type == "task-definitions":
            logger.debug("about to return definitions")
            return task_definitions(yaml_)
        raise ValueError(f"Invalid information type: {info_type}.")

import re
import os
from pathlib import Path
import yaml

# set up logging
import logging
logging.basicConfig(level=logging.INFO)
fre_logger = logging.getLogger(__name__)

def get_components(yamlfile):
    """Retrieve active pp components from the yaml

    Arguments:
        yamlfile (str): Filepath to the yaml
"""
    fre_logger.debug(f"Yaml file: {yamlfile}")
    components = []

    with open(yamlfile) as file_:
        yaml_ = yaml.safe_load(file_)

        for component in yaml_["postprocess"]["components"]:
            if component['postprocess_on'] is True:
                components.append(component["type"])

    # we want to return a list, but some other scripts are expecting a space-separated string
    #return(components)
    return(" ".join(components))

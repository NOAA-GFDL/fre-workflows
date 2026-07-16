"""
Return a space separated string of components to be post-processed.
"""
import logging
import yaml

# set up logging
logging.basicConfig(level=logging.INFO)
fre_logger = logging.getLogger(__name__)

def get_components(yamlfile):
    """
    Retrieve active pp components from the yaml

    :param yamlfile: Filepath to the yaml
    :type yamlfile: str
    :return: Space separated string of components to be post-processed
    :rtype: str
    """
    fre_logger.debug("Yaml file: %s", yamlfile)

    components = []
    with open(yamlfile) as file_:
        yaml_ = yaml.safe_load(file_)

        for component in yaml_["postprocess"]["components"]:
            # if postprocess_on key exists, evaluate value
            if "postprocess_on" in component:
                if component['postprocess_on'] is True:
                    components.append(component["type"])
                    fre_logger.info("%s to be post-processed", component["type"])
                else:
                    fre_logger.info("%s will NOT be post-processed", component["type"])
            else:
                # default is True, if not set
                components.append(component["type"])
                fre_logger.info("%s to be post-processed", component["type"])

    # we want to return a list, but some other scripts are expecting a space-separated string
    #return(components)
    return " ".join(components)

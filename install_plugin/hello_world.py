from cylc.flow import LOG
from pathlib import Path
import yaml

def pre_configure(srcdir=None, opts=None, rundir="/home/Dana.Singh/cylc-run"):
    LOG.info("PLUGIN OUTPUT")
    LOG.info("Hello world. How the heck are you?")

    yml_info = {}
    yaml_file = Path(f"{srcdir}/resolved.yaml")
    if yaml_file:
        yf = yaml_file #[0]
        with open(yf, 'r') as f:
            yml_info = yaml.safe_load(f)

    LOG.info(yml_info)
    if yml_info:
        return {'template_variables': {'yml': yml_info},
                'templating_detected': 'jinja2'}
    else:
        return {}

####another things to try
#    if yml_info:
#        jinja2vars['yml_info'] = yml_info
#
#    return {'templating_detected': 'jinja2'}
####

## want this script to accept resolved yaml and create everything needed to run workflow
# - in dictionary format
# - gets rid of rose-suite.conf
# - removes dependency on cylc-rose...I think

## questions/notes:
# - can function in this script be anything? or does it need to be post_install to be recognized? (as a plugin type)
# - I think it can be anything as long as its registered under one of the plugin types in setup.py 

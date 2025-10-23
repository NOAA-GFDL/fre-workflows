#test analysis_validator macro

import pytest
from meta.lib.python.macros.analysis_validator import Analysis_Validator
from metomi.rose.config import load, ConfigNode 
import configparser

def test_skip_analysis_validator():
   '''checks that analysis validation is skipped if no analysis is requested.'''
   validator = Analysis_Validator()
   config_node = ConfigNode()
   config=config_node.set(keys=['template variables','DO_ANALYSIS'], value='False')
   config=config_node.set(keys=['template variables','DO_ANALYSIS_ONLY'], value='False')
   output = validator.validate(config=config,
                               meta_config=None)
   assert [] == output

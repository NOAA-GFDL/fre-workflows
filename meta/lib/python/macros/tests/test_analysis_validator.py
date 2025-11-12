'''
tests for analysis_validator
'''

from metomi.rose.config import ConfigNode

from meta.lib.python.macros.analysis_validator import Analysis_Validator # pylint: disable=import-error

def test_skip_analysis_validator():
    '''
    checks that analysis validation passes no analysis is requested. 
    
    passing here means an empty list, i.e. no "reports"
    '''
    validator = Analysis_Validator()
    config_node = ConfigNode()
    config = config_node.set( keys = ['template variables', 'DO_ANALYSIS'], value = 'False' )
    config = config_node.set( keys = ['template variables', 'DO_ANALYSIS_ONLY'], value = 'False' )
    output = validator.validate( config = config,
                                 meta_config = None )
    assert [] == output

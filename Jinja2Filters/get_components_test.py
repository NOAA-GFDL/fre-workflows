import pytest
import yaml
import metomi.isodatetime.parsers
from . import get_components

CONFIG = {'postprocess': {'components': [{'postprocess_on': True, 'type': 'comp1'},
                                       {'postprocess_on': True, 'type': 'comp2'},
                                       {'postprocess_on': False, 'type': 'comp3'}]}}

def test_get_components(tmp_path):
    """Give 2 active components and one inactive component, expect the first two back"""
    # create temporary directory
    temp_dir = tmp_path
    temp_dir.mkdir(exist_ok=True)

    # write sample configuration to yaml
    temp_file = temp_dir / 'config.yaml'
    with open(temp_file, 'w') as file_:
        yaml.dump(CONFIG, file_)

    assert 'comp1 comp2' == get_components.get_components((temp_file))

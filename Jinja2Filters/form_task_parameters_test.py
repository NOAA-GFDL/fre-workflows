import pytest
import yaml
from . import form_task_parameters

@pytest.fixture()
def yaml_file(tmp_path):
    """example atmos and land component yaml"""
    CONFIG = {'postprocess': {'components': [{'postprocess_on': True,
                                 'sources': [{'history_file': 'atmos_month'},
                                             {'history_file': 'atmos_daily'}],
                                 'static': [{'source': 'atmos_month'},
                                            {'source': 'grid_spec'}],
                                 'type': 'atmos',
                                 'xyInterp': 'true'},
                                {'postprocess_on': True,
                                 'sources': [{'history_file': 'land_month'},
                                             {'history_file': 'land_daily'}],
                                 'static': [{'source': 'land_static'}],
                                 'type': 'land',
                                 'xyInterp': 'true'},
                                {'postprocess_on': True,
                                 'sources': [{'history_file': 'land_month'},
                                             {'history_file': 'land_daily'},
                                             {'history_file': 'river'}],
                                 'static': [{'source': 'land_static'}],
                                 'type': 'land_cubic'}]}}

    # create temporary directory
    temp_dir = tmp_path
    temp_dir.mkdir(exist_ok=True)

    # write sample configuration to yaml
    yaml_file = temp_dir / 'config.yaml'
    with open(yaml_file, 'w') as file_:
        yaml.dump(CONFIG, file_)

    yield(yaml_file)

def test_retrieve_only_atmos(yaml_file):
    """Retrieve only atmos component"""
    assert 'atmos_daily, atmos_month' == form_task_parameters.form_task_parameters('regrid-xy', 'temporal', 'atmos', yaml_file)
    assert 'atmos_month, grid_spec' == form_task_parameters.form_task_parameters('regrid-xy', 'static', 'atmos', yaml_file)

def test_no_results_found(yaml_file):
    """Empty if no history files match the search, atmos does not have native, and foo does not exist"""
    assert '' == form_task_parameters.form_task_parameters('native', 'temporal', 'atmos', yaml_file)
    assert '' == form_task_parameters.form_task_parameters('native', 'temporal', 'foo', yaml_file)

def test_retrieve_both_atmos_and_land(yaml_file):
    """Retrieve both atmos and land"""
    assert 'atmos_daily, atmos_month, land_daily, land_month' == form_task_parameters.form_task_parameters('regrid-xy', 'temporal', 'atmos land land_cubic', yaml_file)
    assert 'atmos_month, grid_spec, land_static'              == form_task_parameters.form_task_parameters('regrid-xy', 'static', 'atmos land land_cubic', yaml_file)
    assert 'land_daily, land_month, river'                    == form_task_parameters.form_task_parameters('native', 'temporal', 'atmos land land_cubic', yaml_file)
    assert 'land_static'                                      == form_task_parameters.form_task_parameters('native', 'static', 'atmos land land_cubic', yaml_file)

# This test does not work but Chris cannot figure out why.
# It fails with the same error we're trying to check for:
# E       FileNotFoundError: [Errno 2] No such file or directory: '/nbhome/c2b/git/fre-workflows/not-here'
# It looks good based on https://docs.pytest.org/en/stable/how-to/assert.html
#def test_file_not_found():
#    """Raise FileNotFoundError if yamlfile does not exist"""
#    with pytest.raises(RuntimeError) as excinfo:
        #raise FileNotFoundError
        #form_task_parameters.form_task_parameters('native', 'temporal', 'foo', 'not-here')
#    assert excinfo.type is FileNotFoundError

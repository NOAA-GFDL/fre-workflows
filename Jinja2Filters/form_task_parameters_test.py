import pytest
import yaml
import metomi.isodatetime.parsers
from . import form_task_parameters

# example atmos and land component mapping
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

def test(tmp_path):
    # create temporary directory
    temp_dir = tmp_path
    temp_dir.mkdir(exist_ok=True)

    # write sample configuration to yaml
    yaml_file = temp_dir / 'config.yaml'
    with open(yaml_file, 'w') as file_:
        yaml.dump(CONFIG, file_)

    # Retrieve only atmos component
    assert 'atmos_daily, atmos_month' == form_task_parameters.form_task_parameters('regrid-xy', 'temporal', 'atmos', yaml_file)
    assert 'atmos_month, grid_spec' == form_task_parameters.form_task_parameters('regrid-xy', 'static', 'atmos', yaml_file)

    # Empty if no history files
    assert '' == form_task_parameters.form_task_parameters('native', 'temporal', 'atmos', yaml_file)
    assert '' == form_task_parameters.form_task_parameters('native', 'temporal', 'foo', yaml_file)

    # Retrieve both atmos and land
    assert 'atmos_daily, atmos_month, land_daily, land_month' == form_task_parameters.form_task_parameters('regrid-xy', 'temporal', 'atmos land', yaml_file)
    assert 'atmos_month, grid_spec, land_static' == form_task_parameters.form_task_parameters('regrid-xy', 'static', 'atmos land', yaml_file)
    assert 'land_daily, land_month, river' == form_task_parameters.form_task_parameters('native', 'temporal', 'land_cubic', yaml_file)
    assert 'land_static' == form_task_parameters.form_task_parameters('native', 'static', 'land_cubic', yaml_file)

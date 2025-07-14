import pytest
import yaml
from . import form_remap_dep

@pytest.fixture()
def sample_yaml(tmp_path):
    """Create sample pp yaml that contains atmos and land components"""

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


def test_regrid_one_one(sample_yaml):
    """atmos regrid 1-year history to 1-year timeseries"""
    result = "rename-split-to-pp-regrid_atmos_daily & rename-split-to-pp-regrid_atmos_month => remap-pp-components-ts-P1Y_atmos\n"
    assert result == form_remap_dep.form_remap_dep(grid_type='regrid-xy',
                                                   temporal_type='temporal',
                                                   chunk='P1Y',
                                                   pp_components_str='atmos',
                                                   output_type='ts',
                                                   yamlfile=sample_yaml,
                                                   history_segment='P1Y')

def test_regrid_two_one(sample_yaml):
    """atmos regrid 2-year history to 1-year timeseries"""
    result = "make-timeseries-regrid-P2Y_atmos_daily & make-timeseries-regrid-P2Y_atmos_month => remap-pp-components-ts-P2Y_atmos\n"
    assert result == form_remap_dep.form_remap_dep(grid_type='regrid-xy',
                                                   temporal_type='temporal',
                                                   chunk='P2Y',
                                                   pp_components_str='atmos',
                                                   output_type='ts',
                                                   yamlfile=sample_yaml,
                                                   history_segment='P1Y')

def test_regrid_two_one(sample_yaml):
    """atmos and land regrid 2-year history to 1-year timeseries"""
    result = "make-timeseries-regrid-P2Y_atmos_daily & make-timeseries-regrid-P2Y_atmos_month => remap-pp-components-ts-P2Y_atmos\nmake-timeseries-regrid-P2Y_land_daily & make-timeseries-regrid-P2Y_land_month => remap-pp-components-ts-P2Y_land\n"

    assert result == form_remap_dep.form_remap_dep(grid_type='regrid-xy',
                                                   temporal_type='temporal',
                                                   chunk='P2Y',
                                                   pp_components_str='atmos land land_cubic',
                                                   output_type='ts',
                                                   yamlfile=sample_yaml,
                                                   history_segment='P1Y')

def test_native_one_one(sample_yaml):
    """land native 1-year history to 1-year timeseries"""
    result = "rename-split-to-pp-native_land_daily & rename-split-to-pp-native_land_month & rename-split-to-pp-native_river => remap-pp-components-ts-P1Y_land_cubic\n"
    assert result == form_remap_dep.form_remap_dep(grid_type='native',
                                                   temporal_type='temporal',
                                                   chunk='P1Y',
                                                   pp_components_str='atmos land land_cubic',
                                                   output_type='ts',
                                                   yamlfile=sample_yaml,
                                                   history_segment='P1Y')

import pytest
import yaml
from Jinja2Filters import get_climatology_info

CONFIG = {'postprocess': {'components': [{'postprocess_on': True,
                                           'type': 'comp1',
                                           'sources': [{'history_file': 'comp1_month'}],
                                           'climatology': [{'frequency': 'mon', 'interval_years': 2}]},
                                          {'type': 'comp2',
                                           'sources': [{'history_file': 'comp2_month'}],
                                           'climatology': [{'frequency': 'mon', 'interval_years': 2}]},
                                          {'postprocess_on': False,
                                           'type': 'comp3',
                                           'sources': [{'history_file': 'comp3_month'}],
                                           'climatology': [{'frequency': 'mon', 'interval_years': 2}]}],
                          'settings': {'pp_chunks': ['P1Y'],
                                       'history_segment': 'P1Y'},
                          'switches': {'clean_work': False}}}


@pytest.fixture()
def sample_yaml(tmp_path):
    """Create sample pp yaml with one component explicitly on, one with
    postprocess_on omitted (should default to on), and one explicitly off"""
    temp_dir = tmp_path
    temp_dir.mkdir(exist_ok=True)

    yaml_file = temp_dir / 'config.yaml'
    with open(yaml_file, 'w') as file_:
        yaml.dump(CONFIG, file_)

    yield yaml_file


def test_postprocess_on_omitted_defaults_to_on(sample_yaml):
    """comp1 (explicitly on) and comp2 (postprocess_on omitted) should be
    included; comp3 (explicitly off) should be excluded"""
    result = get_climatology_info.get_climatology_info(sample_yaml, 'task-definitions')

    assert 'climo-mon-P2Y_comp1' in result
    assert 'climo-mon-P2Y_comp2' in result
    assert 'climo-mon-P2Y_comp3' not in result


def test_postprocess_on_omitted_defaults_to_on_graph(sample_yaml):
    """Same as above, but for the task-graph output"""
    result = get_climatology_info.get_climatology_info(sample_yaml, 'task-graph')

    assert 'climo-mon-P2Y_comp1' in result
    assert 'climo-mon-P2Y_comp2' in result
    assert 'climo-mon-P2Y_comp3' not in result

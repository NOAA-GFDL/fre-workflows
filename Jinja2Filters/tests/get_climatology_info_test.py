import shutil
import subprocess
import textwrap

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
                                       'history_segment': 'P1Y',
                                       'pp_start': '0001',
                                       'pp_stop': '0002'},
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


@pytest.mark.skipif(shutil.which('cylc') is None, reason='cylc is not installed')
@pytest.mark.parametrize('interval_years,clean_work', [(1, False), (1, True),
                                                         (4, False), (4, True)])
def test_multi_chunk_climatology_is_a_valid_cylc_graph(tmp_path, interval_years, clean_work):
    """A climatology interval that spans more than one pp_chunk (e.g. a
    P4Y climatology built from P1Y chunks) must produce a task graph
    that cylc can actually validate, not just one that contains the
    expected substrings.

    This is a regression test for a bug where make-timeseries[+offset]
    (and later climo[+offset]) dependencies underflowed a TimePoint
    year when cylc sanity-checked tasks at the workflow's initial
    cycle point, crashing `cylc validate` with e.g.
    "Cannot dump TimePoint year: -14 not in bounds 0 to 9999" -- but
    only for climatologies needing more than one chunk (interval_years
    == pp_chunk size always worked, which is why the bug went
    unnoticed for single-chunk climatologies).
    """
    config = {
        'postprocess': {
            'components': [{
                'type': 'comp1',
                'sources': [{'history_file': 'comp1_month'}],
                'climatology': [{'frequency': 'yr', 'interval_years': interval_years}],
            }],
            'settings': {'pp_chunks': ['P1Y'],
                         'history_segment': 'P1Y',
                         'pp_start': '0001',
                         'pp_stop': '0004'},
            'switches': {'clean_work': clean_work},
        }
    }
    yaml_file = tmp_path / 'config.yaml'
    with open(yaml_file, 'w') as file_:
        yaml.dump(config, file_)

    graph = get_climatology_info.get_climatology_info(yaml_file, 'task-graph')
    definitions = get_climatology_info.get_climatology_info(yaml_file, 'task-definitions')

    flow_cylc = tmp_path / 'flow.cylc'
    flow_cylc.write_text(
        "[scheduler]\n"
        "    allow implicit tasks = True\n"
        "[scheduling]\n"
        "    initial cycle point = 0001\n"
        "    final cycle point = 0004\n"
        "    [[graph]]\n"
        + textwrap.indent(graph, ' ' * 8) + "\n"
        "[runtime]\n"
        "    [[MAKE-TIMEAVGS]]\n"
        "        script = true\n"
        "    [[REMAP-PP-COMPONENTS-AV]]\n"
        "        script = true\n"
        "    [[COMBINE-TIMEAVGS]]\n"
        "        script = true\n"
        "    [[CLEAN]]\n"
        "        script = true\n"
        "    [[CLEAN-SHARDS-AV]]\n"
        "        inherit = CLEAN\n"
        "    [[CLEAN-PP-TIMEAVGS]]\n"
        "        inherit = CLEAN\n"
        + textwrap.indent(definitions, ' ' * 4)
    )

    result = subprocess.run(
        ['cylc', 'validate', str(tmp_path)],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr

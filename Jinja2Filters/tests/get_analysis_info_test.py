import pytest
import yaml
from Jinja2Filters import get_analysis_info


def _write_yaml(tmp_path, product, interval_years):
    config = {
        'postprocess': {
            'components': [{
                'type': 'comp1',
                'sources': [{'history_file': 'comp1_month'}],
                'climatology': [{'frequency': 'mon', 'interval_years': interval_years}],
            }],
        },
        'analysis': {
            'ana1': {
                'legacy': {'script': '/path/to/ana1.csh'},
                'required': {'data_frequency': 'mon', 'date_range': [1, 1]},
                'workflow': {'components': ['comp1'],
                             'product': product,
                             'script_type': 'independent',
                             'chunk_size': f'P{interval_years}Y'},
            },
        },
    }
    yaml_file = tmp_path / 'config.yaml'
    with open(yaml_file, 'w') as file_:
        yaml.dump(config, file_)
    return yaml_file


@pytest.mark.parametrize('interval_years,pp_stop,expected_header', [
    # remainder chunk 0006-0007 is partial, so only one complete chunk
    (5, '0007', 'R1/0001-01-01T00:00:00Z/P5Y'),
    # no remainder
    (5, '0010', 'R2/0001-01-01T00:00:00Z/P5Y'),
    (2, '0007', 'R3/0001-01-01T00:00:00Z/P2Y'),
])
def test_independent_av_analysis_skips_partial_chunk(tmp_path, interval_years,
                                                     pp_stop, expected_header):
    """Independent timeaverage analyses depend on climatologies, which are
    only made for complete chunks, so their recurrence must stop before a
    trailing partial chunk. Regression test for issue #267, where the
    analysis graph pulled in combine-climo tasks at the partial chunk.
    """
    yaml_file = _write_yaml(tmp_path, 'av', interval_years)
    graph = get_analysis_info.get_analysis_info(
        yaml_file, 'task-graph', 'comp1', '/pp', '0001', pp_stop,
        [f'P{interval_years}Y'])

    assert graph.startswith(f'{expected_header} = """\n')
    assert 'COMBINE-TIMEAVGS-' in graph
    # trigger the script's own task: the ANALYSIS-<chunk> family would also
    # pull in av scripts at the partial chunk via any ts script's graph
    assert '=> analysis-ana1?' in graph


def test_independent_av_analysis_with_no_complete_chunk(tmp_path):
    """If no chunk is complete, there are no climatologies to analyze."""
    yaml_file = _write_yaml(tmp_path, 'av', 5)
    graph = get_analysis_info.get_analysis_info(
        yaml_file, 'task-graph', 'comp1', '/pp', '0001', '0003', ['P5Y'])

    assert graph == ''


def test_independent_ts_analysis_includes_partial_chunk(tmp_path):
    """Timeseries are made for partial chunks too, so timeseries analyses
    keep recurring every chunk."""
    yaml_file = _write_yaml(tmp_path, 'ts', 5)
    graph = get_analysis_info.get_analysis_info(
        yaml_file, 'task-graph', 'comp1', '/pp', '0001', '0007', ['P5Y'])

    assert graph.startswith('P5Y = """\n')
    assert '=> analysis-ana1?' in graph

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


def test_two_frequencies_for_one_component(tmp_path):
    """A single component defining climatologies for both 'mon' and 'yr'
    frequencies should produce independent tasks for each frequency in
    both the task graph and the task definitions, rather than one
    overwriting the other."""
    config = {
        'postprocess': {
            'components': [{
                'type': 'comp1',
                'sources': [{'history_file': 'comp1_month'}],
                'climatology': [{'frequency': 'mon', 'interval_years': 2},
                                 {'frequency': 'yr', 'interval_years': 2}],
            }],
            'settings': {'pp_chunks': ['P1Y'],
                         'history_segment': 'P1Y',
                         'pp_start': '0001',
                         'pp_stop': '0002'},
            'switches': {'clean_work': False},
        }
    }
    yaml_file = tmp_path / 'config.yaml'
    with open(yaml_file, 'w') as file_:
        yaml.dump(config, file_)

    definitions = get_climatology_info.get_climatology_info(yaml_file, 'task-definitions')
    graph = get_climatology_info.get_climatology_info(yaml_file, 'task-graph')

    assert 'climo-mon-P2Y_comp1' in definitions
    assert 'climo-yr-P2Y_comp1' in definitions
    assert 'climo-mon-P2Y_comp1' in graph
    assert 'climo-yr-P2Y_comp1' in graph


def _build_climatology_workflow(tmp_path, pp_chunks, interval_years, pp_start,
                                 pp_stop, clean_work, runahead_limit='P999'):
    """Render a minimal, self-contained cylc workflow around a single
    climatology component, for tests that need to hand the generated
    graph/definitions to a real cylc install."""
    config = {
        'postprocess': {
            'components': [{
                'type': 'comp1',
                'sources': [{'history_file': 'comp1_month'}],
                'climatology': [{'frequency': 'yr', 'interval_years': interval_years}],
            }],
            'settings': {'pp_chunks': pp_chunks,
                         'history_segment': 'P1Y',
                         'pp_start': pp_start,
                         'pp_stop': pp_stop},
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
        f"    initial cycle point = {pp_start}\n"
        f"    final cycle point = {pp_stop}\n"
        f"    runahead limit = {runahead_limit}\n"
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
    return flow_cylc


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
    flow_cylc = _build_climatology_workflow(
        tmp_path, pp_chunks=['P1Y'], interval_years=interval_years,
        pp_start='0001', pp_stop='0004', clean_work=clean_work,
    )

    result = subprocess.run(
        ['cylc', 'validate', str(flow_cylc.parent)],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.skipif(shutil.which('cylc') is None, reason='cylc is not installed')
def test_multi_chunk_climatology_runahead_does_not_overflow(tmp_path):
    """A *valid* graph is not enough on its own: `cylc play` separately
    walks every cycling sequence up to the configured runahead limit
    (a raw cycle count when `runahead limit` is given as `Pn`, e.g.
    the `P999` used in production) to work out how far ahead it is
    safe to run. The climatology recurrence header used to be written
    as an open-ended "+P{offset}Y/P{interval}Y" (offset/period, with
    no explicit end or repetition count), which per ISO8601 recurs
    forever -- it does not stop at the workflow's own final cycle
    point. For a large enough climatology period (e.g. 20 years) that
    walk overflows the 4-digit TimePoint year before the runahead
    count limit is reached, crashing `cylc play` at startup with
    "Cannot dump TimePoint year: N not in bounds 0 to 9999" -- even
    though `cylc validate` on the same workflow passes cleanly, since
    validate never walks sequences this far.

    This reproduces the real-world scale (5-year pp_chunks, a 20-year
    climatology, runahead limit = P999) that triggered it in
    production, and replicates cylc's own runahead walk directly
    against the rendered workflow's config, in-process against the
    cylc.flow installed alongside pytest (the `cylc` skip guard above
    and this import share one environment in this repo's tooling).

    get_next_point() raises metomi.isodatetime's
    TimePointDumperBoundsError directly -- with the exact "Cannot dump
    TimePoint year: N not in bounds 0 to 9999" message `cylc play`
    crashed with -- once a walked point exceeds the 4-digit year
    range, so that's caught explicitly here and turned into a
    pytest.fail() naming the offending year, rather than letting an
    unrelated-looking traceback speak for itself.
    """
    from cylc.flow.config import WorkflowConfig
    from cylc.flow.scripts.validate import get_option_parser
    from cylc.flow.templatevars import get_template_vars
    from metomi.isodatetime.exceptions import TimePointDumperBoundsError

    flow_cylc = _build_climatology_workflow(
        tmp_path, pp_chunks=['P5Y'], interval_years=20,
        pp_start='0001', pp_stop='0020', clean_work=True,
        runahead_limit='P999',
    )

    parser = get_option_parser()
    opts, _ = parser.parse_args([str(flow_cylc.parent)])
    cfg = WorkflowConfig('test', str(flow_cylc), opts, get_template_vars(opts))

    ilimit = int(cfg.runahead_limit)
    for sequence in cfg.sequences:
        seq_point = sequence.get_first_point(cfg.start_point)
        count = 1
        while seq_point is not None and count <= 1 + ilimit:
            count += 1
            try:
                # This is where cylc play crashed: get_next_point() on
                # an unbounded sequence eventually produces a
                # TimePoint whose year cannot be represented.
                seq_point = sequence.get_next_point(seq_point)
            except TimePointDumperBoundsError as exc:
                pytest.fail(f"cylc runahead walk went out of bounds: {exc}")

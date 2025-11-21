"""
Tests for get_climatology_info module
"""
import sys
from pathlib import Path

from yaml import safe_load

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from get_climatology_info import task_graphs, duration_parser


def test_climatology_graph_uses_interval_years_recurrence():
    """
    Test that climatology graph uses interval_years recurrence to avoid creating too many tasks
    """
    yaml_content = """
postprocess:
  components:
    - type: "atmos_month"
      sources:
        - history_file: "atmos_month"
      xyInterp: "180,288"
      interpMethod: "conserve_order2"
      inputRealm: 'atmos'
      sourceGrid: 'cubedsphere'
      postprocess_on: True
      climatology:
      - frequency: mon
        interval_years: 2

  settings:
    history_segment: "P1Y"
    pp_chunks: ["P1Y"]

  switches:
    clean_work: True
"""
    yaml_ = safe_load(yaml_content)
    history_segment = duration_parser.parse(yaml_["postprocess"]["settings"]["history_segment"])
    clean_work = yaml_["postprocess"]["switches"]["clean_work"]

    graph = task_graphs(yaml_, history_segment, clean_work)

    # Verify that the graph uses P2Y (interval_years) recurrence for climo tasks
    assert "P2Y = \"\"\"" in graph, "Graph should use P2Y recurrence matching interval_years"

    # Verify dependencies use positive offsets to look ahead for additional data
    assert "rename-split-to-pp-regrid_atmos_month & rename-split-to-pp-regrid_atmos_month[P1Y]" in graph
    assert "=> climo-mon-P2Y_atmos_month" in graph

    # Verify clean dependencies are also present (since clean_work=True)
    # Clean tasks use P1Y (pp_chunk) recurrence and wait for all climo tasks
    assert "climo-mon-P2Y_atmos_month => clean-shards-ts-P1Y" in graph

    print("✓ Climatology graph correctly uses interval_years recurrence")


def test_climatology_with_multiple_sources():
    """
    Test climatology graph generation with multiple sources
    """
    yaml_content = """
postprocess:
  components:
    - type: "atmos"
      sources:
        - history_file: "atmos_daily"
        - history_file: "atmos_month"
      postprocess_on: True
      climatology:
      - frequency: yr
        interval_years: 5

  settings:
    history_segment: "P1Y"
    pp_chunks: ["P1Y"]

  switches:
    clean_work: False
"""
    yaml_ = safe_load(yaml_content)
    history_segment = duration_parser.parse(yaml_["postprocess"]["settings"]["history_segment"])
    clean_work = yaml_["postprocess"]["switches"]["clean_work"]

    graph = task_graphs(yaml_, history_segment, clean_work)

    # Verify both sources are included
    assert "rename-split-to-pp-native_atmos_daily" in graph
    assert "rename-split-to-pp-native_atmos_month" in graph

    # Verify P5Y recurrence is used (interval_years), not P1Y (pp_chunk)
    assert "P5Y = \"\"\"" in graph
    assert "P1Y = \"\"\"" not in graph

    # Verify positive offsets for 5-year interval with 1-year chunks (0, 1, 2, 3, 4)
    assert "[P1Y]" in graph
    assert "[P2Y]" in graph
    assert "[P3Y]" in graph
    assert "[P4Y]" in graph

    print("✓ Climatology with multiple sources correctly structured")


def test_climatology_make_timeseries_dependency():
    """
    Test that climatology uses make-timeseries when pp_chunk != history_segment
    """
    yaml_content = """
postprocess:
  components:
    - type: "ocean"
      sources:
        - history_file: "ocean"
      postprocess_on: True
      climatology:
      - frequency: mon
        interval_years: 2

  settings:
    history_segment: "P1M"
    pp_chunks: ["P1Y"]

  switches:
    clean_work: False
"""
    yaml_ = safe_load(yaml_content)
    history_segment = duration_parser.parse(yaml_["postprocess"]["settings"]["history_segment"])
    clean_work = yaml_["postprocess"]["switches"]["clean_work"]

    graph = task_graphs(yaml_, history_segment, clean_work)

    # When history_segment != pp_chunk, should use make-timeseries
    assert "make-timeseries-native-P1Y_ocean" in graph
    assert "rename-split-to-pp-native_ocean" not in graph

    # Should use P2Y recurrence (interval_years)
    assert "P2Y = \"\"\"" in graph

    print("✓ Climatology correctly uses make-timeseries dependencies")


def test_consolidated_clean_dependencies():
    """
    Test that clean tasks wait for ALL climatology tasks to complete
    """
    yaml_content = """
postprocess:
  components:
    - type: "atmos_month"
      sources:
        - history_file: "atmos_month"
      xyInterp: "180,288"
      interpMethod: "conserve_order2"
      postprocess_on: True
      climatology:
      - frequency: yr
        interval_years: 2
      - frequency: mon
        interval_years: 2
    - type: "atmos_scalar"
      sources:
        - history_file: "atmos_scalar"
      postprocess_on: True
      climatology:
      - frequency: yr
        interval_years: 2

  settings:
    history_segment: "P1Y"
    pp_chunks: ["P1Y"]

  switches:
    clean_work: True
"""
    yaml_ = safe_load(yaml_content)
    history_segment = duration_parser.parse(yaml_["postprocess"]["settings"]["history_segment"])
    clean_work = yaml_["postprocess"]["switches"]["clean_work"]

    graph = task_graphs(yaml_, history_segment, clean_work)

    # Verify all climo tasks are present
    assert "climo-yr-P2Y_atmos_month" in graph
    assert "climo-mon-P2Y_atmos_month" in graph
    assert "climo-yr-P2Y_atmos_scalar" in graph

    # Verify clean dependency requires ALL climo tasks
    # Extract the clean dependency line and check all tasks are present
    expected_tasks = ["climo-yr-P2Y_atmos_month", "climo-mon-P2Y_atmos_month", "climo-yr-P2Y_atmos_scalar"]
    clean_line_found = False
    for line in graph.split('\n'):
        if "=> clean-shards-ts-P1Y" in line:
            # Check that all expected tasks appear in the dependency line
            if all(task in line for task in expected_tasks):
                clean_line_found = True
                break

    assert clean_line_found, "Clean task should wait for ALL climo tasks: " + ", ".join(expected_tasks)

    print("✓ Clean tasks correctly wait for all climatology tasks")


if __name__ == "__main__":
    test_climatology_graph_uses_interval_years_recurrence()
    test_climatology_with_multiple_sources()
    test_climatology_make_timeseries_dependency()
    test_consolidated_clean_dependencies()
    print("\nAll tests passed!")

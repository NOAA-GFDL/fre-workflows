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
    # Clean tasks use R1/$ to run once at final cycle point
    assert "R1/$ = \"\"\"" in graph
    assert "clean-shards-ts-P1Y" in graph

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

    # Verify clean dependency requires ALL climo tasks AND remap tasks
    # Clean should use R1/$ recurrence to run once at final cycle
    assert "R1/$ = \"\"\"" in graph, "Clean section should use R1/$ recurrence"
    
    # Extract the clean dependency line and check all tasks are present with :succeed-all
    expected_tasks = ["climo-yr-P2Y_atmos_month", "climo-mon-P2Y_atmos_month", "climo-yr-P2Y_atmos_scalar"]
    clean_line_found = False
    remap_dependency_found = False
    succeed_all_found = False
    for line in graph.split('\n'):
        if "=> clean-shards-ts-P1Y" in line:
            # Check that all expected tasks appear in the dependency line with :succeed-all
            if all(task in line for task in expected_tasks):
                clean_line_found = True
                # Check for :succeed-all qualifiers
                if ":succeed-all" in line:
                    succeed_all_found = True
                # Also check for remap task dependency
                if "REMAP-PP-COMPONENTS-TS-P1Y:succeed-all" in line:
                    remap_dependency_found = True
                break

    assert clean_line_found, "Clean task should wait for ALL climo tasks: " + ", ".join(expected_tasks)
    assert remap_dependency_found, "Clean task should also wait for all REMAP-PP-COMPONENTS-TS tasks"
    assert succeed_all_found, "Clean task dependencies should use :succeed-all to wait across all cycles"

    print("✓ Clean tasks correctly wait for all climatology tasks AND remap tasks with :succeed-all")


def test_has_climatology_detection():
    """
    Test that has_climatology correctly detects climatology configuration
    """
    from get_climatology_info import has_climatology
    import tempfile
    import os
    
    def test_yaml_config(yaml_content, expected_result, message):
        """Helper function to test climatology detection with proper cleanup"""
        temp_file = None
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
                temp_file = f.name
                f.write(yaml_content)
                f.flush()
            
            result = has_climatology(temp_file)
            assert result == expected_result, message
        finally:
            if temp_file and os.path.exists(temp_file):
                os.unlink(temp_file)
    
    # Test with climatology
    yaml_with_climo = """
postprocess:
  components:
    - type: "atmos"
      postprocess_on: True
      climatology:
      - frequency: yr
        interval_years: 2
"""
    test_yaml_config(yaml_with_climo, True, "Should detect climatology")
    
    # Test without climatology
    yaml_without_climo = """
postprocess:
  components:
    - type: "atmos"
      postprocess_on: True
"""
    test_yaml_config(yaml_without_climo, False, "Should not detect climatology")
    
    print("✓ has_climatology correctly detects climatology configuration")


if __name__ == "__main__":
    test_climatology_graph_uses_interval_years_recurrence()
    test_climatology_with_multiple_sources()
    test_climatology_make_timeseries_dependency()
    test_consolidated_clean_dependencies()
    test_has_climatology_detection()
    print("\nAll tests passed!")

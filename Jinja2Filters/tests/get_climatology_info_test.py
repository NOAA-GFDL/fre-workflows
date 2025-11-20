"""Tests for get_climatology_info module"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from get_climatology_info import task_graphs, duration_parser
from yaml import safe_load


def test_climatology_graph_uses_pp_chunk_recurrence():
    """Test that climatology graph uses pp_chunk recurrence, not interval_years"""
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
    
    # Verify that the graph uses P1Y (pp_chunk) recurrence, not P2Y (interval_years)
    assert "P1Y = \"\"\"" in graph, "Graph should use P1Y recurrence matching pp_chunk"
    assert "P2Y = \"\"\"" not in graph, "Graph should not use P2Y recurrence"
    
    # Verify dependencies are correctly structured
    assert "rename-split-to-pp-regrid_atmos_month & rename-split-to-pp-regrid_atmos_month[P1Y]" in graph
    assert "=> climo-mon-P2Y_atmos_month" in graph
    
    print("✓ Climatology graph correctly uses pp_chunk recurrence")


def test_climatology_with_multiple_sources():
    """Test climatology graph generation with multiple sources"""
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
    
    # Verify P1Y recurrence is used (pp_chunk), not P5Y (interval_years)
    assert "P1Y = \"\"\"" in graph
    assert "P5Y = \"\"\"" not in graph
    
    # Verify offsets for 5-year interval with 1-year chunks (0, 1, 2, 3, 4)
    assert "[P1Y]" in graph
    assert "[P2Y]" in graph
    assert "[P3Y]" in graph
    assert "[P4Y]" in graph
    
    print("✓ Climatology with multiple sources correctly structured")


def test_climatology_make_timeseries_dependency():
    """Test that climatology uses make-timeseries when pp_chunk != history_segment"""
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
    # Verify that rename-split-to-pp is not directly connected to climo
    assert "rename-split-to-pp-native_ocean => climo" not in graph
    
    # Should still use P1Y recurrence
    assert "P1Y = \"\"\"" in graph
    
    print("✓ Climatology correctly uses make-timeseries dependencies")


if __name__ == "__main__":
    test_climatology_graph_uses_pp_chunk_recurrence()
    test_climatology_with_multiple_sources()
    test_climatology_make_timeseries_dependency()
    print("\nAll tests passed!")

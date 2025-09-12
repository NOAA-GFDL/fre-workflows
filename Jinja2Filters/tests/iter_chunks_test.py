import pytest
import metomi.isodatetime
from metomi.isodatetime.parsers import DurationParser, TimePointParser
from Jinja2Filters import iter_chunks

duration_parser = DurationParser()
time_parser = TimePointParser(default_to_unknown_time_zone=True)

def test_simple():
    """2-year chunk from one year history, years 1-2.
    The simplest possible usage of the method,
    and does not use partial chunks"""
    result = [{'chunk_size': duration_parser.parse('P2Y'),
               'cycle_point': time_parser.parse('0001-01-01T00:00:00Z'),
               'is_partial': False,
               'segments': [time_parser.parse('0001-01-01T00:00:00Z'),
                            time_parser.parse('0002-01-01T00:00:00Z')]}]
    assert result == list(iter_chunks.iter_chunks(["P2Y"], "P1Y", "0001", "0002"))

def test_complex():
    """2 and 3-year chunks from one-year history, years 1-3.
    The answer is a full two year chunk and a partial chunk (one year),
    and then a three year chunk."""
    result = [{'chunk_size': duration_parser.parse('P2Y'),
               'cycle_point': time_parser.parse('0001-01-01T00:00:00Z'),
               'is_partial': False,
               'segments': [time_parser.parse('0001-01-01T00:00:00Z'),
                            time_parser.parse('0002-01-01T00:00:00Z')]},
              {'chunk_size': duration_parser.parse('P2Y'),
               'cycle_point': time_parser.parse('0003-01-01T00:00:00Z'),
               'is_partial': True,
                'segments': [time_parser.parse('0003-01-01T00:00:00Z')]},
              {'chunk_size': duration_parser.parse('P3Y'),
                'cycle_point': time_parser.parse('0001-01-01T00:00:00Z'),
                'is_partial': False,
                'segments': [time_parser.parse('0001-01-01T00:00:00Z'),
                             time_parser.parse('0002-01-01T00:00:00Z'),
                             time_parser.parse('0003-01-01T00:00:00Z')]}]
    assert result == list(iter_chunks.iter_chunks(["P2Y", "P3Y"], "P1Y", "0001", "0003"))

import pytest
import metomi.isodatetime.parsers
from . import subtract_durations

@pytest.mark.parametrize("minuend, subtrahend, difference",
    [('P10D', 'P9D', 'P1D'),
     ('P2M', 'P1M', 'P1M'),
     ('P3M', 'P2M', 'P1M'),
     ('P3M', 'P1M', 'P2M'),
     ('P2Y', 'P1Y', 'P1Y')])
def test_subtraction(minuend, subtrahend, difference):
    """Test some common date subtractions"""
    assert metomi.isodatetime.parsers.DurationParser().parse(difference) \
    == subtract_durations.subtract_durations(minuend, subtrahend)

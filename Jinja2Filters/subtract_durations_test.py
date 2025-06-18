import pytest
import metomi.isodatetime.parsers
from . import subtract_durations

def test_subtraction():
    P1D = metomi.isodatetime.parsers.DurationParser().parse('P1D')
    P1M = metomi.isodatetime.parsers.DurationParser().parse('P1M')
    P2M = metomi.isodatetime.parsers.DurationParser().parse('P2M')
    P1Y = metomi.isodatetime.parsers.DurationParser().parse('P1Y')

    assert P1D == subtract_durations.subtract_durations('P10D', 'P9D')
    assert P1M == subtract_durations.subtract_durations('P2M', 'P1M')
    assert P1M == subtract_durations.subtract_durations('P3M', 'P2M')
    assert P2M == subtract_durations.subtract_durations('P3M', 'P1M')
    assert P1Y == subtract_durations.subtract_durations('P2Y', 'P1Y')

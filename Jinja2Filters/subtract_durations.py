import metomi.isodatetime.parsers

def subtract_durations(duration1, duration2):
    """Return the difference of two durations

    Arguments:
        duration (str)
        duration (int)

    Examples:
    >>> subtract_durations('P2Y', 'P6M')
    P15M
"""
    dur1 = metomi.isodatetime.parsers.DurationParser().parse(duration1)
    dur2 = metomi.isodatetime.parsers.DurationParser().parse(duration2)
    return(dur1 - dur2)

#print(subtract_durations('P2M', 'P1M'))
#print(subtract_durations('P2Y', 'P1Y'))

# also odd
#print(subtract_durations('P2Y', 'P6M'))

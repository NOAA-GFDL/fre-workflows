import metomi.isodatetime.parsers

def add_durations(duration1, duration2):
    """Return the sum of two durations

    Arguments:
        duration (str)
        duration (int)

    Examples:
    >>> add_durations('P2Y', -'P6M')
    P15M
"""
    dur1 = metomi.isodatetime.parsers.DurationParser().parse(duration1)
    dur2 = metomi.isodatetime.parsers.DurationParser().parse(duration2)
    return(dur1 + dur2)

#print(add_durations('P2M', 'P1M'))
#print(add_durations('PT2H', 'P1Y'))
#print(add_durations('P2Y', '-P1Y'))

# odd
#print(add_durations('P2Y', 'P6M'))

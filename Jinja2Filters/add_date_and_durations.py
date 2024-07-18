import metomi.isodatetime.parsers

def add_date_and_durations(date, d1, d2):
    """Return the sum of a date and one or more durations

    Arguments:
        date (str)
        durations (str)

    Examples:
    # Add two years to 2000-01-01
    >>> add_date_and_duration('20000101T0000Z', 'P2Y')
    2002-01-01T00:00:00Z
    # Add two years to 2000-01-01, minus a month
    >>> add_date_and_duration('20000101T0000Z', 'P2Y', '-P1M')
    2002-01-01T00:00:00Z
"""
    # set the time zone to be UTC or else the cycle points will not align
    d = metomi.isodatetime.parsers.TimePointParser(assumed_time_zone=(0,0)).parse(date)
    dur1 = metomi.isodatetime.parsers.DurationParser().parse(d1)
    dur2 = metomi.isodatetime.parsers.DurationParser().parse(d2)
    return(d + dur1 + dur2)

#print(add_date_and_duration('2000', 'P1Y'))
#print(add_date_and_durations('2000', 'P1Y', '-P1M'))

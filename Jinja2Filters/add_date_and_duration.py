import metomi.isodatetime.parsers

def add_date_and_duration(date, duration):
    """Return the sum of a date and duration

    Arguments:
        date (str)
        duration (str)

    Examples:
    # Add two years to 2000-01-01
    >>> add_date_and_duration('20000101T0000Z', 'P2Y')
    2002-01-01T00:00:00Z
"""
    # set the time zone to be UTC or else the cycle points will not align
    d = metomi.isodatetime.parsers.TimePointParser(assumed_time_zone=(0,0)).parse(date)
    dur = metomi.isodatetime.parsers.DurationParser().parse(duration)
    return(d + dur)

#print(add_date_and_duration('2000', 'P1Y'))

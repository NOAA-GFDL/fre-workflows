import metomi.isodatetime.parsers

def add_date_and_duration(date, duration):
    """Return the sum of a data and duration

    Arguments:
        date (str)
        duration (str)

    Examples:
    # Add two years to 2000-01-01
    >>> add_date_and_duration('20000101T0000Z', 'P2Y')
    2002-01-01T00:00:00Z
"""
    d = metomi.isodatetime.parsers.TimePointParser().parse(date)
    dur = metomi.isodatetime.parsers.DurationParser().parse(duration)
    return(d + dur)

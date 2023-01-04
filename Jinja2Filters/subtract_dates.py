import metomi.isodatetime.parsers

def subtract_dates(date2, date1):
    """Return the difference of two dates

    Arguments:
        date1 (str)
        date2 (int)

    Examples:
    >>> subtract_durations('P2Y', 'P6M')
    P15M
"""
    date1 = metomi.isodatetime.parsers.TimePointParser().parse(date1)
    date2 = metomi.isodatetime.parsers.TimePointParser().parse(date2)
    return(date2 - date1)

#print(subtract_dates('2015-01-01', '1979-01-01'))

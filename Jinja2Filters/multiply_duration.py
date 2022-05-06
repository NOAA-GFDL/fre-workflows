import metomi.isodatetime.parsers

def multiply_duration(duration, N):
    """Return the product of a duration and an integar

    Arguments:
        duration (str)
        number (int)

    Examples:
    >>> multiply_duration('P3M', 5)
    P15M
"""
    # set the time zone to be UTC or else the cycle points will not align
    dur = metomi.isodatetime.parsers.DurationParser().parse(duration)
    return(dur * N)

#print(multiply_duration('P2M', 5))
#print(multiply_duration('PT2H', 10))

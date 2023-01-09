import metomi.isodatetime.parsers

def divide_durations(big_dur_str, small_dur_str):
    """Divide two durations

    Examples:
    >>> divide_durations('P2Y', 'P1Y')
    2
"""
    print("DEBUG HELP")
    small_dur = metomi.isodatetime.parsers.DurationParser().parse(small_dur_str)
    print(type(small_dur_str))
    big_dur = metomi.isodatetime.parsers.DurationParser().parse(big_dur_str)
    small_dur = metomi.isodatetime.parsers.DurationParser().parse(small_dur_str)
    print("DEBUG:", big_dur, small_dur)
    return(big_dur.get_seconds() / small_dur.get_seconds())

#print(divide_durations('P2Y', 'P1Y'))

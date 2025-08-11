import re

def legacy_date_conversions():
    """This is kludge to pass cylc processing."""
    raise Exception("This is not a usable custom filter.")

def convert_iso_duration_to_bronx_freq(duration):
    """Convert ISO8601 duration to Bronx-style frequency."""

    lookup = {
        'P1Y': 'annual',
        'P1M': 'monthly',
        'P3M': 'seasonal',
        'P1D': 'daily',
        'PT120H': '120hr',
        'PT12H': '12hr',
        'PT8H': '8hr',
        'PT6H': '6hr',
        'PT4H': '4hr',
        'PT3H': '3hr',
        'PT2H': '2hr',
        'PT1H': 'hourly',
        'PT30M': '30min'
    }

    try:
        return(lookup[duration])
    except KeyError:
        print(f"ERROR: Conversion of ISO duration '{duration}' to Bronx-style frequency not known")
        raise

def convert_iso_duration_to_bronx_chunk(duration):
    """Convert ISO8601 duration to Bronx-style timeseries chunk."""

    # need to convert to string
    if isinstance(duration, str):
        duration_str = duration
    else:
        duration_str = str(duration)

    match_obj = re.match('^P([0-9]+)Y$', duration_str)
    if match_obj:
        return(match_obj.group(1) + 'yr')
    match_obj = re.match('^P([0-9]+)M$', duration_str)
    if match_obj:
        return(match_obj.group(1) + 'mo')
    raise Exception(f"Conversion of ISO duration '{duration}' to Bronx-style timeseries chunk not known")

#print(convert_iso_duration_to_bronx_freq('PT30M'))
#print(convert_iso_duration_to_bronx_chunk('P2D'))

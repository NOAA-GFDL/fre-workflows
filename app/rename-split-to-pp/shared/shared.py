"""
Shared utility functions for rename-split-to-pp.
These functions were originally in shared.sh and have been converted to Python.
"""

import sys
import re
from datetime import datetime


def err(message: str) -> None:
    """
    Print a message to standard error with timestamp.

    Args:
        message: The message to print
    """
    timestamp = datetime.now().strftime('%Y-%m-%dT%H:%M:%S%z')
    print(f"[{timestamp}]: {message}", file=sys.stderr)


def freq_to_date_format(freq: str) -> str:
    """
    Return legacy Bronx-like date template format given a frequency (ISO 8601 duration).

    Args:
        freq: ISO 8601 duration string (e.g., 'P1Y', 'P1M', 'P1D', 'PT1H')

    Returns:
        Format string for dates (e.g., 'CCYY', 'CCYYMM', 'CCYYMMDD', 'CCYYMMDDThh')

    Raises:
        ValueError: If frequency is not recognized
    """
    format_map = {
        'P1Y': 'CCYY',
        'P1M': 'CCYYMM',
        'P1D': 'CCYYMMDD',
    }

    if freq in format_map:
        return format_map[freq]

    # Handle hourly frequencies like PT1H, PT6H, etc.
    if freq.startswith('PT') and freq.endswith('H'):
        return 'CCYYMMDDThh'

    raise ValueError(f"Unknown frequency: {freq}")


def get_freq_and_format_from_hours(hours: float) -> tuple:
    """
    Determine frequency and format based on hours.

    Args:
        hours: Number of hours

    Returns:
        Tuple of (frequency, format) strings
    """
    hours_floor = int(hours)
    hours_remainder = hours - hours_floor

    # Annual (this is so questionable)
    if hours_floor > 4320:
        return ('P1Y', 'CCYY')

    # Monthly
    if 671 < hours_floor < 745:
        return ('P1M', 'CCYYMM')

    # Daily
    if hours_floor == 24:
        return ('P1D', 'CCYYMMDD')

    # Hourly (less than 24 hours but not 0)
    if hours_floor < 24 and hours_floor != 0:
        return (f'PT{hours_floor}H', 'CCYYMMDDThh')

    # Subhourly
    if hours_floor == 0 and hours_remainder > 0:
        # Convert remainder to a clean decimal string
        remainder_str = f"{hours_remainder:.10f}".rstrip('0').lstrip('0').lstrip('.')
        return (f'PT0.{remainder_str}H', 'CCYYMMDDThh')

    err(f"ERROR: Could not determine frequency for hours={hours}")
    return ('error', 'error')


def get_freq_and_format_from_two_days(d1: float, d2: float) -> tuple:
    """
    Determine frequency based on two days values.

    Args:
        d1: First day value
        d2: Second day value

    Returns:
        Tuple of (frequency, format) strings
    """
    hours = (d1 + d2) * 24
    return get_freq_and_format_from_hours(hours)


def get_freq_and_format_from_two_dates(d1: str, d2: str) -> tuple:
    """
    Determine frequency based on two ISO dates.
    This version uses metomi.isodatetime for proper ISO8601 handling.

    Args:
        d1: First date string in ISO8601 format
        d2: Second date string in ISO8601 format

    Returns:
        Tuple of (frequency, format) strings
    """
    try:
        from metomi.isodatetime.parsers import TimePointParser
        from metomi.isodatetime.data import Calendar

        parser = TimePointParser()

        # Parse the dates
        tp1 = parser.parse(d1)
        tp2 = parser.parse(d2)

        # Calculate difference using 365-day calendar
        Calendar.default().set_mode(Calendar.MODE_365)
        duration = tp2 - tp1

        # Get total hours
        hours = duration.get_days_and_seconds()[0] * 24 + duration.get_days_and_seconds()[1] / 3600.0

        return get_freq_and_format_from_hours(hours)

    except ImportError:
        # Fallback if metomi.isodatetime not available
        err("WARNING: metomi.isodatetime not available, using fallback date parsing")
        return _get_freq_and_format_fallback(d1, d2)


def _get_freq_and_format_fallback(d1: str, d2: str) -> tuple:
    """
    Fallback frequency calculation when metomi.isodatetime is not available.

    Args:
        d1: First date string
        d2: Second date string

    Returns:
        Tuple of (frequency, format) strings
    """
    # Try to parse various date formats
    formats = [
        '%Y-%m-%dT%H:%M:%S',
        '%Y-%m-%dT%H:%M',
        '%Y-%m-%d',
        '%Y%m%dT%H%M%S',
        '%Y%m%dT%H%M',
        '%Y%m%d',
    ]

    dt1 = None
    dt2 = None

    for fmt in formats:
        try:
            dt1 = datetime.strptime(d1, fmt)
            dt2 = datetime.strptime(d2, fmt)
            break
        except ValueError:
            continue

    if dt1 is None or dt2 is None:
        err(f"ERROR: Could not parse dates: {d1}, {d2}")
        return ('error', 'error')

    # Calculate difference in hours
    delta = dt2 - dt1
    hours = delta.total_seconds() / 3600.0

    return get_freq_and_format_from_hours(hours)


def freq_to_legacy(freq: str) -> str:
    """
    Convert ISO8601 duration to Bronx-style frequency name.

    Args:
        freq: ISO 8601 duration string

    Returns:
        Bronx-style frequency name

    Raises:
        ValueError: If frequency is not recognized
    """
    freq_map = {
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
        'PT30M': '30min',
    }

    if freq in freq_map:
        return freq_map[freq]

    raise ValueError(f"Unknown frequency: {freq}")


def chunk_to_legacy(chunk: str) -> str:
    """
    Convert ISO8601 duration chunk to Bronx-style chunk name.

    Args:
        chunk: ISO 8601 duration string

    Returns:
        Bronx-style chunk name (e.g., '1yr', '6mo')
    """
    # Match PnY (years)
    match = re.match(r'^P(\d+)Y$', chunk)
    if match:
        return f"{match.group(1)}yr"

    # Match PnM (months)
    match = re.match(r'^P(\d+)M$', chunk)
    if match:
        return f"{match.group(1)}mo"

    err(f"ERROR: Unknown chunk {chunk}")
    return 'error'

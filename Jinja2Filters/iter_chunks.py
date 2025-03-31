from metomi.isodatetime.parsers import DurationParser, TimePointParser

def iter_chunks(chunk_sizes, history_segment, pp_start, pp_stop):
    """Return an iterator over all PP chunks. For each chunk, a dictionary is
       yielded consisting of `chunk_size`, `cycle_point`, and `segments` keys.

    Arguments:
        chunk_sizes (list of strings)
        history_segment (string)
        pp_start (string)
        pp_stop (string)

    Example:
    >>> list(iter_chunks(["P2Y", "P3Y"], "P1Y", "0001", "0003"))
    Result:
    [
      {
        'chunk_size': Duration<P2Y>,
        'cycle_point': TimePoint<0001-01-01>,
        'segments': [TimePoint<0001-01-01>, TimePoint<0002-01-01>]
      },
      {
        'chunk_size': Duration<P2Y>,
        'cycle_point': TimePoint<0003-01-01>,
        'segments': [TimePoint<0003-01-01>]
      },
      {
        'chunk_size': Duration<P3Y>,
        'cycle_point': TimePoint<0001-01-01>,
        'segments': [TimePoint<0001-01-01>, TimePoint<0002-01-01>, TimePoint<0003-01-01>]
      }
    ]
"""
    duration_parser = DurationParser()
    time_point_parser = TimePointParser(default_to_unknown_time_zone=True)

    chunk_sizes = (duration_parser.parse(cs) for cs in chunk_sizes)
    history_segment = duration_parser.parse(history_segment)
    pp_start = time_point_parser.parse(pp_start)
    pp_stop = time_point_parser.parse(pp_stop)

    def n_segments(interval):
        return int(interval.get_seconds() / history_segment.get_seconds())

    for cs in chunk_sizes:
        n_segments_full_chunk = n_segments(cs)
        cycle_point = pp_start
        while cycle_point <= pp_stop:
            n_segments_remaining = n_segments(pp_stop + history_segment - cycle_point)
            n = min(n_segments_full_chunk, n_segments_remaining)
            yield {
                'chunk_size': cs,
                'cycle_point': cycle_point,
                'segments': [cycle_point + history_segment*i for i in range(n)]
            }
            cycle_point += cs

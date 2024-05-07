import sys
import pytest
import gzip
import base64
from unittest.mock import patch
from data_lineage.bloomfilter.StringCompression import compress_string, decompress_bytes


@pytest.mark.parametrize("input_string, expected_output", [
    ("String that's less than bytes..............................", False),
    ("String that's over 125 bytes.................................................", True),
    ("A" * 1_000, True),
    ("A" * 1_000_000, True),
    ("", False)
])

def test_compress_string(input_string, expected_output, capsys):
    """
    Every string with a memory allocation larger than 125 bytes will be smaller
    after compression.

    Due to the compression behavior being designed for large strings, strings
    smaller than 125 bytes will increase in size after compression.
    """
    compressed = compress_string(input_string)

    uncompressed_size = sys.getsizeof(input_string)
    compressed_size = sys.getsizeof(compressed)

    is_compression_effective = uncompressed_size > compressed_size

    assert is_compression_effective == expected_output

@pytest.mark.parametrize("input_string", [
    "String == to 72 bytes..",
    "String that's over 72 bytes",
    "b" * 1_000,
    "b" * 1_000_000,
    ""
])

def test_compression(input_string):
    """
    Test that compressing and then decompressing conserves the contents
    of a string.
    """
    compressed_bytes = compress_string(input_string)
    decompressed_string = decompress_bytes(compressed_bytes)

    assert decompressed_string == input_string

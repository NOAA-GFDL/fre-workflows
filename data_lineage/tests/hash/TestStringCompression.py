import sys
import pytest
import gzip
import base64
from data_lineage.bloomfilter.StringCompression import compress_string, decompress_bytes


INPUT_DATA = {
    "less_than_100_bytes": ("String that's less than 100 bytes..", False),
    "over_125_bytes": ("String that's over 125 bytes.....................................................", True),
    "1000_A": ("A" * 1_000, True),
    "1000000_A": ("A" * 1_000_000, True),
    "empty_string": ("", False)
}

@pytest.mark.parametrize("input_identifier", INPUT_DATA.keys())
def test_compress_string(input_identifier):
    """
    Every string with a memory allocation typically larger than 100 bytes will be smaller
    after compression. This line at which the size after compression begins to decrease
    fluctuates depending on the string sometimes. It appears like strings that are over
    100-125 bytes will tend to become smaller after compression.

    Due to the compression behavior being designed for large strings, strings
    smaller than 100 bytes will increase in size after compression.
    """
    input_string, expected_output = INPUT_DATA[input_identifier]
    compressed = compress_string(input_string)

    uncompressed_size = sys.getsizeof(input_string)
    compressed_size = sys.getsizeof(compressed)

    is_compression_effective = uncompressed_size > compressed_size

    assert is_compression_effective == expected_output

@pytest.mark.parametrize("input_identifier", INPUT_DATA.keys())
def test_compression(input_identifier):
    """
    Test that compressing and then decompressing conserves the contents
    of a string.
    """
    input_string, _ = INPUT_DATA[input_identifier]
    compressed_bytes = compress_string(input_string)
    decompressed_string = decompress_bytes(compressed_bytes)

    assert decompressed_string == input_string

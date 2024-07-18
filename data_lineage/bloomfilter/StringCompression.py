import gzip
import base64
import sys
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

ORIGINAL_SIZE_FORMAT = 'size of input string: {}'
COMPRESSED_SIZE_FORMAT = 'size of compressed bytes: {}'
COMPRESSED_B64_SIZE_FORMAT  = 'size of compressed base64 bytes: {}'
DECOMPRESSED_SIZE_FORMAT = 'size of decompressed bytes: {}'

def compress_string(input_string):
    """
    Called directly in the bash script. Compresses input_string into a base64
    representation of the compressed bytes from the python library gzip.

    The size of compression varies, but any string with a size > 72 bytes
    typically saves space with this compression method.
    """
    input_bytes = input_string.encode('utf-8')
    compressed_bytes = gzip.compress(input_bytes)
    b64_bytes = base64.b64encode(compressed_bytes)

    logging.info(ORIGINAL_SIZE_FORMAT.format(sys.getsizeof(input_string)))
    logging.info(COMPRESSED_SIZE_FORMAT.format(sys.getsizeof(compressed_bytes)))
    logging.info(COMPRESSED_B64_SIZE_FORMAT.format(sys.getsizeof(b64_bytes)))

    b64_string = str(b64_bytes)[2:-1]

    # https://en.wikipedia.org/wiki/Base64#:~:text=Output%20padding%5B,the%20output%20padding%3A
    # Bash scripts handle `=` weirdly. To avoid this, replace the buffers with the
    # temporary string representation  `_pad`
    b64_string = b64_string.replace('=', '_pad')

    print(b64_string)

    return b64_string


def decompress_bytes(b64_string):
    """
    Reverts the compression for the file annotation.
    """

    # Base64 encodes '=' as padding at the end since it uses 24-bit sequences
    # https://stackoverflow.com/questions/38763771/how-do-i-remove-double-back-slash-from-a-bytes-object
    b64_string = b64_string.replace('_pad', '=')
    compressed_data = b64_string.encode().decode('unicode_escape').encode("raw_unicode_escape")

    b64_decoded_bytes = base64.b64decode(compressed_data)
    decompressed_bytes = gzip.decompress(b64_decoded_bytes)
    decompressed_string = str(decompressed_bytes)[2:-1]

    logging.info(DECOMPRESSED_SIZE_FORMAT.format(sys.getsizeof(decompressed_string)))

    return decompressed_string


if __name__ == "__main__":

    if len(sys.argv) != 2:
        logging.info(sys.argv)
        logging.error("Usage: python StringCompression.py <str>")
        sys.exit(1)

    if len(sys.argv) == 2:
        my_bytes = compress_string(sys.argv[1])

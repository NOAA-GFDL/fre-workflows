import gzip
import base64
import sys
import logging


def compress_string(input_string):

    input_bytes = input_string.encode('utf-8')
    compressed_bytes = gzip.compress(input_bytes)
    b64_bytes = base64.b64encode(compressed_bytes)

    size_original = sys.getsizeof(input_string)
    size_compressed = sys.getsizeof(compressed_bytes)
    size_b64 = sys.getsizeof(b64_bytes)

    logging.info(f'size of input string                      : {size_original}')
    logging.info(f'size of input string in utf-8 bytes       : {size_compressed}')
    logging.info(f'size of input string in b64 bytes         : {size_b64}')

    b64_string = str(b64_bytes)[2:-1]

    # https://en.wikipedia.org/wiki/Base64#:~:text=Output%20padding%5B,the%20output%20padding%3A
    b64_string = b64_string.replace('=', '_pad')

    print(b64_string)

    return b64_string


def decompress_bytes(_bytes):
    b64_decoded_bytes = base64.b64decode(_bytes)
    decompressed_bytes = gzip.decompress(b64_decoded_bytes)
    decompressed_string = str(decompressed_bytes)[2:-1]
    len_str = sys.getsizeof(decompressed_string)

    logging.info(f'size of decompressed bytes          : {len_str}')

    # print(str(decompressed_string)[2:-1])

    return decompressed_string


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    if len(sys.argv) != 2:
        logging.info(sys.argv)
        # compress_string('19810101.land_daily_cmip.tile1.nc  1eed5b1bbde501,19810101.land_daily_cmip.tile2.nc
        # 1dc1f4b980e4f,19810101.land_daily_cmip.tile3.nc  ec8a56a6fe669,19810101.land_daily_cmip.tile4.nc
        # 1b89f8e65223f2,19810101.land_daily_cmip.tile5.nc  bb3b2c0fe1f24,19810101.land_daily_cmip.tile6.nc
        # 111ef0b6a1a31c')
        logging.error("Usage: python StringCompression.py <str>")
        sys.exit(1)

    if len(sys.argv) == 2:
        my_bytes = compress_string(sys.argv[1])

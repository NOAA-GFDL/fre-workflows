from data_lineage.bloomfilter.Bloomfilter import BloomFilter
import netCDF4 as nc
import logging
import binascii
import time
import sys

# ncks -M /archive/Cole.Harvey/canopy/am5/c96L33_amip/pp/atmos/av/monthly_2yr/atmos.1980-1981.11.nc
# /home/Cole.Harvey/.conda/envs/bloom-filter-env/bin/python

def scrape_metadata(file_path):
    """
    Given a netcdf file, parse it and scrape the dimensions, variables, and history.
    Concatenate this metadata together to create a unique identifier for this
    specific netcdf file.

    The file path is appended to the end of the metadata to ensure files that have
    the same contents but are stored in different locations do not have colliding
    hashes.
    """
    rootgrp = nc.Dataset(file_path, "r")
    meta_data = ''

    for dim_name, dim in rootgrp.dimensions.items():
        dim_header = str(f'{dim_name} = {len(dim)}\n')
        meta_data += dim_header
    for var_name, var in rootgrp.variables.items():
        var_header = str(f'{var.dtype} {var_name}({var.dimensions}) ;\n')
        meta_data += var_header

    history = rootgrp.__dict__.get('history')
    meta_data += str(history)
    meta_data += file_path

    rootgrp.close()

    logging.info(f'\n\nPrinting metadata for {file_path}\n\n{meta_data}\n\nFinished printing metadata\n')
    return meta_data


def generate_hash(meta_data):
    """
    Create a hash of the 'meta_data' object passed in. Should be a string.

    To adjust the length of the returned hash value, modify the magnitude
    of 10 which takes the modulo of the bit_array_int at the end of the
    bit_array_int_reduced line.
    """
    # Keep size a power of 2
    size = 2 ** 8
    hash_count = 200

    # Initialize the bloomfilter
    bf = BloomFilter(size, hash_count)

    logging.info(f'Size of bit array : {bf.size}')
    logging.info(f'Number of hash functions : {bf.hash_count}')
    logging.info(f'Hash Power : {bf.size * bf.hash_count}')

    start_time = time.time()
    bit_array = bf.hash(meta_data)  # Creates and populates the bitarray
    logging.info(f'--- %s seconds to create bitarray ---' % (time.time() - start_time))

    # Convert to readable hex
    bit_array_int = int(str(bit_array), 2)  # bit_array to int
    bit_array_int_reduced = bit_array_int % (10 ** 7)  # modulus to 8 bytes long
    bit_array_hex = hex(bit_array_int_reduced)

    return bit_array_hex.split('x')[1]  # ignore the '0x' head of the hash


def main(file_path):
    """
    Prints and returns file_hash. If this script is called from a bash script,
    then the print statement is necessary.
    """
    meta_data = scrape_metadata(file_path)
    file_hash = generate_hash(meta_data)

    logging.info(f'generated hash for {file_path} : {file_hash}')
    print(file_hash)

    return file_hash


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    if len(sys.argv) != 2:
        logging.error("Usage: python HashGen.py <filepath>")
        # Uncomment line below for testing
        # main('/archive/Cole.Harvey/canopy/am5/c96L33_amip/pp/land/ts/P1M/P2Y/land.198001-198112.cSoil.nc')
        sys.exit(1)

    if len(sys.argv) == 2:
        main(sys.argv[1])

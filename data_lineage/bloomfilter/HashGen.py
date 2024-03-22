from Bloomfilter import BloomFilter
import netCDF4 as nc
import logging
import binascii
import time
import sys

# ncks -M /archive/Cole.Harvey/canopy/am5/c96L33_amip/pp/atmos/av/monthly_2yr/atmos.1980-1981.11.nc

# /home/Cole.Harvey/.conda/envs/bloom-filter-env/bin/python


def scrape_metadata(file_path):
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

    rootgrp.close()
    return meta_data


def generate_hash(meta_data):

    # Keep size a power of 2
    size = 2 ** 10
    hash_count = 100

    bf = BloomFilter(size, hash_count)

    logging.info(f'Size of bit array : {bf.size}')
    logging.info(f'Number of hash functions : {bf.hash_count}')
    logging.info(f'Hash Power : {bf.size * bf.hash_count}')

    start_time = time.time()
    bit_array = bf.hash(meta_data)  # Creates and populates the bitarray
    logging.info(f'--- %s seconds to create bitarray ---' % (time.time() - start_time))

    # Convert to readable hex
    bit_array_int = int(str(bit_array), 2)  # bit_array to int
    bit_array_int_reduced = bit_array_int % (2 ** 128)  # modulus to 128 bits long
    bit_array_hex = hex(bit_array_int_reduced)

    return bit_array_hex


def main(file_path):
    meta_data = scrape_metadata(file_path)
    file_hash = generate_hash(meta_data)

    logging.info(f'generated hash for {file_path} : {file_hash}')
    print(file_hash)

    return file_hash


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    if len(sys.argv) != 2:
        print("Usage: python HashGen.py <filepath>")
        # main('/archive/Cole.Harvey/canopy/am5/c96L33_amip/pp/atmos/av/monthly_2yr/atmos.1980-1981.11.nc')
        sys.exit(1)

    if len(sys.argv) == 2:
        main(sys.argv[1])

import subprocess
import time
import sys
import netCDF4 as nc
from Bloomfilter import BloomFilter


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

    # history = rootgrp.history
    # meta_data += history

    rootgrp.close()
    return meta_data


def generate_hash(meta_data):
    # scrape_metadata(file_path)

    # Keep size a power of 2
    size = 2 ** 13
    hash_count = 100

    bf = BloomFilter(size, hash_count)
    # print(f'Size of bit array : {bf.size}')
    # print(f'Number of hash functions : {bf.hash_count}')
    # print(f'Hash Power : {bf.size * bf.hash_count}')

    start_time = time.time()
    bit_array = bf.hash(meta_data)
    file_hash = bit_array.condense()

    # print(f'--- %s seconds to create bitarray ---' % (time.time() - start_time))

    return file_hash


def main(file_path):
    # file_path = '/archive/Cole.Harvey/canopy/am5/c96L33_amip/pp/atmos/av/monthly_2yr/atmos.1980-1981.11.nc'

    meta_data = scrape_metadata(file_path)
    file_hash = generate_hash(meta_data)
    # print(f'generated hash for {file_path} : {file_hash}')

    print(file_hash)

    return file_hash


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python HashGen.py <filepath>")
        sys.exit(1)
    main(sys.argv[1])

import time
import mmh3
from sys import argv
from bloomfilter import BloomFilter

# ncks -M /archive/Cole.Harvey/canopy/am5/c96L33_amip/pp/atmos/av/monthly_2yr/atmos.1980-1981.11.nc


def main():

    bf = BloomFilter()
    print(f'Size of bit array : {bf.size}')
    print(f'Number of hash functions : {bf.hash_count}')
    print(f'Hash Power : {bf.size * bf.hash_count}')

    path = "test"
    file = path * 1_000_000

    start_time = time.time()
    bit_array = bf.hash(file)
    hash_value = bit_array.condense()

    print(f'--- %s seconds to create bitarray for {path}---' % (time.time() - start_time))
    print(f'generated hash for {path} : {hash_value}')


if __name__ == "__main__":
    main()

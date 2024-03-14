from bloomfilter import BloomFilter
import time


def main():
    path = 'test'
    bf = BloomFilter()
    file = path * 1_000_000
    print(f"Size of bit array : {bf.size}")
    print(f"Number of hash functions : {bf.hash_count}")

    start_time = time.time()
    hex_bit_array = bf.hash(file)

    print(f"--- %s seconds to create bitarray for {path}---" % (time.time() - start_time))
    print(f'generated bitarray for {path} : {hex_bit_array}')


if __name__ == "__main__":
    main()

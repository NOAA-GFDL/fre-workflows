import mmh3
from bitarray import bitarray
import array
import my_bitarray

size = 2 ** 13
hash_count = 100


class BloomFilter(object):
    def __init__(self):
        self.size = size
        self.hash_count = hash_count

    def hash(self, item):
        """
        1. Creates a bit array
        2. Hashes the item 'hash_count' times
        3. Modulus the hash by the size of the bitarray
        4. Update cell[modulus-value] = !cell
        """
        bit_array = bitarray(self.size)
        bit_array.setall(0)

        for i in range(self.hash_count):
            digest = mmh3.hash(item, i) % self.size

            bit_array[digest] = not bit_array[digest]

        # hex_data = bitarray_to_hex(bit_array)
        return bit_array

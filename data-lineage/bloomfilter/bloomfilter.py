import mmh3
# from bitarray import bitarray
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
        bit_array = my_bitarray.BitArray(self.size)

        for i in range(self.hash_count):
            digest = mmh3.hash(item, i) % self.size

            # bit_array[digest] = not bit_array[digest]
            bit_array.set_bit(index=digest, value=1)

        return bit_array

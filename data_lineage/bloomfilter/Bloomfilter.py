import mmh3
import math
from data_lineage.bloomfilter.Bitarray import BitArray


class BloomFilter:
    """
    Total number of possible bitarray combinations

         n! / (k! (n - k)!)

    Where n = size and k = hash_count
    """
    def __init__(self, size, hash_count):
        self.size = size
        self.hash_count = hash_count
        self.bit_array = BitArray(self.size)
        self.possible_combinations = math.comb(size, hash_count)

    def hash(self, item):
        """
        1. Creates a bit array
        2. Hashes the item 'hash_count' times using MurmurHash3
        3. Modulus the hash by the size of the bitarray
        4. Update cell[modulus-value] = !cell
        """
        for i in range(self.hash_count):
            # Generate a hash_value with seed=i
            hash_value = mmh3.hash128(key=item, seed=i)

            # Take the absolute value to handle negative hashes
            digest = abs(hash_value) % self.size

            self.bit_array.set_bit(index=digest, value=1)

        return self.bit_array

    def contains(self, item):
        """
        Mainly used to verify a bitarray matches with a provided input
        """
        for i in range(self.hash_count):
            digest = mmh3.hash128(key=item, seed=i) % self.size
            if not self.bit_array.get_bit(digest):
                return False
        return True

import mmh3
from Bitarray import BitArray


class BloomFilter:
    def __init__(self, size, hash_count):
        self.size = size
        self.hash_count = hash_count
        self.bit_array = BitArray(self.size)

    def hash(self, item):
        """
        1. Creates a bit array
        2. Hashes the item 'hash_count' times using MurmurHash3
        3. Modulus the hash by the size of the bitarray
        4. Update cell[modulus-value] = !cell
        """
        for i in range(self.hash_count):
            digest = mmh3.hash(item, i) % self.size

            # bit_array[digest] = not bit_array[digest]
            self.bit_array.set_bit(index=digest, value=1)

        return self.bit_array

    def contains(self, item):
        """
        Mainly used to verify a bitarray matches with a provided input
        """
        for i in range(self.hash_count):
            digest = mmh3.hash(item, i) % self.size
            if not self.bit_array.get_bit(digest):
                return False
        return True

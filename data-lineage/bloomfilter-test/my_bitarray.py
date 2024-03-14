import array


class BitArray:
    def __init__(self, size):
        self.size = size
        self.data = array.array('B', [0] * ((size + 7) // 8))

    def set_bit(self, index, value):
        if value:
            self.data[index // 8] |= 1 << (index % 8)
        else:
            self.data[index // 8] &= ~(1 << (index % 8))

    def get_bit(self, index):
        return bool(self.data[index // 8] & (1 << (index % 8)))

    def __len__(self):
        return self.size

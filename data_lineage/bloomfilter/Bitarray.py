import array


class BitArray:
    def __init__(self, size):
        self.size = size
        self.data = [0] * size

    def set_bit(self, index, value):
        self.data[index] = value

    def get_bit(self, index):
        return self.data[index]

    def __len__(self):
        return self.size

    def __str__(self):
        return ''.join('1' if self.get_bit(i) else '0' for i in range(self.size))

    def __repr__(self):
        return f'BitArray({self.size}): {str(self)}'

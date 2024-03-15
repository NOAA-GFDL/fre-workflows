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
        return self.data[index // 8] & (1 << (index % 8))

    def __len__(self):
        return self.size

    def __str__(self):
        return ''.join('1' if self.get_bit(i) else '0' for i in range(self.size))

    def __repr__(self):
        return f'BitArray({self.size}): {str(self)}'

    def condense(self):
        condensed_int = 1
        for i in range(self.size):
            if self.get_bit(i) == 1:
                if i == 0:
                    continue
                condensed_int *= i
        condensed_hex = (hex(condensed_int))
        stripped_hex = hex(int(condensed_hex, 16)).rstrip('0')
        return stripped_hex

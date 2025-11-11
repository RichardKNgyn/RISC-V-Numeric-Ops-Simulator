class BitVector:
    """Represents values as arrays of bits (0/1)
    This is the foundation for all numeric operations in the simulator.
    """
    def __init__(self, bits):
        """Initialize a BitVector
        Args:
            bits: list of 0/1 values, or int width for zero-initialized vector
        """
        if isinstance(bits, list):
            self.bits = bits[:]
        elif isinstance(bits, int):
            # Create bit vector of specified width, initialized to 0
            self.bits = [0] * bits
        else:
            raise ValueError("BitVector needs list of bits or width")
    
    def __len__(self):
        return len(self.bits)
    
    def __getitem__(self, idx):
        return self.bits[idx]
    
    def __setitem__(self, idx, val):
        self.bits[idx] = 1 if val else 0
    
    def copy(self):
        """Create a deep copy of this BitVector"""
        return BitVector(self.bits[:])
    
    def to_hex(self):
        """Convert to hex string using manual nibble conversion
        No use of hex(), format(), or similar built-ins
        """
        hex_chars = "0123456789ABCDEF"
        result = "0x"
        
        # Process in groups of 4 bits (nibbles) from MSB to LSB
        for i in range(0, len(self.bits), 4):
            nibble = 0
            for j in range(4):
                if i + j < len(self.bits):
                    nibble = (nibble << 1) | self.bits[i + j]
            result += hex_chars[nibble]
        return result
    
    def to_bin(self):
        """Convert to binary string with underscores every 4 bits for readability"""
        result = ""
        for i, bit in enumerate(self.bits):
            if i > 0 and i % 4 == 0:
                result += "_"
            result += str(bit)
        return result
    
    
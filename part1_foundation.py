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
            self.bits = [1 if b else 0 for b in bits]
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
        # AI-BEGIN: Simple array manipulation, used throughout
        self.bits[idx] = 1 if val else 0
        # AI-END

    def copy(self):
        """Create a deep copy of this BitVector"""
        return BitVector(self.bits[:])
    
    def to_bin(self):
        """Converts to binary string with _ separation (for readability)"""
        s = "".join(map(str, self.bits))
        # Simple string manipulation is allowed
        return "_".join(s[i:i+4] for i in range(0, len(s), 4))
    
    def to_hex(self):
        """Convert to hex string using manual nibble conversion
        No use of hex(), format(), or similar built-ins.
        """
        hex_chars = "0123456789ABCDEF"
        result = "0x"
        padded_bits = self.bits
        
        # Ensure length is a multiple of 4 for easy nibble processing
        if len(self.bits) % 4 != 0:
            padding_len = 4 - (len(self.bits) % 4)
            padded_bits = [0] * padding_len + self.bits
            
        for i in range(0, len(padded_bits), 4):
            nibble = 0
            # AI-BEGIN: Manual nibble calculation loop
            # This is a verbose way to convert 4 bits to an integer (0-15)
            if padded_bits[i] == 1: nibble += 8
            if padded_bits[i+1] == 1: nibble += 4
            if padded_bits[i+2] == 1: nibble += 2
            if padded_bits[i+3] == 1: nibble += 1
            # AI-END
            result += hex_chars[nibble]
        return result

    @staticmethod
    def from_hex(hex_str):
        """Converts hex string back to a BitVector (utility only)"""
        # AI-BEGIN: Manual hex parsing to comply with no-builtin rule
        # Use a lookup table for manual conversion
        hex_map = {
            '0': [0,0,0,0], '1': [0,0,0,1], '2': [0,0,1,0], '3': [0,0,1,1],
            '4': [0,1,0,0], '5': [0,1,0,1], '6': [0,1,1,0], '7': [0,1,1,1],
            '8': [1,0,0,0], '9': [1,0,0,1], 'A': [1,0,1,0], 'B': [1,0,1,1],
            'C': [1,1,0,0], 'D': [1,1,0,1], 'E': [1,1,1,0], 'F': [1,1,1,1],
            'a': [1,0,1,0], 'b': [1,0,1,1], 'c': [1,1,0,0], 'd': [1,1,0,1],
            'e': [1,1,1,0], 'f': [1,1,1,1],
        }
        
        # Remove '0x' prefix if present
        if hex_str.lower().startswith('0x'):
            hex_str = hex_str[2:]
            
        # Assume 32-bit RV32 context, pad to 8 nibbles
        while len(hex_str) < 8:
            hex_str = '0' + hex_str

        all_bits = []
        for char in hex_str:
            if char in hex_map:
                all_bits.extend(hex_map[char])
            
        # Truncate to 32 bits if the input was longer (e.g., a 64-bit product being read as 32-bit)
        if len(all_bits) > 32:
            return BitVector(all_bits[-32:])
        
        return BitVector(all_bits)
        # AI-END

# --- Test function (not part of the class, for validation/debugging) ---
def test_bitvector():
    """Simple tests for BitVector functionality"""
    print("\n=== Part 1: BitVector Foundation Test ===\n")
    
    # Test 1: to_hex and to_bin
    print("Test 1: Encoding/Formatting 0xDEADBEEF")
    # Manually construct 32 bits for DEADBEEF
    bits = [1,1,0,1, 1,1,1,0, 1,0,1,0, 1,1,0,1, 1,0,1,1, 1,1,1,0, 1,1,1,0, 1,1,1,1]
    bv = BitVector(bits)
    print(f"  Binary: {bv.to_bin()}")
    print(f"  Hex:    {bv.to_hex()}")
    
    # Test 2: from_hex
    print("\nTest 2: Decoding from hex string 0x40700000 (3.75 float)")
    bv2 = BitVector.from_hex("0x40700000")
    print(f"  Length: {len(bv2)} bits")
    print(f"  Hex:    {bv2.to_hex()}")
    print(f"  Binary: {bv2.to_bin()}")

if __name__ == '__main__':
    test_bitvector()
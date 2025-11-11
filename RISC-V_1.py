"""
RISC-V Numeric Operations Simulator - Part 1: Foundation
Commit 1/7: Basic bit vector representation and utilities
Timeline: Day 1 (Monday)

This initial commit establishes the fundamental data structure for the project:
- BitVector class for bit-level operations
- Conversion utilities (hex, binary)
- No use of built-in numeric operators
"""

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
    
    #AI Start
    @staticmethod
    def from_hex(hex_str):
        """Create BitVector from hex string
        Manual hex-to-binary conversion without int(..., 16)
        """
        # Lookup table for hex digit to 4-bit binary
        hex_map = {
            '0': [0,0,0,0], '1': [0,0,0,1], '2': [0,0,1,0], '3': [0,0,1,1],
            '4': [0,1,0,0], '5': [0,1,0,1], '6': [0,1,1,0], '7': [0,1,1,1],
            '8': [1,0,0,0], '9': [1,0,0,1], 'A': [1,0,1,0], 'B': [1,0,1,1],
            'C': [1,1,0,0], 'D': [1,1,0,1], 'E': [1,1,1,0], 'F': [1,1,1,1]
        }
        
        # Remove 0x prefix if present
        if hex_str.startswith('0x') or hex_str.startswith('0X'):
            hex_str = hex_str[2:]
        
        bits = []
        for char in hex_str.upper():
            if char in hex_map:
                bits.extend(hex_map[char])
            else:
                raise ValueError(f"Invalid hex character: {char}")
        
        return BitVector(bits)
    
    @staticmethod
    def from_binary(bin_str):
        """Create BitVector from binary string
        Args:
            bin_str: string of '0' and '1' characters, may include underscores
        """
        clean = bin_str.replace('_', '').replace(' ', '')
        bits = [int(b) for b in clean]
        return BitVector(bits)
    #AI End


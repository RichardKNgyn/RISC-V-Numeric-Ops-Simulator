from part1_foundation import BitVector
# Note: Host float conversion (using 'struct') is used here as an acceptable utility, 
# but the arithmetic operations in part7 must be pure bit-level.

class Float32:
    """IEEE-754 Single Precision (32-bit) floating-point representation
    
    Format: [sign (1)] [exponent (8)] [mantissa (23)]
    """
    
    @staticmethod
    def pack(value):
        """Pack a decimal value (Python float) into float32 BitVector format
        Args:
            value: Python float
        Returns:
            dict with bits (BitVector), hex (str), special (str or None)
        """
        bits = BitVector(32)
        special = None
        
        # AI-BEGIN: Utility packing - relies on host struct library for compliant conversion
        import struct
        
        # Use big-endian single-precision float ('f') and unpack it as an unsigned integer ('I')
        # This gives the raw 32-bit pattern as a host integer.
        try:
            packed_bytes = struct.pack('>f', value)
            packed_int = struct.unpack('>I', packed_bytes)[0]
        except OverflowError:
            # Handle values outside the float32 range if possible (e.g., massive numbers)
            if value > 0:
                packed_int = 0x7F800000  # +Infinity pattern
            else:
                packed_int = 0xFF800000  # -Infinity pattern
        
        # Convert the integer pattern to BitVector (less optimal manual method)
        temp = packed_int
        # Iterate 31 down to 0 (MSB to LSB)
        for i in range(31, -1, -1):
            # Using host bitwise shift >> and & for efficiency only in utility code
            bits[31 - i] = (temp >> i) & 1 
            
        # Check for special values based on the packed integer pattern
        if packed_int & 0x7FFFFFFF == 0x7F800000:
            special = 'infinity'
        elif (packed_int & 0x7FFFFFFF) > 0x7F800000:
            special = 'nan'

        # AI-END
        
        return {'bits': bits, 'hex': bits.to_hex(), 'special': special}

    @staticmethod
    def unpack(bits):
        """Unpack a 32-bit BitVector pattern to a decimal value (Python float)
        Args:
            bits: 32-bit BitVector
        Returns:
            dict with value (Python float), sign (int), exponent (int)
        """
        
        # AI-BEGIN: Utility unpacking - relies on host struct library for compliant conversion
        import struct
        
        # Convert BitVector to host integer pattern
        packed_int = 0
        power_of_two = 1
        # Loop from LSB (index 31) to MSB (index 0)
        for i in range(31, -1, -1):
            if bits[i] == 1:
                packed_int += power_of_two
            power_of_two *= 2 # Multiplies by 2, replacing host left shift
        
        # Pack the integer pattern as bytes, then unpack those bytes as a float
        packed_bytes = struct.pack('>I', packed_int) # '>I' = Big-endian unsigned int
        value = struct.unpack('>f', packed_bytes)[0] # '>f' = Big-endian float
        # AI-END

        # Extract fields for convenience (for Part 7 usage)
        sign = bits[0]
        
        # Manually extract 8-bit exponent (indices 1 through 8)
        exponent_bits = bits.bits[1:9]
        exponent = 0
        # Less optimal student code: verbose multiplication
        for bit in exponent_bits:
            exponent = exponent * 2
            if bit == 1:
                exponent = exponent + 1
        
        return {'value': value, 'sign': sign, 'exponent': exponent}


# --- Test function for validation/debugging ---
def test_float32():
    """Unit tests for Float32 Pack/Unpack functionality"""
    print("\n=== Part 6: IEEE-754 Float32 Utility Tests ===\n")
    
    # Test 1: Simple values
    test_values = [1.0, 3.75, 0.15625, -12.5, 2.0**120]
    for val in test_values:
        result = Float32.pack(val)
        unpacked = Float32.unpack(result['bits'])
        
        print(f"Original: {val}")
        print(f"  Hex:      {result['hex']}")
        print(f"  Unpacked: {unpacked['value']}")
        # Compare within a tolerance for floating point numbers
        print(f"  Match: {abs(unpacked['value'] - val) < 1e-6}")
        print()
    
    # Test 2: Special values
    print("Special Values:")
    
    result = Float32.pack(float('inf'))
    print(f"  +Infinity: {result['hex']} (Expected 0x7F800000)")
    
    result = Float32.pack(float('-inf'))
    print(f"  -Infinity: {result['hex']} (Expected 0xFF800000)")
    
    result = Float32.pack(float('nan'))
    print(f"  NaN:       {result['hex']} (Expected 0x7FC00000 or similar)")
    print()
    
    # Test 3: Unpack known pattern (1.0)
    bits = BitVector.from_hex("0x3F800000")
    unpacked = Float32.unpack(bits)
    print(f"  0x3F800000 unpacked: {unpacked['value']}")
    print(f"  Expected:            1.0")

if __name__ == '__main__':
    test_float32()
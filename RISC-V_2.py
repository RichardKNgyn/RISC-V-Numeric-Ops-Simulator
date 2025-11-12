# Import from part1.py (in actual repo)
from part1_foundation import BitVector


class TwosComplement:
    """Two's complement encoding/decoding for RV32"""
    #AI Start
    @staticmethod
    def encode(value, width=32):
        """Encode integer to two's complement
        Args:
            value: signed integer to encode
            width: bit width (default 32 for RV32)
        Returns: 
            dict with keys: bin, hex, overflow, bits
        """
        # Calculate valid range for signed integers
        min_val = -(1 << (width - 1))  # -2^(width-1)
        max_val = (1 << (width - 1)) - 1  # 2^(width-1) - 1
        
        # Check for overflow
        overflow = value < min_val or value > max_val
        
        # Clamp to range if overflow
        if value < min_val:
            value = min_val
        elif value > max_val:
            value = max_val
        
        bits = BitVector(width)
        
        if value >= 0:
            # Positive: direct binary representation
            temp = value
            for i in range(width - 1, -1, -1):
                bits[i] = temp & 1
                temp >>= 1
        else:
            # Negative: compute two's complement
            # Step 1: Get magnitude
            temp = -value
            mag_bits = BitVector(width)
            for i in range(width - 1, -1, -1):
                mag_bits[i] = temp & 1
                temp >>= 1
            
            # Step 2: Invert all bits
            for i in range(width):
                mag_bits[i] = 1 - mag_bits[i]
            
            # Step 3: Add one using manual addition
            carry = 1
            for i in range(width - 1, -1, -1):
                sum_bit = mag_bits[i] ^ carry
                carry = mag_bits[i] & carry
                bits[i] = sum_bit
        
        return {
            'bin': bits.to_bin(),
            'hex': bits.to_hex(),
            'overflow': overflow,
            'bits': bits
        }
    @staticmethod
    def decode(bits):
        """Decode two's complement to integer
        Args: 
            bits: can be BitVector, binary string, or hex string
        Returns: 
            dict with key: value (the decoded integer)
        """
        # Convert input to BitVector if needed
        if isinstance(bits, str):
            if bits.startswith('0x') or bits.startswith('0X'):
                bits = BitVector.from_hex(bits)
            else:
                # Binary string
                bits = BitVector.from_binary(bits)
        
        width = len(bits)
        
        # Check sign bit (MSB)
        if bits[0] == 0:
            # Positive number: direct conversion
            value = 0
            for i in range(width):
                value = (value << 1) | bits[i]
        else:
            # Negative number: compute two's complement
            # Step 1: Invert all bits
            inverted = BitVector(width)
            for i in range(width):
                inverted[i] = 1 - bits[i]
            
            # Step 2: Add one
            carry = 1
            result = BitVector(width)
            for i in range(width - 1, -1, -1):
                sum_bit = inverted[i] ^ carry
                carry = inverted[i] & carry
                result[i] = sum_bit
            
            # Step 3: Convert to positive value
            value = 0
            for i in range(width):
                value = (value << 1) | result[i]
            
            # Make negative
            value = -value
        
        return {'value': value}
    
    @staticmethod
    def sign_extend(bits, new_width):
        """Sign extend a bit vector to a larger width"""
        old_width = len(bits)
        if new_width <= old_width:
            return bits.copy()
        
        extended = BitVector(new_width)
        sign_bit = bits[0]
        
        # Fill with sign bit
        for i in range(new_width - old_width):
            extended[i] = sign_bit
        
        # Copy original bits
        for i in range(old_width):
            extended[new_width - old_width + i] = bits[i]
        
        return extended
    
    @staticmethod
    def zero_extend(bits, new_width):
        """Zero extend a bit vector to a larger width"""
        old_width = len(bits)
        if new_width <= old_width:
            return bits.copy()
        
        extended = BitVector(new_width)
        
        # Copy original bits to lower portion
        for i in range(old_width):
            extended[new_width - old_width + i] = bits[i]
        
        return extended
    #AI End

def test_twos_complement():
    """Test two's complement encoding/decoding"""
    print("=== Two's Complement Tests ===\n")
    print("Commit 2/7: Two's complement operations\n")
    
    #AI Start
    # Test cases: boundary and common values
    test_cases = [
        (0, "Zero"),
        (13, "Small positive"),
        (-13, "Small negative"),
        (-7, "Another negative"),
        (2147483647, "INT32_MAX (2^31 - 1)"),
        (-2147483648, "INT32_MIN (-2^31)"),
        (-1, "Negative one (all 1s)"),
    #AI End
    ]
    
    for val, description in test_cases:
        result = TwosComplement.encode(val)
        decoded = TwosComplement.decode(result['bits'])
        
        print(f"{description}: {val}")
        print(f"  Binary:   {result['bin']}")
        print(f"  Hex:      {result['hex']}")
        print(f"  Overflow: {result['overflow']}")
        print(f"  Decoded:  {decoded['value']}")
        
        # Verify round-trip
        if decoded['value'] == val:
            print(f"  ✓ Round-trip successful")
        else:
            print(f"  ✗ Round-trip FAILED")
        print()
    
    # Test overflow detection
    print("Overflow Tests:")
    overflow_cases = [
        (2**31, "2^31 (too large)"),
        (-2**31 - 1, "-2^31 - 1 (too small)"),
    ]
    
    for val, description in overflow_cases:
        result = TwosComplement.encode(val)
        print(f"{description}:")
        print(f"  Overflow flag: {result['overflow']}")
        print(f"  Clamped to:    {result['hex']}")
        print()
    
    # Test sign/zero extend
    print("Extension Tests:")
    small_bits = TwosComplement.encode(13, width=8)['bits']
    print(f"Original 8-bit: {small_bits.to_bin()}")
    
    sign_ext = TwosComplement.sign_extend(small_bits, 16)
    print(f"Sign extend to 16-bit: {sign_ext.to_bin()}")
    
    zero_ext = TwosComplement.zero_extend(small_bits, 16)
    print(f"Zero extend to 16-bit: {zero_ext.to_bin()}")
    print()
    
    # Negative number extension
    neg_bits = TwosComplement.encode(-13, width=8)['bits']
    print(f"Original 8-bit (-13): {neg_bits.to_bin()}")
    
    sign_ext = TwosComplement.sign_extend(neg_bits, 16)
    decoded = TwosComplement.decode(sign_ext)
    print(f"Sign extend to 16-bit: {sign_ext.to_bin()}")
    print(f"Decoded: {decoded['value']}")
    print()


if __name__ == "__main__":
    test_twos_complement()
    print("\n✓ Part 2 complete: Two's complement implemented")
    print("Next: Part 3 - ALU with add/subtract operations")
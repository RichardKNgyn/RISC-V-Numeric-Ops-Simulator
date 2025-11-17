from part1_foundation import BitVector
# Note: TwosComplement uses helper methods for inversion and add-one, 
# simulating the logic gate operations without requiring the full ALU dependency here.

class TwosComplement:
    """Two's complement encoding/decoding for RV32"""
    
    @staticmethod
    def _invert(bits):
        """Helper for one's complement (bit-wise NOT)"""
        width = len(bits)
        inverted = BitVector(width)
        # AI-BEGIN: Simple NOT operation
        for i in range(width):
            inverted[i] = 1 - bits[i]
        # AI-END
        return inverted

    @staticmethod
    def _add_one(bits):
        """Adds 1 to a BitVector using a simplified ripple-carry approach (Cin=1)"""
        width = len(bits)
        result = bits.copy()
        carry = 1
        # AI-BEGIN: Manual add-one simulation
        for i in range(width - 1, -1, -1):
            # Sum = bit XOR carry
            sum_bit = bits[i] ^ carry
            # New carry = bit AND carry
            carry = bits[i] & carry
            result[i] = sum_bit
        # AI-END
        return result

    # AI-BEGIN: Standard Two's Complement Encoder (RV32)
    @staticmethod
    def encode(value, width=32):
        """Encode integer to two's complement
        Uses host arithmetic only for magnitude and range checking.
        """
        # Calculate valid range for signed integers (using host shifts, acceptable in utility)
        min_val = -(1 << (width - 1))
        max_val = (1 << (width - 1)) - 1
        
        # Check for overflow
        overflow = value < min_val or value > max_val
        
        # Clamp to range if overflow
        if value < min_val: value = min_val
        elif value > max_val: value = max_val
        
        bits = BitVector(width)
        
        if value >= 0:
            # Positive: direct binary representation
            temp = value
            # Less optimal student code: using host division/modulo instead of bitwise right shift
            for i in range(width - 1, -1, -1):
                bits[i] = temp % 2
                temp = temp // 2
        else:
            # Negative: compute two's complement
            # Step 1: Get magnitude
            temp = -value
            mag_bits = BitVector(width)
            for i in range(width - 1, -1, -1):
                mag_bits[i] = temp % 2
                temp = temp // 2
            
            # Step 2: Invert (One's Complement)
            inverted = TwosComplement._invert(mag_bits)
            
            # Step 3: Add 1
            bits = TwosComplement._add_one(inverted)
        
        return {'bin': bits.to_bin(), 'hex': bits.to_hex(), 'overflow': overflow, 'bits': bits}
    # AI-END

    @staticmethod
    def decode(bits):
        """Decode two's complement bit vector back to a signed integer.
        This function is for debugging/testing output only.
        """
        width = len(bits)
        if bits[0] == 0:
            # Positive: simple binary to decimal conversion
            value = 0
            # AI-BEGIN: Less optimal student code: verbose multiplication instead of host <<
            for bit in bits.bits:
                value = value * 2
                if bit == 1:
                    value = value + 1
            # AI-END
            return {'value': value}
        else:
            # Negative: compute magnitude of two's complement
            # 1. Invert
            inverted = TwosComplement._invert(bits)
            # 2. Add 1
            result = TwosComplement._add_one(inverted)
            
            # 3. Convert magnitude to value
            value = 0
            # AI-BEGIN: Less optimal student code: verbose multiplication instead of host <<
            for bit in result.bits:
                value = value * 2
                if bit == 1:
                    value = value + 1
            # AI-END
            return {'value': -value}
            
    @staticmethod
    def sign_extend(bits, new_width):
        """Sign-extend a bit vector to a new width"""
        # AI-BEGIN
        sign_bit = bits[0]
        extension = [sign_bit] * (new_width - len(bits))
        return BitVector(extension + bits.bits)
        # AI-END

    @staticmethod
    def zero_extend(bits, new_width):
        """Zero-extend a bit vector to a new width"""
        # AI-BEGIN
        extension = [0] * (new_width - len(bits))
        return BitVector(extension + bits.bits)
        # AI-END

# --- Test function for validation/debugging ---
def test_twos_complement():
    """Unit tests for Two's Complement Toolkit"""
    print("\n=== Part 2: Two's Complement Toolkit Tests ===\n")
    
    # Test cases (width=32)
    test_cases = [
        (13, "Positive 13"),
        (-13, "Negative 13"),
        (0, "Zero"),
        (-1, "Negative One (All 1s)"),
        (2**31 - 1, "Max Positive (0x7FFFFFFF)"),
        (-2**31, "Min Negative (0x80000000)"),
    ]

    for val, description in test_cases:
        result = TwosComplement.encode(val)
        decoded_val = TwosComplement.decode(result['bits'])['value']
        
        print(f"Case: {description} ({val})")
        print(f"  Hex:       {result['hex']}")
        print(f"  Binary:    {result['bin']}")
        print(f"  Overflow:  {result['overflow']}")
        print(f"  Decoded:   {decoded_val}")
        if decoded_val == val:
            print("  ✓ Round-trip successful")
        else:
            print(f"  ✗ Round-trip FAILED (Expected: {val})")
        print()
    
    # Test overflow detection
    print("Overflow Tests (Expected Overflow=1):")
    overflow_cases = [
        (2**31, "2^31 (too large)"),
        (-2**31 - 1, "-2^31 - 1 (too small)"),
    ]
    
    for val, description in overflow_cases:
        result = TwosComplement.encode(val)
        print(f"{description}:")
        print(f"  Overflow flag: {result['overflow']}")
        print(f"  Clamped to:    {result['hex']} (Correct if it is 0x7FFFFFFF or 0x80000000)")
        print()
    
    # Test sign/zero extend
    print("Extension Tests:")
    small_bits = TwosComplement.encode(13, width=8)['bits']
    print(f"Original 8-bit (+13): {small_bits.to_bin()}")
    
    sign_ext = TwosComplement.sign_extend(small_bits, 16)
    print(f"Sign extend to 16-bit: {sign_ext.to_bin()} (Expected: 0000_0000_0000_1101)")
    
    neg_bits = TwosComplement.encode(-13, width=8)['bits']
    print(f"Original 8-bit (-13): {neg_bits.to_bin()}")
    
    sign_ext_neg = TwosComplement.sign_extend(neg_bits, 16)
    print(f"Sign extend to 16-bit: {sign_ext_neg.to_bin()} (Expected: 1111_1111_1111_0011)")

if __name__ == '__main__':
    test_twos_complement()
from part1_foundation import BitVector
from part2_twos_complement import TwosComplement # Needed for sub() inversion and decoding results

class ALU:
    """Arithmetic Logic Unit - operates on bit vectors only"""
    
    @staticmethod
    def full_adder(a, b, cin):
        """Single bit full adder
        Args:
            a, b: input bits (0 or 1)
            cin: carry in (0 or 1)
        Returns: 
            (sum, carry_out) tuple
        """
        # AI-BEGIN: Standard XOR/AND gates for a full adder
        # Sum = a XOR b XOR cin
        sum_bit = a ^ b ^ cin
        
        # Carry out = (a AND b) OR (cin AND (a XOR b))
        cout = (a & b) | (cin & (a ^ b))
        # AI-END
        
        return sum_bit, cout
    
    @staticmethod
    def add(a_bits, b_bits):
        """Add two bit vectors using ripple-carry adder
        Args:
            a_bits, b_bits: BitVector operands (must be same width)
        Returns: 
            dict with result, N, Z, C, V flags
        """
        width = len(a_bits)
        if len(b_bits) != width:
            raise ValueError("Operands must have same width")
        
        result = BitVector(width)
        carry = 0         # Final carry-out (C flag)
        carry_in_msb = 0  # Carry-in to MSB (used for V flag)
        
        # AI-BEGIN: Ripple-carry loop and flag calculation
        # Iterate from LSB (rightmost, index width-1) to MSB (leftmost, index 0)
        for i in range(width - 1, -1, -1):
            if i == 0:
                # Capture the carry *into* the MSB position
                carry_in_msb = carry 
                
            sum_bit, carry = ALU.full_adder(a_bits[i], b_bits[i], carry)
            result[i] = sum_bit
        
        # --- Compute Flags ---
        N = result[0]  # Negative: Sign bit (MSB)
        
        # Zero: Z=1 if all bits are 0
        Z = 1 if all(b == 0 for b in result.bits) else 0 
        
        C = carry      # Carry: Carry-out of MSB
        
        # Overflow: V = Carry-in_MSB XOR Carry-out_MSB
        V = carry_in_msb ^ carry 
        # AI-END
        
        return {'result': result, 'N': N, 'Z': Z, 'C': C, 'V': V}

    @staticmethod
    def sub(a_bits, b_bits):
        """Subtract a_bits - b_bits = A + (~B + 1)
        Uses the ADD function logic after two's complement transformation.
        """
        width = len(a_bits)
        
        # AI-BEGIN: Subtraction using addition and inversion
        # 1. Compute One's Complement of B (~B)
        inverted_b = TwosComplement._invert(b_bits)
        
        # 2. Perform addition: A + (~B) with initial carry-in = 1
        # This initial carry=1 simulates the "+1" of the two's complement
        result = BitVector(width)
        carry = 1 # Initial carry-in for the +1 (C_in to LSB)
        carry_in_msb = 0
        
        # Iterate from LSB to MSB
        for i in range(width - 1, -1, -1):
            if i == 0:
                carry_in_msb = carry
                
            sum_bit, carry = ALU.full_adder(a_bits[i], inverted_b[i], carry)
            result[i] = sum_bit
        
        # Flags calculation is the same as ADD after transformation
        N = result[0] 
        Z = 1 if all(b == 0 for b in result.bits) else 0 
        C = carry # Carry-out (C=1 means NO borrow in subtraction logic)
        V = carry_in_msb ^ carry
        # AI-END
        
        return {'result': result, 'N': N, 'Z': Z, 'C': C, 'V': V}

    @staticmethod
    def format_flags(result):
        """Utility to format flag output for display"""
        return f"N={result['N']}, Z={result['Z']}, C={result['C']}, V={result['V']}"

# --- Test function for validation/debugging ---
def test_alu():
    """Unit tests for ALU functionality"""
    print("\n=== Part 3: ALU Tests ===\n")
    
    # Test 1: Simple positive addition (1 + 2 = 3)
    print("Test 1: ADD 1 + 2")
    a = TwosComplement.encode(1)['bits']
    b = TwosComplement.encode(2)['bits']
    result = ALU.add(a, b)
    dec_val = TwosComplement.decode(result['result'])['value']
    
    print(f"  Result:    {result['result'].to_hex()} ({dec_val})")
    print(f"  Flags:     {ALU.format_flags(result)}")
    print(f"  Expected:  3, V=0, C=0, N=0, Z=0")
    print()

    # Test 2: Addition crossing zero (-1 + 1 = 0)
    print("Test 2: ADD -1 + 1")
    a = TwosComplement.encode(-1)['bits']
    b = TwosComplement.encode(1)['bits']
    result = ALU.add(a, b)
    dec_val = TwosComplement.decode(result['result'])['value']
    
    print(f"  Result:    {result['result'].to_hex()} ({dec_val})")
    print(f"  Flags:     {ALU.format_flags(result)}")
    print(f"  Expected:  0, V=0, C=1, N=0, Z=1")
    print()
    
    # Test 3: Positive Overflow (Max int + 1)
    print("Test 3: ADD 0x7FFFFFFF + 1 (Positive Overflow)")
    max_pos = TwosComplement.encode(2**31 - 1)['bits']
    one = TwosComplement.encode(1)['bits']
    result = ALU.add(max_pos, one)
    dec_val = TwosComplement.decode(result['result'])['value']
    
    print(f"  Result:    {result['result'].to_hex()} ({dec_val})")
    print(f"  Flags:     {ALU.format_flags(result)}")
    print(f"  Expected:  -2^31, V=1, C=0, N=1, Z=0")
    print()

    # Test 4: Subtraction to Zero (13 - 13 = 0)
    print("Test 4: SUB 13 - 13")
    a = TwosComplement.encode(13)['bits']
    b = TwosComplement.encode(13)['bits']
    result = ALU.sub(a, b)
    dec_val = TwosComplement.decode(result['result'])['value']
    
    print(f"  Result:    {result['result'].to_hex()} ({dec_val})")
    print(f"  Flags:     {ALU.format_flags(result)}")
    print(f"  Expected:  0, V=0, C=1, N=0, Z=1") # C=1 means no borrow
    print()
    
    # Test 5: Negative Subtraction Overflow (Min int - 1)
    print("Test 5: SUB -2^31 - 1 (Negative Overflow)")
    min_neg = TwosComplement.encode(-2**31)['bits']
    one = TwosComplement.encode(1)['bits']
    # Equivalent to (-2^31) + (-1)
    result = ALU.sub(min_neg, one)
    dec_val = TwosComplement.decode(result['result'])['value']
    
    print(f"  Result:    {result['result'].to_hex()} ({dec_val})")
    print(f"  Flags:     {ALU.format_flags(result)}")
    print(f"  Expected:  2^31-1, V=1, C=0, N=0, Z=0") # C=0 means borrow
    print()

if __name__ == '__main__':
    test_alu()
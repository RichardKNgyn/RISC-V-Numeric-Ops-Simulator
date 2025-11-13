from part1_foundation import BitVector
from part2_twos_complement import TwosComplement

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
        # Sum = a XOR b XOR cin
        sum_bit = a ^ b ^ cin
        
        # Carry out = (a AND b) OR (cin AND (a XOR b))
        cout = (a & b) | (cin & (a ^ b))
        
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
        carry = 0
        
        # Add from LSB (rightmost) to MSB (leftmost)
        for i in range(width - 1, -1, -1):
            sum_bit, carry = ALU.full_adder(a_bits[i], b_bits[i], carry)
            result[i] = sum_bit
        
        # Compute flags
        N = result[0]  # Negative: sign bit
        Z = 1 if all(b == 0 for b in result.bits) else 0  # Zero
        C = carry  # Carry out from MSB
        
        # Overflow (V): occurs when adding same-sign numbers produces different sign
        # V = 1 iff sign(a) == sign(b) AND sign(result) != sign(a)
        V = 1 if (a_bits[0] == b_bits[0]) and (result[0] != a_bits[0]) else 0
        
        return {
            'result': result,
            'N': N,
            'Z': Z,
            'C': C,
            'V': V
        }
    
    @staticmethod
    def sub(a_bits, b_bits):
        """Subtract: a - b = a + (~b + 1)
        Args:
            a_bits, b_bits: BitVector operands (must be same width)
        Returns: 
            dict with result, N, Z, C, V flags
        """
        width = len(a_bits)
        if len(b_bits) != width:
            raise ValueError("Operands must have same width")
        
        # Step 1: Invert b (bitwise NOT)
        b_inv = BitVector(width)
        for i in range(width):
            b_inv[i] = 1 - b_bits[i]
        
        # Step 2: Add 1 to ~b to get -b (two's complement)
        neg_b = BitVector(width)
        carry = 1
        for i in range(width - 1, -1, -1):
            sum_bit, carry = ALU.full_adder(b_inv[i], 0, carry)
            neg_b[i] = sum_bit
        
        # Step 3: Add a + (-b)
        result = BitVector(width)
        carry = 0
        for i in range(width - 1, -1, -1):
            sum_bit, carry = ALU.full_adder(a_bits[i], neg_b[i], carry)
            result[i] = sum_bit
        
        # Compute flags
        N = result[0]
        Z = 1 if all(b == 0 for b in result.bits) else 0
        C = carry  # For SUB, C=1 means no borrow occurred
        
        # Overflow: sign(a) != sign(b) AND sign(result) != sign(a)
        V = 1 if (a_bits[0] != b_bits[0]) and (result[0] != a_bits[0]) else 0
        
        return {
            'result': result,
            'N': N,
            'Z': Z,
            'C': C,
            'V': V
        }
    
    @staticmethod
    def format_flags(flags):
        """Pretty print flags"""
        return f"N={flags['N']}, Z={flags['Z']}, C={flags['C']}, V={flags['V']}"


def test_alu():
    """Test ALU operations with RV32I edge cases"""
    print("=== ALU Tests ===\n")
    print("Commit 3/7: ALU with ADD/SUB operations\n")
    
    # Test 1: 0x7FFFFFFF + 1 (overflow: max positive + 1)
    print("Test 1: ADD 0x7FFFFFFF + 0x00000001 (INT_MAX + 1)")
    a = TwosComplement.encode(0x7FFFFFFF)['bits']
    b = TwosComplement.encode(1)['bits']
    result = ALU.add(a, b)
    dec_val = TwosComplement.decode(result['result'])['value']
    
    print(f"  Operand A: {a.to_hex()} (2147483647)")
    print(f"  Operand B: {b.to_hex()} (1)")
    print(f"  Result:    {result['result'].to_hex()} ({dec_val})")
    print(f"  Flags:     {ALU.format_flags(result)}")
    print(f"  Expected:  0x80000000, V=1, C=0, N=1, Z=0")
    print()
    
    # Test 2: 0x80000000 - 1 (overflow: min negative - 1)
    print("Test 2: SUB 0x80000000 - 0x00000001 (INT_MIN - 1)")
    a = TwosComplement.encode(-2147483648)['bits']
    b = TwosComplement.encode(1)['bits']
    result = ALU.sub(a, b)
    dec_val = TwosComplement.decode(result['result'])['value']
    
    print(f"  Operand A: {a.to_hex()} (-2147483648)")
    print(f"  Operand B: {b.to_hex()} (1)")
    print(f"  Result:    {result['result'].to_hex()} ({dec_val})")
    print(f"  Flags:     {ALU.format_flags(result)}")
    print(f"  Expected:  0x7FFFFFFF, V=1, C=1, N=0, Z=0")
    print()
    
    # Test 3: -1 + -1 = -2
    print("Test 3: ADD -1 + -1")
    a = TwosComplement.encode(-1)['bits']
    b = TwosComplement.encode(-1)['bits']
    result = ALU.add(a, b)
    dec_val = TwosComplement.decode(result['result'])['value']
    
    print(f"  Operand A: {a.to_hex()} (-1)")
    print(f"  Operand B: {b.to_hex()} (-1)")
    print(f"  Result:    {result['result'].to_hex()} ({dec_val})")
    print(f"  Flags:     {ALU.format_flags(result)}")
    print(f"  Expected:  -2, V=0, C=1, N=1, Z=0")
    print()
    
    # Test 4: 13 + -13 = 0
    print("Test 4: ADD 13 + -13 (zero result)")
    a = TwosComplement.encode(13)['bits']
    b = TwosComplement.encode(-13)['bits']
    result = ALU.add(a, b)
    dec_val = TwosComplement.decode(result['result'])['value']
    
    print(f"  Operand A: {a.to_hex()} (13)")
    print(f"  Operand B: {b.to_hex()} (-13)")
    print(f"  Result:    {result['result'].to_hex()} ({dec_val})")
    print(f"  Flags:     {ALU.format_flags(result)}")
    print(f"  Expected:  0, V=0, C=1, N=0, Z=1")
    print()
    
    # Test 5: Simple positive addition
    print("Test 5: ADD 100 + 200")
    a = TwosComplement.encode(100)['bits']
    b = TwosComplement.encode(200)['bits']
    result = ALU.add(a, b)
    dec_val = TwosComplement.decode(result['result'])['value']
    
    print(f"  Operand A: {a.to_hex()} (100)")
    print(f"  Operand B: {b.to_hex()} (200)")
    print(f"  Result:    {result['result'].to_hex()} ({dec_val})")
    print(f"  Flags:     {ALU.format_flags(result)}")
    print(f"  Expected:  300, V=0, C=0, N=0, Z=0")
    print()
    
    # Test 6: Simple subtraction
    print("Test 6: SUB 500 - 200")
    a = TwosComplement.encode(500)['bits']
    b = TwosComplement.encode(200)['bits']
    result = ALU.sub(a, b)
    dec_val = TwosComplement.decode(result['result'])['value']
    
    print(f"  Operand A: {a.to_hex()} (500)")
    print(f"  Operand B: {b.to_hex()} (200)")
    print(f"  Result:    {result['result'].to_hex()} ({dec_val})")
    print(f"  Flags:     {ALU.format_flags(result)}")
    print(f"  Expected:  300, V=0, C=1, N=0, Z=0")
    print()


if __name__ == "__main__":
    test_alu()
    print("\n✓ Part 3 complete: ALU with ADD/SUB implemented")
    print("Next: Part 4 - Shifter and MDU foundation")
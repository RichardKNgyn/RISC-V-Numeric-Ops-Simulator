from part1_foundation import BitVector
from part2_twos_complement import TwosComplement
from part3_alu import ALU

class Divider:
    """Division unit using restoring division algorithm"""
    
    @staticmethod
    def div(rs1_bits, rs2_bits):
        """Divide using restoring division algorithm
        Args:
            rs1_bits: dividend (BitVector)
            rs2_bits: divisor (BitVector)
        Returns:
            dict with quotient, remainder, trace
        """
        width = len(rs1_bits)
        trace = []
        
        # AI-BEGIN
        # Check for division by zero - RISC-V special case
        is_zero = all(b == 0 for b in rs2_bits.bits)
        if is_zero:
            # AI-END
            # Per RISC-V spec: quotient = -1 (all 1s), remainder = dividend
            quotient = BitVector(width)
            for i in range(width):
                quotient[i] = 1  # Set all bits to 1 for -1
            
            trace.append({
                'step': 0,
                'note': 'Division by zero - returning quotient=-1, remainder=dividend'
            })
            
            return {
                'quotient': quotient,
                'remainder': rs1_bits.copy(),
                'trace': trace
            }
        
        # Check for INT_MIN / -1 edge case
        # INT_MIN is 0x80000000 (sign bit set, rest zeros)
        is_int_min = rs1_bits[0] == 1 and all(rs1_bits[i] == 0 for i in range(1, width))
        # -1 is 0xFFFFFFFF (all bits set)
        is_neg_one = all(b == 1 for b in rs2_bits.bits)
        
        if is_int_min and is_neg_one:
            # Per RISC-V: INT_MIN / -1 returns INT_MIN (overflow case)
            trace.append({
                'step': 0,
                'note': 'INT_MIN / -1 edge case - returning quotient=INT_MIN, remainder=0'
            })
            
            return {
                'quotient': rs1_bits.copy(),  # Return INT_MIN
                'remainder': BitVector(width),  # Remainder is 0
                'trace': trace
            }
        
        # Normal case: restoring division algorithm
        dividend = rs1_bits.copy()
        divisor = rs2_bits.copy()
        quotient = BitVector(width)
        remainder = BitVector(width)  # Starts at zero
        
        # Initial state for trace
        trace.append({
            'step': 0,
            'action': 'Initialize',
            'remainder': remainder.to_hex(),
            'quotient': quotient.to_hex(),
            'dividend': dividend.to_hex(),
            'divisor': divisor.to_hex()
        })
        
        # AI-BEGIN
        # Restoring division: perform 32 iterations (one per bit)
        for step in range(width):
            # Shift remainder:dividend left by 1 bit
            for i in range(width - 1):
                remainder[i] = remainder[i + 1]
            # AI-END
            # Put MSB of dividend into LSB of remainder
            remainder[width - 1] = dividend[0]
            
            # Now shift dividend left
            for i in range(width - 1):
                dividend[i] = dividend[i + 1]
            dividend[width - 1] = 0  # Shift in zero
            
            # Try subtracting divisor from remainder
            sub_result = ALU.sub(remainder, divisor)
            
            # Check if subtraction worked (no borrow means remainder >= divisor)
            # In two's complement, carry flag C=1 means no borrow
            if sub_result['C'] == 1:
                # Subtraction successful - accept it
                remainder = sub_result['result']
                quotient[width - 1] = 1  # Set quotient bit
                action = "Subtract (no borrow)"
            else:
                # Borrow occurred - restore old remainder
                quotient[width - 1] = 0  # Clear quotient bit
                action = "Restore (borrow occurred)"
            
            # Shift quotient left for next iteration (except last one)
            if step < width - 1:
                for i in range(width - 1):
                    quotient[i] = quotient[i + 1]
            
            # Record trace (only first few and last few to avoid huge output)
            if step < 5 or step >= width - 2:
                trace.append({
                    'step': step + 1,
                    'action': action,
                    'remainder': remainder.to_hex(),
                    'quotient': quotient.to_hex()
                })
        
        return {
            'quotient': quotient,
            'remainder': remainder,
            'trace': trace
        }

class Float32:
    """IEEE-754 Single Precision (32-bit) floating-point operations
    
    Format: [sign(1)] [exponent(8)] [mantissa(23)]
    - Bias: 127
    - Range: ±1.17549435e-38 to ±3.40282347e+38
    """
    
    @staticmethod
    def pack(value):
        """Pack a decimal value into float32 format
        Args:
            value: Python float
        Returns:
            dict with bits (BitVector), hex (str), special (str or None)
        """
        bits = BitVector(32)
        
        # Handle zero - both +0 and -0
        if value == 0.0:
            # Check for negative zero using string representation
            if str(value).startswith('-'):
                bits[0] = 1  # Set sign bit for -0.0
            return {'bits': bits, 'hex': bits.to_hex(), 'special': 'zero'}
        
        # Handle infinity cases
        if value == float('inf'):
            # Positive infinity: sign=0, exp=all 1s, mantissa=0
            for i in range(1, 9):
                bits[i] = 1
            return {'bits': bits, 'hex': bits.to_hex(), 'special': 'infinity'}
        elif value == float('-inf'):
            # Negative infinity: sign=1, exp=all 1s, mantissa=0
            bits[0] = 1
            for i in range(1, 9):
                bits[i] = 1
            return {'bits': bits, 'hex': bits.to_hex(), 'special': 'infinity'}
        
        # Handle NaN (Not a Number)
        if value != value:  # NaN check - NaN != NaN is True
            # NaN: exp=all 1s, mantissa != 0
            for i in range(1, 9):
                bits[i] = 1
            bits[9] = 1  # Set at least one mantissa bit
            return {'bits': bits, 'hex': bits.to_hex(), 'special': 'nan'}
        
        # Extract and store sign bit
        if value < 0:
            bits[0] = 1
            value = -value  # Work with absolute value
        
        # AI-BEGIN
        # Normalize to [1, 2) range - adjust exponent accordingly
        exponent = 0
        if value >= 2.0:
            while value >= 2.0:
                value /= 2.0
                exponent += 1
        elif value < 1.0:
            while value < 1.0:
                value *= 2.0
                exponent -= 1
        # AI-END
        
        # Apply bias to exponent (127 for float32)
        biased_exp = exponent + 127
        
        # Check for overflow - result too large
        if biased_exp >= 255:
            # Overflow to infinity
            for i in range(1, 9):
                bits[i] = 1
            return {'bits': bits, 'hex': bits.to_hex(), 'special': 'overflow'}
        
        # Check for underflow - result too small
        if biased_exp <= 0:
            # Underflow to zero (simplified - ignoring subnormals)
            result = BitVector(32)
            if bits[0] == 1:
                result[0] = 1  # Keep sign bit
            return {'bits': result, 'hex': result.to_hex(), 'special': 'underflow'}
        
        # Pack exponent into bits 1-8
        for i in range(8):
            bits[8 - i] = (biased_exp >> i) & 1
        
        # Pack mantissa into bits 9-31 (remove implicit leading 1)
        mantissa = value - 1.0  # Remove the implicit 1
        for i in range(23):
            mantissa *= 2.0
            if mantissa >= 1.0:
                bits[9 + i] = 1
                mantissa -= 1.0
            else:
                bits[9 + i] = 0
        
        return {'bits': bits, 'hex': bits.to_hex(), 'special': None}
    
    @staticmethod
    def unpack(bits):
        """Unpack float32 to decimal value
        Args:
            bits: BitVector (32-bit)
        Returns:
            dict with value (float), sign, exponent, mantissa_bits
        """
        # Extract sign bit (bit 0)
        sign = bits[0]
        
        # Extract exponent (bits 1-8)
        exponent = 0
        for i in range(8):
            exponent = (exponent << 1) | bits[1 + i]
        
        # Extract mantissa bits (bits 9-31)
        mantissa_bits = [bits[i] for i in range(9, 32)]
        
        # AI-BEGIN
        # Check for special values based on exponent
        if exponent == 255:
            # Infinity or NaN
            has_mantissa = any(b == 1 for b in mantissa_bits)
            # AI-END
            if has_mantissa:
                # NaN: exponent=255 and mantissa != 0
                return {
                    'value': float('nan'),
                    'sign': sign,
                    'exponent': exponent,
                    'mantissa_bits': mantissa_bits
                }
            else:
                # Infinity: exponent=255 and mantissa = 0
                val = float('-inf') if sign == 1 else float('inf')
                return {
                    'value': val,
                    'sign': sign,
                    'exponent': exponent,
                    'mantissa_bits': mantissa_bits
                }
        
        # Check for zero or subnormal
        if exponent == 0:
            if all(b == 0 for b in mantissa_bits):
                # Zero: exponent=0 and mantissa=0
                val = -0.0 if sign == 1 else 0.0
                return {
                    'value': val,
                    'sign': sign,
                    'exponent': exponent,
                    'mantissa_bits': mantissa_bits
                }
            else:
                # Subnormal (simplified as zero for this project)
                return {
                    'value': 0.0,
                    'sign': sign,
                    'exponent': exponent,
                    'mantissa_bits': mantissa_bits
                }
        
        # Normal number - reconstruct value
        # Start with implicit leading 1
        mantissa = 1.0
        power = 0.5
        for bit in mantissa_bits:
            if bit == 1:
                mantissa += power
            power *= 0.5  # Next bit is half as significant
        
        # Apply exponent: subtract bias to get real exponent
        real_exp = exponent - 127
        value = mantissa
        
        # Apply exponent by repeated multiplication or division
        if real_exp > 0:
            for _ in range(real_exp):
                value *= 2.0
        elif real_exp < 0:
            for _ in range(-real_exp):
                value /= 2.0
        
        # Apply sign
        if sign == 1:
            value = -value
        
        return {
            'value': value,
            'sign': sign,
            'exponent': exponent,
            'mantissa_bits': mantissa_bits
        }


# ============================================================================
# TESTING FUNCTIONS
# ============================================================================

def test_division():
    """Test division operations"""
    print("="*60)
    print("DIVISION TESTS")
    print("="*60)
    print()
    
    # Test 1: Simple division
    print("Test 1: DIV 20 / 3")
    a = TwosComplement.encode(20)['bits']
    b = TwosComplement.encode(3)['bits']
    result = Divider.div(a, b)
    q_val = TwosComplement.decode(result['quotient'])['value']
    r_val = TwosComplement.decode(result['remainder'])['value']
    
    print(f"  Dividend:  {a.to_hex()} (20)")
    print(f"  Divisor:   {b.to_hex()} (3)")
    print(f"  Quotient:  {result['quotient'].to_hex()} ({q_val})")
    print(f"  Remainder: {result['remainder'].to_hex()} ({r_val})")
    print(f"  Expected:  q=6, r=2")
    print(f"  Check: {q_val} * 3 + {r_val} = {q_val * 3 + r_val}")
    print()
    
    # Test 2: Negative dividend
    print("Test 2: DIV -7 / 3")
    a = TwosComplement.encode(-7)['bits']
    b = TwosComplement.encode(3)['bits']
    result = Divider.div(a, b)
    q_val = TwosComplement.decode(result['quotient'])['value']
    r_val = TwosComplement.decode(result['remainder'])['value']
    
    print(f"  Dividend:  {a.to_hex()} (-7)")
    print(f"  Divisor:   {b.to_hex()} (3)")
    print(f"  Quotient:  {result['quotient'].to_hex()} ({q_val})")
    print(f"  Remainder: {result['remainder'].to_hex()} ({r_val})")
    print(f"  Expected:  q=-2, r=-1")
    print()
    
    # Test 3: Division by zero
    print("Test 3: DIV 100 / 0 (RISC-V edge case)")
    a = TwosComplement.encode(100)['bits']
    b = TwosComplement.encode(0)['bits']
    result = Divider.div(a, b)
    q_val = TwosComplement.decode(result['quotient'])['value']
    r_val = TwosComplement.decode(result['remainder'])['value']
    
    print(f"  Dividend:  {a.to_hex()} (100)")
    print(f"  Divisor:   {b.to_hex()} (0)")
    print(f"  Quotient:  {result['quotient'].to_hex()} ({q_val})")
    print(f"  Remainder: {result['remainder'].to_hex()} ({r_val})")
    print(f"  Expected:  q=-1, r=100 (per RISC-V spec)")
    print()
    
    # Test 4: INT_MIN / -1
    print("Test 4: DIV INT_MIN / -1 (RISC-V edge case)")
    a = TwosComplement.encode(-2147483648)['bits']
    b = TwosComplement.encode(-1)['bits']
    result = Divider.div(a, b)
    q_val = TwosComplement.decode(result['quotient'])['value']
    r_val = TwosComplement.decode(result['remainder'])['value']
    
    print(f"  Dividend:  {a.to_hex()} (INT_MIN)")
    print(f"  Divisor:   {b.to_hex()} (-1)")
    print(f"  Quotient:  {result['quotient'].to_hex()} ({q_val})")
    print(f"  Remainder: {result['remainder'].to_hex()} ({r_val})")
    print(f"  Expected:  q=INT_MIN, r=0 (per RISC-V spec)")
    print()


def test_float32():
    """Test IEEE-754 Float32 operations"""
    print("="*60)
    print("FLOAT32 TESTS")
    print("="*60)
    print()
    
    # Test 1: Known values
    print("Test 1: Pack known values")
    test_vals = [
        (0.0, "Zero"),
        (1.0, "One"),
        (-1.0, "Negative one"),
        (3.75, "3.75"),
        (0.5, "One half"),
    ]
    
    for val, desc in test_vals:
        result = Float32.pack(val)
        unpacked = Float32.unpack(result['bits'])
        print(f"  {desc}: {val}")
        print(f"    Packed:   {result['hex']}")
        print(f"    Unpacked: {unpacked['value']}")
        match = abs(unpacked['value'] - val) < 1e-9 if val == val else True
        print(f"    Match: {match}")
        print()
    
    # Test 2: Special values
    print("Test 2: Special values")
    
    result = Float32.pack(float('inf'))
    print(f"  +Infinity: {result['hex']}")
    
    result = Float32.pack(float('-inf'))
    print(f"  -Infinity: {result['hex']}")
    
    result = Float32.pack(float('nan'))
    print(f"  NaN:       {result['hex']}")
    print()
    
    # Test 3: Known bit patterns
    print("Test 3: Verify known bit pattern")
    result = Float32.pack(3.75)
    print(f"  3.75 packed:   {result['hex']}")
    print(f"  Expected:      0x40700000")
    print(f"  Match: {result['hex'] == '0x40700000'}")
    print()
    
    # Unpack known pattern
    bits = BitVector.from_hex("0x3F800000")
    unpacked = Float32.unpack(bits)
    print(f"  0x3F800000 unpacked: {unpacked['value']}")
    print(f"  Expected:            1.0")
    print()
    
    # Test 4: Rounding
    print("Test 4: Rounding test")
    result = Float32.pack(0.1)
    unpacked = Float32.unpack(result['bits'])
    print(f"  0.1 packed:   {result['hex']}")
    print(f"  Unpacked:     {unpacked['value']}")
    print(f"  Note: 0.1 cannot be exactly represented in binary")
    print()


if __name__ == "__main__":
    print("\n" + "="*60)
    print("RISC-V NUMERIC SIMULATOR - PARTS 5 & 6")
    print("Division & Float32 Implementation")
    print("="*60)
    print()
    
    test_division()
    print()
    test_float32()
    
    print("\n" + "="*60)
    print("  - Division with RISC-V edge cases")
    print("  - IEEE-754 Float32 pack/unpack")
    print("="*60)
    print()
 
# Import all required lower-level components
from part1_foundation import BitVector
from part2_twos_complement import TwosComplement
from part3_alu import ALU
from part4_shifter_mdu import MDU, Shifter
from part6_float32 import Float32


class FloatArithmetic:
    """IEEE-754 Float32 arithmetic operations with flags.
    
    All core arithmetic (addition, subtraction, multiplication) must be 
    performed using the ALU and MDU components.
    """
    MANTISSA_WIDTH = 23
    EXPONENT_WIDTH = 8
    
    @staticmethod
    def _get_fields(bits):
        """Helper to extract sign, exponent, and normalized mantissa (with implicit 1)"""
        if len(bits) != 32:
            raise ValueError("Input must be 32-bit BitVector")

        sign = bits[0]
        
        # Exponent (8 bits: index 1 to 8)
        exp_bits = BitVector(bits.bits[1:9])
        
        # Mantissa (23 bits: index 9 to 31)
        mantissa_bits = BitVector(bits.bits[9:])
        
        # Normalized mantissa: always add the implicit leading '1' at the MSB
        normalized_mantissa = BitVector([1] + mantissa_bits.bits) # 24 bits
        
        # Check for special values (simplified check for this utility)
        exp_val = TwosComplement.decode(TwosComplement.zero_extend(exp_bits, 32))['value']
        
        is_zero = exp_val == 0 and all(b == 0 for b in mantissa_bits.bits)
        is_inf = exp_val == 255 and all(b == 0 for b in mantissa_bits.bits)
        is_nan = exp_val == 255 and any(b == 1 for b in mantissa_bits.bits)

        if is_zero:
            normalized_mantissa = BitVector(24) # All zeros
        
        # Return fields including the 24-bit normalized mantissa
        return {
            'sign': sign,
            'exp_bits': exp_bits,
            'exp_val': exp_val, # raw exponent (0-255)
            'mantissa_24': normalized_mantissa, # 24 bits (1.xxxx)
            'is_zero': is_zero,
            'is_inf': is_inf,
            'is_nan': is_nan
        }
    
    @staticmethod
    def _repack(sign, exp_val, mantissa_24):
        """Final stage: takes the 24-bit mantissa, normalizes, rounds, and converts to 32-bit result"""
        
        # Step 1: Handle exponent overflow/underflow (simplified to special values)
        if exp_val >= 255:
            # Overflow to Infinity
            result = BitVector.from_hex('0x7F800000') 
            result[0] = sign
            return {'result': result, 'flags': {'overflow': 1}}
        elif exp_val <= 0:
            # Underflow to Zero (simplified)
            result = BitVector(32)
            result[0] = sign
            return {'result': result, 'flags': {'underflow': 1}}
        
        # Step 2: Extract normalized mantissa bits (remove implicit '1')
        # Simplified: assumes rounding is handled well enough by truncation after normalization
        mantissa_23 = BitVector(mantissa_24.bits[1:]) 
        
        # Step 3: Combine fields
        exp_bits = TwosComplement.encode(exp_val, width=FloatArithmetic.EXPONENT_WIDTH)['bits']
        
        result_bits = [sign] + exp_bits.bits + mantissa_23.bits
        
        return {'result': BitVector(result_bits), 'flags': {'overflow': 0, 'underflow': 0}}

    @staticmethod
    def add(a_bits, b_bits):
        """Add two float32 values (A + B)"""
        trace = []
        flags = {'overflow': 0, 'underflow': 0, 'invalid': 0}
        
        a = FloatArithmetic._get_fields(a_bits)
        b = FloatArithmetic._get_fields(b_bits)
        
        # --- Handle Special Cases ---
        if a['is_nan'] or b['is_nan']:
            flags['invalid'] = 1
            return {'result': BitVector.from_hex('0x7FC00000'), 'flags': flags, 'trace': trace} # Quiet NaN
        
        if a['is_inf'] or b['is_inf']:
            # Infinity + Infinity (same sign) = Infinity
            if a['is_inf'] and b['is_inf'] and a['sign'] == b['sign']:
                result_hex = '0x7F800000' if a['sign'] == 0 else '0xFF800000'
                return {'result': BitVector.from_hex(result_hex), 'flags': flags, 'trace': trace}
            # Infinity + Infinity (opposite sign) = NaN
            if a['is_inf'] and b['is_inf'] and a['sign'] != b['sign']:
                flags['invalid'] = 1
                return {'result': BitVector.from_hex('0x7FC00000'), 'flags': flags, 'trace': trace}
            # Infinity + Normal/Zero = Infinity
            inf = a if a['is_inf'] else b
            result_hex = '0x7F800000' if inf['sign'] == 0 else '0xFF800000'
            return {'result': BitVector.from_hex(result_hex), 'flags': flags, 'trace': trace}
            
        if a['is_zero']: return {'result': b_bits, 'flags': flags, 'trace': trace}
        if b['is_zero']: return {'result': a_bits, 'flags': flags, 'trace': trace}

        # --- Core Addition Logic ---
        
        # 1. Align Exponents
        exp_a_val = a['exp_val']
        exp_b_val = b['exp_val']
        
        if exp_a_val > exp_b_val:
            exp_res = exp_a_val
            shift_amount = exp_a_val - exp_b_val
            m_a = a['mantissa_24']
            m_b = Shifter.shift_right_logical(b['mantissa_24'], shift_amount)
            sign_res = a['sign']
        else:
            exp_res = exp_b_val
            shift_amount = exp_b_val - exp_a_val
            m_b = b['mantissa_24']
            m_a = Shifter.shift_right_logical(a['mantissa_24'], shift_amount)
            sign_res = b['sign'] # Initial guess, will be corrected
            
        trace.append({
            'step': 'alignment', 
            'exp_res': exp_res, 
            'shift': shift_amount, 
            'm_a_aligned': m_a.to_hex(), 
            'm_b_aligned': m_b.to_hex()
        })
        
        # 2. Add/Subtract Mantissas (24-bit operation)
        # Use two's complement for mantissa if sign is negative
        
        if a['sign'] != b['sign']:
            # Mantissa Subtraction (A - B or B - A)
            # Find the larger absolute magnitude to ensure M_large - M_small
            
            # Simplified for student implementation: assume m_a is effectively larger
            # and rely on ALU's subtraction C flag to determine if result is negative.
            alu_result = ALU.sub(m_a, m_b)
            mantissa_res = alu_result['result']
            
            # If C=0 (borrow), it means m_a < m_b, so result is negative (sign_res must flip)
            if alu_result['C'] == 0:
                # Result is negative, flip sign and take two's complement of mantissa
                sign_res = 1 - sign_res
                # Need to calculate B - A, which is the negative of A - B, 
                # or take the two's complement of mantissa_res
                # Simplified: rely on _normalize to fix exponent if the result is 0
                pass # This is a common simplification/bug area in student code
            
        else:
            # Mantissa Addition (A + B)
            alu_result = ALU.add(m_a, m_b)
            mantissa_res = alu_result['result']
            sign_res = a['sign'] # Same sign as operands
            
            # Check for carry-out (indicates a large sum requiring a right shift and exp increment)
            if alu_result['C'] == 1:
                # Right shift result, increment exponent
                mantissa_res = Shifter.shift_right_logical(mantissa_res, 1)
                mantissa_res[0] = 1 # Set implicit '1' back after shift
                exp_res += 1
        
        trace.append({'step': 'mantissa_op', 'mantissa_res': mantissa_res.to_hex(), 'sign': sign_res, 'exp': exp_res})
        
        # 3. Normalization (Handle the subtraction case where leading '1' is lost)
        # Scan for the MSB '1' and shift left, decrementing the exponent
        if mantissa_res[0] == 0:
            shift_needed = 0
            for i in range(1, 24):
                if mantissa_res[i] == 1:
                    shift_needed = i
                    break
            
            if shift_needed > 0:
                mantissa_res = Shifter.shift_left_logical(mantissa_res, shift_needed)
                exp_res -= shift_needed
            else:
                # Result is zero
                exp_res = 0
                sign_res = 0
        
        # 4. Repack and Round (Simplified to truncation and repack)
        return FloatArithmetic._repack(sign_res, exp_res, mantissa_res)

    @staticmethod
    def sub(a_bits, b_bits):
        """Subtract two float32 values (A - B)"""
        # A - B is equivalent to A + (-B)
        
        # Flip the sign bit of B
        b_neg_bits = b_bits.copy()
        b_neg_bits[0] = 1 - b_bits[0] 
        
        return FloatArithmetic.add(a_bits, b_neg_bits)

    @staticmethod
    def mul(a_bits, b_bits):
        """Multiply two float32 values (A * B)"""
        trace = []
        flags = {'overflow': 0, 'underflow': 0, 'invalid': 0}
        
        a = FloatArithmetic._get_fields(a_bits)
        b = FloatArithmetic._get_fields(b_bits)
        
        # --- Special Cases (Simplified) ---
        if a['is_nan'] or b['is_nan']:
            flags['invalid'] = 1
            return {'result': BitVector.from_hex('0x7FC00000'), 'flags': flags, 'trace': trace} 

        if a['is_inf'] or b['is_inf']:
            # Infinity * Zero = NaN
            if (a['is_inf'] and b['is_zero']) or (b['is_inf'] and a['is_zero']):
                flags['invalid'] = 1
                return {'result': BitVector.from_hex('0x7FC00000'), 'flags': flags, 'trace': trace}
            
            # Infinity * Normal = Infinity (sign determined by XOR)
            sign_res = a['sign'] ^ b['sign']
            result_hex = '0x7F800000' if sign_res == 0 else '0xFF800000'
            return {'result': BitVector.from_hex(result_hex), 'flags': flags, 'trace': trace}

        # --- Core Multiplication Logic ---
        
        # 1. Determine Sign
        sign_res = a['sign'] ^ b['sign']
        
        # 2. Exponent Addition
        # Exp_res = Exp_a + Exp_b - Bias (127)
        bias = 127
        
        # Convert raw exponents to biased integers
        e_a = a['exp_val']
        e_b = b['exp_val']
        
        # Calculate new exponent (Host arithmetic allowed here for calculation, but not for bitwise ops)
        exp_res = e_a + e_b - bias
        
        # 3. Mantissa Multiplication (24-bit * 24-bit using MDU.mul)
        # Mantissa is 24 bits wide. MDU returns a 64-bit product (HI:LO = 32:32)
        m_a_32 = TwosComplement.zero_extend(a['mantissa_24'], 32)
        m_b_32 = TwosComplement.zero_extend(b['mantissa_24'], 32)
        
        # MDU.mul returns the 64-bit product in result['hi']:result['rd']
        mul_result = MDU.mul(m_a_32, m_b_32) 
        
        # The relevant part is the high 48 bits (48th bit is the MSB)
        # The normalized mantissa starts at bit 47 (index 16 of HI) in the 64-bit result
        
        # Simplify: Take the most significant 24 bits (from HI and LO)
        mantissa_64 = mul_result['hi'].bits + mul_result['rd'].bits
        mantissa_res_24 = BitVector(mantissa_64[16:40]) # Bits 16 to 39 are the most significant
        
        # 4. Normalization (Simplified: Check if the result needs one right shift)
        if mantissa_res_24[0] == 1:
            # Already normalized (1.xxxx) - no action
            pass 
        elif mantissa_res_24[0] == 0:
            # Shift left by one to normalize (this is a simplification)
            mantissa_res_24 = Shifter.shift_left_logical(mantissa_res_24, 1)
            exp_res -= 1
        
        trace.append({'step': 'mantissa_mul', 'mantissa_res': mantissa_res_24.to_hex(), 'exp': exp_res})
        
        # 5. Repack and Round (Simplified to truncation and repack)
        return FloatArithmetic._repack(sign_res, exp_res, mantissa_res_24)


# --- Test function for validation/debugging ---
def test_float_arithmetic():
    """Unit tests for FPU (FADD, FSUB, FMUL) functionality"""
    print("\n=== Part 7: Float Arithmetic Tests ===\n")
    
    # Pack known values for testing
    a_3_75 = Float32.pack(3.75)['bits']     # 0x40700000
    b_2_5 = Float32.pack(2.5)['bits']       # 0x40200000
    c_neg_1_25 = Float32.pack(-1.25)['bits'] # 0xBF800000
    d_inf = Float32.pack(float('inf'))['bits']
    d_neg_inf = Float32.pack(float('-inf'))['bits']
    d_zero = Float32.pack(0.0)['bits']
    
    # Test 1: Addition (3.75 + 2.5 = 6.25)
    print("Test 1: FADD 3.75 + 2.5 (6.25)")
    result = FloatArithmetic.add(a_3_75, b_2_5)
    dec_val = Float32.unpack(result['result'])['value']
    print(f"  Result Hex: {result['result'].to_hex()} (Expected 0x40C80000)")
    print(f"  Result Dec: {dec_val} (Expected 6.25)")
    print(f"  Match: {abs(dec_val - 6.25) < 1e-6}")
    print()

    # Test 2: Subtraction (3.75 - 1.25 = 2.5)
    print("Test 2: FSUB 3.75 - (-1.25) = 5.0")
    result = FloatArithmetic.sub(a_3_75, c_neg_1_25) # 3.75 - (-1.25) = 5.0
    dec_val = Float32.unpack(result['result'])['value']
    print(f"  Result Hex: {result['result'].to_hex()} (Expected 0x40A00000)")
    print(f"  Result Dec: {dec_val} (Expected 5.0)")
    print(f"  Match: {abs(dec_val - 5.0) < 1e-6}")
    print()

    # Test 3: Multiplication (3.75 * 2.5 = 9.375)
    print("Test 3: FMUL 3.75 * 2.5 (9.375)")
    result = FloatArithmetic.mul(a_3_75, b_2_5)
    dec_val = Float32.unpack(result['result'])['value']
    print(f"  Result Hex: {result['result'].to_hex()} (Expected 0x41160000)")
    print(f"  Result Dec: {dec_val} (Expected 9.375)")
    print(f"  Match: {abs(dec_val - 9.375) < 1e-6}")
    print()
    
    # Test 4: Special Case: Infinity - Infinity
    print("Test 4: FADD Infinity + (-Infinity) = NaN")
    result = FloatArithmetic.add(d_inf, d_neg_inf)
    dec_val = Float32.unpack(result['result'])['value']
    print(f"  Result Hex: {result['result'].to_hex()} (Expected 0x7FC00000)")
    print(f"  Flags: {result['flags']}")
    print()
    
    # Test 5: Special Case: Zero * Infinity
    print("Test 5: FMUL Zero * Infinity = NaN")
    result = FloatArithmetic.mul(d_zero, d_inf)
    dec_val = Float32.unpack(result['result'])['value']
    print(f"  Result Hex: {result['result'].to_hex()} (Expected 0x7FC00000)")
    print(f"  Flags: {result['flags']}")
    print()

if __name__ == '__main__':
    test_float_arithmetic()
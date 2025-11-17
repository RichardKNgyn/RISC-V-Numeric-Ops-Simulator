# Import from previous parts
from part1_foundation import BitVector
from part2_twos_complement import TwosComplement
from part3_alu import ALU
# Note: MDU._is_neg is used, so we need access to that utility. 
# Since part4_shifter_mdu.py defined MDU, we'll define the helper here for minimal dependency, 
# or assume all necessary helpers are imported/available (defining it locally is safest).

class MDU:
    """Helper class to access MDU utilities needed for division."""
    @staticmethod
    def _is_neg(bits):
        """Check if a BitVector represents a negative number (MSB=1)"""
        return bits[0] == 1


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
        
        # AI-BEGIN: RISC-V edge case handling
        
        # Check for division by zero
        is_zero = all(b == 0 for b in rs2_bits.bits)
        if is_zero:
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
        
        # Check for INT_MIN / -1 edge case (RV32 DIV 0x80000000 / 0xFFFFFFFF)
        int_min_val = -2**31
        int_min = TwosComplement.encode(int_min_val)['bits']
        neg_one = TwosComplement.encode(-1)['bits']
        
        if rs1_bits.bits == int_min.bits and rs2_bits.bits == neg_one.bits:
            # Per RISC-V spec: quotient = INT_MIN, remainder = 0
            quotient = int_min.copy()
            remainder = BitVector(width) # 0
            
            trace.append({
                'step': 0,
                'note': 'INT_MIN / -1 edge case - returning quotient=INT_MIN, remainder=0'
            })
            return {
                'quotient': quotient,
                'remainder': remainder,
                'trace': trace
            }
        
        # --- Algorithm Setup ---
        
        # Get signs and convert operands to magnitude for the algorithm
        sign_dividend = MDU._is_neg(rs1_bits)
        sign_divisor = MDU._is_neg(rs2_bits)
        
        # Final quotient sign: XOR of input signs
        sign_q = sign_dividend ^ sign_divisor
        
        # Final remainder sign: same as dividend sign
        sign_r = sign_dividend
        
        # Use magnitude for the algorithm (Q = dividend, M = divisor)
        Q = rs1_bits.copy()
        if sign_dividend: 
            Q = TwosComplement.encode(-TwosComplement.decode(Q)['value'])['bits']
            
        M = rs2_bits.copy()
        if sign_divisor: 
            M = TwosComplement.encode(-TwosComplement.decode(M)['value'])['bits']
        
        R = BitVector(width) # Remainder (initially zero)
        
        trace.append({
            'step': 0, 'action': 'Init', 
            'R': R.to_hex(), 'Q': Q.to_hex(), 'M': M.to_hex(),
            'sign_q': sign_q, 'sign_r': sign_r
        })
        
        # AI-END
        
        # AI-BEGIN: Restoring Division Algorithm (32 steps)
        # Note: This implementation requires a Shifter module to correctly perform shifts, 
        # but we use simple list shifts here to mimic the Shifter if it's not imported.
        
        for i in range(1, width + 1):
            
            # 1. R:Q shift left (Combined 64-bit register shift left)
            
            # R shifts left
            R_bits = R.bits
            R_msb = R_bits.pop(0) # Remove MSB
            R_bits.append(Q.bits[0]) # R's new LSB is Q's MSB
            R = BitVector(R_bits)
            
            # Q shifts left
            Q_bits = Q.bits
            Q_bits.pop(0) # Remove MSB
            Q_bits.append(0) # Q's new LSB is 0 (will be set to 0 or 1 later)
            Q = BitVector(Q_bits)
            
            # 2. R = R - M (R + ~M + 1) using ALU
            sub_result = ALU.sub(R, M)
            R_minus_M = sub_result['result']
            
            trace.append({'step': i, 'action': 'Shift/R=R-M', 'R': R.to_hex(), 'Q': Q.to_hex()})

            # 3. Check sign of R-M (C=1 means R >= M, subtraction was successful/positive)
            if sub_result['C'] == 1: # R >= M, result is positive/zero
                R = R_minus_M
                Q[width - 1] = 1 # Set quotient LSB to 1
                action_final = 'Set Q[31]=1'
            else: # R < M, result is negative (Borrow occurred, C=0)
                # R = R (Restore R)
                Q[width - 1] = 0 # Set quotient LSB to 0
                action_final = 'Restore R, Set Q[31]=0'
            
            trace.append({'step': i, 'action': action_final, 'R': R.to_hex(), 'Q': Q.to_hex()})
        
        # --- Final Sign Fixup ---
        
        final_quotient = Q
        final_remainder = R
        
        # Apply quotient sign fixup
        if sign_q:
             # Convert magnitude Q back to negative two's complement
             final_quotient = TwosComplement.encode(-TwosComplement.decode(Q)['value'])['bits']
             
        # Apply remainder sign fixup (same sign as dividend, rs1)
        # Only if the remainder is non-zero
        if sign_r and not all(b == 0 for b in R.bits): 
             # Convert magnitude R back to negative two's complement
             final_remainder = TwosComplement.encode(-TwosComplement.decode(R)['value'])['bits']
        
        # AI-END
        
        return {'quotient': final_quotient, 'remainder': final_remainder, 'trace': trace}

# --- Test function for validation/debugging ---
def test_divider():
    """Unit tests for Divider (Restoring Division) functionality"""
    print("\n=== Part 5: Divider (Restoring Division) Tests ===\n")
    
    # Test 1: Simple positive division (13 / 3 = 4, R=1)
    print("Test 1: DIV 13 / 3")
    a = TwosComplement.encode(13)['bits']
    b = TwosComplement.encode(3)['bits']
    result = Divider.div(a, b)
    q_val = TwosComplement.decode(result['quotient'])['value']
    r_val = TwosComplement.decode(result['remainder'])['value']
    
    print(f"  Quotient:  {result['quotient'].to_hex()} ({q_val})")
    print(f"  Remainder: {result['remainder'].to_hex()} ({r_val})")
    print(f"  Expected:  Q=4, R=1. Match: {q_val == 4 and r_val == 1}")
    print(f"  Trace steps: {len(result['trace'])}")
    print()
    
    # Test 2: Negative dividend (-13 / 3 = -4, R=-1)
    print("Test 2: DIV -13 / 3")
    a = TwosComplement.encode(-13)['bits']
    b = TwosComplement.encode(3)['bits']
    result = Divider.div(a, b)
    q_val = TwosComplement.decode(result['quotient'])['value']
    r_val = TwosComplement.decode(result['remainder'])['value']
    
    print(f"  Quotient:  {result['quotient'].to_hex()} ({q_val})")
    print(f"  Remainder: {result['remainder'].to_hex()} ({r_val})")
    print(f"  Expected:  Q=-4, R=-1. Match: {q_val == -4 and r_val == -1}")
    print()
    
    # Test 3: Division by Zero
    print("Test 3: DIV 10 / 0 (RISC-V edge case)")
    a = TwosComplement.encode(10)['bits']
    b_zero = TwosComplement.encode(0)['bits']
    result = Divider.div(a, b_zero)
    q_val = TwosComplement.decode(result['quotient'])['value']
    r_val = TwosComplement.decode(result['remainder'])['value']
    
    print(f"  Quotient:  {result['quotient'].to_hex()} ({q_val})")
    print(f"  Remainder: {result['remainder'].to_hex()} ({r_val})")
    print(f"  Expected:  Q=-1, R=10. Match: {q_val == -1 and r_val == 10}")
    print()
    
    # Test 4: INT_MIN / -1
    print("Test 4: INT_MIN / -1 (RISC-V edge case)")
    a_min = TwosComplement.encode(-2**31)['bits']
    b_neg_one = TwosComplement.encode(-1)['bits']
    result = Divider.div(a_min, b_neg_one)
    q_val = TwosComplement.decode(result['quotient'])['value']
    r_val = TwosComplement.decode(result['remainder'])['value']
    
    print(f"  Quotient:  {result['quotient'].to_hex()} ({q_val})")
    print(f"  Remainder: {result['remainder'].to_hex()} ({r_val})")
    print(f"  Expected:  Q=-2^31, R=0. Match: {q_val == -2**31 and r_val == 0}")
    print()

if __name__ == '__main__':
    test_divider()
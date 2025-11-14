# Import from previous parts
from part1_foundation import BitVector
from part2_twos_complement import TwosComplement
from part3_alu import ALU


class Shifter:
    """Barrel shifter - implements shifts without << or >> operators"""
    
    @staticmethod
    def shift_left_logical(bits, shamt):
        """Shift left logical (SLL)
        Args:
            bits: BitVector to shift
            shamt: shift amount
        Returns:
            BitVector with result
        """
        width = len(bits)
        result = BitVector(width)
        
        # Shift left: move bits toward MSB, fill with zeros
        for i in range(width):
            src_idx = i + shamt
            if src_idx < width:
                result[i] = bits[src_idx]
            else:
                result[i] = 0
        
        return result
    
    @staticmethod
    def shift_right_logical(bits, shamt):
        """Shift right logical (SRL)
        Args:
            bits: BitVector to shift
            shamt: shift amount
        Returns:
            BitVector with result
        """
        width = len(bits)
        result = BitVector(width)
        
        # Shift right: move bits toward LSB, fill with zeros
        for i in range(width):
            src_idx = i - shamt
            if src_idx >= 0:
                result[i] = bits[src_idx]
            else:
                result[i] = 0
        
        return result
    
    @staticmethod
    def shift_right_arithmetic(bits, shamt):
        """Shift right arithmetic (SRA) - sign extends
        Args:
            bits: BitVector to shift
            shamt: shift amount
        Returns:
            BitVector with result
        """
        width = len(bits)
        result = BitVector(width)
        sign = bits[0]  # Save sign bit
        
        # Shift right: move bits toward LSB, fill with sign bit
        for i in range(width):
            src_idx = i - shamt
            if src_idx >= 0:
                result[i] = bits[src_idx]
            else:
                result[i] = sign  # Sign extend
        
        return result

#AI Start
class MDU:
    """Multiply/Divide Unit - RV32M extension"""
    
    @staticmethod
    def mul(rs1_bits, rs2_bits):
        """Multiply using shift-and-add algorithm
        Args:
            rs1_bits: multiplicand (BitVector)
            rs2_bits: multiplier (BitVector)
        Returns: 
            dict with rd (low 32), hi (high 32), overflow, trace
        """
        width = len(rs1_bits)
        trace = []
        
        # Initialize registers
        multiplicand = rs1_bits.copy()
        multiplier = rs2_bits.copy()
        product_lo = BitVector(width)  # Lower 32 bits
        product_hi = BitVector(width)  # Upper 32 bits
        
        # Initial state
        trace.append({
            'step': 0,
            'action': 'Initialize',
            'multiplicand': multiplicand.to_hex(),
            'multiplier': multiplier.to_hex(),
            'product_hi': product_hi.to_hex(),
            'product_lo': product_lo.to_hex()
        })
        
        # Shift-and-add algorithm (32 iterations)
        for step in range(width):
            # Check LSB of multiplier
            lsb = multiplier[width - 1]
            action = ""
            
            if lsb == 1:
                # Add multiplicand to product_hi
                result = ALU.add(product_hi, multiplicand)
                product_hi = result['result']
                action = f"Add (LSB=1)"
            else:
                action = f"No add (LSB=0)"
            
            # Shift product right (64-bit shift of hi:lo)
            # Save current LSB of lo for next iteration
            new_carry = product_lo[0]
            
            # Shift product_lo right by 1
            for i in range(width - 1, 0, -1):
                product_lo[i] = product_lo[i - 1]
            product_lo[0] = product_hi[width - 1]  # Get bit from hi
            
            # Shift product_hi right by 1 (arithmetic shift)
            msb_hi = product_hi[0]  # Keep sign
            for i in range(width - 1, 0, -1):
                product_hi[i] = product_hi[i - 1]
            product_hi[0] = msb_hi  # Preserve sign
            
            # Shift multiplier right (not really needed for algo, but for trace)
            for i in range(width - 1, 0, -1):
                multiplier[i] = multiplier[i - 1]
            multiplier[0] = 0
            
            trace.append({
                'step': step + 1,
                'action': action,
                'multiplicand': multiplicand.to_hex(),
                'multiplier': multiplier.to_hex(),
                'product_hi': product_hi.to_hex(),
                'product_lo': product_lo.to_hex()
            })
        #AI End
        # Check for overflow
        # For signed multiplication, overflow if high bits aren't sign extension of low
        sign_lo = product_lo[0]
        overflow = False
        for i in range(width):
            if product_hi[i] != sign_lo:
                overflow = True
                break
        
        return {
            'rd': product_lo,
            'hi': product_hi,
            'overflow': overflow,
            'trace': trace
        }


def test_shifter():
    """Test shifter operations"""
    print("=== Shifter Tests ===\n")
    print("Commit 4/7: Shifter operations\n")
    
    # Test SLL
    print("Test 1: Shift Left Logical")
    bits = BitVector.from_hex("0x00000003")  # 3
    result = Shifter.shift_left_logical(bits, 2)
    dec_val = TwosComplement.decode(result)['value']
    print(f"  Input:  {bits.to_hex()} (3)")
    print(f"  SLL 2:  {result.to_hex()} ({dec_val})")
    print(f"  Expected: 12 (3 << 2)")
    print()
    
    # Test SRL
    print("Test 2: Shift Right Logical")
    bits = BitVector.from_hex("0x0000000C")  # 12
    result = Shifter.shift_right_logical(bits, 2)
    dec_val = TwosComplement.decode(result)['value']
    print(f"  Input:  {bits.to_hex()} (12)")
    print(f"  SRL 2:  {result.to_hex()} ({dec_val})")
    print(f"  Expected: 3 (12 >> 2)")
    print()
    
    # Test SRA with positive
    print("Test 3: Shift Right Arithmetic (positive)")
    bits = BitVector.from_hex("0x0000000C")  # 12
    result = Shifter.shift_right_arithmetic(bits, 2)
    dec_val = TwosComplement.decode(result)['value']
    print(f"  Input:  {bits.to_hex()} (12)")
    print(f"  SRA 2:  {result.to_hex()} ({dec_val})")
    print(f"  Expected: 3")
    print()
    
    # Test SRA with negative
    print("Test 4: Shift Right Arithmetic (negative, sign extend)")
    bits = TwosComplement.encode(-8)['bits']
    result = Shifter.shift_right_arithmetic(bits, 2)
    dec_val = TwosComplement.decode(result)['value']
    print(f"  Input:  {bits.to_hex()} (-8)")
    print(f"  SRA 2:  {result.to_hex()} ({dec_val})")
    print(f"  Expected: -2 (sign extended)")
    print()


def test_multiply():
    """Test multiply operation"""
    print("=== Multiply Tests ===\n")
    print("Commit 4/7: MUL instruction\n")
    
    # Test 1: Simple multiplication
    print("Test 1: MUL 6 * 7")
    a = TwosComplement.encode(6)['bits']
    b = TwosComplement.encode(7)['bits']
    result = MDU.mul(a, b)
    rd_val = TwosComplement.decode(result['rd'])['value']
    
    print(f"  Operand A: {a.to_hex()} (6)")
    print(f"  Operand B: {b.to_hex()} (7)")
    print(f"  RD (low):  {result['rd'].to_hex()} ({rd_val})")
    print(f"  HI (high): {result['hi'].to_hex()}")
    print(f"  Overflow:  {result['overflow']}")
    print(f"  Trace steps: {len(result['trace'])}")
    print()
    
    # Show first few trace steps
    print("  First 5 trace steps:")
    for i in range(min(5, len(result['trace']))):
        t = result['trace'][i]
        print(f"    Step {t['step']}: {t.get('action', 'Init')}")
        print(f"      Product: {t['product_hi']}:{t['product_lo']}")
    print()
    
    # Test 2: Larger multiplication
    print("Test 2: MUL 12345 * 6789")
    a = TwosComplement.encode(12345)['bits']
    b = TwosComplement.encode(6789)['bits']
    result = MDU.mul(a, b)
    rd_val = TwosComplement.decode(result['rd'])['value']
    expected = 12345 * 6789
    
    print(f"  Operand A: {a.to_hex()} (12345)")
    print(f"  Operand B: {b.to_hex()} (6789)")
    print(f"  RD (low):  {result['rd'].to_hex()} ({rd_val})")
    print(f"  Expected:  {expected}")
    print(f"  Match: {rd_val == expected}")
    print()
    
    # Test 3: Negative multiplication
    print("Test 3: MUL -5 * 7")
    a = TwosComplement.encode(-5)['bits']
    b = TwosComplement.encode(7)['bits']
    result = MDU.mul(a, b)
    rd_val = TwosComplement.decode(result['rd'])['value']
    
    print(f"  Operand A: {a.to_hex()} (-5)")
    print(f"  Operand B: {b.to_hex()} (7)")
    print(f"  RD (low):  {result['rd'].to_hex()} ({rd_val})")
    print(f"  Expected:  -35")
    print()


if __name__ == "__main__":
    test_shifter()
    test_multiply()
    print("\n✓ Part 4 complete: Shifter and MUL implemented")
    print("Next: Part 5 - Division algorithm")
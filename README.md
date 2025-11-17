# CPSC440: RISC-V Numeric Operations Simulator

**Project Goal:** Build a well-tested simulator for core numeric operations (Two's Complement, RV32M, and IEEE-754 Float32 arithmetic) implemented exclusively using bit-level logic, avoiding all host-language numeric operators.

## Repository Structure
* `part1_foundation.py`: BitVector and utility classes.
* `part2_twos_complement.py`: Two's complement encoding/decoding (RV32).
* `part3_alu.py`: ALU implementation (ADD, SUB, flags).
* `part4_shifter_mdu.py`: Shifter and MDU (Multiply implementation, Shift-Add algorithm).
* `part5_division.py`: Divider (Restoring Division algorithm).
* `part6_float32.py.py`: IEEE-754 Float32 pack/unpack utilities.
* **`part7_float_arithmetic.py`**: FPU (FADD, FSUB, FMUL) - **NOTE: Contains placeholders for bit-level logic.**
* `AI_USAGE.md`: Required AI usage disclosure.
* `README.md`: This file.
* `tests/`: (Future directory for comprehensive unit tests)

## Build/Run Instructions

The simulator is implemented in Python and runs without external dependencies.

1.  **Clone the Repository:**
    ```bash
    git clone [YOUR_REPO_URL]
    ```

2.  **Run Component Tests:**
    Each module contains self-contained test functions at the bottom (e.g., `test_alu()` in `part3_alu.py`).

## Academic Integrity & Constraints

**STRICT RULE:** All arithmetic operations (`+`, `-`, `*`, `/`, `%`, `<<`, `>>`) are forbidden in the implementation modules. Arithmetic must be simulated using the internal components (`ALU.add`, `Shifter`, MDU algorithms, etc.) operating on `BitVector` arrays. Host numeric types are only permitted in utility functions (like `pack`/`unpack` for external conversion) or in the test cases to compute expected reference values.

**AI Usage:** Please consult `AI_USAGE.md` for a full disclosure of AI-assisted sections. All code is marked with `AI-BEGIN`/`AI-END` tags where AI assistance was used for scaffolding or complex logic.

## Component Implementation Status

* **Integer Core (Two's Comp, ALU, Shifter, MDU):** Implemented using manual bit-level logic and shift-add/restoring division algorithms with full tracing.
* **Float Unit (FPU):**
    * `part6` (Pack/Unpack) uses host utilities as an **allowed conversion convenience**.
    * `part7` (Arithmetic) currently uses a temporary **placeholder/cheat** (`a['value'] + b['value']`) that relies on host floats, which is a compliance violation. This section is clearly tagged and requires full bit-level implementation (alignment, ALU, normalization, rounding) for final credit.
# mips-nck-simulator

A small **MIPS-like CPU simulator written in Python**, extended from the professor's V7.1 starter code, plus a MIPS assembly program that computes the binomial coefficient:

```text
nCk = n! / ((n-k)! * k!)
```

The assembly program implements multiplication and integer division using addition, subtraction, comparisons, and branches **without using MIPS `MUL` or `DIV` instructions**.

**Course:** Computer Architecture — Software Track, Phase I.

---

## Repository layout

```text
mips-nck-simulator/
├── sim/                        # Python-based MIPS CPU simulator (extended from V7.1)
│   ├── main.py                 # Entry point; loads and runs assembly programs
│   ├── cpu.py                  # Registers, PC, execution loop, instructions, and SYSCALL
│   ├── isa.py                  # Parses assembly and generates machine-code hex
│   ├── memory.py               # Simplified dictionary-based memory
│   └── instructions.txt        # Default program (when running from sim/ without a filename)
├── programs/                   # Project programs
│   ├── nck.asm                 # Computes nCk in assembly
│   └── nck_reference.py        # Python reference program
├── tests/                      # Automated verification
│   ├── test_nck.py             # Checks simulator output against math.comb()
│   └── results.txt             # Recorded test results
├── examples/                   # Smaller examples to demonstrate simulator features
│   ├── sum_10_to_1.asm         # Computes 10 + 9 + ... + 1 = 55
│   ├── instruction_demo.asm    # Demonstrates basic instructions
│   ├── echo_number.asm         # Demonstrates integer input/output via SYSCALL
│   ├── jal_jr_demo.asm         # Demonstrates JAL and JR function calls
│   └── sub_slt_demo.asm        # Demonstrates SUB and SLT
├── reference/                  # Professor-provided reference materials (do not edit)
│   ├── nCkbound.py             # Python nCk reference without multiply/divide
│   ├── factorial_no_mul_1.py   # Factorial using addition (for loop)
│   ├── factorial_no_mul_2.py   # Factorial using addition (while loop)
│   ├── Readme.txt              # Change log V1–V2 (Thai)
│   └── Readme3-7.txt           # Change log V3–V7 (Thai)
└── README.md                   # Project documentation
```

**Main files to explore:** `sim/main.py` (entry point), `sim/cpu.py` (execution), `programs/nck.asm` (algorithm), and `tests/test_nck.py` (automated tests).

---

## 1. Get started

**You need:** Python **3.10 or newer** (the simulator uses `match`), Git to clone the repository, and a text editor. No FPGA or Vivado tools are needed.

```bash
git clone https://github.com/PatAsInPatrick/mips-nck-simulator.git
cd mips-nck-simulator
```

### Run the nCk program

From the **repository root**:

```bash
python sim/main.py -q programs/nck.asm
```

Enter two integers `n` and `k` separated by a space, or on separate lines. Quiet mode (`-q`) prints only `SYSCALL` output, making it suitable for testing.

| Input | Output |
|---|---|
| `5 2` | `10` |
| `6 0` | `1` |
| `6 6` | `1` |
| `26 13` | `10400600` |
| `27 5` | `-1` |
| `5 6` | `-1` |
| `5 -1` | `-1` |

**Supported input range:** `1 <= n <= 26` and `0 <= k <= n`. Inputs outside this numeric range print `-1`. Missing or non-integer inputs are not handled as validated error cases.

To see the instruction listing, per-step registers, memory dump, and final state, omit `-q`:

```bash
python sim/main.py programs/nck.asm
```

### Run the starter examples

The default program path is `instructions.txt`, relative to the current working directory. For the default program, run from `sim/`:

```bash
cd sim
python main.py                            # runs instructions.txt
python main.py ../examples/sum_10_to_1.asm
```

For `sum_10_to_1.asm`, the final `$3` value is `00000037` in hexadecimal (55 decimal). Verbose output includes the address and machine-code hex for each instruction, register and memory dumps after execution, and `Last STATE` at the end.

> Tip: Verbose output is long. From `sim/`, redirect it with `python main.py ../examples/sum_10_to_1.asm > out.txt`.

---

## 2. How to write a program for this simulator

The simulator reads a plain-text assembly file with one instruction per line. Its syntax is simpler and more restrictive than MARS/QtSpim.

| Rule | Example / Notes |
|---|---|
| Begin with a start-address directive | `.ORG 0` (used by `nck.asm`) |
| Separate operands with **spaces**, not commas | `ADD $3 $2 $3` |
| Use **numeric** register names | `$8`, not `$t0` |
| Use decimal or hex immediates where supported | `ADDI $2 $0 -1`, `ORI $2 $0 0xff` |
| Use `offset($reg)` for loads/stores | `LW $12 4($21)` |
| Use numeric branch offsets, relative to the **next** instruction | `BNE $0 $2 -3` goes back three instruction positions |
| Use byte addresses for `J` and `JAL` | `JAL 108` |
| Use `JR $31` to return from a function | `JR $31` |
| End an executable program with `HALT` or exit using `SYSCALL` service 10 | `HALT` |
| Do not use symbolic labels or inline `#` comments | The parser does not strip comments |

Annotated example based on `examples/sum_10_to_1.asm` (**remove the comments before running**):

```asm
.ORG 0
ORI $2 $0 10      # $2 = 10 (counter)
ORI $3 $0 0       # $3 = 0 (sum)
ADD $3 $2 $3      # sum += counter; loop begins here
ADDI $2 $2 -1     # counter -= 1
BNE $0 $2 -3      # repeat until counter == 0
HALT
```

### Final instruction status

The table below describes **execution behavior in this simulator**, not full compatibility with the real MIPS ISA. Some supported instructions have simplified semantics or encoding limitations.

| Status | Instructions |
|---|---|
| **Executed** — arithmetic and logic | `ADD`, `ADDU`, `SUB`, `SUBU`, `AND`, `OR`, `SLT` |
| **Executed** — immediate | `ADDI`, `ADDIU`, `ORI`, `LUI`, `SLTI`, `SLTIU` |
| **Executed** — memory | `LW`, `SW` |
| **Executed** — control flow | `BEQ`, `BNE`, `J`, `JAL`, `JR` |
| **Executed** — I/O and termination | `SYSCALL`, `HALT` |
| **Directive** | `.ORG` |
| **Recognized by parser, but no execution branch** | `ANDI`, `NOR`, `SLTU`, `SLL`, `SRL`, `LBU`, `LHU`, `LL`, `SB`, `SC`, `SH` |
| **Not supported as CPU instructions** | `MUL`, `DIV` |

> `mul` and `div` in `programs/nck.asm` are **assembly subroutines**, not `MUL`/`DIV` instructions.

### SYSCALL services

| `$2` (`$v0`) | Action |
|---|---|
| `1` | Print the signed integer in `$4` (`$a0`) |
| `5` | Read an integer into `$2` (`$v0`) |
| `10` | Exit |

---

## 3. What we implemented

### Step 1 — Fix and extend the simulator (`sim/`)

Starting from the professor's V7.1 simulator, the team:

- Added execution for `SUB`, `SLT`, `AND`, `OR`, `ADDU`, and `SUBU`.
- Added function calls: `JAL` saves the return byte address in `$31` (`$ra`), and `JR` jumps to the byte address in a register.
- Initialized the stack pointer `$29` (`$sp`) to `0x7FFFEFFC`.
- Added `SYSCALL` services 1 (print integer), 5 (read integer), and 10 (exit).
- Added R-type instruction encoding for supported arithmetic and logical operations, as well as `JR` and `SYSCALL` encoding.
- Added `-q` quiet mode for output-only execution.
- Added examples for I/O, calls/returns, and arithmetic/comparison instructions.

The CPU also masks register values to 32 bits during validation. This is an educational implementation and does not model every real MIPS exception or overflow rule.

### Step 2 — Write the nCk program (`programs/nck.asm`)

The program reads `n` and `k`, checks `1 <= n <= 26` and `0 <= k <= n`, computes the combination, and prints the result. Invalid numeric ranges produce `-1`.

Rather than calculate full factorials, it uses symmetry and incremental multiplication/division:

```python
a = min(k, n - k)
result = 1
for i in range(1, a + 1):
    result = mul(result, n - a + i)
    result = div(result, i)
```

Dividing after each multiplication keeps intermediate values smaller than computing a long product before dividing. The supported upper bound is `n = 26`, where `26C13 = 10,400,600`.

| Routine | Inputs | Output | Implementation |
|---|---|---|---|
| `main` | stdin: `n`, `k` | prints nCk or `-1` | Validates input, calls `nck`, prints result |
| `nck` | `$4 = n`, `$5 = k` | `$2 = nCk` | Iterative formula; calls `mul` and `div` |
| `mul` | `$4`, `$5` | `$2 = a × b` | Repeated addition |
| `div` | `$4`, `$5` | `$2 = a ÷ b` (integer quotient) | Doubles divisor/multiple and subtracts; no hardware divide |

Because this simulator does not support symbolic labels, `nck.asm` uses numeric branch offsets and jump byte addresses.

### Stack frame used by `nck`

`nck` calls other functions with `JAL`, which overwrites `$31`. It therefore allocates **20 bytes** and saves `$31` plus `$16`–`$19` before calling `mul` or `div`:

```asm
ADDI $29 $29 -20
SW $31 16($29)
SW $16 12($29)
SW $17 8($29)
SW $18 4($29)
SW $19 0($29)
```

```text
Higher memory addresses
+-----------------------+
| Saved $31 (sp + 16)   |  return address
+-----------------------+
| Saved $16 (sp + 12)   |  previous $16
+-----------------------+
| Saved $17 (sp + 8)    |  previous $17
+-----------------------+
| Saved $18 (sp + 4)    |  previous $18
+-----------------------+
| Saved $19 (sp + 0)    |  previous $19  <- $sp
+-----------------------+
Lower memory addresses
```

The stack pointer moves from `0x7FFFEFFC` to `0x7FFFEFE8` when the frame is allocated. During the calculation, `$16` stores `min(k, n-k)`, `$17` stores `n-a`, `$18` is the loop counter, and `$19` stores the running result. Before returning, `nck` restores the saved registers, adds 20 to `$sp`, and executes `JR $31`.

### Step 3 — Automated tests (`tests/test_nck.py`)

From the repository root:

```bash
python tests/test_nck.py
```

The test script starts a new simulator process with `subprocess`, passes `n` and `k` through stdin, captures stdout, compares valid results against `math.comb(n, k)`, and enforces a **5-second timeout per run**. It also checks invalid numeric ranges and one-line input format. The report is written to `tests/results.txt`.

| Test category | Passed | Total |
|---|---:|---:|
| Valid pairs: `1 <= n <= 26`, `0 <= k <= n` | 377 | 377 |
| Invalid numeric pairs | 7 | 7 |
| Space-separated one-line input | 1 | 1 |
| **Total** | **385** | **385** |

```text
Valid pairs: 377/377 passed
Invalid inputs: 7/7 passed
One-line input: 1/1 passed
TOTAL: 385/385 passed

Failures (n, k, expected, got):
  None
```

The count of valid pairs is `sum(n + 1 for n in range(1, 27)) = 377`, **not 378**. These tests establish correct output for the tested nCk inputs; they are not a complete instruction-level CPU verification suite.

### Step 4 — Documentation and demo

The final demonstration shows normal, boundary, and invalid inputs using `nck.asm`, followed by the automated test summary. A separate short report can explain the simulator extensions, nCk algorithm, stack frame, results, and limitations in more detail.

---

## 4. Working together with Git

Work in feature branches and open Pull Requests instead of pushing directly to `main`:

```bash
git switch main
git pull origin main
git switch -c step4-docs
# edit and review documentation
git add README.md
git commit -m "Update README"
git push -u origin step4-docs
```

- Have another teammate review the Pull Request before merging.
- Keep changes focused and understandable.
- Do not modify files in `reference/`.

---

## 5. Known limitations and remaining issues

The original V7.1 simulator had missing instruction implementations and incomplete R-type encoding. The project added the instructions needed by `nck.asm`, but it remains a **simplified educational simulator**:

- **Partial ISA:** Several instructions are recognized by the parser but do not have an execution implementation. `MUL` and `DIV` are not CPU instructions here.
- **Simplified memory:** `Memory` stores address-to-value mappings in a Python dictionary. `SW` writes a full register value at one address, rather than four separate bytes as real MIPS memory would; the memory dump shows only the low byte of each entry.
- **Encoding is not complete:** Not every recognized instruction is assembled to a fully correct MIPS machine-code word. Execution operates on parsed `Instruction` objects, not by decoding bytes back from memory.
- **Instruction semantics:** Some arithmetic and comparison behavior differs from hardware MIPS, including overflow handling and the `SLTI` source-register side effect.
- **Assembly syntax:** Numeric registers, numeric branch offsets, and numeric jump addresses are required. Symbolic labels and inline comments are not supported.
- **Input scope:** The nCk program validates numeric bounds, but malformed, missing, or non-integer input is not covered by the current test suite.
- **Performance:** Multiplication by repeated addition and division by doubling/subtraction are slower than native hardware operations.

---

## 6. Quick demo commands

Run these from the repository root:

```bash
python sim/main.py -q programs/nck.asm
# Enter: 5 2      -> 10
# Enter: 26 13    -> 10400600
# Enter: 27 5     -> -1

python tests/test_nck.py
# Expected summary: TOTAL: 385/385 passed
```

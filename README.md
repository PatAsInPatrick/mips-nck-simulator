# mips-nck-simulator

A small MIPS CPU simulator written in Python, plus a MIPS assembly program that computes

```
nCk = n! / ((n-k)! * k!)
```

using only addition and subtraction (no multiply/divide instructions).

Computer Architecture term project — Software track, Phase I.

---

## Repository layout

```
mips-nck-simulator/
├── sim/                  # The simulator (starting point: professor's V7.1)
│   ├── main.py           # Entry point — run this
│   ├── cpu.py            # Registers, PC, fetch/execute loop, instruction behavior
│   ├── isa.py            # Parses each line + assembles it into machine code (hex)
│   ├── memory.py         # Memory (a dictionary: address -> value)
│   └── instructions.txt  # Default program loaded when no file is given
├── examples/             # Small assembly programs that already run
│   ├── sum_10_to_1.asm   # Adds 10+9+...+1 -> result in $3 (= 55 = 0x37)
│   └── instruction_demo.asm
├── reference/            # Material from the professor (read-only, do not edit)
│   ├── nCkbound.py              # nCk without multiply/divide (Python version)
│   ├── factorial_no_mul_1.py    # n! using only addition (for loop)
│   ├── factorial_no_mul_2.py    # n! using only addition (while loop)
│   ├── Readme.txt               # Change log V1–V2 (Thai)
│   └── Readme3-7.txt            # Change log V3–V7 (Thai)
└── README.md
```

New files we create later:

```
programs/nck.asm          # Our nCk program (Step 2)
tests/test_nck.py         # Automatic checker (Step 3)
```

---

## 1. Get started

**You need:** Python **3.10 or newer** (the code uses `match`), Git, and any editor (VS Code is fine).
No Vivado, no FPGA tools — this track is software only.

```bash
git clone https://github.com/<owner>/mips-nck-simulator.git
cd mips-nck-simulator/sim

python main.py                               # runs instructions.txt
python main.py ../examples/sum_10_to_1.asm   # runs any program file
```

What you will see:

1. Every instruction with its address and machine code (hex).
2. After each executed instruction: all 32 registers and a memory dump.
3. `Last STATE` — the final registers. For `sum_10_to_1.asm`, register `$3` = `00000037` (55).

> Tip: the output is long. Save it with `python main.py ../examples/sum_10_to_1.asm > out.txt`.

---

## 2. How to write a program for this simulator

The simulator reads a plain text file, one instruction per line.
Its syntax is simpler (and stricter) than MARS/QtSpim:

| Rule | Example |
|---|---|
| First line sets the start address | `.ORG 0` or `.ORG 0x2000` |
| Operands are separated by **spaces**, no commas | `ADD $3 $2 $3` |
| Registers by **number only** (`$t0` is not supported yet) | `$8` not `$t0` |
| Immediates can be decimal or hex | `ADDI $2 $0 -1`, `ORI $2 $0 0xff` |
| Load/store use `offset($reg)` | `LW $12 4($21)` |
| No labels — branch offset = how many lines to jump, counted from the **next** line | `BNE $0 $2 -3` jumps 3 lines back from the next line |
| `J` takes a real byte address | `J 0x2030` |
| End with `HALT` | `HALT` |
| No comments, no blank-line tricks | — |

Annotated example (`examples/sum_10_to_1.asm`):

```
.ORG 0
ORI $2 $0 10      # $2 = 10          (counter)
ORI $3 $0 0       # $3 = 0           (sum)
ADD $3 $2 $3      # sum = sum + counter    <- loop starts here
ADDI $2 $2 -1     # counter = counter - 1
BNE $0 $2 -3      # if counter != 0, go back 3 lines (to ADD)
HALT
```

(The `# ...` comments above are for explanation only — remove them in real files.)

### Instruction status in V7.1

| Status | Instructions |
|---|---|
| ✅ Works | `ADD` `ADDI` `ADDIU` `ORI` `LUI` `LW` `SW` `SLTI` `SLTIU` `BEQ` `BNE` `J` `HALT` `.ORG` |
| ⚠️ Parsed but **not executed** (does nothing) | `SUB` `SUBU` `ADDU` `AND` `OR` `NOR` `SLT` `SLTU` `JAL` |
| ❌ Not supported | `JR` `SLL` `SRL` (parsed as nothing), `SYSCALL`, `MUL`, `DIV` |

---

## 3. Project steps

Work through the steps in order.

### Step 1 — Fix and extend the simulator (`sim/`)

Goal: the simulator supports everything the nCk program needs.

- **Execute missing instructions** in `cpu.py → execute()`: `SUB`, `SLT`, `AND`, `OR`, `ADDU`, `SUBU`
- **Function calls**
  - `JAL addr` → `$31` (`$ra`) = address of the next instruction, then jump
  - `JR $rs` → jump to the address in `$rs` (also add parsing in `isa.py → decode2()`)
- **Stack pointer** — set `$29` (`$sp`) to a starting value in `CPU.__init__` (e.g. `0x7FFFEFFC`, same as QtSpim)
- **Input / output with `SYSCALL`** (same codes as MARS/QtSpim):

  | `$2` (`$v0`) | Action |
  |---|---|
  | `1` | print integer in `$4` (`$a0`) |
  | `5` | read integer from keyboard into `$2` (`$v0`) |
  | `10` | exit (same as `HALT`) |

- **Assemble R-type to machine code** in `isa.py → decode3()` (now outputs `00000000`).
  Format: `opcode(6) rs(5) rt(5) rd(5) shamt(5) funct(6)` — funct codes are already in `cmdDict`.
- **Fix bug** in `cpu.py → validate()`: `int(hex(...)[-8:])` must be `int(hex(...)[-8:], 16)`
- **Quiet mode** — option to print only `SYSCALL` output and the final state (the per-step dump is too long for testing)
- After every change: `examples/sum_10_to_1.asm` still ends with `$3 = 0x37`

### Step 2 — Write the nCk program (`programs/nck.asm`)

Goal: read `n` and `k`, print `nCk`.

**Input limits:** `1 ≤ n ≤ 26` and `0 ≤ k ≤ n`. Print an error value (e.g. `-1`) for anything else.
Why 26: the largest answer (26C13 = 10,400,600) and every intermediate value must fit in a 32-bit register.

**Algorithm** — multiply and divide step by step so numbers stay small:

```
a = min(k, n - k)
result = 1
for i = 1 .. a:
    result = mul(result, n - a + i)
    result = div(result, i)        # always divides exactly
```

> ⚠️ Do **not** compute `n × (n-1) × ...` first and divide at the end (like `reference/nCkbound.py`).
> It overflows 32 bits from n = 18 (e.g. 18×17×…×10 = 17,643,225,600).

**Program structure** (functions called with `JAL` / returned with `JR $31`):

| Function | Input | Output | Calls others? | Needs stack? |
|---|---|---|---|---|
| `mul` | `$4`, `$5` | `$2` = a × b (repeated add) | no | no |
| `div` | `$4`, `$5` | `$2` = a ÷ b (repeated subtract) | no | no |
| `nck` | `$4` = n, `$5` = k | `$2` = nCk | yes (`mul`, `div`) | **yes** — save `$31` and any registers it still needs |
| main | — | reads n, k → `JAL nck` → prints result → exits | yes | — |

Tips:
- Write the logic in Python first (copy the loop above), then translate line by line.
- Because there are no labels, write each function's start address in a note and count branch offsets carefully.
- Optional: run the same logic in MARS/QtSpim to compare.

### Step 3 — Test (`tests/test_nck.py`)

Goal: prove the simulator gives the same answer as Python.

- Script runs the simulator for **every** pair `1 ≤ n ≤ 26, 0 ≤ k ≤ n` (378 pairs)
- Compares each result with `math.comb(n, k)`
- Prints a summary, e.g. `378/378 passed`, and lists any failures
- Also tests invalid input (`n = 27`, `k > n`, negative numbers)
- Save the output as `tests/results.txt`

### Step 4 — Write-up and demo

- Update this README: final instruction table, how to run `nck.asm`, test result
- Short report: what we added to the simulator, how the nCk program works (with a stack diagram), test results, limits
- Demo: run `nck.asm` live with a few inputs + show the full test pass

---

## 4. Working together with Git

```bash
git pull                              # always start with the latest main
git checkout -b step1-sub-slt         # one branch per task
# ...edit, run, check...
git add .
git commit -m "Add SUB and SLT to execute()"
git push -u origin step1-sub-slt      # then open a Pull Request on GitHub
```

- Never push directly to `main`; merge through a Pull Request after one teammate checks it.
- Keep each Pull Request small (one feature or fix).
- Don't edit files in `reference/`.

---

## 5. Known issues in the starting code (V7.1)

- R-type instructions are not assembled (memory shows `00 00 00 00`).
- `SW` stores the whole value at one byte address, but the memory dump only shows the last 2 hex digits. It works for the simulator, but it is not real byte-level memory. Data written with `SW` can also overlap the program's own code area — keep the stack far away (e.g. `0x7FFFEFFC`).
- `SLTI` / `SLTIU` change the value of `rs` while comparing (side effect).
- Unknown opcodes stop the program with `error unknown opcode`.


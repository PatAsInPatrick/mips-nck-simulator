"""List every valid nCk case one by one (expected vs. simulator output).

Usage (from any working directory):
    python tests/list_cases.py        # all valid pairs, 1 <= n <= 26 (377 cases)
    python tests/list_cases.py 10     # only n = 10
"""

import math
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
COMMAND = [sys.executable, "sim/main.py", "-q", "programs/nck.asm"]

ns = [int(sys.argv[1])] if len(sys.argv) > 1 else range(1, 27)
for n in ns:
    for k in range(n + 1):
        got = subprocess.run(COMMAND, input=f"{n} {k}\n", capture_output=True,
                             text=True, cwd=PROJECT_ROOT).stdout.strip()
        exp = math.comb(n, k)
        status = "OK" if got == str(exp) else "FAIL"
        print(f"{n:>2} {k:>2}  expected={exp:<10} got={got:<10} {status}")

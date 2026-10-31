"""Black-box tests for the nCk program. Run from any working directory."""

import math
import subprocess
import sys
from pathlib import Path


# Switch the command here when nck.asm and the simulator are ready.
# COMMAND = [sys.executable, "programs/nck_reference.py"]
COMMAND = [sys.executable, "sim/main.py", "-q", "programs/nck.asm"]

TIMEOUT_SECONDS = 5
PROJECT_ROOT = Path(__file__).resolve().parent.parent
RESULTS_FILE = PROJECT_ROOT / "tests" / "results.txt"

# (n, k) pairs that must print -1.
INVALID_CASES = [
    (27, 13),  # n above 26
    (0, 0),    # n below 1
    (5, 6),    # k > n
    (26, 27),  # k > n at the upper boundary
    (-1, 0),   # negative n
    (5, -1),   # negative k
    (-1, -1),  # both negative
]


def run_program(n: int, k: int, *, one_line: bool = False) -> str:
    """Run a fresh process and return its output or a diagnostic string."""
    stdin_text = f"{n} {k}\n" if one_line else f"{n}\n{k}\n"

    try:
        completed = subprocess.run(
            COMMAND,
            input=stdin_text,
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT,
            timeout=TIMEOUT_SECONDS,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return f"<TIMEOUT after {TIMEOUT_SECONDS}s>"
    except OSError as error:
        return f"<PROCESS ERROR: {error}>"

    output = completed.stdout.strip()
    if completed.returncode != 0:
        error_text = completed.stderr.strip()[:200]
        return (
            f"<EXIT {completed.returncode}; "
            f"stdout={output!r}; stderr={error_text!r}>"
        )
    return output if output else "<EMPTY OUTPUT>"


def main() -> int:
    RESULTS_FILE.parent.mkdir(parents=True, exist_ok=True)

    # Give one clear error instead of generating hundreds of missing-file failures.
    program_file = PROJECT_ROOT / COMMAND[-1]
    if not program_file.is_file():
        message = f"ERROR: Program file not found: {program_file}"
        print(message)
        RESULTS_FILE.write_text(message + "\n", encoding="utf-8")
        return 2

    failures = []
    valid_passed = 0
    valid_total = 0

    # All distinct valid pairs: sum(n + 1 for n in 1..26) = 377.
    for n in range(1, 27):
        for k in range(n + 1):
            valid_total += 1
            expected = math.comb(n, k)
            got = run_program(n, k)
            if got == str(expected):
                valid_passed += 1
            else:
                failures.append(("valid", n, k, expected, got))

    invalid_passed = 0
    for n, k in INVALID_CASES:
        got = run_program(n, k)
        if got == "-1":
            invalid_passed += 1
        else:
            failures.append(("invalid", n, k, -1, got))

    # The regular cases use two-line stdin. Check space-separated stdin as well.
    format_n, format_k = 5, 2
    format_expected = math.comb(format_n, format_k)
    format_got = run_program(format_n, format_k, one_line=True)
    format_passed = int(format_got == str(format_expected))
    if not format_passed:
        failures.append(("one-line input", format_n, format_k,
                         format_expected, format_got))

    total_passed = valid_passed + invalid_passed + format_passed
    total_tests = valid_total + len(INVALID_CASES) + 1

    lines = [
        f"Command: {' '.join(COMMAND)}",
        f"Timeout: {TIMEOUT_SECONDS} seconds per run",
        f"Valid pairs: {valid_passed}/{valid_total} passed",
        f"Invalid inputs: {invalid_passed}/{len(INVALID_CASES)} passed",
        f"One-line input: {format_passed}/1 passed",
        f"TOTAL: {total_passed}/{total_tests} passed",
        "",
        "Failures (n, k, expected, got):",
    ]
    if failures:
        for category, n, k, expected, got in failures:
            lines.append(f"  [{category}] ({n}, {k}, {expected}, {got!r})")
    else:
        lines.append("  None")

    report = "\n".join(lines) + "\n"
    print(report, end="")
    RESULTS_FILE.write_text(report, encoding="utf-8")
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())

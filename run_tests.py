#!/usr/bin/env python3
"""
run_tests.py — Run all test transcripts through the audit system and report results.
Usage: python run_tests.py
"""

import subprocess
import sys
from pathlib import Path

PYTHON = sys.executable

# ── Test definitions ──────────────────────────────────────────────────────────
# Each test: (description, script, args, expect_pass)
#   expect_pass = True means we expect exit code 0 (script runs without error)

TESTS = [
    # ── Level 1 ───────────────────────────────────────────────────────────────
    ("L1: Basic credit tally",
     "audit_l1.py", ["test_L1.csv"], True),

    ("L1: Main transcript",
     "audit_l1.py", ["transcript.csv"], True),

    ("L1: Worse retake (best grade kept)",
     "audit_l1.py", ["test_worse_retake.csv"], True),

    # ── Level 2 ───────────────────────────────────────────────────────────────
    ("L2: Semester CGPA",
     "audit_l2.py", ["test_L2.csv", "--waivers", "NONE"], True),

    ("L2: Main transcript",
     "audit_l2.py", ["transcript.csv", "--waivers", "NONE"], True),

    ("L2: Worse retake (best grade kept)",
     "audit_l2.py", ["test_worse_retake.csv", "--waivers", "NONE"], True),

    # ── Level 3: CSE ─────────────────────────────────────────────────────────
    ("L3: CSE basic audit",
     "audit_l3.py", ["test_L3.csv", "CSE", "program.md"], True),

    ("L3: CSE retake scenario",
     "audit_l3.py", ["test_L3_retake.csv", "CSE", "program.md"], True),

    ("L3: CSE main transcript",
     "audit_l3.py", ["transcript.csv", "CSE", "program.md"], True),

    ("L3: CSE invalid course codes (ART101, MUS200, DNC150, ZOO999)",
     "audit_l3.py", ["test_invalid_courses.csv", "CSE", "program.md"], True),

    ("L3: CSE prerequisite violations",
     "audit_l3.py", ["test_prereqs.csv", "CSE", "program.md"], True),

    ("L3: CSE worse retake (best grade kept)",
     "audit_l3.py", ["test_worse_retake.csv", "CSE", "program.md"], True),

    # ── Level 3: BBA ─────────────────────────────────────────────────────────
    ("L3: BBA basic audit",
     "audit_l3.py", ["test_BBA.csv", "BBA", "program.md"], True),

    ("L3: BBA major declaration before 60 credits",
     "audit_l3.py", ["test_BBA_major_declaration.csv", "BBA", "program.md"], True),
]

# ── ANSI helpers ──────────────────────────────────────────────────────────────
GR = '\033[92m'; RD = '\033[91m'; YL = '\033[93m'; CY = '\033[96m'
BL = '\033[1m';  DM = '\033[2m';  RS = '\033[0m'


def run_test(desc, script, args, expect_pass):
    """Run a single test and return (passed: bool, stdout, stderr)."""
    cmd = [PYTHON, script] + args
    result = subprocess.run(cmd, capture_output=True, text=True, input='\n')

    ok = (result.returncode == 0) == expect_pass
    return ok, result.stdout, result.stderr, result.returncode


def main():
    print(f"\n{BL}{CY}{'═' * 60}{RS}")
    print(f"{BL}{CY}  NSU Audit System — Test Runner{RS}")
    print(f"{BL}{CY}{'═' * 60}{RS}\n")

    passed = 0
    failed = 0
    total  = len(TESTS)

    for i, (desc, script, args, expect_pass) in enumerate(TESTS, 1):
        ok, stdout, stderr, rc = run_test(desc, script, args, expect_pass)

        status = f"{GR}PASS{RS}" if ok else f"{RD}FAIL{RS}"
        print(f"  [{status}]  {BL}{i:>2}/{total}{RS}  {desc}")

        if not ok:
            failed += 1
            print(f"         {DM}Exit code: {rc}{RS}")
            if stderr.strip():
                for line in stderr.strip().split('\n')[:5]:
                    print(f"         {RD}{line}{RS}")
        else:
            passed += 1

        # Show key output lines for L3 tests (verdict + advisories)
        if 'audit_l3' in script and stdout:
            for line in stdout.split('\n'):
                stripped = line.strip()
                if any(kw in stripped for kw in [
                    'ELIGIBLE', 'NOT ELIGIBLE',
                    'Invalid Elective', 'Prerequisite violation',
                    'Major declaration', 'ADVISORY'
                ]):
                    print(f"         {DM}▸ {stripped}{RS}")

    # ── Summary ──────────────────────────────────────────────────────────────
    print(f"\n{BL}{'─' * 60}{RS}")
    summary_color = GR if failed == 0 else RD
    print(f"  {summary_color}{BL}{passed}/{total} tests passed{RS}", end="")
    if failed:
        print(f"  ({RD}{failed} failed{RS})")
    else:
        print(f"  {GR}✓  All tests passed!{RS}")
    print(f"{BL}{'─' * 60}{RS}\n")

    sys.exit(0 if failed == 0 else 1)


if __name__ == '__main__':
    main()

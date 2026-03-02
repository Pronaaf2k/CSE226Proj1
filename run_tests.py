#!/usr/bin/env python3
"""
run_tests.py — Targeted edge-case test suite for the NSU Audit System.
Usage: python run_tests.py
"""

import subprocess
import sys
from pathlib import Path

PYTHON = sys.executable

# ── ANSI helpers ──────────────────────────────────────────────────────────────
GR = '\033[92m'; RD = '\033[91m'; YL = '\033[93m'; CY = '\033[96m'
BL = '\033[1m';  DM = '\033[2m';  RS = '\033[0m'

# ── Test definition format ────────────────────────────────────────────────────
# (description, script, args, expect_exit_ok, required_in_output, forbidden_in_output)
#   required_in_output  — list of strings that MUST appear in stdout
#   forbidden_in_output — list of strings that must NOT appear in stdout

TESTS = [

    # ══════════════════════════════════════════════════════════════════════════
    # Level 1 — Credit Tally baseline
    # ══════════════════════════════════════════════════════════════════════════
    (
        "L1: Basic credit tally",
        "audit_l1.py", ["test_L1.csv"], True,
        [], []
    ),
    (
        "L1: Sample transcript",
        "audit_l1.py", ["transcript.csv"], True,
        [], []
    ),

    # ══════════════════════════════════════════════════════════════════════════
    # Retake logic — best grade must always win
    # ══════════════════════════════════════════════════════════════════════════
    (
        "L1: Retake worse -- A then C-/F fires Illegal Retake label",
        "audit_l1.py", ["test_retake_worse.csv"], True,
        ["Illegal Retake"],             # A then C-/F are illegal retakes
        []
    ),
    (
        "L1: Retake chain -- D->C->B are all legal retakes (no Illegal Retake)",
        "audit_l1.py", ["test_retake_chain.csv"], True,
        ["Retake (Ignored)"],           # legal retakes still show
        ["Illegal Retake"]              # but no illegal retake fires
    ),
    (
        "L2: Retake worse -- Illegal Retake label shown for post-A attempts",
        "audit_l2.py", ["test_retake_worse.csv", "--waivers", "NONE"], True,
        ["Illegal Retake"], []
    ),
    (
        "L2: Retake chain -- no Illegal Retake label (D->C->B all legal)",
        "audit_l2.py", ["test_retake_chain.csv", "--waivers", "NONE"], True,
        [], ["Illegal Retake"]
    ),
    (
        "L3: Retake worse -- illegal retake advisory fires for post-A attempts",
        "audit_l3.py", ["test_retake_worse.csv", "CSE", "program.md"], True,
        ["NOT ELIGIBLE", "Illegal retake"],  # advisory must fire
        ["\u2022  CSE115"]                        # CSE115 must NOT be in the missing-course list
    ),
    (
        "L3: Retake chain -- D->C->B are legal, no illegal retake advisory",
        "audit_l3.py", ["test_retake_chain.csv", "CSE", "program.md"], True,
        [],
        ["Illegal retake"]
    ),

    # ══════════════════════════════════════════════════════════════════════════
    # Department switch — BBA courses in a CSE audit
    # ══════════════════════════════════════════════════════════════════════════
    (
        "L3: Dept switch BBA->CSE -- BBA courses treated as valid free electives",
        "audit_l3.py", ["test_dept_switch_bba_to_cse.csv", "CSE", "program.md"], True,
        [],                          # BBA courses are real NSU courses (valid free electives)
        ["Invalid Electives"]        # they must NOT be flagged as invalid
    ),
    (
        "L2: Dept switch BBA→CSE — BBA courses still counted in CGPA (GPA is universal)",
        "audit_l2.py", ["test_dept_switch_bba_to_cse.csv", "--waivers", "NONE"], True,
        [], []
    ),

    # ══════════════════════════════════════════════════════════════════════════
    # BBT courses in a CSE transcript
    # ══════════════════════════════════════════════════════════════════════════
    (
        "L3: BBT in CSE — BBT/BIO courses flagged as invalid electives, credits excluded",
        "audit_l3.py", ["test_bbt_in_cse.csv", "CSE", "program.md"], True,
        ["Invalid Electives"],
        []
    ),
    (
        "L1: BBT in CSE — BBT courses still counted in L1 credit tally (L1 is program-agnostic)",
        "audit_l1.py", ["test_bbt_in_cse.csv"], True,
        [], []
    ),

    # ══════════════════════════════════════════════════════════════════════════
    # T-grade (admission-test waiver)
    # ══════════════════════════════════════════════════════════════════════════
    (
        "L2: T-grade — ENG102(T) shown as Waived, excluded from CGPA",
        "audit_l2.py", ["test_t_grade_waiver.csv", "--waivers", "NONE"], True,
        ["Waived"],                   # must appear in L2 output for ENG102
        []
    ),
    (
        "L3: T-grade — ENG102(T) satisfies GED requirement (ENG102 not in missing list)",
        "audit_l3.py", ["test_t_grade_waiver.csv", "CSE", "program.md"], True,
        [],
        ["ENG102"]                    # ENG102 must NOT appear in the missing/deficiency list
    ),

    # ══════════════════════════════════════════════════════════════════════════
    # CGPA truncation — 1.996x must become 1.99, NOT round to 2.00
    # ══════════════════════════════════════════════════════════════════════════
    (
        "L2: CGPA truncation -- borderline 1.994 shows as 1.99 (truncation active)",
        "audit_l2.py", ["test_cgpa_truncation.csv", "--waivers", "NONE"], True,
        ["1.99"],                     # final CGPA must show 1.99
        []                           # (raw=1.9941 rounds to 1.99 too; L3 test is the stronger check)
    ),
    (
        "L3: CGPA truncation -- raw ~1.992 student is NOT eligible (floor rule)",
        "audit_l3.py", ["test_cgpa_truncation.csv", "CSE", "program.md"], True,
        ["NOT ELIGIBLE FOR GRADUATION"],
        ["\u2713   ELIGIBLE FOR GRADUATION"]  # checkmark verdict line must not appear
    ),

    # ======================================================================
    # CSE 0-credit lab co-registration
    # ======================================================================
    (
        "L3: CSE lab coreq -- CSE225L taken without CSE225 in same sem -> advisory",
        "audit_l3.py", ["test_lab_coreq.csv", "CSE", "program.md"], True,
        ["Co-registration"],           # must fire advisory
        []
    ),
    (
        "L3: CSE lab coreq -- PHY107L (1-credit, non-CSE) never triggers co-reg check",
        "audit_l3.py", ["test_lab_coreq.csv", "CSE", "program.md"], True,
        [],
        ["Co-registration: PHY107L"]   # must NOT mention PHY107L
    ),

    # ======================================================================
    # Prerequisite violations (existing test)
    # ======================================================================
    (
        "L3: Prerequisite violations flagged in advisory",
        "audit_l3.py", ["test_prereqs.csv", "CSE", "program.md"], True,
        ["Prerequisite violation"],
        []
    ),

    # ══════════════════════════════════════════════════════════════════════════
    # Invalid course codes (existing test)
    # ══════════════════════════════════════════════════════════════════════════
    (
        "L3: Invalid course codes flagged as invalid electives",
        "audit_l3.py", ["test_invalid_courses.csv", "CSE", "program.md"], True,
        ["Invalid Electives"],
        []
    ),

    # ══════════════════════════════════════════════════════════════════════════
    # BBA audits
    # ══════════════════════════════════════════════════════════════════════════
    (
        "L3: BBA basic audit",
        "audit_l3.py", ["test_BBA.csv", "BBA", "program.md"], True,
        [], []
    ),
    (
        "L3: BBA major declaration before 60 credits → advisory fired",
        "audit_l3.py", ["test_BBA_major_declaration.csv", "BBA", "program.md"], True,
        ["Major declaration"],
        []
    ),

    # ======================================================================
    # Sanity: sample transcript still passes through all 3 levels
    # ======================================================================
    (
        "L3: Sample transcript (CSE) — runs without error",
        "audit_l3.py", ["transcript.csv", "CSE", "program.md"], True,
        [], []
    ),

    # ======================================================================
    # Graduation — full transcripts that should reach ELIGIBLE
    # ======================================================================
    (
        "L3: CSE graduation — complete transcript is ELIGIBLE",
        "audit_l3.py", ["test_grad_CSE.csv", "CSE", "program.md"], True,
        ["ELIGIBLE FOR GRADUATION"],
        ["NOT ELIGIBLE"]
    ),
    (
        "L3: CSE graduation — credit total meets 130",
        "audit_l3.py", ["test_grad_CSE.csv", "CSE", "program.md"], True,
        ["Credits Required : 130"],
        []
    ),

    # ======================================================================
    # Elective overload — too many free electives fires advisory (non-blocking)
    # ======================================================================
    (
        "L3: Elective overload — ELIGIBLE despite excess free electives",
        "audit_l3.py", ["test_elective_overflow.csv", "CSE", "program.md"], True,
        ["ELIGIBLE FOR GRADUATION", "Elective overload"],
        ["NOT ELIGIBLE"]
    ),
    (
        "L3: Elective overload — excess courses listed in advisory",
        "audit_l3.py", ["test_elective_overflow.csv", "CSE", "program.md"], True,
        ["excess"],
        []
    ),
]


def run_test(desc, script, args, expect_exit_ok, required, forbidden):
    """Run a single test. Returns (passed, detail_lines)."""
    cmd = [PYTHON, script] + args
    result = subprocess.run(cmd, capture_output=True, text=True, input='\n',
                             encoding='utf-8', errors='replace')

    exit_ok = (result.returncode == 0) == expect_exit_ok
    output  = (result.stdout or "") + (result.stderr or "")
    detail  = []
    passed  = exit_ok

    if not exit_ok:
        detail.append(f"Exit code: {result.returncode} (expected {'0' if expect_exit_ok else '!=0'})")
        for line in (result.stderr or "").strip().split('\n')[:3]:
            if line.strip():
                detail.append(f"stderr: {line.strip()}")

    for needle in required:
        if needle not in output:
            passed = False
            detail.append(f"MISSING in output: {repr(needle)}")

    for needle in forbidden:
        if needle in output:
            passed = False
            detail.append(f"SHOULD NOT appear in output: {repr(needle)}")

    return passed, detail, result.stdout


def main():
    print(f"\n{BL}{CY}{'=' * 62}{RS}")
    print(f"{BL}{CY}  NSU Audit System -- Edge Case Test Suite{RS}")
    print(f"{BL}{CY}{'=' * 62}{RS}\n")

    ok_count = 0
    fail_count = 0
    total = len(TESTS)

    for i, (desc, script, args, expect_exit_ok, required, forbidden) in enumerate(TESTS, 1):
        passed, details, stdout = run_test(desc, script, args, expect_exit_ok, required, forbidden)

        tag = f"{GR}PASS{RS}" if passed else f"{RD}FAIL{RS}"
        print(f"  [{tag}]  {BL}{i:>2}/{total}{RS}  {desc}")

        if not passed:
            fail_count += 1
            for d in details:
                print(f"           {RD}> {d}{RS}")
        else:
            ok_count += 1
            # For L3 tests, show verdict line
            if 'audit_l3' in script and stdout:
                for line in stdout.split('\n'):
                    s = line.strip()
                    if any(kw in s for kw in [
                        'ELIGIBLE', 'NOT ELIGIBLE',
                        'Invalid Elective', 'Prerequisite violation',
                        'Major declaration', 'ADVISORY', 'CGPA Earned'
                    ]):
                        print(f"           {DM}> {s}{RS}")

    print(f"\n{BL}{'-' * 62}{RS}")
    colour = GR if fail_count == 0 else RD
    print(f"  {colour}{BL}{ok_count}/{total} tests passed{RS}", end="")
    if fail_count:
        print(f"  ({RD}{fail_count} failed{RS})")
    else:
        print(f"  {GR}  All tests passed!{RS}")
    print(f"{BL}{'-' * 62}{RS}\n")

    sys.exit(0 if fail_count == 0 else 1)


if __name__ == '__main__':
    main()

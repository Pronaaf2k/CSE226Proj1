#!/usr/bin/env python3
"""
NSU Graduation Audit System - Test Transcript Generator
Generates 2000 diverse test transcripts covering all 15 NSU programs.
Usage: python generate_tests.py
"""

import csv
import os
import random
import subprocess
import sys
from pathlib import Path

random.seed(42)   # reproducible

# ── Grade data ──────────────────────────────────────────────────────────────────
GRADE_POINTS = {
    'A': 4.0, 'A-': 3.7, 'B+': 3.3, 'B': 3.0, 'B-': 2.7,
    'C+': 2.3, 'C': 2.0, 'C-': 1.7, 'D+': 1.3, 'D': 1.0, 'F': 0.0
}
EXCELLENT  = ['A', 'A-', 'B+']
GOOD       = ['B+', 'B', 'B-', 'C+']
AVERAGE    = ['C+', 'C', 'C-', 'B-']
POOR       = ['C-', 'D+', 'D', 'F']
ALL_LETTER = list(GRADE_POINTS.keys())

SEMESTERS = [f"{s} {y}" for y in range(2019, 2026)
             for s in ['Spring', 'Summer', 'Fall']]

# ── Program definitions ──────────────────────────────────────────────────────────
# Format: (course_code, credits)
PROGRAMS = {
    "Computer Science & Engineering": {
        "alias": "CSE", "total": 130,
        "ged":  [("ENG102",3),("ENG103",3),("HIS103",3),("PHI101",3),
                 ("BEN205",3),("POL101",3),("ECO101",3),("SOC101",3),("ENV203",3)],
        "math": [("MAT116",0),("MAT120",3),("MAT125",3),("MAT130",3),
                 ("MAT250",3),("MAT350",3),("MAT361",3)],
        "sci":  [("PHY107",3),("PHY107L",1),("PHY108",3),("PHY108L",1),
                 ("CHE101",3),("CHE101L",1)],
        "core": [("CSE115",4),("CSE115L",0),("CSE173",3),("CSE215",4),
                 ("CSE215L",0),("CSE225",3),("CSE225L",1),("CSE231",3),
                 ("CSE231L",1),("CSE311",3),("CSE311L",1),("CSE323",3),
                 ("CSE323L",1),("CSE327",3),("CSE327L",1),("CSE331",3),
                 ("CSE331L",1),("CSE332",3),("CSE373",3),("CSE425",3),("CSE499",3)],
        "elec": [("CSE445",3),("CSE447",3),("CSE461",3),("CSE471",3),("CSE477",3)],
    },
    "Electrical & Electronic Engineering": {
        "alias": "EEE", "total": 130,
        "ged":  [("ENG102",3),("ENG103",3),("ENG111",3),("HIS101",3),
                 ("PHI104",3),("POL101",3),("ECO101",3),("ENV203",3)],
        "math": [("MAT116",0),("MAT120",3),("MAT125",3),("MAT130",3),
                 ("MAT250",3),("MAT350",3),("MAT361",3)],
        "sci":  [("PHY107",3),("PHY107L",1),("PHY108",3),("PHY108L",1),
                 ("CHE101",3),("CHE101L",1),("BIO103",3)],
        "core": [("CSE115",3),("CSE115L",1),("EEE141",3),("EEE141L",1),
                 ("EEE241",3),("EEE241L",1),("EEE111",3),("EEE111L",1),
                 ("EEE211",3),("EEE211L",1),("EEE311",3),("EEE311L",1),
                 ("EEE221",3),("EEE361",3),("EEE342",3),("EEE342L",1),
                 ("EEE363",3),("EEE363L",1),("EEE312",3),("EEE312L",1),
                 ("EEE299",1),("EEE321",3),("EEE321L",1),
                 ("EEE499A",3),("EEE499B",3)],
        "elec": [("EEE410",3),("EEE422",3),("EEE461",3),("EEE432",3)],
    },
    "Electronic & Telecom Engineering": {
        "alias": "ETE", "total": 130,
        "ged":  [("ENG102",3),("ENG103",3),("ENG111",3),("HIS103",3),
                 ("PHI101",3),("POL101",3),("SOC101",3),("ENV203",3)],
        "math": [("MAT116",0),("MAT120",3),("MAT125",3),("MAT130",3),
                 ("MAT350",3),("MAT361",3)],
        "sci":  [("PHY107",3),("PHY107L",1),("PHY108",3),("PHY108L",1),
                 ("CHE101",3),("CHE101L",1)],
        "core": [("ETE131",3),("ETE131L",1),("ETE132",3),("ETE132L",1),
                 ("ETE211",3),("ETE211L",1),("ETE212",3),("ETE212L",1),
                 ("ETE221",3),("ETE283",2),("ETE311",3),("ETE311L",1),
                 ("ETE331",3),("ETE331L",1),("ETE361",3),("ETE381",2),
                 ("ETE423",3),("ETE424",3),("ETE481",2),
                 ("ETE499A",2),("ETE499B",2)],
        "elec": [("ETE412",3),("ETE422",3),("ETE431",3),("ETE451",3)],
    },
    "Civil & Environmental Engineering": {
        "alias": "CEE", "total": 149,
        "ged":  [("ENG102",3),("ENG103",3),("HIS103",3),("PHI101",3),
                 ("POL101",3),("SOC101",3),("ENV203",3)],
        "math": [("MAT116",0),("MAT120",3),("MAT125",3),("MAT130",3),
                 ("MAT250",3),("MAT350",3),("MAT361",3)],
        "sci":  [("PHY107",3),("PHY107L",1),("PHY108",3),("PHY108L",1),
                 ("CHE101",3),("CHE101L",1)],
        "core": [("CEE110",3),("CEE210",3),("CEE211",3),("CEE214",3),
                 ("CEE215",3),("CEE250",3),("CEE311",3),("CEE311L",1),
                 ("CEE312",3),("CEE313",3),("CEE313L",1),("CEE314",3),
                 ("CEE315",3),("CEE320",3),("CEE330",3),("CEE330L",1),
                 ("CEE335",3),("CEE335L",1),("CEE350",3),("CEE360",3),
                 ("CEE370",3),("CEE410",3),("CEE470",3),
                 ("CEE498",3),("CEE499",3)],
        "elec": [("CEE421",3),("CEE422",3),("CEE431",3)],
    },
    "Environmental Science & Management": {
        "alias": "ENV", "total": 130,
        "ged":  [("ENG103",3),("ENG105",3),("HIS103",3),("PHI101",3)],
        "math": [("MAT120",3),("ENV172",3),("ENV173",3)],
        "sci":  [("CHE101",3),("CHE101L",1),("BIO103",3),("BIO103L",1)],
        "core": [("ENV102",3),("ENV107",3),("ENV203",3),("ENV205",3),
                 ("ENV207",3),("ENV208",3),("ENV209",3),("ENV214",3),
                 ("ENV215",4),("ENV260",3),("ENV307",3),("ENV315",3),
                 ("ENV316",3),("ENV373",3),("ENV375",3),("ENV405",3),
                 ("ENV408",3),("ENV409",3),("ENV410",3),("ENV414",3),
                 ("ENV455",3),("ENV498",3),("ENV499",3)],
        "elec": [("ENV304",3),("ENV311",3),("ENV312",3),("ENV401",3)],
    },
    "English": {
        "alias": "ENG", "total": 123,
        "ged":  [("HIS103",3),("PHI101",3),("SOC101",3),("ENV203",3),("POL101",3)],
        "math": [("MIS105",3)],
        "sci":  [("SCI101",3)],
        "core": [("ENG109",3),("ENG110",3),("ENG111",3),("ENG115",3),
                 ("ENG210",3),("ENG220",3),("ENG230",3),("ENG260",3),
                 ("ENG311",3),("ENG312",3),("ENG321",3),("ENG322",3),
                 ("ENG331",3),("ENG401",3),("ENG402",3),("ENG499",3)],
        "elec": [("ENG341",3),("ENG342",3),("ENG351",3),("ENG361",3)],
    },
    "Business Administration": {
        "alias": "BBA", "total": 120,
        "ged":  [("ENG102",3),("ENG103",3),("HIS103",3),("PHI101",3),
                 ("BEN205",3),("ENV203",3),("PSY101",3)],
        "math": [("BUS172",3),("QM212",3)],
        "sci":  [("MIS205",3)],
        "core": [("ACT201",3),("ACT202",3),("ECO101",3),("ECO104",3),
                 ("FIN254",3),("MGT210",3),("MGT314",3),("MGT368",3),
                 ("MKT202",3),("LAW200",3),("BUS101",3),("BUS112",3),
                 ("BUS134",3),("BUS251",3),("BUS401",3),("BUS498",4),
                 ("MGT321",3),("MGT489",3)],
        "elec": [("FIN301",3),("MKT301",3),("MGT401",3),("ACT301",3)],
    },
    "Economics": {
        "alias": "ECO", "total": 120,
        "ged":  [("ENG103",3),("ENG105",3),("BEN205",3),("HIS103",3),
                 ("PHI101",3),("POL101",3)],
        "math": [("MAT125",3),("ECO172",3),("ECO173",3)],
        "sci":  [("MIS107",3)],
        "core": [("ECO101",3),("ECO104",3),("ECO201",3),("ECO204",3),
                 ("ECO317",3),("ECO328",3),("ECO349",3),("ECO354",3),
                 ("ECO372",3),("ECO414",3),("ECO490",3)],
        "elec": [("ECO441",3),("ECO443",3),("ECO415",3),("ECO492",3)],
    },
}

# ── Scenario definitions ─────────────────────────────────────────────────────────
# Each scenario returns (required_fraction, grade_pool, add_retakes, add_w, add_i)
SCENARIOS = {
    "eligible_top":      (1.00, EXCELLENT,  False, False, False),
    "eligible_good":     (1.00, GOOD,       False, False, False),
    "eligible_borderline":(1.00, AVERAGE,   False, False, False),
    "missing_ged":       (1.00, GOOD,       False, False, False),  # drops some GED
    "missing_core":      (1.00, GOOD,       False, False, False),  # drops some core
    "retake_pass":       (1.00, AVERAGE,    True,  False, False),
    "retake_fail":       (0.90, POOR,       True,  False, False),
    "withdrawal_heavy":  (1.00, GOOD,       False, True,  False),
    "probation":         (1.00, POOR,       False, False, False),
    "probation_recovery":(1.00, POOR,       True,  False, False),
    "partial":           (0.50, GOOD,       False, False, False),
    "near_grad":         (0.95, GOOD,       False, False, False),
    "incomplete":        (1.00, AVERAGE,    False, False, True),
    "mixed_complex":     (0.85, AVERAGE,    True,  True,  False),
}
SCENARIO_NAMES = list(SCENARIOS.keys())


def spread_into_semesters(courses):
    """Spread a flat list of (code,credits,grade) into semester buckets."""
    sems = random.sample(SEMESTERS, min(len(SEMESTERS), max(4, len(courses)//4 + 1)))
    sems.sort(key=lambda s: SEMESTERS.index(s))
    result = []
    for i, course in enumerate(courses):
        sem = sems[i % len(sems)]
        result.append((*course, sem))
    return result


def pick_grade(pool, force_fail=False):
    if force_fail:
        return 'F'
    return random.choice(pool)


def generate_transcript(prog_name, prog_data, scenario_name):
    required_frac, grade_pool, add_retakes, add_w, add_i = SCENARIOS[scenario_name]

    all_required = (
        prog_data["ged"] + prog_data["math"] +
        prog_data["sci"] + prog_data["core"]
    )
    all_electives = prog_data["elec"]

    rows = []  # (code, credits, grade)

    # ── Select required courses ──────────────────────────────────────────────
    n = max(1, int(len(all_required) * required_frac))
    chosen = all_required[:n]

    for code, cred in chosen:
        grade = pick_grade(grade_pool)
        rows.append((code, cred, grade))

    # ── Scenario-specific tweaks ─────────────────────────────────────────────
    if scenario_name == "missing_ged":
        drop = random.randint(1, min(3, len(prog_data["ged"])))
        rows = [r for r in rows if r[0] not in
                [c for c, _ in prog_data["ged"][:drop]]]

    elif scenario_name == "missing_core":
        core_codes = [c for c, _ in prog_data["core"]]
        drop = random.sample(core_codes, min(3, len(core_codes)))
        rows = [r for r in rows if r[0] not in drop]

    elif scenario_name in ("probation", "probation_recovery"):
        # Force some F grades → low CGPA
        new_rows = []
        for code, cred, grade in rows:
            if cred > 0 and random.random() < 0.45:
                grade = random.choice(['F', 'D', 'D+', 'C-'])
            new_rows.append((code, cred, grade))
        rows = new_rows

    # ── Retakes ──────────────────────────────────────────────────────────────
    if add_retakes:
        retake_rows = []
        for code, cred, grade in rows:
            if grade == 'F' and cred > 0 and random.random() < 0.7:
                better = random.choice(GOOD + AVERAGE)
                retake_rows.append((code, cred, better))
        rows += retake_rows

    # ── Withdrawals ───────────────────────────────────────────────────────────
    if add_w:
        new_rows = []
        for code, cred, grade in rows:
            if random.random() < 0.12:
                new_rows.append((code, cred, 'W'))
                # re-enroll with a grade
                new_rows.append((code, cred, pick_grade(grade_pool)))
            else:
                new_rows.append((code, cred, grade))
        rows = new_rows

    # ── Incompletes ───────────────────────────────────────────────────────────
    if add_i:
        new_rows = []
        for code, cred, grade in rows:
            if random.random() < 0.08:
                new_rows.append((code, cred, 'I'))
            else:
                new_rows.append((code, cred, grade))
        rows = new_rows

    # ── Add a few electives ───────────────────────────────────────────────────
    n_elec = random.randint(0, min(4, len(all_electives)))
    for code, cred in random.sample(all_electives, n_elec):
        rows.append((code, cred, pick_grade(grade_pool)))

    # ── Spread into semesters, build final dicts ──────────────────────────────
    spread = spread_into_semesters(rows)
    final = []
    for code, cred, grade, sem in spread:
        final.append({
            "Course_Code": code,
            "Credits":     cred,
            "Grade":       grade,
            "Semester":    sem,
        })
    return final


def run_audit(transcript_path, alias):
    """Run audit_l3.py on a transcript and return (returncode, stdout)."""
    result = subprocess.run(
        [sys.executable, "audit_l3.py", str(transcript_path), alias, "program.md"],
        capture_output=True, text=True
    )
    return result.returncode, result.stdout


def main():
    out_dir = Path("test_transcripts")
    out_dir.mkdir(exist_ok=True)

    programs  = list(PROGRAMS.items())
    total     = 2000
    per_prog  = total // len(programs)   # 133 each; leftover goes to first programs
    remainder = total - per_prog * len(programs)

    counts    = [per_prog + (1 if i < remainder else 0) for i in range(len(programs))]

    written   = 0
    errors    = 0

    for (prog_name, prog_data), n in zip(programs, counts):
        alias = prog_data["alias"]
        print(f"  Generating {n:>4} transcripts for {alias} ({prog_name})")

        for i in range(n):
            scenario = SCENARIO_NAMES[written % len(SCENARIO_NAMES)]
            rows = generate_transcript(prog_name, prog_data, scenario)

            fname = out_dir / f"transcript_{alias}_{written+1:04d}_{scenario[:12]}.csv"
            with open(fname, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=["Course_Code","Credits","Grade","Semester"])
                writer.writeheader()
                writer.writerows(rows)

            # Quick audit smoke-test for every 50th file
            if (written + 1) % 50 == 0:
                rc, _ = run_audit(fname, alias)
                if rc != 0:
                    errors += 1
                    print(f"    [WARN] Audit failed on {fname.name}")

            written += 1

    print(f"\n✓  {written} transcripts written to '{out_dir}/'")
    if errors:
        print(f"⚠  {errors} audit error(s) detected — check program.md aliases")
    else:
        print("✓  All sampled audits completed without errors")


if __name__ == "__main__":
    print("NSU Test Transcript Generator")
    print("=" * 50)
    main()

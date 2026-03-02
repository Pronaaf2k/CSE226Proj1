# CSE226 Project 1 — NSU Graduation Audit System

A 3-level CLI audit engine that processes student transcripts against NSU program
requirements to determine graduation eligibility, calculate CGPA, and identify deficiencies.

---

## 🚀 Quick Start

> **macOS / Linux** — runs natively with beautiful Unicode & colour output:
> ```bash
> python3 audit_l3.py transcript.csv CSE program.md
> python3 run_tests.py
> ```
>
> **Windows PowerShell** — set encoding first, then identical commands:
> ```powershell
> $env:PYTHONIOENCODING = 'utf-8'
> python audit_l3.py transcript.csv CSE program.md
> python run_tests.py
> ```

**Program aliases** (use the short code as `<PROGRAM>`):

| Alias | Program |
|---|---|
| `CSE` | Computer Science & Engineering |
| `ETE` | Electronic & Telecom Engineering |
| `ENV` | Environmental Science & Management |
| `ENG` | English |
| `BBA` | Business Administration |
| `ECO` | Economics |

---

## How to Play

<details>
<summary>📖 Click to expand</summary>

### Input: Transcript CSV
```
Course_Code,Credits,Grade,Semester
ENG102,3,A,Spring 2023
CSE115,4,F,Spring 2023
CSE115,4,A-,Summer 2023
CSE173,3,W,Fall 2023
```
- Valid seasons: `Spring`, `Summer`, `Fall`
- Valid grades: `A A- B+ B B- C+ C C- D+ D F W I`

### Level 1 output
Prints a per-course table showing whether each course's credits were `Counted`,
`Retake (Ignored)`, `Failed`, `Withdrawn`, or `Incomplete`.

### Level 2 output
Prints a semester-by-semester table with **TGPA** (term GPA) and **CGPA** after
each semester, plus a probation flag when CGPA drops below 2.00.

### Level 3 output
Prints a full graduation audit report: eligible/not-eligible verdict, credit
deficiency, CGPA, and a list of every missing required course by category.

</details>

---

## 🧪 Running Tests

````bash
# macOS / Linux
python3 run_tests.py

# Windows PowerShell
$env:PYTHONIOENCODING = 'utf-8'
python run_tests.py
````

Runs **27 test cases** across all 3 audit levels:

| Category | Tests |
|---|---|
| Retake logic (best grade kept, illegal B+ retake) | 6 |
| Dept switch & cross-department free electives | 2 |
| BBT/BIO invalid courses flagged | 2 |
| T-grade waiver | 2 |
| CGPA truncation (floor, not round) | 2 |
| CSE lab co-registration (0-credit labs) | 2 |
| Prerequisite violations | 1 |
| Invalid course codes | 1 |
| BBA basic audit + major declaration advisory | 2 |
| CSE graduation (full eligible transcript) | 2 |
| Elective overload advisory (non-blocking) | 2 |
| Sanity / sample transcript | 3 |

---

## Files

| File | Purpose |
|---|---|
| `audit_l1.py` | Level 1 — Credit Tally Engine |
| `audit_l2.py` | Level 2 — Semester CGPA & Probation Tracker |
| `audit_l3.py` | Level 3 — Graduation Audit & Deficiency Reporter |
| `program.md` | Knowledge base — all 8 NSU programs (with prerequisites) |
| `generate_tests.py` | Test transcript generator (2000 cases) |
| `run_tests.py` | Automated test runner (14 test cases) |
| `transcript.csv` | Sample student transcript |
| `test_L1.csv` | Edge-case test for Level 1 |
| `test_L2.csv` | Edge-case test for Level 2 |
| `test_L3.csv` | Edge-case test for Level 3 |
| `test_L3_retake.csv` | Retake scenario (fail → pass) |
| `test_BBA.csv` | BBA-specific test |
| `test_BBA_major_declaration.csv` | BBA major courses before 60 credits |
| `test_invalid_courses.csv` | Invalid course codes (ART101, MUS200, etc.) |
| `test_prereqs.csv` | Prerequisite violation scenarios |
| `test_worse_retake.csv` | Retake with worse grade (best grade kept) |
| `test_transcripts/` | Generated 2000 test transcripts |

---

## ⚠️ Known Limitations

The following programs are **supported** by the audit engine but their course lists
in `program.md` are **approximated** from publicly available NSU web pages and may
not reflect the exact current curriculum. Treat results for these programs as
indicative rather than authoritative:

| Program | Alias | Reason |
|---|---|---|
| Architecture | `ARCH` | Official semester-wise course codes not publicly indexed |
| Biochemistry & Biotechnology | `BBT` | Limited online course-code detail |
| Microbiology | `MIC` | Limited online course-code detail |
| Public Health | `PBH` | Limited online course-code detail |
| Pharmacy | `PHARM` | Very large programme (199 cr); full course list not scraped |
| Law (LLB Hons) | `LLB` | Online listing incomplete |
| Media, Communication & Journalism | `MCJ` | Department established 2022; limited public data |
| Electrical & Electronic Engineering | `EEE` | Lab credit rules (credit vs non-credit) could not be fully verified |
| Civil & Environmental Engineering | `CEE` | Lab credit rules (credit vs non-credit) could not be fully verified |

The following programs are **well-sourced** from official NSU pages and academic documents:

| Program | Alias | Source quality |
|---|---|---|
| Computer Science & Engineering | `CSE` | ✅ Official curriculum |
| Electronic & Telecom Engineering | `ETE` | ✅ Official curriculum |
| Environmental Science & Management | `ENV` | ✅ Official curriculum |
| English | `ENG` | ✅ Official curriculum |
| Business Administration | `BBA` | ✅ Official curriculum |
| Economics | `ECO` | ✅ Official curriculum |

---

## 🎓 Demo Commands

> All commands are shown in **macOS/Linux** (`python3`) and **Windows PowerShell** (`python`) format.
> For PowerShell, run `$env:PYTHONIOENCODING = 'utf-8'` once per session before any command.

---

### Level 1 — Credit Tally

````bash
# macOS / Linux
python3 audit_l1.py transcript.csv
python3 audit_l1.py test_L1.csv

# Windows PowerShell
python audit_l1.py transcript.csv
python audit_l1.py test_L1.csv
````

---

### Level 2 — Semester CGPA

````bash
# macOS / Linux
python3 audit_l2.py transcript.csv --waivers NONE
python3 audit_l2.py test_L2.csv --waivers ENG102,MAT116
python3 audit_l2.py test_cgpa_truncation.csv --waivers NONE   # shows 1.99, not 2.00

# Windows PowerShell
python audit_l2.py transcript.csv --waivers NONE
python audit_l2.py test_L2.csv --waivers ENG102,MAT116
python audit_l2.py test_cgpa_truncation.csv --waivers NONE
````

---

### Level 3 — Full Graduation Audit

#### ✅ CSE — Graduation eligible
````bash
# macOS / Linux
python3 audit_l3.py test_grad_CSE.csv CSE program.md

# Windows PowerShell
python audit_l3.py test_grad_CSE.csv CSE program.md
````

#### ⚠️ CSE — Elective overload (too many free electives, still eligible)
````bash
# macOS / Linux
python3 audit_l3.py test_elective_overflow.csv CSE program.md

# Windows PowerShell
python audit_l3.py test_elective_overflow.csv CSE program.md
````

#### ❌ CSE — CGPA too low (1.99, truncation floor rule)
````bash
# macOS / Linux
python3 audit_l3.py test_cgpa_truncation.csv CSE program.md

# Windows PowerShell
python audit_l3.py test_cgpa_truncation.csv CSE program.md
````

#### ⚠️ CSE — Illegal retake (retook a course with A on record)
````bash
# macOS / Linux
python3 audit_l3.py test_retake_worse.csv CSE program.md

# Windows PowerShell
python audit_l3.py test_retake_worse.csv CSE program.md
````

#### ⚠️ CSE — Lab co-registration violation (CSE225L without CSE225)
````bash
# macOS / Linux
python3 audit_l3.py test_lab_coreq.csv CSE program.md

# Windows PowerShell
python audit_l3.py test_lab_coreq.csv CSE program.md
````

#### ⚠️ CSE — Prerequisite violations
````bash
# macOS / Linux
python3 audit_l3.py test_prereqs.csv CSE program.md

# Windows PowerShell
python audit_l3.py test_prereqs.csv CSE program.md
````

#### ❌ CSE — Invalid course codes (courses not in any NSU program)
````bash
# macOS / Linux
python3 audit_l3.py test_invalid_courses.csv CSE program.md

# Windows PowerShell
python audit_l3.py test_invalid_courses.csv CSE program.md
````

#### ⚠️ BBA — Major declaration before 60 credits
````bash
# macOS / Linux
python3 audit_l3.py test_BBA_major_declaration.csv BBA program.md

# Windows PowerShell
python audit_l3.py test_BBA_major_declaration.csv BBA program.md
````

#### ℹ️ T-grade waiver example
````bash
# macOS / Linux
python3 audit_l3.py test_t_grade_waiver.csv CSE program.md

# Windows PowerShell
python audit_l3.py test_t_grade_waiver.csv CSE program.md
````

---

### Run All Tests

````bash
# macOS / Linux
python3 run_tests.py

# Windows PowerShell
$env:PYTHONIOENCODING = 'utf-8'
python run_tests.py
````


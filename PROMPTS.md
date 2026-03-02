# NSU Graduation Audit — AI Prompts & Development Log

> **CSE226 Project 1 — Vibecoding Demo**  
> This file documents every natural-language prompt used to build this project, along with the plan the AI produced for each one. Nothing in this codebase was written manually — all code, tests, and documentation were generated through AI-assisted development.

---

## 📐 Project Architecture (from the first session)

```
audit_l1.py   → Level 1: Credit Tally Engine
audit_l2.py   → Level 2: Semester-by-Semester CGPA Calculator
audit_l3.py   → Level 3: Full Graduation Audit & Deficiency Reporter
program.md    → Knowledge base (all NSU programs, credits, prerequisites)
style.py      → Shared terminal styling (Unicode + ANSI, cross-platform)
run_tests.py  → Automated test runner
```

---

## 🗂️ Session 1 — System Design & Initial Build
*(Conversation: "Graduation Audit System", Feb 15)*

### Prompt 1
> *"Build a graduation audit system for NSU. It needs three levels: a credit tally engine, a CGPA calculator with waiver handling, and a deficiency reporter. Process student transcripts against a program knowledge base. Must be precise, handle messy data, provide clear reports."*

**Plan produced:**
- Define transcript CSV format: `Course_Code, Credits, Grade, Semester`
- Level 1: read CSV, track best grade per course, sum valid credits, flag retakes/fails/withdrawals
- Level 2: group by semester, compute TGPA per semester, accumulate CGPA using truncation (floor, not rounding), flag probation when CGPA < 2.00
- Level 3: parse `program.md` for required courses by category (GED / Core Math / Core Science / Major Core / Core Business), check each against passed courses, report missing per category, check prereqs
- Create `style.py` for shared Unicode box-drawing + ANSI colour rendering that auto-detects terminal capability

---

## 🗂️ Session 2 — Program Refinement & Test Generation
*(Conversation: "Refining Graduation Audit", Feb 28 – Mar 1)*

### Prompt 2
> *"Remove approximated programs. Delete Architecture, BBT, Microbiology, Public Health, Pharmacy, Law, and MCJ from program.md, audit_l3.py, and generate_tests.py."*

**Plan produced:**
- Remove 7 program blocks from `program.md`
- Remove their keys from `program_map` in `audit_l3.py`
- Remove them from `generate_tests.py` program list
- Document them in `README.md` under Known Limitations with reason: "course list could not be verified from official NSU sources"
- Retain: CSE, ETE, ENV, ENG, BBA, ECO

### Prompt 3
> *"Regenerate 2000 test transcripts using only the 8 verified programs."*

**Plan produced:**
- Run `generate_tests.py` producing ~133 transcripts per program
- Scenarios per program: eligible (top/good/borderline), probation, retake (pass/fail), withdrawal, partial, near-graduation, missing GED/core

---

## 🗂️ Session 3 — Retake Logic, Lab Credits, Elective Cap
*(Current conversation)*

### Prompt 4
> *"Fix the bugs and then do a sanity check."*

**Plan produced:**
- Run `run_tests.py`, identify failures
- Fix any broken assertions from prior changes
- Confirm all tests pass with clean output

---

### Prompt 5
> *"Remove the 2000 test transcripts. Make actual edge cases — wrong courses, retakes that got worse grades, department switches, BBT courses in CSE. Check that best grade is always counted."*

**Plan produced:**
- Delete `test_transcripts/` directory and all `generate_tests.py` references
- Create hand-crafted edge case CSVs:
  - `test_retake_worse.csv` — CSE115 passed with A, then retaken getting C- and F; verifies best grade kept
  - `test_retake_chain.csv` — 3 attempts D→C→B; verifies each attempt builds correctly
  - `test_dept_switch_bba_to_cse.csv` — BBA courses (ACT201, MKT202, MGT210) in a CSE audit; verifies they are treated as valid free electives, not invalid
  - `test_bbt_in_cse.csv` — BBT/BIO-only courses in a CSE transcript; verifies they are flagged as invalid (not in any supported program)
- Add corresponding test cases to `run_tests.py`

---

### Prompt 6
> *"225L is non credit btw."*

**Plan produced:**
- Correct `CSE225L` from 1 credit → **0 credits** in `program.md`
- Propagate to all test CSVs that reference `CSE225L`

---

### Prompt 7
> *"Any CSE course lab after 215L is non credit."*

**Plan produced:**
- Set all 6 post-215L CSE labs to 0 credits in `program.md`:  
  `CSE225L(0)`, `CSE231L(0)`, `CSE311L(0)`, `CSE323L(0)`, `CSE327L(0)`, `CSE331L(0)`
- Note: `CSE332L` initially missed, caught in next prompt

---

### Prompt 8
> *"You missed 332L."*

**Plan produced:**
- Add `CSE332L` to the 0-credit list in `program.md`
- Verify `CSE332L` in all test CSVs is updated to 0 credits

---

### Prompt 9
> *"Can you check that all the non-credit labs are taken with their main course? And credit labs can be retaken with or without lab."*

**Plan produced:**
- Implement **co-registration check** in `audit_l3.py`:
  - For each 0-credit CSE lab (ending in `L`), verify the student took the corresponding lecture in the **same semester**
  - If lecture and lab are in different semesters → advisory fires (non-blocking)
  - Credit labs (CSE115L, CSE215L, PHY107L, etc.) are exempt — can be taken/retaken independently
- Create `test_lab_coreq.csv` and add 2 tests to `run_tests.py`

---

### Prompt 10
> *"No, this applies only for CSE labs. Other labs like PHY labs and CHE labs are completely different — when done for the first time it doesn't require to be taken together for any department."*

**Plan produced:**
- Add `course.startswith('CSE')` guard to the co-registration check
- PHY107L, PHY108L, CHE101L etc. are **never** subject to the co-registration rule
- Confirm with test: `test_lab_coreq.csv` includes PHY107L in wrong semester — must NOT fire advisory

---

### Prompt 11
> *"Can you look this up for EEE and CEE for non-credit labs?"*

**Plan produced:**
- Research EEE and CEE lab credit rules from NSU curriculum pages
- (Unable to conclusively verify — ambiguous results)

---

### Prompt 12
> *"Okay stop that. Remove EEE and CEE from the list."*

**Plan produced:**
- Remove EEE and CEE program blocks from `program.md`
- Remove from `program_map` in `audit_l3.py`
- Update `README.md`: remove from supported programs table, add to Known Limitations with note "Lab credit rules could not be fully verified"

---

### Prompt 13
> *"You can't retake if you have a B+ or higher in a course."*

**Plan produced:**
- Track `best_grade_points` per course across all three audit levels
- **L1 (`audit_l1.py`)**: If previous best ≥ 3.3 (B+), label current attempt `⚠ Illegal Retake` (red); otherwise `↩ Retake (Ignored)` (yellow)
- **L2 (`audit_l2.py`)**: Same label logic — computed **before** printing the row (bug fix: was printed after)
- **L3 (`audit_l3.py`)**: Fire advisory: `Illegal retake: CSE115 retaken in Summer 2024 while already holding A (B+ or higher cannot be retaken)` — non-blocking
- Add 4 retake tests to `run_tests.py` covering both illegal and legal retakes across all levels

---

### Prompt 14
> *"CSE115(3) + CSE115L(1) + CSE173(3) + CSE215(3) + CSE215L(1)..."*

**Plan produced:**
- Correct `CSE115` from 4 → **3 credits** and `CSE115L` from 0 → **1 credit** in `program.md`
- Correct `CSE215` from 4 → **3 credits** and `CSE215L` from 0 → **1 credit** in `program.md`
- Total per pair stays 4 credits (3+1 = 4), but split matters for GPA — labs are now GPA-bearing
- Propagate to all 15 CSV files in one automated Python pass

---

### Prompt 15
> *"Update the README with new tests. Test for graduation for each department. Check credit count. Make some edge cases where they've crossed their elective limit and have to declare allowed elective courses."*

**Plan produced:**

#### Elective cap system
- Add `parse_global_courses(md_file)` to `audit_l3.py` — scans all programs, builds a registry `{ course_code: credits }` of every NSU course
- Compute `elective_cap = total_credits_required − sum_of_all_required_course_credits` in `parse_program_knowledge()`
- Elective classification in `audit_student()`:
  - **Required**: course in the program's requirement lists → always counts
  - **Valid free elective**: course in global registry but not required → counts toward total, tracked separately
  - **Excess elective**: valid free elective credits exceed `elective_cap` → still counts (non-blocking), advisory fires
  - **Invalid elective**: course not in any NSU program whatsoever → excluded from credit total, listed as deficiency

| Program | Total | Fixed | Elective Cap |
|---------|-------|-------|-------------|
| CSE | 130 | 98 | 32 |
| ETE | 130 | 97 | 33 |
| ENV | 130 | 99 | 31 |
| ENG | 123 | 69 | 54 |
| BBA | 120 | 85 | 35 |
| ECO | 120 | 63 | 57 |

*ENG and ECO have large caps intentionally — they are humanities/social science degrees where students genuinely fill ~half their credits with electives.*

#### Graduation transcripts
- `test_grad_CSE.csv` — all required CSE courses (GED + Math + Science + Major Core) + 34 cr of free electives → 132 cr total, ELIGIBLE ✅
- `test_elective_overflow.csv` — same CSE required courses + 43 cr of free electives (cap = 32) → ELIGIBLE ✅ with elective overload advisory listing 4 excess courses

#### Tests added
| Test | Expected |
|---|---|
| CSE graduation — ELIGIBLE | ELIGIBLE FOR GRADUATION |
| CSE graduation — credit total | Credits Required : 130 |
| Elective overload — still ELIGIBLE | ELIGIBLE, "Elective overload" advisory |
| Elective overload — excess listed | "excess" appears in output |

#### dept-switch behaviour corrected
- BBA courses (ACT201, MGT210…) in a CSE transcript are now **valid free electives** (they are real NSU courses in global registry), not invalid. Test updated accordingly.

---

### Prompt 16
> *"You're saying some departments have over 30 credits for elective. Can you check the GED and school requirements — what are core courses and what aren't?"*

**Plan produced:**
- Dump every required course for every program with per-section credit sums
- Verify ENG (54 cap) and ECO (57 cap) are correct:
  - ENG GED: 15 cr, Math: 3 cr, Sci: 3 cr, Core: 48 cr → fixed = 69. Elective cap = 54 ✅ (by design)
  - ECO GED: 18 cr, Math: 9 cr, Sci: 3 cr, Core: 33 cr → fixed = 63. Elective cap = 57 ✅ (by design)
- No bugs — large caps are accurate for those programs

---

### Prompt 17
> *"Make a command list for PowerShell and a command list for Unix systems in the README. Also use a system that makes Unix output look good just like PowerShell — I'll demo on a Mac."*

**Plan produced:**
- Verify `style.py` cross-platform status:
  - Already auto-detects TTY (ANSI only when interactive)
  - Already auto-detects UTF-8 encoding (Unicode boxes or ASCII fallback)
  - `sys.stdout.reconfigure(encoding='utf-8')` only runs on Windows where needed
  - **macOS `python3` renders natively — zero changes needed ✅**
- Update README with dual command blocks for every demo scenario:
  - **macOS/Linux**: `python3 audit_l3.py ...`
  - **Windows PowerShell**: `$env:PYTHONIOENCODING = 'utf-8'` then `python audit_l3.py ...`
- Update test count in README from 14 → **27**
- Replace deleted `test_transcripts/` references with actual hand-crafted test files

---

## 📊 Final Test Suite — 27/27 ✅

| # | Test | Category |
|---|---|---|
| 1 | L1: Basic credit tally | Credit counting |
| 2 | L1: Sample transcript | Sanity |
| 3 | L1: A then C-/F → Illegal Retake label | Illegal retake |
| 4 | L1: D→C→B legal retakes, no Illegal Retake | Legal retake |
| 5 | L2: Illegal Retake label shown post-A attempt | Illegal retake |
| 6 | L2: D→C→B — no Illegal Retake label | Legal retake |
| 7 | L3: Illegal retake advisory fires | Illegal retake |
| 8 | L3: D→C→B — no illegal retake advisory | Legal retake |
| 9 | L3: BBA courses in CSE → valid free electives | Dept switch |
| 10 | L2: BBA courses in CSE → counted in CGPA | Dept switch |
| 11 | L3: BBT/BIO courses → invalid electives | Invalid courses |
| 12 | L1: BBT courses → counted in L1 (program-agnostic) | Credit counting |
| 13 | L2: T-grade → Waived, excluded from CGPA | T-grade waiver |
| 14 | L3: T-grade → satisfies requirement | T-grade waiver |
| 15 | L2: 1.994 → shows 1.99 (truncation, not rounding) | CGPA floor rule |
| 16 | L3: 1.992 student is NOT eligible | CGPA floor rule |
| 17 | L3: CSE225L without CSE225 → co-reg advisory | Lab co-registration |
| 18 | L3: PHY107L never triggers co-reg check | Lab co-registration |
| 19 | L3: Prereq violations flagged | Prerequisites |
| 20 | L3: Invalid course codes flagged | Invalid courses |
| 21 | L3: BBA basic audit | BBA audit |
| 22 | L3: BBA major declaration before 60 cr → advisory | BBA major decl. |
| 23 | L3: Sample transcript runs without error | Sanity |
| 24 | L3: CSE graduation — ELIGIBLE | Graduation |
| 25 | L3: CSE graduation — 130 cr total | Graduation |
| 26 | L3: Elective overload — ELIGIBLE + advisory | Elective cap |
| 27 | L3: Elective overload — excess courses listed | Elective cap |

---

## 🧠 Key Design Decisions Made Through Prompting

| Decision | Reason |
|---|---|
| CGPA uses **floor truncation**, not rounding | NSU policy — 1.996 shows as 1.99, never 2.00 |
| 0-credit CSE labs must be co-registered | Labs are graded together with lecture at NSU |
| Non-CSE labs (PHY, CHE, BIO) are exempt | Other-department labs are standalone courses |
| B+ or higher → illegal retake | NSU policy — no retaking a well-passed course |
| `style.py` auto-detects Unicode + TTY | Works on Windows PowerShell, macOS Terminal, piped output |
| Global course registry for elective validation | Distinguishes "wrong NSU course" from "not an NSU course at all" |
| Elective cap is **advisory-only** | You can't take a fraction of a course; ALL valid electives count toward credits |
| ENG/ECO have 54/57 cr elective caps | Humanities programs are genuinely elective-heavy by design |
| EEE and CEE removed from supported programs | Lab credit rules could not be authoritatively verified |

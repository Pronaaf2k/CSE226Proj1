# Project 1 Requirement Checklist
**CSE226.1 — Spring 2026 | Dr. Nabeel Mohammed**

> ✅ Done &nbsp;|&nbsp; ⚠️ Partial / needs attention &nbsp;|&nbsp; ❌ Missing

---

## Level 1 — The Credit Tally Engine (10 marks)

| # | Requirement | Status | Notes |
|---|---|---|---|
| 1.1 | Read transcript CSV and calculate total valid credits | ✅ | `audit_l1.py` |
| 1.2 | Decide which grades count — handle `F`, `W`, `I` distinctly | ✅ | Each is labelled separately: `Failed`, `Withdrawn`, `Incomplete` |
| 1.3 | Handle 0-credit lab courses (they are counted but add 0 credits) | ✅ | Courses with `Credits = 0` are marked `Counted` but don't change the total |
| 1.4 | Retake deduplication — a course passed twice is only counted once | ✅ | Second passing copy is labelled `Retake (Ignored)` |
| 1.5 | Provide `test_L1.csv` proving correct identification of valid credits | ✅ | `test_L1.csv` includes: pass, 0-credit pass, `F` → retake pass, `W` → retake pass |

---

## Level 2 — The Logic Gate & Waiver Handler (10 marks)

| # | Requirement | Status | Notes |
|---|---|---|---|
| 2.1 | Calculate weighted CGPA using the NSU grade-point scale | ✅ | All 11 letter grades mapped exactly per NSU policy |
| 2.2 | Semester-by-semester TGPA (term GPA) display | ✅ | Each semester block shows its own TGPA |
| 2.3 | Cumulative CGPA shown after each semester | ✅ | Updated after every semester using best-grade history |
| 2.4 | Interactive waiver prompt — "Waivers granted for ENG102 or BUS112?" | ✅ | Prompts at runtime; also accepts `--waivers` flag for non-interactive |
| 2.5 | Waivers excluded from CGPA calculation | ✅ | Waived courses are skipped entirely |
| 2.6 | `W` and `I` entries do not break CGPA calculation | ✅ | Excluded from GPA math; labelled `Withdrawn` / `Incomplete` |
| 2.7 | Probation flag when CGPA < 2.0 | ✅ | Shows `*** ACADEMIC PROBATION (consecutive semesters below 2.00 : N) ***` |
| 2.8 | Probation counter resets when CGPA recovers to ≥ 2.00 | ✅ | Counter resets to 0 as soon as CGPA returns to 2.00+ |
| 2.9 | Retake policy: best grade used for CGPA, not latest | ✅ | `course_history` keeps highest-points entry only |
| 2.10 | Provide `test_L2.csv` that tests the math and edge cases | ✅ | Tests: 0-credit `P` grade, `F` → better retake, `W` → retake, double-`W`, trailing `F` |

---

## Level 3 — The Audit & Deficiency Reporter (10 marks)

| # | Requirement | Status | Notes |
|---|---|---|---|
| 3.1 | Compare transcript against `program.md` rules | ✅ | `audit_l3.py` parses the knowledge base per program |
| 3.2 | Identify missing mandatory courses by category | ✅ | Reports missing GED / Math / Core / Science / Business courses |
| 3.3 | Flag Probation status (CGPA < 2.0) | ✅ | Shown in `[Deficiency Details]` section |
| 3.4 | Clear graduation verdict | ✅ | Prints `ELIGIBLE FOR GRADUATION` or `NOT ELIGIBLE FOR GRADUATION` |
| 3.5 | Credit deficiency reported (how many more credits needed) | ✅ | `(!) Credit Deficiency: Need N more credits.` |
| 3.6 | Invalid electives flagged and their credits excluded | ✅ | Listed under `(!) Invalid Electives Taken` |
| 3.7 | Course equivalency handling (e.g. `MAT112` ↔ `BUS112`) | ✅ | Satisfied via `equivalent_courses` dict |
| 3.8 | Retake scenario handled accurately | ✅ | Best-grade logic in `audit_student()` |
| 3.9 | Provide a **retake scenario** test file for L3 | ✅ | `test_L3_retake.csv` — `CSE225` and `PHI101` both fail then retake-pass; neither appears in missing list |
| 3.10 | Support multiple programs (`CSE`, `BBA`) | ✅ | `program_map` aliases short names to full headers in `program.md` |
| 3.11 | Provide `test_L3.csv` and `test_BBA.csv` | ✅ | Both present and cleaned up |

---

## Deliverables

| # | Deliverable | Status | Notes |
|---|---|---|---|
| D1 | One CLI script per level | ✅ | `audit_l1.py`, `audit_l2.py`, `audit_l3.py` |
| D2 | Uniform CLI signature: `script transcript.csv program_name program.md` | ✅ | All three accept the same positional args |
| D3 | Optimized `transcript.csv` | ✅ | Sample transcript with retakes, W, F, 0-credit labs |
| D4 | `program.md` knowledge base with real NSU requirements | ✅ | 8 verified programs: CSE (130 cr), EEE (130 cr), ETE (130 cr), CEE (149 cr), ENV (130 cr), ENG (123 cr), BBA (120 cr), ECO (120 cr) |
| D5 | Custom test cases for each level | ✅ | `test_L1.csv`, `test_L2.csv`, `test_L3.csv`, `test_BBA.csv` |

---


## Summary

| Level | Marks Available | Coverage |
|---|---|---|
| Level 1 | 10 | ✅ Fully covered |
| Level 2 | 10 | ✅ Fully covered + bonus (per-semester TGPA & probation tracking) |
| Level 3 | 10 | ✅ Fully covered — retake file `test_L3_retake.csv` added |
| **Total** | **30** | **30/30 — all requirements met** |

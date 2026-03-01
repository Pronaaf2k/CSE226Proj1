# NSU Graduation Audit System — Feature List

A 3-level CLI tool that processes a student transcript (CSV) against NSU program
requirements and produces audit reports at increasing depth.

---

## Shared Behaviour (All Levels)

| Feature | Detail |
|---|---|
| **NSU Grading Scale** | Supports all 11 letter grades: `A`, `A-`, `B+`, `B`, `B-`, `C+`, `C`, `C-`, `D+`, `D`, `F` with their exact grade-point values per NSU policy |
| **Non-GPA grade handling** | `W` (Withdrawn) and `I` (Incomplete) are recognized and excluded from GPA calculation; `F` is included with 0.0 points |
| **Best-grade retake policy** | When a course appears more than once, the attempt with the **highest grade points** is used for CGPA — not the latest attempt — matching NSU's official retake policy |
| **Uniform CLI signature** | All three scripts accept the same positional arguments: `transcript` → `program_name` → `program_knowledge`, making them drop-in compatible |
| **Whitespace-tolerant CSV parsing** | Header names and field values are stripped of leading/trailing whitespace before processing |

---

## Level 1 — Credit Tally Engine (`audit_l1.py`)

Answers: *"How many valid credits has this student earned?"*

| Feature | Detail |
|---|---|
| **Credit counting** | Sums credits for every course the student passed; each unique course is counted only once regardless of how many times it appears |
| **Retake deduplication** | If a student passed a course on a later attempt, only one passing instance is counted; earlier passing copies are marked `Retake (Ignored)` |
| **Distinct status labels** | Each row is tagged with one of: `Counted`, `Retake (Ignored)`, `Failed`, `Withdrawn`, or `Incomplete` — distinguishing all three non-passing grade types separately |
| **Tabular output** | Prints a per-course table (`Course | Credits | Grade | Status`) followed by a total |

---

## Level 2 — Semester-by-Semester CGPA Calculator (`audit_l2.py`)

Answers: *"What is the student's CGPA, and how did it evolve each semester?"*

| Feature | Detail |
|---|---|
| **Semester grouping** | Courses are grouped by their `Semester` column and displayed in chronological order (`Spring → Summer → Fall`, earliest year first) |
| **TGPA (Term GPA)** | Calculated for each semester using only that semester's own grades; `W`, `I`, and pass/fail (`P`) courses are excluded from the calculation |
| **Cumulative CGPA** | Recalculated after every semester using the running best-grade history; reflects how the student's overall standing changes over time |
| **Academic probation tracking** | A consecutive-semester counter increments whenever the CGPA falls below **2.00** at the end of a semester |
| **Probation counter reset** | The counter resets to **0** the moment CGPA returns to 2.00 or above, as per NSU policy |
| **Probation display** | Semesters on probation show `*** ACADEMIC PROBATION (consecutive semesters below 2.00 : N) ***`; passing semesters show `Status : Good Standing` |
| **Course waivers** | Courses can be excluded from all GPA calculations via `--waivers CSE115,MAT116` or interactively at runtime |
| **Final summary** | Prints final CGPA, total GPA-weighted credits, and overall standing at the end of the report |

---

## Level 3 — Graduation Audit & Deficiency Reporter (`audit_l3.py`)

Answers: *"Is this student eligible to graduate, and what's missing?"*

| Feature | Detail |
|---|---|
| **Program parsing** | Reads `program.md` to extract all requirements for the requested program (supports `CSE` / `Computer Science & Engineering` and `BBA` / `Business Administration`) |
| **Multi-category requirement checking** | Checks courses against five requirement buckets: Mandatory GED, Core Math, Major Core, Core Science, Core Business |
| **Credit equivalency** | `MAT112` ↔ `BUS112` are treated as equivalent; passing either satisfies the other's requirement |
| **Earned credit tally** | Only credits from required courses and approved electives are counted toward the graduation total |
| **Invalid elective detection** | Courses that are neither required nor approved electives are flagged and their credits excluded |
| **CGPA eligibility check** | Flags probation (`CGPA < 2.00`) as a barrier to graduation |
| **Credit deficiency reporting** | Reports exactly how many more credits are needed if the student is short |
| **Missing course reporting** | Lists every missing course by category (GED / Math / Major Core / Science / Business) |
| **Graduation verdict** | Prints a clear `ELIGIBLE FOR GRADUATION` or `NOT ELIGIBLE FOR GRADUATION` status at the top of the report |
| **Program name aliases** | Accepts short names (`CSE`, `BBA`) and maps them to the full program header in `program.md` |

---

## Data Formats

### Transcript CSV
```
Course_Code, Credits, Grade, Semester
ENG102, 3, A, Spring 2023
CSE115, 4, F, Spring 2023
CSE115, 4, A-, Summer 2023
CSE173, 3, W, Fall 2023
```
- `Semester` format: `<Season> <Year>` — e.g. `Spring 2023`, `Summer 2024`, `Fall 2024`
- Valid seasons for sorting: `Spring`, `Summer`, `Fall`

### Program Knowledge Base (`program.md`)
```markdown
## [Program: Computer Science & Engineering]
- **Total Credits Required**: 130
- **Minimum CGPA**: 2.0
- **Mandatory GED**:
  - ENG102: Introduction to Composition (3 credits)
- **Core Math**:
  - MAT120: Calculus I (3 credits)
...
```

---

## Grading Reference

| Numerical Score | Letter Grade | Grade Points |
|---|---|---|
| 93 and above | A | 4.0 |
| 90 – 92 | A- | 3.7 |
| 87 – 89 | B+ | 3.3 |
| 83 – 86 | B | 3.0 |
| 80 – 82 | B- | 2.7 |
| 77 – 79 | C+ | 2.3 |
| 73 – 76 | C | 2.0 |
| 70 – 72 | C- | 1.7 |
| 67 – 69 | D+ | 1.3 |
| 60 – 66 | D | 1.0 |
| Below 60 | F | 0.0 |
| — | I (Incomplete) | Not counted in GPA |
| — | W (Withdrawal) | Not counted in GPA |

---

## GPA – Class Equivalence

| CGPA Range | Class |
|---|---|
| 3.00 and above | First Class |
| 2.50 – 2.99 | Second Class |
| 2.00 – 2.49 | Third Class |
| Below 2.00 | Academic Probation |

# CSE226 Project 1 — NSU Graduation Audit System

A 3-level CLI audit engine that processes student transcripts against NSU program
requirements to determine graduation eligibility, calculate CGPA, and identify deficiencies.

---

## Usage

```bash
# Level 1 — Credit Tally
python audit_l1.py transcript.csv

# Level 2 — Semester-by-Semester CGPA (interactive waiver prompt)
python audit_l2.py transcript.csv
python audit_l2.py transcript.csv --waivers ENG102,BUS112

# Level 3 — Full Graduation Audit
python audit_l3.py transcript.csv <PROGRAM> program.md
```

**Program aliases** (use the short code as `<PROGRAM>`):

| Alias | Program |
|---|---|
| `CSE` | Computer Science & Engineering |
| `EEE` | Electrical & Electronic Engineering |
| `ETE` | Electronic & Telecom Engineering |
| `CEE` | Civil & Environmental Engineering |
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

## Generating Test Transcripts

```bash
python generate_tests.py
```
Creates **2000 CSV transcripts** in `test_transcripts/` — ~133 per program,
covering 14 scenarios: eligible, probation, retakes, withdrawals, missing GED,
missing core, partial completion, near-graduation, and more.

---

## Files

| File | Purpose |
|---|---|
| `audit_l1.py` | Level 1 — Credit Tally Engine |
| `audit_l2.py` | Level 2 — Semester CGPA & Probation Tracker |
| `audit_l3.py` | Level 3 — Graduation Audit & Deficiency Reporter |
| `program.md` | Knowledge base — all 15 NSU programs |
| `generate_tests.py` | Test transcript generator (2000 cases) |
| `transcript.csv` | Sample student transcript |
| `test_L1.csv` | Edge-case test for Level 1 |
| `test_L2.csv` | Edge-case test for Level 2 |
| `test_L3.csv` | Edge-case test for Level 3 |
| `test_BBA.csv` | BBA-specific test |
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

The following programs are **well-sourced** from official NSU pages and academic documents:

| Program | Alias | Source quality |
|---|---|---|
| Computer Science & Engineering | `CSE` | ✅ Official curriculum |
| Electrical & Electronic Engineering | `EEE` | ✅ Official curriculum |
| Electronic & Telecom Engineering | `ETE` | ✅ Official curriculum |
| Civil & Environmental Engineering | `CEE` | ✅ Official curriculum |
| Environmental Science & Management | `ENV` | ✅ Official curriculum |
| English | `ENG` | ✅ Official curriculum |
| Business Administration | `BBA` | ✅ Official curriculum |
| Economics | `ECO` | ✅ Official curriculum |

---

## 🎓 Demo Commands

> Copy-paste commands for every supported department and every transcript scenario.
> All transcript files are in `test_transcripts/`.

### Level 1 — Credit Tally  *(works with any CSV)*

```bash
python audit_l1.py test_transcripts/transcript_CSE_0001_eligible_top.csv
python audit_l1.py test_transcripts/transcript_BBA_1502_missing_ged.csv
python audit_l1.py test_L1.csv
```

---

### Level 2 — Semester CGPA  *(works with any CSV)*

```bash
# Good standing student
python audit_l2.py test_transcripts/transcript_CSE_0001_eligible_top.csv --waivers=

# Probation student
python audit_l2.py test_transcripts/transcript_CSE_0009_probation.csv --waivers=

# With waiver
python audit_l2.py test_L2.csv --waivers=ENG102,MAT116
```

---

### Level 3 — Full Graduation Audit

> Format: `python audit_l3.py <transcript> <DEPT> program.md`

#### 🖥️ Computer Science & Engineering — `CSE`

```bash
# Top student (eligible)
python audit_l3.py test_transcripts/transcript_CSE_0001_eligible_top.csv CSE program.md

# Good student (eligible)
python audit_l3.py test_transcripts/transcript_CSE_0002_eligible_goo.csv CSE program.md

# Borderline CGPA
python audit_l3.py test_transcripts/transcript_CSE_0003_eligible_bor.csv CSE program.md

# Missing GED courses
python audit_l3.py test_transcripts/transcript_CSE_0004_missing_ged.csv CSE program.md

# Missing core courses
python audit_l3.py test_transcripts/transcript_CSE_0005_missing_core.csv CSE program.md

# Retake — passed on second attempt
python audit_l3.py test_transcripts/transcript_CSE_0006_retake_pass.csv CSE program.md

# Retake — still failing
python audit_l3.py test_transcripts/transcript_CSE_0007_retake_fail.csv CSE program.md

# Heavy withdrawals
python audit_l3.py test_transcripts/transcript_CSE_0008_withdrawal_h.csv CSE program.md

# Academic probation
python audit_l3.py test_transcripts/transcript_CSE_0009_probation.csv CSE program.md

# Probation recovery
python audit_l3.py test_transcripts/transcript_CSE_0010_probation_re.csv CSE program.md

# Partial completion (2-3 semesters)
python audit_l3.py test_transcripts/transcript_CSE_0011_partial.csv CSE program.md

# Near graduation (1-2 courses missing)
python audit_l3.py test_transcripts/transcript_CSE_0012_near_grad.csv CSE program.md
```

#### ⚡ Electrical & Electronic Engineering — `EEE`

```bash
python audit_l3.py test_transcripts/transcript_EEE_0253_eligible_top.csv EEE program.md
python audit_l3.py test_transcripts/transcript_EEE_0256_missing_ged.csv EEE program.md
python audit_l3.py test_transcripts/transcript_EEE_0257_missing_core.csv EEE program.md
python audit_l3.py test_transcripts/transcript_EEE_0258_retake_pass.csv EEE program.md
python audit_l3.py test_transcripts/transcript_EEE_0259_retake_fail.csv EEE program.md
python audit_l3.py test_transcripts/transcript_EEE_0261_probation.csv EEE program.md
python audit_l3.py test_transcripts/transcript_EEE_0264_near_grad.csv EEE program.md
```

#### 📡 Electronic & Telecom Engineering — `ETE`

```bash
python audit_l3.py test_transcripts/transcript_ETE_0505_eligible_top.csv ETE program.md
python audit_l3.py test_transcripts/transcript_ETE_0508_missing_ged.csv ETE program.md
python audit_l3.py test_transcripts/transcript_ETE_0509_missing_core.csv ETE program.md
python audit_l3.py test_transcripts/transcript_ETE_0510_retake_pass.csv ETE program.md
python audit_l3.py test_transcripts/transcript_ETE_0513_probation.csv ETE program.md
python audit_l3.py test_transcripts/transcript_ETE_0502_near_grad.csv ETE program.md
```

#### 🏗️ Civil & Environmental Engineering — `CEE`

```bash
python audit_l3.py test_transcripts/transcript_CEE_0753_eligible_top.csv CEE program.md
python audit_l3.py test_transcripts/transcript_CEE_0756_missing_ged.csv CEE program.md
python audit_l3.py test_transcripts/transcript_CEE_0757_missing_core.csv CEE program.md
python audit_l3.py test_transcripts/transcript_CEE_0758_retake_pass.csv CEE program.md
python audit_l3.py test_transcripts/transcript_CEE_0761_probation.csv CEE program.md
python audit_l3.py test_transcripts/transcript_CEE_0764_near_grad.csv CEE program.md
```

#### 🌿 Environmental Science & Management — `ENV`

```bash
python audit_l3.py test_transcripts/transcript_ENV_1009_eligible_top.csv ENV program.md
python audit_l3.py test_transcripts/transcript_ENV_1012_missing_ged.csv ENV program.md
python audit_l3.py test_transcripts/transcript_ENV_1013_missing_core.csv ENV program.md
python audit_l3.py test_transcripts/transcript_ENV_1001_retake_fail.csv ENV program.md
python audit_l3.py test_transcripts/transcript_ENV_1014_retake_pass.csv ENV program.md
python audit_l3.py test_transcripts/transcript_ENV_1003_probation.csv ENV program.md
python audit_l3.py test_transcripts/transcript_ENV_1006_near_grad.csv ENV program.md
```

#### 📖 English — `ENG`

```bash
python audit_l3.py test_transcripts/transcript_ENG_1261_eligible_top.csv ENG program.md
python audit_l3.py test_transcripts/transcript_ENG_1264_missing_ged.csv ENG program.md
python audit_l3.py test_transcripts/transcript_ENG_1251_missing_core.csv ENG program.md
python audit_l3.py test_transcripts/transcript_ENG_1252_retake_pass.csv ENG program.md
python audit_l3.py test_transcripts/transcript_ENG_1255_probation.csv ENG program.md
python audit_l3.py test_transcripts/transcript_ENG_1258_near_grad.csv ENG program.md
```

#### 💼 Business Administration — `BBA`

```bash
python audit_l3.py test_transcripts/transcript_BBA_1501_eligible_bor.csv BBA program.md
python audit_l3.py test_transcripts/transcript_BBA_1502_missing_ged.csv BBA program.md
python audit_l3.py test_transcripts/transcript_BBA_1503_missing_core.csv BBA program.md
python audit_l3.py test_transcripts/transcript_BBA_1504_retake_pass.csv BBA program.md
python audit_l3.py test_transcripts/transcript_BBA_1507_probation.csv BBA program.md
python audit_l3.py test_transcripts/transcript_BBA_1510_near_grad.csv BBA program.md
python audit_l3.py test_transcripts/transcript_BBA_1737_eligible_top.csv BBA program.md
```

#### 📊 Economics — `ECO`

```bash
python audit_l3.py test_transcripts/transcript_ECO_1751_eligible_top.csv ECO program.md
python audit_l3.py test_transcripts/transcript_ECO_1754_missing_ged.csv ECO program.md
python audit_l3.py test_transcripts/transcript_ECO_1755_missing_core.csv ECO program.md
python audit_l3.py test_transcripts/transcript_ECO_1756_retake_pass.csv ECO program.md
python audit_l3.py test_transcripts/transcript_ECO_1759_probation.csv ECO program.md
python audit_l3.py test_transcripts/transcript_ECO_1762_near_grad.csv ECO program.md
```

#### ✨ Special-Purpose Test Files (hand-crafted)

```bash
# Hand-crafted L3 retake demo (CSE225 + PHI101 fail then pass)
python audit_l3.py test_L3_retake.csv CSE program.md

# BBA-specific edge cases
python audit_l3.py test_BBA.csv BBA program.md

# L1 edge cases (F, W, I, 0-credit, retake)
python audit_l1.py test_L1.csv

# L2 edge cases with waiver
python audit_l2.py test_L2.csv --waivers=ENG102

# Known sample transcript
python audit_l3.py transcript.csv CSE program.md
```

---


# CSE226 Project 1 - Graduation Audit System

This project implements a 3-level graduation audit system for NSU, capable of processing student transcripts against program requirements.

## Files
- **Scripts**:
  - `audit_l1.py`: Level 1 - Credit Tally Engine
  - `audit_l2.py`: Level 2 - Logic Gate & Waiver Handler
  - `audit_l3.py`: Level 3 - Audit & Deficiency Reporter
- **Data**:
  - `transcript.csv`: Sample student transcript
  - `program.md`: Knowledge base containing degree requirements for CSE and BBA
- **Test Data**:
  - `test_L1.csv`, `test_L2.csv`, `test_L3.csv`: Edge case test scenarios

## Usage Instructions

### Level 1: Check Total Credits
```bash
python audit_l1.py transcript.csv
```
_Counts valid earned credits, ignoring F/W grades and duplicate passes._

### Level 2: Check CGPA (Interactive)
```bash
python audit_l2.py transcript.csv
```
_Calculates CGPA based on NSU grading scale with optional waivers._

### Level 3: Full Graduation Audit
```bash
python audit_l3.py transcript.csv "Computer Science & Engineering" program.md
```
_Performs a complete audit against the requirements. Reports detailed deficiencies._

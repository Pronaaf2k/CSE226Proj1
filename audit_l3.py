#!/usr/bin/env python3
import csv
import sys
import re
import argparse
from style import (
    GR, RD, YL, CY, BL, DM, RS,
    H, V, TL, TR, BL2, BR, ML, MR,
    DH, DV, DTL, DTR, DBL, DBR, DML, DMR,
    CHK, XMK, WRN, BULL, SLP
)

# ── NSU Grading Scale ──────────────────────────────────────────────────────────
GRADE_POINTS = {
    'A': 4.0, 'A-': 3.7, 'B+': 3.3, 'B': 3.0, 'B-': 2.7,
    'C+': 2.3, 'C': 2.0, 'C-': 1.7, 'D+': 1.3, 'D': 1.0, 'F': 0.0
}

def is_passing(grade):
    return grade.upper() not in ['F', 'W', 'I', 'X']

# --- Level 3 Specific Logic ---

def parse_program_knowledge(md_file, program_name):
    """
    Parses the program.md file to extract requirements for the specified program.
    Returns a dict with:
    - total_credits_required
    - min_cgpa
    - mandatory_ged
    - core_math
    - major_core
    etc.
    """
    requirements = {
        'total_credits_required': 0,
        'min_cgpa': 2.0,
        'mandatory_ged': [],
        'core_math': [],
        'major_core': [],
        'core_business': [], # For BBA
        'core_science': []
    }
    
    current_section = None
    target_program_found = False
    
    try:
        with open(md_file, 'r') as f:
            lines = f.readlines()
            
        for line in lines:
            line = line.strip()
            # Detect Program Section
            program_match = re.match(r'^## \[Program: (.*)\]', line)
            if program_match:
                if program_match.group(1).strip() == program_name:
                    target_program_found = True
                    current_section = 'PROGRAM_HEADER'
                else:
                    target_program_found = False
                    current_section = None
                continue
                
            if not target_program_found:
                continue

            # Parse Requirements within the section
            if line.startswith('- **Total Credits Required**:'):
                requirements['total_credits_required'] = int(re.search(r'\d+', line).group())
            elif line.startswith('- **Minimum CGPA**:'):
                # Optional implementation detail
                pass
            elif line.startswith('- **Mandatory GED**:'):
                current_section = 'GED'
            elif line.startswith('- **Core Math**:'):
                current_section = 'MATH'
            elif line.startswith('- **Major Core**:'):
                current_section = 'CORE'
            elif line.startswith('- **Core Business**:'):
                current_section = 'BUSINESS'
            elif line.startswith('- **Core Science**:'):
                current_section = 'SCIENCE'
            
            # Parse List Items (Courses)
            # Lines look like: "  - ENG102: ..." or just "- ENG102..." if simplistic
            # Using regex to capture Course Code at start of bullet
            course_match = re.search(r'^\s*-\s*([A-Z]{3}\d{3}[L]?)', line)
            if course_match:
                course_code = course_match.group(1)
                if current_section == 'GED':
                    requirements['mandatory_ged'].append(course_code)
                elif current_section == 'MATH':
                    requirements['core_math'].append(course_code)
                elif current_section == 'CORE':
                    requirements['major_core'].append(course_code)
                elif current_section == 'BUSINESS':
                    requirements['core_business'].append(course_code)
                elif current_section == 'SCIENCE':
                    requirements['core_science'].append(course_code)

    except FileNotFoundError:
        print(f"Error: Program file '{md_file}' not found.")
        sys.exit(1)
        
    return requirements

def audit_student(transcript_file, requirements):
    # 1. Tally Credits & Calculate CGPA (Level 1 & 2 Logic)
    earned_credits = 0.0
    passed_courses = set()
    course_history = {} # For CGPA (latest attempt)
    
    try:
        with open(transcript_file, 'r') as f:
            reader = csv.DictReader(f)
            reader.fieldnames = [name.strip() for name in reader.fieldnames]
            
            for row in reader:
                course = row['Course_Code'].strip()
                grade = row['Grade'].strip()
                try:
                    credits = float(row['Credits'])
                except: credits = 0.0
                
                # Logic for Credits (Level 1): valid if passing
                # (Simplification: Count if passing and not already counted? 
                # Actually, usually retakes replace logic implies we just take the set of unique passed courses)
                if is_passing(grade):
                    passed_courses.add(course)
                
                # Logic for CGPA (Level 2): Latest attempt
                # Assuming transcript is chronological or we process all and keep last?
                # We'll just overwrite
                if GRADE_POINTS.get(grade) is not None:
                    points = GRADE_POINTS[grade]
                    # NSU Policy: "only the best grade will be used to calculate the CGPA"
                    # Keep whichever attempt has the higher grade points.
                    existing = course_history.get(course)
                    if existing is None or points > existing['points']:
                        course_history[course] = {'grade': grade, 'credits': credits, 'points': points}

    except FileNotFoundError:
        print(f"Error: Transcript '{transcript_file}' not found.")
        sys.exit(1)

    # Calculate Totals
    # Re-sum credits from passed set to be sure (need credit values for passed courses)
    # We need a map of Course -> Credits to sum accurately for passed courses
    # We can infer credits from the course_history (latest) if passed
    
    # Calculate CGPA
    gpa_points = 0.0
    gpa_credits = 0.0
    for data in course_history.values():
        if data['credits'] > 0: # Only count if > 0 credits
            gpa_points += data['points'] * data['credits']
            gpa_credits += data['credits']
            
    cgpa = gpa_points / gpa_credits if gpa_credits > 0 else 0.0
    
    # 2. Check Requirements (Level 3 Logic)
    missing = {
        'GED': [],
        'Math': [],
        'Core': [],
        'Science': [],
        'Business': []
    }
    
    equivalent_courses = {'MAT112': 'BUS112', 'BUS112': 'MAT112'}
    valid_electives = {'ENG102', 'MAT112', 'BUS112'}
    
    expanded_passed_courses = set(passed_courses)
    for c in passed_courses:
        if c in equivalent_courses:
            expanded_passed_courses.add(equivalent_courses[c])
            
    for req in requirements['mandatory_ged']:
        if req not in expanded_passed_courses: missing['GED'].append(req)
        
    for req in requirements['core_math']:
        if req not in expanded_passed_courses: missing['Math'].append(req)

    for req in requirements['major_core']:
        if req not in expanded_passed_courses: missing['Core'].append(req)
        
    for req in requirements['core_science']:
        if req not in expanded_passed_courses: missing['Science'].append(req)
        
    for req in requirements['core_business']:
        if req not in expanded_passed_courses: missing['Business'].append(req)

    all_reqs = set(
        requirements['mandatory_ged'] +
        requirements['core_math'] +
        requirements['major_core'] +
        requirements['core_business'] +
        requirements['core_science']
    )

    invalid_electives = []
    total_earned_credits = 0.0
    
    for course in passed_courses:
        is_required = course in all_reqs or (course in equivalent_courses and equivalent_courses[course] in all_reqs)
        is_valid_elective = course in valid_electives or (course in equivalent_courses and equivalent_courses[course] in valid_electives)
        
        curr = course_history.get(course)
        if curr:
            if is_required or is_valid_elective:
                total_earned_credits += curr['credits']
            else:
                invalid_electives.append(course)

    return {
        'total_earned': total_earned_credits,
        'cgpa': cgpa,
        'missing': missing,
        'invalid_electives': invalid_electives,
        'passed_courses': passed_courses
    }

def print_report(audit, requirements, program_name):
    W   = 64   # inner width
    req = requirements['total_credits_required']
    min_cgpa   = requirements['min_cgpa']
    earned     = audit['total_earned']
    cgpa       = audit['cgpa']
    cgpa_ok    = cgpa >= min_cgpa
    credits_ok = earned >= req
    has_missing = any(len(m) > 0 for m in audit['missing'].values())
    has_invalid = len(audit['invalid_electives']) > 0
    is_eligible = cgpa_ok and credits_ok and not has_missing and not has_invalid

    def cc(val, threshold): return GR if val >= threshold else RD

    # ── Header panel ──────────────────────────────────────────────────────────
    print()
    print(f'╔{"═" * W}╗')
    label = 'GRADUATION AUDIT REPORT'
    print(f'║  {BL}{CY}{label}{RS}{" " * (W - len(label) - 2)}║')
    prog_line = f'Program  :  {program_name}'
    print(f'║  {DM}{prog_line}{RS}{" " * max(0, W - len(prog_line) - 2)}║')
    print(f'╠{"═" * W}╣')

    # ── Metrics grid ──────────────────────────────────────────────────────────
    cred_c = cc(earned, req)
    cgpa_c = cc(cgpa, min_cgpa)
    cr_str = f'{cred_c}{BL}{earned:.1f}{RS}'
    cg_str = f'{cgpa_c}{BL}{cgpa:.2f}{RS}'
    print(f'║  Credits Required : {BL}{req:<8}{RS}  │  Credits Earned : {cr_str}{" " * max(0, 14 - len(f"{earned:.1f}"))}║')
    print(f'║  Min CGPA         : {BL}{min_cgpa:<8}{RS}  │  CGPA Earned    : {cg_str}{" " * max(0, 14 - len(f"{cgpa:.2f}"))}║')
    print(f'╠{"═" * W}╣')

    # ── Verdict ───────────────────────────────────────────────────────────────
    if is_eligible:
        verdict = '✓   ELIGIBLE FOR GRADUATION'
        vc = GR
    else:
        verdict = '✗   NOT ELIGIBLE FOR GRADUATION'
        vc = RD
    pad = W - len(verdict) - 2
    print(f'║  {vc}{BL}{verdict}{RS}{" " * max(0,pad)}║')
    print(f'╚{"═" * W}╝')

    if is_eligible:
        print()
        return

    # ── Deficiency section ────────────────────────────────────────────────────
    print(f'\n  {BL}DEFICIENCY REPORT{RS}')
    print(f'  {"─" * (W - 2)}')

    if not cgpa_ok:
        msg = f'CGPA {cgpa:.2f} is below the required minimum of {min_cgpa:.2f}'
        print(f'  {RD}⚠  Probation :{RS}  {msg}')

    if not credits_ok:
        gap = req - earned
        print(f'  {YL}⚠  Credits   :{RS}  Need {BL}{gap:.1f}{RS} more credits to reach {req}')

    if has_invalid:
        print(f'\n  {YL}⊘  Invalid Electives (credits excluded):{RS}')
        for course in audit['invalid_electives']:
            print(f'       •  {course}')

    categories_map = {
        'GED':      'General Education',
        'Math':     'Core Mathematics',
        'Core':     'Major Core',
        'Science':  'Core Science',
        'Business': 'Core Business',
    }
    missing_count = 0
    for cat_key, cat_name in categories_map.items():
        missing_list = audit['missing'].get(cat_key, [])
        if missing_list:
            n = len(missing_list)
            print(f'\n  {RD}✗  Missing {cat_name}{RS}  ({n} course{"s" if n>1 else ""})')
            for course in missing_list:
                print(f'       •  {course}')
            missing_count += n

    if missing_count == 0 and not has_invalid:
        print(f'\n  {GR}✓  All subject requirements satisfied.{RS}')

    print(f'\n  {"─" * (W - 2)}')
    print()



def main():
    parser = argparse.ArgumentParser(description="Level 3: Audit & Deficiency Reporter")
    parser.add_argument('transcript', help="Path to transcript CSV file")
    parser.add_argument('program_name', nargs='?', default="Computer Science & Engineering", help="Full Header Name in Markdown")
    parser.add_argument('program_knowledge', nargs='?', default="program.md", help="Path to program knowledge file")
    
    args = parser.parse_args()
    
    # Supported programs (verified from official NSU curriculum pages)
    program_map = {
        "CSE":   "Computer Science & Engineering",
        "EEE":   "Electrical & Electronic Engineering",
        "ETE":   "Electronic & Telecom Engineering",
        "CEE":   "Civil & Environmental Engineering",
        "ENV":   "Environmental Science & Management",
        "ENG":   "English",
        "BBA":   "Business Administration",
        "ECO":   "Economics",
    }
    
    full_program_name = program_map.get(args.program_name.upper(), args.program_name)
    
    # 1. Parse Requirements
    requirements = parse_program_knowledge(args.program_knowledge, full_program_name)
    
    # 2. Audit
    result = audit_student(args.transcript, requirements)
    
    # 3. Report
    print_report(result, requirements, full_program_name)

if __name__ == '__main__':
    main()

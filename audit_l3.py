#!/usr/bin/env python3
import csv
import sys
import re
import argparse
from style import (
    GR, RD, YL, CY, BL, DM, RS,
    H, V, TL, TR, BL2, BR, ML, MR,
    DH, DV, DTL, DTR, DBL, DBR, DML, DMR,
    CHK, XMK, WRN, BULL, SLP,
    visible_len, pad_row
)

# ── NSU Grading Scale ──────────────────────────────────────────────────────────
GRADE_POINTS = {
    'A': 4.0, 'A-': 3.7, 'B+': 3.3, 'B': 3.0, 'B-': 2.7,
    'C+': 2.3, 'C': 2.0, 'C-': 1.7, 'D+': 1.3, 'D': 1.0, 'F': 0.0
}

def is_passing(grade):
    return grade.upper() not in ['F', 'W', 'I', 'X']

# --- Level 3 Specific Logic ---

SEMESTER_SEASON_ORDER = {'Spring': 0, 'Summer': 1, 'Fall': 2}

def semester_sort_key(sem_str):
    parts = sem_str.strip().split()
    if len(parts) == 2:
        try: return (int(parts[1]), SEMESTER_SEASON_ORDER.get(parts[0], 99))
        except: pass
    return (9999, 99)

def parse_program_knowledge(md_file, program_name):
    """
    Parses the program.md file to extract requirements for the specified program.
    Returns a dict with:
    - total_credits_required
    - min_cgpa
    - mandatory_ged, core_math, major_core, core_business, core_science
    - prerequisites  (dict: course -> prereq course)
    - major_declaration_credits  (int, 0 = no restriction)
    """
    requirements = {
        'total_credits_required': 0,
        'min_cgpa': 2.0,
        'mandatory_ged': [],
        'core_math': [],
        'major_core': [],
        'core_business': [],
        'core_science': [],
        'prerequisites': {},
        'major_declaration_credits': 0,
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
                pass
            elif line.startswith('- **Major Declaration Credits**:'):
                requirements['major_declaration_credits'] = int(re.search(r'\d+', line).group())
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
            elif line.startswith('- **Prerequisites**:'):
                current_section = 'PREREQS'
            
            # Parse prerequisite lines:  "  - CSE215: CSE115"
            if current_section == 'PREREQS':
                prereq_match = re.match(r'^\s*-\s*([A-Z]{2,3}\d{3}[A-Z]?):\s*([A-Z]{2,3}\d{3}[A-Z]?)$', line)
                if prereq_match:
                    requirements['prerequisites'][prereq_match.group(1)] = prereq_match.group(2)
                continue

            # Parse List Items (Courses)
            course_match = re.search(r'^\s*-\s*([A-Z]{2,3}\d{3}[A-Z]?)', line)
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
    # 1. Read transcript rows
    rows = []
    try:
        with open(transcript_file, 'r') as f:
            reader = csv.DictReader(f)
            reader.fieldnames = [name.strip() for name in reader.fieldnames]
            for row in reader:
                rows.append({
                    'course':  row['Course_Code'].strip(),
                    'grade':   row['Grade'].strip(),
                    'credits': float(row.get('Credits', 0)),
                    'semester': row.get('Semester', 'Unknown').strip(),
                })
    except FileNotFoundError:
        print(f"Error: Transcript '{transcript_file}' not found.")
        sys.exit(1)
    except Exception:
        for r in rows: pass  # already read what we could

    # 2. Sort rows chronologically for prerequisite / declaration checks
    rows.sort(key=lambda r: semester_sort_key(r['semester']))

    passed_courses = set()
    course_history = {}
    advisories = []           # non-blocking warnings
    prereqs = requirements.get('prerequisites', {})
    major_decl_credits = requirements.get('major_declaration_credits', 0)

    # Sets of courses that are considered "major" (core + business)
    major_course_set = set(requirements['major_core'] + requirements['core_business'])

    # Track which courses were passed BEFORE the current semester
    passed_before_semester = set()
    credits_before_semester = 0.0
    prev_sem = None

    for r in rows:
        course  = r['course']
        grade   = r['grade']
        credits = r['credits']
        sem     = r['semester']

        # On semester boundary, snapshot the passed set and credit total
        if sem != prev_sem:
            passed_before_semester = set(passed_courses)
            # Sum credits from course_history for courses already passed
            credits_before_semester = 0.0
            for c in passed_courses:
                ch = course_history.get(c)
                if ch:
                    credits_before_semester += ch['credits']
            prev_sem = sem

        # ── Prerequisite check ────────────────────────────────────────────
        if course in prereqs:
            needed = prereqs[course]
            if needed not in passed_before_semester:
                advisories.append(
                    f'Prerequisite violation: {course} taken in {sem} '
                    f'without passing {needed} first'
                )

        # ── BBA major-declaration check ───────────────────────────────────
        if major_decl_credits > 0 and course in major_course_set:
            if credits_before_semester < major_decl_credits:
                advisories.append(
                    f'Major declaration: {course} taken in {sem} '
                    f'with only {credits_before_semester:.0f} earned credits '
                    f'(major courses require {major_decl_credits} credits first)'
                )

        # ── Credit / GPA bookkeeping ──────────────────────────────────────
        if is_passing(grade):
            passed_courses.add(course)

        if GRADE_POINTS.get(grade) is not None:
            points = GRADE_POINTS[grade]
            existing = course_history.get(course)
            if existing is None or points > existing['points']:
                course_history[course] = {'grade': grade, 'credits': credits, 'points': points}

    # ── CSE498R conditional credit logic ──────────────────────────────────
    if 'CSE498R' in course_history:
        if 'BIO103L' in passed_courses:
            course_history['CSE498R']['credits'] = 0.0
        else:
            course_history['CSE498R']['credits'] = 1.0

    # ── Calculate CGPA ────────────────────────────────────────────────────
    gpa_points = 0.0
    gpa_credits = 0.0
    for data in course_history.values():
        if data['credits'] > 0:
            gpa_points += data['points'] * data['credits']
            gpa_credits += data['credits']
    cgpa = gpa_points / gpa_credits if gpa_credits > 0 else 0.0
    
    # ── Check Requirements ────────────────────────────────────────────────
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
        'passed_courses': passed_courses,
        'advisories': advisories,
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
    content = f'  {BL}{CY}{label}{RS}'
    print(pad_row(content, W, '║', '║'))
    prog_line = f'Program  :  {program_name}'
    content = f'  {DM}{prog_line}{RS}'
    print(pad_row(content, W, '║', '║'))
    print(f'╠{"═" * W}╣')

    # ── Metrics grid ──────────────────────────────────────────────────────────
    cred_c = cc(earned, req)
    cgpa_c = cc(cgpa, min_cgpa)
    cr_str = f'{cred_c}{BL}{earned:.1f}{RS}'
    cg_str = f'{cgpa_c}{BL}{cgpa:.2f}{RS}'
    content = f'  Credits Required : {BL}{req:<8}{RS}  │  Credits Earned : {cr_str}'
    print(pad_row(content, W, '║', '║'))
    content = f'  Min CGPA         : {BL}{min_cgpa:<8}{RS}  │  CGPA Earned    : {cg_str}'
    print(pad_row(content, W, '║', '║'))
    print(f'╠{"═" * W}╣')

    # ── Verdict ───────────────────────────────────────────────────────────────
    if is_eligible:
        verdict = '✓   ELIGIBLE FOR GRADUATION'
        vc = GR
    else:
        verdict = '✗   NOT ELIGIBLE FOR GRADUATION'
        vc = RD
    content = f'  {vc}{BL}{verdict}{RS}'
    print(pad_row(content, W, '║', '║'))
    print(f'╚{"═" * W}╝')

    if is_eligible and not audit.get('advisories'):
        print()
        return

    # ── Deficiency section ────────────────────────────────────────────────────
    if not is_eligible:
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

    # ── Advisory Notes (non-blocking warnings) ────────────────────────────────
    advisories = audit.get('advisories', [])
    if advisories:
        print(f'\n  {BL}ADVISORY NOTES{RS}')
        print(f'  {"─" * (W - 2)}')
        for note in advisories:
            print(f'  {YL}⚠{RS}  {note}')
        print(f'  {"─" * (W - 2)}')

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

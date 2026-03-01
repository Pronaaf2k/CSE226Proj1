#!/usr/bin/env python3
import csv
import sys
import argparse
from collections import defaultdict
from style import (
    GR, RD, YL, CY, BL, DM, RS,
    H, V, TL, TR, BL2, BR, ML, MR, MC, TM, BM,
    DH, DV, DTL, DTR, DBL, DBR, DML, DMR,
    CHK, XMK, WRN, ARW, BULL, SLP
)


# ── NSU Grading Scale ──────────────────────────────────────────────────────────
GRADE_POINTS = {
    'A': 4.0, 'A-': 3.7,
    'B+': 3.3, 'B': 3.0, 'B-': 2.7,
    'C+': 2.3, 'C': 2.0, 'C-': 1.7,
    'D+': 1.3, 'D': 1.0, 'F': 0.0
}

SEMESTER_SEASON_ORDER = {'Spring': 0, 'Summer': 1, 'Fall': 2}

def semester_sort_key(sem_str):
    parts = sem_str.strip().split()
    if len(parts) == 2:
        try: return (int(parts[1]), SEMESTER_SEASON_ORDER.get(parts[0], 99))
        except: pass
    return (9999, 99)

def get_grade_points(grade):
    return GRADE_POINTS.get(grade.strip().upper(), None)

def grade_status_label(grade):
    g = grade.strip().upper()
    if g == 'W':  return 'Withdrawn'
    if g == 'I':  return 'Incomplete'
    if g == 'F':  return 'Failed'
    if get_grade_points(g) is not None: return 'Counted'
    return 'N/A'

def status_display(status):
    icons = {
        'Counted':    f'{GR}✓{RS}',
        'Withdrawn':  f'{YL}~{RS}',
        'Incomplete': f'{YL}?{RS}',
        'Failed':     f'{RD}✗{RS}',
        'N/A':        f'{DM}–{RS}',
        'Waived':     f'{CY}⊘{RS}',
    }
    return f'{icons.get(status,"·")} {status}'

def cgpa_colour(cgpa):
    if cgpa >= 3.0:  return GR
    if cgpa >= 2.0:  return YL
    return RD

def calculate_cgpa(transcript_file, waivers=None):
    if waivers is None: waivers = []
    waiver_set = {w.upper() for w in waivers}

    semester_rows = defaultdict(list)
    try:
        with open(transcript_file, mode='r') as f:
            reader = csv.DictReader(f)
            reader.fieldnames = [h.strip() for h in reader.fieldnames]
            for row in reader:
                sem = row.get('Semester', 'Unknown').strip()
                semester_rows[sem].append(row)
    except FileNotFoundError:
        print(f'{RD}Error:{RS} File "{transcript_file}" not found.')
        sys.exit(1)

    sorted_sems = sorted(semester_rows.keys(), key=semester_sort_key)

    # ── Banner ─────────────────────────────────────────────────────────────────
    W = 66
    print()
    print(f'╔{"═" * W}╗')
    title = 'SEMESTER-BY-SEMESTER CGPA REPORT'
    print(f'║  {BL}{CY}{title}{RS}{" " * (W - len(title) - 2)}║')
    print(f'║  {DM}Transcript : {transcript_file}{RS}{" " * max(0, W - 15 - len(transcript_file))}║')
    if waivers:
        wl = f'Waivers    : {", ".join(waivers)}'
        print(f'║  {DM}{wl}{RS}{" " * max(0, W - 2 - len(wl))}║')
    print(f'╚{"═" * W}╝')

    cumulative_best    = {}
    consecutive_prob   = 0

    for sem in sorted_sems:
        rows = semester_rows[sem]

        # ── Semester card header ───────────────────────────────────────────────
        print(f'\n  ┌─ {BL}{sem}{RS} {"─" * max(0, W - len(sem) - 5)}┐')
        C1, C2, C3, C4 = 14, 9, 7, 20
        print(f'  │  {BL}{"Course":<{C1}}{RS} {BL}{"Credits":>{C2}}{RS}  '
              f'{BL}{"Grade":<{C3}}{RS}  {BL}{"Status":<{C4}}{RS}    │')
        print(f'  ├{"─" * (W + 2)}┤')

        sem_pts  = 0.0
        sem_cred = 0.0

        for row in rows:
            course  = row['Course_Code'].strip()
            grade   = row['Grade'].strip()
            try:    credits = float(row['Credits'])
            except: credits = 0.0

            if course.upper() in waiver_set:
                label = status_display('Waived')
                print(f'  │  {course:<{C1}} {credits:>{C2}.1f}  {grade:<{C3}}  {label:<{C4}}    │')
                continue

            label  = status_display(grade_status_label(grade))
            print(f'  │  {course:<{C1}} {credits:>{C2}.1f}  {grade:<{C3}}  {label}    │')

            points = get_grade_points(grade)
            if points is not None and credits > 0:
                sem_pts  += points * credits
                sem_cred += credits

            if points is not None:
                ex = cumulative_best.get(course)
                if ex is None or points > ex['points']:
                    cumulative_best[course] = {'credits': credits, 'grade': grade, 'points': points}

        # ── Compute TGPA and CGPA ──────────────────────────────────────────────
        tgpa = sem_pts / sem_cred if sem_cred > 0 else 0.0
        cgpa_pts   = sum(d['points'] * d['credits'] for d in cumulative_best.values() if d['credits'] > 0)
        cgpa_creds = sum(d['credits']               for d in cumulative_best.values() if d['credits'] > 0)
        cgpa = cgpa_pts / cgpa_creds if cgpa_creds > 0 else 0.0

        if cgpa_creds > 0 and cgpa < 2.0:
            consecutive_prob += 1
        else:
            consecutive_prob = 0

        cc = cgpa_colour(cgpa)
        tc = cgpa_colour(tgpa)

        # ── Semester summary bar ───────────────────────────────────────────────
        print(f'  ├{"─" * (W + 2)}┤')
        print(f'  │  Sem Credits : {BL}{sem_cred:<5.1f}{RS}  '
              f'TGPA : {BL}{tc}{tgpa:.2f}{RS}   '
              f'│   Cumulative CGPA : {BL}{cc}{cgpa:.2f}{RS}{"  " * 4}│')

        if consecutive_prob > 0:
            msg = f'⚠  ACADEMIC PROBATION  (semester {consecutive_prob} below 2.00)'
            print(f'  │  {RD}{BL}{msg}{RS}{" " * max(0, W - len(msg))}│')
        else:
            print(f'  │  {GR}✓  Good Standing{RS}{" " * (W - 15)}│')

        print(f'  └{"─" * (W + 2)}┘')

    # ── Final summary ──────────────────────────────────────────────────────────
    f_pts   = sum(d['points'] * d['credits'] for d in cumulative_best.values() if d['credits'] > 0)
    f_creds = sum(d['credits']               for d in cumulative_best.values() if d['credits'] > 0)
    f_cgpa  = f_pts / f_creds if f_creds > 0 else 0.0
    fc = cgpa_colour(f_cgpa)

    print()
    print(f'╔{"═" * W}╗')
    print(f'║  {BL}FINAL SUMMARY{RS}{" " * (W - 15)}║')
    print(f'╠{"═" * W}╣')
    print(f'║  Final CGPA              :  {BL}{fc}{f_cgpa:.2f}{RS}{" " * (W - 32)}║')
    print(f'║  Total GPA-Bearing Credits :  {BL}{f_creds:.1f}{RS}{" " * (W - 34)}║')

    if consecutive_prob > 0:
        msg = f'⚠  Currently on ACADEMIC PROBATION  ({consecutive_prob} consecutive semester(s))'
        print(f'╠{"═" * W}╣')
        print(f'║  {RD}{BL}{msg}{RS}{" " * max(0, W - 2 - len(msg))}║')
    else:
        print(f'╠{"═" * W}╣')
        print(f'║  {GR}✓  Student is in Good Standing{RS}{" " * (W - 32)}║')
    print(f'╚{"═" * W}╝')
    print()


def main():
    parser = argparse.ArgumentParser(description='Level 2: Semester-by-Semester CGPA Calculator')
    parser.add_argument('transcript',        help='Path to transcript CSV file')
    parser.add_argument('program_name',      nargs='?', help='Program name (unused at L2)')
    parser.add_argument('program_knowledge', nargs='?', help='Program knowledge file (unused at L2)')
    parser.add_argument('--waivers',         help='Comma-separated course codes to waive', default='')
    args = parser.parse_args()

    waiver_list = []
    if args.waivers:
        waiver_list = [w.strip() for w in args.waivers.split(',') if w.strip()]
    else:
        print(f'\n{CY}Waivers{RS} — enter course codes to exclude (comma-separated), or press Enter for none:')
        user_input = input('  > ')
        if user_input.strip():
            waiver_list = [w.strip() for w in user_input.split(',')]

    calculate_cgpa(args.transcript, waivers=waiver_list)

if __name__ == '__main__':
    main()

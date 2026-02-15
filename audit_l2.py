#!/usr/bin/env python3
import csv
import sys
import argparse

# NSU Grading Scale (Standard approximation)
GRADE_POINTS = {
    'A': 4.0, 'A-': 3.7,
    'B+': 3.3, 'B': 3.0, 'B-': 2.7,
    'C+': 2.3, 'C': 2.0, 'C-': 1.7,
    'D+': 1.3, 'D': 1.0, 'F': 0.0
}

def get_grade_points(grade):
    return GRADE_POINTS.get(grade.upper(), None)

def calculate_cgpa(transcript_file, waivers=[]):
    # Dictionary to store the *latest* attempt for each course
    # Key: Course_Code, Value: {'credits': float, 'grade': str, 'points': float}
    course_history = {}
    
    print(f"Processing transcript: {transcript_file}")
    if waivers:
        print(f"Applying Waivers for: {', '.join(waivers)}")
    print("-" * 50)

    try:
        with open(transcript_file, mode='r') as infile:
            reader = csv.DictReader(infile)
            reader.fieldnames = [name.strip() for name in reader.fieldnames]
            
            # Read all rows
            entries = list(reader)
            
            # Process chronologically (assuming file is ordered or naive order)
            for row in entries:
                course_code = row['Course_Code'].strip()
                grade = row['Grade'].strip()
                
                if course_code in waivers:
                    continue

                try:
                    credits = float(row['Credits'])
                except ValueError:
                    credits = 0.0

                # Check if it's a valid grade for GPA (Excluding W, I, etc.)
                points = get_grade_points(grade)
                
                if points is not None:
                    # Logic: Latest attempt replaces previous attempts for CGPA calculation
                    # We simply overwrite the entry in the dictionary
                    course_history[course_code] = {
                        'credits': credits,
                        'grade': grade,
                        'points': points
                    }
    except FileNotFoundError:
        print(f"Error: File '{transcript_file}' not found.")
        return

    # Calculate CGPA based on final state of course_history
    total_points = 0.0
    total_credits = 0.0
    
    print(f"{'Course':<10} | {'Credits':<7} | {'Grade':<5} | {'Points':<6}")
    print("-" * 50)
    
    for course, data in course_history.items():
        # Only count towards CGPA if credits > 0 (Labs often 1, some invalid ones 0)
        # Assuming F counts (0 points * credits), but 0-credit courses don't impact GPA division
        if data['credits'] > 0:
            crs_points = data['points'] * data['credits']
            total_points += crs_points
            total_credits += data['credits']
            print(f"{course:<10} | {data['credits']:<7} | {data['grade']:<5} | {crs_points:<6.2f}")
        else:
             print(f"{course:<10} | {data['credits']:<7} | {data['grade']:<5} | {'0.00 (N/A)'}")

    print("-" * 50)
    
    if total_credits > 0:
        cgpa = total_points / total_credits
        print(f"Total Credits Attempted (for GPA): {total_credits}")
        print(f"Total Grade Points: {total_points:.2f}")
        print(f"CGPA: {cgpa:.2f}")
    else:
        print("CGPA: 0.00 (No GPA credits attempted)")
    print("-" * 50)

def main():
    parser = argparse.ArgumentParser(description="Level 2: Logic Gate & Waiver Handler")
    parser.add_argument('transcript', help="Path to transcript CSV file")
    parser.add_argument('program_name', nargs='?', help="Name of the program")
    parser.add_argument('program_knowledge', nargs='?', help="Path to program knowledge file")
    
    # Optional non-interactive mode for testing
    parser.add_argument('--waivers', help="Comma separated list of courses to waive", default="")

    args = parser.parse_args()

    # Interactive Waiver Prompt
    waiver_list = []
    if args.waivers:
        waiver_list = [w.strip() for w in args.waivers.split(',') if w.strip()]
    else:
        # Prompt user
        print("Enter course codes to waive (comma separated, or press Enter for none):")
        user_input = input("> ")
        if user_input.strip():
            waiver_list = [w.strip() for w in user_input.split(',')]

    calculate_cgpa(args.transcript, waivers=waiver_list)

if __name__ == '__main__':
    main()

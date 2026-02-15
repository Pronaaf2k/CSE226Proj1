#!/usr/bin/env python3
import csv
import sys
import argparse

def is_passing_grade(grade):
    """
    Returns True if the grade is a passing grade.
    F, W, I, and others are considered non-passing for credit accrual.
    """
    failing_grades = ['F', 'W', 'I', 'X']
    return grade.upper() not in failing_grades

def calculate_credits(transcript_file):
    passed_courses = set()
    total_credits = 0
    
    print(f"Processing transcript: {transcript_file}")
    print("-" * 50)
    print(f"{'Course':<10} | {'Credits':<7} | {'Grade':<5} | {'Status':<10}")
    print("-" * 50)

    try:
        with open(transcript_file, mode='r') as infile:
            reader = csv.DictReader(infile)
            # Strip whitespace from headers just in case
            reader.fieldnames = [name.strip() for name in reader.fieldnames]
            
            # Sort rows by semester/date if possible to handle retakes chronologically? 
            # For Level 1, we just need to know if they *eventually* passed. 
            # A simple set of passed courses is sufficient to avoid double counting.
            
            entries = list(reader)
            
            for row in entries:
                course_code = row['Course_Code'].strip()
                try:
                    credits = float(row['Credits'])
                except ValueError:
                    credits = 0.0
                grade = row['Grade'].strip()
                
                status = "Skipped"
                if is_passing_grade(grade):
                    if course_code not in passed_courses:
                        total_credits += credits
                        passed_courses.add(course_code)
                        status = "Counted"
                    else:
                        status = "Retake (Ignored)"
                else:
                    status = "Failed/Withdrawn"
                
                print(f"{course_code:<10} | {credits:<7} | {grade:<5} | {status:<10}")

    except FileNotFoundError:
        print(f"Error: File '{transcript_file}' not found.")
        return
    except Exception as e:
        print(f"An error occurred: {e}")
        return

    print("-" * 50)
    print(f"Total Valid Earned Credits: {total_credits}")
    print("-" * 50)

def main():
    parser = argparse.ArgumentParser(description="Level 1: Credit Tally Engine")
    parser.add_argument('transcript', help="Path to transcript CSV file")
    # Arguments below are placeholders for standard invocation format but not used in Level 1 logic per se
    parser.add_argument('program_name', nargs='?', help="Name of the program (e.g., CSE)") 
    parser.add_argument('program_knowledge', nargs='?', help="Path to program knowledge file (e.g., program.md)")
    
    args = parser.parse_args()
    
    calculate_credits(args.transcript)

if __name__ == '__main__':
    main()

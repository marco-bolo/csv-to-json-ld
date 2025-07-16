#!/usr/bin/env python3

import csv
import sys
import glob

def check_file(file_path):
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        expected = None
        for line_num, row in enumerate(reader, start=1):
            if expected is None:
                expected = len(row)
                continue
            if not row or all(cell.strip() == '' for cell in row):
                print(f"{file_path}: line {line_num} is empty")
            elif len(row) != expected:
                print(f"{file_path}: line {line_num} has {len(row)} fields, expected {expected}")

errors = 0
for f in glob.glob("*.csv"):
    print(f"Checking {f}")
    try:
        check_file(f)
    except Exception as e:
        print(f"Error checking {f}: {e}")
        errors = 1

if errors:
    print("❌ CSV format errors found. Fix them before continuing.")
    sys.exit(1)
else:
    print("✅ All CSV files passed format check.")


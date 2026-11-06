"""
init_sample_data.py - Standalone Sample Data Initializer

Populates emp.txt, department.txt, and employee_department.txt
in CSV format using Python's built-in csv module.
"""

import sys
import os

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from file_handler import (
    EMP_FILE,
    EMP_HEADERS,
    DEPT_FILE,
    DEPT_HEADERS,
    ASG_FILE,
    ASG_HEADERS,
    write_records,
)


def populate_sample_data():
    sample_employees = [
        {"Employee ID": "EMP001", "Name": "Rajan S", "Age": "21", "City": "Coimbatore", "State": "Tamil Nadu", "Country": "India"},
        {"Employee ID": "EMP002", "Name": "Arun", "Age": "25", "City": "Chennai", "State": "Tamil Nadu", "Country": "India"},
        {"Employee ID": "EMP003", "Name": "Kumar", "Age": "30", "City": "Madurai", "State": "Tamil Nadu", "Country": "India"},
        {"Employee ID": "EMP004", "Name": "Prem Kumar S", "Age": "20", "City": "Coimbatore", "State": "Tamilnadu", "Country": "India"},
    ]

    sample_departments = [
        {"Department ID": "DEP001", "Description": "Human Resources"},
        {"Department ID": "DEP002", "Description": "Software Development"},
        {"Department ID": "DEP003", "Description": "Finance"},
    ]

    sample_assignments = [
        {"Assignment ID": "ASG001", "Employee ID": "EMP001", "Department ID": "DEP001", "Start Date": "01-01-2024", "End Date": "06-30-2024"},
        {"Assignment ID": "ASG002", "Employee ID": "EMP001", "Department ID": "DEP002", "Start Date": "07-01-2024", "End Date": "Current"},
        {"Assignment ID": "ASG003", "Employee ID": "EMP002", "Department ID": "DEP003", "Start Date": "02-01-2024", "End Date": "Current"},
        {"Assignment ID": "ASG004", "Employee ID": "EMP003", "Department ID": "DEP001", "Start Date": "03-01-2024", "End Date": "05-31-2024"},
        {"Assignment ID": "ASG005", "Employee ID": "EMP003", "Department ID": "DEP002", "Start Date": "06-01-2024", "End Date": "Current"},
    ]

    write_records(EMP_FILE, EMP_HEADERS, sample_employees)
    write_records(DEPT_FILE, DEPT_HEADERS, sample_departments)
    write_records(ASG_FILE, ASG_HEADERS, sample_assignments)

    print("\n[SUCCESS] Sample data initialized in CSV format inside .txt files successfully!")


if __name__ == "__main__":
    print("Initializing sample data for Employee & Department Management System...")
    populate_sample_data()

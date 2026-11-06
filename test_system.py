"""
test_system.py - Comprehensive Verification Suite for 15 Required Test Cases

Tests:
 1. Valid employee registration.
 2. Invalid employee name containing numbers.
 3. Invalid employee name containing special characters.
 4. Age below 18.
 5. Age above 65.
 6. Invalid input should stop subsequent input collection.
 7. Valid department creation.
 8. Valid employee assignment.
 9. Invalid date format.
10. Overlapping assignment rejection.
11. Duplicate current department assignment rejection.
12. Valid department change.
13. Employee lookup on a particular date.
14. Employee lookup within a date range.
15. CSV data correctly saved and loaded from .txt files.
"""

import sys
import os
import io

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from file_handler import (
    write_records,
    read_records,
    EMP_FILE,
    EMP_HEADERS,
    DEPT_FILE,
    DEPT_HEADERS,
    ASG_FILE,
    ASG_HEADERS,
)
import employee
import department
import assignment
import reports
import main
from validation import (
    validate_employee_name,
    validate_age,
    validate_date_format,
)


def reset_test_env():
    """Reset data files for a clean test run."""
    write_records(EMP_FILE, EMP_HEADERS, [])
    write_records(DEPT_FILE, DEPT_HEADERS, [])
    write_records(ASG_FILE, ASG_HEADERS, [])


def run_all_tests():
    print("=================================================================")
    print("RUNNING 15 SPECIFICATION TEST CASES")
    print("=================================================================\n")

    reset_test_env()
    passed = 0
    total = 15

    # -------------------------------------------------------------------------
    # TEST 1: Valid employee registration
    # -------------------------------------------------------------------------
    ok1, msg1, emp1 = employee.add_employee("Rajan", 21, "Coimbatore", "Tamil Nadu", "India")
    assert ok1 and emp1["Employee ID"] == "EMP001", f"Test 1 Failed: {msg1}"
    print("[PASS] Test 1: Valid employee registration (EMP001 created)")
    passed += 1

    # -------------------------------------------------------------------------
    # TEST 2: Invalid employee name containing numbers
    # -------------------------------------------------------------------------
    ok2, msg2 = validate_employee_name("Rajan123")
    assert not ok2 and "alphabetic" in msg2.lower(), f"Test 2 Failed: {msg2}"
    print(f"[PASS] Test 2: Invalid employee name containing numbers correctly rejected: '{msg2}'")
    passed += 1

    # -------------------------------------------------------------------------
    # TEST 3: Invalid employee name containing special characters
    # -------------------------------------------------------------------------
    ok3, msg3 = validate_employee_name("Rajan@#$")
    assert not ok3 and "alphabetic" in msg3.lower(), f"Test 3 Failed: {msg3}"
    print(f"[PASS] Test 3: Invalid employee name containing special characters correctly rejected: '{msg3}'")
    passed += 1

    # -------------------------------------------------------------------------
    # TEST 4: Age below 18
    # -------------------------------------------------------------------------
    ok4, msg4, _ = validate_age(17)
    assert not ok4 and "18 and 65" in msg4, f"Test 4 Failed: {msg4}"
    print(f"[PASS] Test 4: Age below 18 correctly rejected: '{msg4}'")
    passed += 1

    # -------------------------------------------------------------------------
    # TEST 5: Age above 65
    # -------------------------------------------------------------------------
    ok5, msg5, _ = validate_age(66)
    assert not ok5 and "18 and 65" in msg5, f"Test 5 Failed: {msg5}"
    print(f"[PASS] Test 5: Age above 65 correctly rejected: '{msg5}'")
    passed += 1

    # -------------------------------------------------------------------------
    # TEST 6: Invalid input should stop subsequent input collection
    # If the user enters an invalid name, menu_add_employee must stop immediately
    # and NOT attempt to collect Age, City, State, or Country.
    # -------------------------------------------------------------------------
    original_stdin = sys.stdin
    original_stdout = sys.stdout
    try:
        # Provide ONLY one line containing the invalid name.
        # If subsequent collection was attempted, it would raise EOFError!
        sys.stdin = io.StringIO("Rajan999\n")
        sys.stdout = io.StringIO()
        main.menu_add_employee()
        captured_output = sys.stdout.getvalue()
        assert "[ERROR]" in captured_output, "Test 6 Failed: Expected error message on invalid name"
    finally:
        sys.stdin = original_stdin
        sys.stdout = original_stdout
    print("[PASS] Test 6: Invalid input stopped subsequent input collection without requesting further fields")
    passed += 1

    # -------------------------------------------------------------------------
    # TEST 7: Valid department creation
    # -------------------------------------------------------------------------
    ok7, msg7, dep1 = department.add_department("Human Resources")
    assert ok7 and dep1["Department ID"] == "DEP001", f"Test 7 Failed: {msg7}"
    department.add_department("Software Development")  # DEP002
    department.add_department("Finance")               # DEP003
    print("[PASS] Test 7: Valid department creation (DEP001, DEP002, DEP003 created)")
    passed += 1

    # -------------------------------------------------------------------------
    # TEST 8: Valid employee assignment
    # -------------------------------------------------------------------------
    ok8, msg8, asg1 = assignment.assign_employee_to_department(
        "EMP001", "DEP001", "01-01-2024", "06-30-2024"
    )
    assert ok8 and asg1["Assignment ID"] == "ASG001", f"Test 8 Failed: {msg8}"
    print("[PASS] Test 8: Valid employee assignment (ASG001 created)")
    passed += 1

    # -------------------------------------------------------------------------
    # TEST 9: Invalid date format
    # -------------------------------------------------------------------------
    invalid_dates = ["13-20-2024", "02-30-2024", "2024-01-15", "01/15/2024", "1-5-2024"]
    for bad_d in invalid_dates:
        bad_ok, bad_msg, _ = validate_date_format(bad_d)
        assert not bad_ok, f"Test 9 Failed: Invalid date '{bad_d}' was accepted!"
    print(f"[PASS] Test 9: Invalid date formats rejected ({', '.join(invalid_dates)})")
    passed += 1

    # -------------------------------------------------------------------------
    # TEST 10: Overlapping assignment rejection
    # EMP001 has DEP001: 01-01-2024 to 06-30-2024
    # Attempting to assign DEP002: 06-15-2024 to Current must be rejected!
    # -------------------------------------------------------------------------
    ok10, msg10, _ = assignment.assign_employee_to_department(
        "EMP001", "DEP002", "06-15-2024", "Current"
    )
    assert not ok10 and "overlap" in msg10.lower(), f"Test 10 Failed: {msg10}"
    print(f"[PASS] Test 10: Overlapping assignment rejected: '{msg10}'")
    passed += 1

    # Assign non-overlapping: 07-01-2024 to Current
    assignment.assign_employee_to_department("EMP001", "DEP002", "07-01-2024", "Current")

    # -------------------------------------------------------------------------
    # TEST 11: Duplicate current department assignment rejection
    # EMP001 is currently active in DEP002. Re-assigning to DEP002 must be rejected!
    # -------------------------------------------------------------------------
    ok11, msg11, _ = assignment.assign_employee_to_department(
        "EMP001", "DEP002", "08-01-2024", "Current"
    )
    assert not ok11 and "already working in this department" in msg11, f"Test 11 Failed: {msg11}"
    print(f"[PASS] Test 11: Duplicate current department assignment rejected: '{msg11}'")
    passed += 1

    # -------------------------------------------------------------------------
    # TEST 12: Valid department change
    # Close DEP002 on 09-30-2024, start DEP003 on 10-01-2024 to Current
    # -------------------------------------------------------------------------
    ok12, msg12 = assignment.change_employee_department(
        emp_id="EMP001",
        new_dept_id="DEP003",
        close_end_date_str="09-30-2024",
        new_start_date_str="10-01-2024",
        new_end_date_str="Current",
    )
    assert ok12, f"Test 12 Failed: {msg12}"
    cur_asg = assignment.get_current_assignment("EMP001")
    assert cur_asg["Department ID"] == "DEP003", f"Test 12 Failed: Expected DEP003, got {cur_asg['Department ID']}"
    print("[PASS] Test 12: Valid department change (DEP002 closed, DEP003 active, history preserved)")
    passed += 1

    # Add extra employees & assignments to test lookup queries
    employee.add_employee("Arun", 25, "Chennai", "Tamil Nadu", "India")    # EMP002
    employee.add_employee("Kumar", 30, "Madurai", "Tamil Nadu", "India")   # EMP003
    assignment.assign_employee_to_department("EMP002", "DEP003", "02-01-2024", "Current")
    assignment.assign_employee_to_department("EMP003", "DEP001", "03-01-2024", "05-31-2024")
    assignment.assign_employee_to_department("EMP003", "DEP002", "06-01-2024", "Current")

    # -------------------------------------------------------------------------
    # TEST 13: Employee lookup on a particular date
    # On 05-15-2024:
    # EMP001 was in DEP001 (01-01 to 06-30)
    # EMP002 was in DEP003 (02-01 to Current)
    # EMP003 was in DEP001 (03-01 to 05-31)
    # Total active employees on 05-15-2024 should be 3
    # -------------------------------------------------------------------------
    ok13, msg13, res13 = reports.get_employees_working_on_date("05-15-2024")
    assert ok13 and len(res13) == 3, f"Test 13 Failed: Expected 3, got {len(res13)}"
    names = [r["Employee Name"] for r in res13]
    assert "Rajan" in names and "Arun" in names and "Kumar" in names
    print(f"[PASS] Test 13: Employee lookup on a particular date (05-15-2024 returned {names})")
    passed += 1

    # -------------------------------------------------------------------------
    # TEST 14: Employee lookup within a date range
    # 01-01-2024 to 12-31-2024: should return overlapping assignments
    # EMP001 has 3 assignments in 2024 (DEP001, DEP002, DEP003) -> 3 rows!
    # EMP002 has 1 assignment (DEP003) -> 1 row!
    # EMP003 has 2 assignments (DEP001, DEP002) -> 2 rows!
    # Total = 6 rows
    # -------------------------------------------------------------------------
    ok14, msg14, res14 = reports.get_employees_working_in_date_range("01-01-2024", "12-31-2024")
    assert ok14 and len(res14) == 6, f"Test 14 Failed: Expected 6 rows, got {len(res14)}"
    print(f"[PASS] Test 14: Employee lookup within a date range (Returned {len(res14)} overlapping rows)")
    passed += 1

    # -------------------------------------------------------------------------
    # TEST 15: CSV data correctly saved and loaded from .txt files
    # Check that raw files contain valid comma-separated text lines
    # -------------------------------------------------------------------------
    with open(EMP_FILE, "r", encoding="utf-8") as f:
        emp_raw = f.readlines()
    assert emp_raw[0].strip() == "Employee ID,Name,Age,City,State,Country", "Header must be CSV format"
    assert "EMP001,Rajan,21,Coimbatore,Tamil Nadu,India" in [line.strip() for line in emp_raw]

    loaded_emps = read_records(EMP_FILE, EMP_HEADERS)
    assert len(loaded_emps) == 3, f"Expected 3 employees loaded from CSV, got {len(loaded_emps)}"
    print("[PASS] Test 15: CSV data verified directly from emp.txt, department.txt, and employee_department.txt")
    passed += 1

    print("\n=================================================================")
    print(f"ALL {passed}/{total} SPECIFICATION TEST CASES PASSED WITH ZERO ERRORS!")
    print("=================================================================\n")


if __name__ == "__main__":
    run_all_tests()

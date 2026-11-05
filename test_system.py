
import sys
import os

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from file_handler import (
    initialize_storage_files,
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
from validation import (
    is_leap_year,
    get_days_in_month,
    validate_date_format,
    compare_dates,
    is_date_before_or_equal,
    is_date_strictly_after,
    check_date_ranges_overlap,
    is_employee_working_on_date,
    find_assignments_overlapping_range,
    MAX_DATE_TUPLE,
)


def reset_test_environment():
    """Reset data files to empty state for test repeatability."""
    write_records(EMP_FILE, EMP_HEADERS, [])
    write_records(DEPT_FILE, DEPT_HEADERS, [])
    write_records(ASG_FILE, ASG_HEADERS, [])


def test_custom_date_engine():
    """Unit test all custom manual date functions."""
    print("=================================================================")
    print("PART A: TESTING CUSTOM MANUAL DATE ENGINE (NO DATETIME/CALENDAR)")
    print("=================================================================")

    # 1. Leap Year Calculation
    assert is_leap_year(2024) is True, "2024 must be leap year"
    assert is_leap_year(2000) is True, "2000 must be leap year (divisible by 400)"
    assert is_leap_year(1900) is False, "1900 must NOT be leap year (divisible by 100 but not 400)"
    assert is_leap_year(2023) is False, "2023 must NOT be leap year"
    assert is_leap_year(2100) is False, "2100 must NOT be leap year"
    print("[PASS] Manual Leap Year Calculation (2024=T, 2000=T, 1900=F, 2023=F, 2100=F)")

    # 2. Monthly Day Limit Checks
    assert get_days_in_month(1, 2024) == 31, "Jan has 31 days"
    assert get_days_in_month(2, 2024) == 29, "Feb 2024 has 29 days (leap)"
    assert get_days_in_month(2, 2023) == 28, "Feb 2023 has 28 days (non-leap)"
    assert get_days_in_month(4, 2024) == 30, "Apr has 30 days"
    assert get_days_in_month(12, 2024) == 31, "Dec has 31 days"
    print("[PASS] Manual Monthly Day Limits (Feb 2024=29, Feb 2023=28, Apr=30, Dec=31)")

    # 3. Custom MM-DD-CCYY Date Format Validation
    ok, _, dt = validate_date_format("01-15-2024")
    assert ok and dt == (2024, 1, 15), "01-15-2024 must be valid (2024, 1, 15)"

    ok, _, dt = validate_date_format("02-29-2024")
    assert ok and dt == (2024, 2, 29), "02-29-2024 must be valid in leap year"

    # Rejection of invalid dates
    bad_dates = [
        "13-20-2024",  # Invalid month 13
        "02-30-2024",  # Feb 30 does not exist
        "02-29-2023",  # Feb 29 invalid in non-leap year
        "04-31-2024",  # April has only 30 days
        "2024-01-15",  # ISO format rejected
        "01/15/2024",  # Slash separator rejected
        "1-5-2024",    # Missing leading zeros rejected
        "not-a-date",  # Non-date string rejected
        "",            # Empty rejected
    ]
    for b in bad_dates:
        bad_ok, msg, _ = validate_date_format(b)
        assert not bad_ok, f"Failed to reject invalid date: {b}"
    print(f"[PASS] Custom MM-DD-CCYY Format Validation ({len(bad_dates)} invalid patterns safely rejected)")

    # 4. Manual Date Comparison
    d1 = (2024, 1, 1)
    d2 = (2024, 6, 30)
    d3 = (2024, 7, 1)
    d4 = (2024, 6, 30)
    assert compare_dates(d1, d2) == -1, "01-01 earlier than 06-30"
    assert compare_dates(d2, d1) == 1, "06-30 later than 01-01"
    assert compare_dates(d2, d4) == 0, "06-30 equals 06-30"
    assert is_date_before_or_equal(d1, d2) is True
    assert is_date_strictly_after(d3, d2) is True
    print("[PASS] Manual Date Comparison (compare_dates, is_date_before_or_equal, is_date_strictly_after)")

    # 5. Custom Date Range Overlap Check
    # Overlapping: [01-01-2024, 06-30-2024] and [06-15-2024, Current]
    assert check_date_ranges_overlap(
        (2024, 1, 1), (2024, 6, 30), (2024, 6, 15), MAX_DATE_TUPLE
    ) is True, "Must detect overlap on June 15-30"

    # Non-overlapping: [01-01-2024, 06-30-2024] and [07-01-2024, Current]
    assert check_date_ranges_overlap(
        (2024, 1, 1), (2024, 6, 30), (2024, 7, 1), MAX_DATE_TUPLE
    ) is False, "Must NOT detect overlap between 06-30 and 07-01"
    print("[PASS] Custom Date Range Overlap Math (s1 <= e2 and s2 <= e1 verified)")

    # 6. Check Employee Working on a Date
    assert is_employee_working_on_date((2024, 1, 1), (2024, 6, 30), (2024, 3, 15)) is True
    assert is_employee_working_on_date((2024, 1, 1), (2024, 6, 30), (2024, 7, 1)) is False
    assert is_employee_working_on_date((2024, 7, 1), MAX_DATE_TUPLE, (2025, 5, 20)) is True
    print("[PASS] Employee Working On Date Check (is_employee_working_on_date)")

    # 7. Find Assignments Overlapping Range
    sample_asgs = [
        {"Assignment ID": "ASG001", "Start Date": "01-01-2024", "End Date": "06-30-2024"},
        {"Assignment ID": "ASG002", "Start Date": "07-01-2024", "End Date": "Current"},
        {"Assignment ID": "ASG003", "Start Date": "01-01-2023", "End Date": "12-31-2023"},
    ]
    overlap_res = find_assignments_overlapping_range((2024, 5, 1), (2024, 8, 1), sample_asgs)
    assert len(overlap_res) == 2, f"Expected 2 overlapping (ASG001 and ASG002), got {len(overlap_res)}"
    print("[PASS] Find Assignments Overlapping Range (find_assignments_overlapping_range)\n")


def test_full_system_scenarios():
    """Verify all 16 specification scenarios end-to-end with manual date logic."""
    print("=================================================================")
    print("PART B: TESTING 16 SYSTEM SCENARIOS (END-TO-END)")
    print("=================================================================")

    reset_test_environment()
    passed = 0
    total = 16

    # 1. Add Employee
    ok, msg, emp1 = employee.add_employee("Rajan", 21, "Coimbatore", "Tamil Nadu", "India")
    assert ok and emp1["Employee ID"] == "EMP001", f"Test 1 Failed: {msg}"
    print("[PASS] Test 1: Add an employee with valid details (EMP001 created)")
    passed += 1

    # 2. Reject age < 18
    ok, msg, _ = employee.add_employee("Underage Person", 17, "Chennai", "Tamil Nadu", "India")
    assert not ok and "18 and 65" in msg, f"Test 2 Failed: {msg}"
    print(f"[PASS] Test 2: Reject an employee younger than 18 ({msg})")
    passed += 1

    # 3. Reject age > 65
    ok, msg, _ = employee.add_employee("Elderly Person", 66, "Chennai", "Tamil Nadu", "India")
    assert not ok and "18 and 65" in msg, f"Test 3 Failed: {msg}"
    print(f"[PASS] Test 3: Reject an employee older than 65 ({msg})")
    passed += 1

    employee.add_employee("Arun", 25, "Chennai", "Tamil Nadu", "India")    # EMP002
    employee.add_employee("Kumar", 30, "Madurai", "Tamil Nadu", "India")   # EMP003

    # 4. Add Department
    ok, msg, dep1 = department.add_department("Human Resources")
    assert ok and dep1["Department ID"] == "DEP001", f"Test 4 Failed: {msg}"
    department.add_department("Software Development")  # DEP002
    department.add_department("Finance")               # DEP003
    print("[PASS] Test 4: Add departments (DEP001, DEP002, DEP003 created)")
    passed += 1

    # 5. Assign Employee to Department
    ok, msg, asg1 = assignment.assign_employee_to_department(
        "EMP001", "DEP001", "01-01-2024", "06-30-2024"
    )
    assert ok and asg1["Assignment ID"] == "ASG001", f"Test 5 Failed: {msg}"
    print("[PASS] Test 5: Assign employee to department (ASG001 created)")
    passed += 1

    # 6. Reject invalid date format
    bad_date_samples = ["13-20-2024", "02-30-2024", "2024-01-15", "01/15/2024"]
    for bd in bad_date_samples:
        ok_d, _, _ = validate_date_format(bd)
        assert not ok_d, f"Failed to reject: {bd}"
    print(f"[PASS] Test 6: Reject invalid dates ({', '.join(bad_date_samples)} all rejected)")
    passed += 1

    # 7. Reject assignment with overlapping dates
    ok, msg, _ = assignment.assign_employee_to_department(
        "EMP001", "DEP002", "06-15-2024", "Current"
    )
    assert not ok and "overlap" in msg.lower(), f"Test 7 Failed: {msg}"
    print(f"[PASS] Test 7: Reject overlapping assignment dates ({msg})")
    passed += 1

    # Assign non-overlapping: 07-01-2024 to Current
    ok, msg, asg2 = assignment.assign_employee_to_department(
        "EMP001", "DEP002", "07-01-2024", "Current"
    )
    assert ok, f"Setup failed: {msg}"

    # 8. Reject duplicate current department
    ok, msg, _ = assignment.assign_employee_to_department(
        "EMP001", "DEP002", "08-01-2024", "Current"
    )
    assert not ok and "already working in this department" in msg, f"Test 8 Failed: {msg}"
    print(f"[PASS] Test 8: Reject assignment to same current department ('{msg}')")
    passed += 1

    # 9. Allow assignment to a different department (Department Change)
    ok, msg = assignment.change_employee_department(
        emp_id="EMP001",
        new_dept_id="DEP003",
        close_end_date_str="09-30-2024",
        new_start_date_str="10-01-2024",
        new_end_date_str="Current"
    )
    assert ok, f"Test 9 Failed: {msg}"
    cur_asg = assignment.get_current_assignment("EMP001")
    assert cur_asg["Department ID"] == "DEP003", f"Expected DEP003, got {cur_asg['Department ID']}"
    print("[PASS] Test 9: Allow department change (DEP002 closed, DEP003 active)")
    passed += 1

    # 10. Allow returning to a previously used department
    ok, msg = assignment.change_employee_department(
        emp_id="EMP001",
        new_dept_id="DEP001",
        close_end_date_str="12-31-2024",
        new_start_date_str="01-01-2025",
        new_end_date_str="Current"
    )
    assert ok, f"Test 10 Failed: {msg}"
    cur_asg = assignment.get_current_assignment("EMP001")
    assert cur_asg["Department ID"] == "DEP001", f"Expected DEP001, got {cur_asg['Department ID']}"
    print("[PASS] Test 10: Allow employee to return to previously used department (EMP001 returned to DEP001 in 2025)")
    passed += 1

    # 11. Reject end date earlier than start date
    ok, msg, _ = assignment.assign_employee_to_department(
        "EMP002", "DEP001", "05-10-2024", "05-01-2024"
    )
    assert not ok and "cannot be earlier than start date" in msg.lower(), f"Test 11 Failed: {msg}"
    print(f"[PASS] Test 11: Reject end date earlier than start date ('{msg}')")
    passed += 1

    # Set up EMP002 and EMP003
    assignment.assign_employee_to_department("EMP002", "DEP003", "02-01-2024", "Current")
    assignment.assign_employee_to_department("EMP003", "DEP001", "03-01-2024", "05-31-2024")
    assignment.assign_employee_to_department("EMP003", "DEP002", "06-01-2024", "Current")

    # 12. Report for specific date
    ok, msg, res_date = reports.get_employees_working_on_date("05-15-2024")
    assert ok and len(res_date) == 3, f"Test 12 Failed: Expected 3, got {len(res_date)}"
    print(f"[PASS] Test 12: Report for specific date (05-15-2024 returned {len(res_date)} active employees)")
    passed += 1

    # 13. Report for date range
    ok, msg, res_range = reports.get_employees_working_in_date_range("01-01-2024", "12-31-2024")
    assert ok and len(res_range) >= 5, f"Test 13 Failed: Expected >= 5, got {len(res_range)}"
    print(f"[PASS] Test 13: Report for date range (01-01-2024 to 12-31-2024 returned {len(res_range)} assignments)")
    passed += 1

    # 14. Display multiple assignments for the same employee
    emp1_history = assignment.get_assignments_for_employee("EMP001")
    assert len(emp1_history) == 4, f"Test 14 Failed: Expected 4 assignments, got {len(emp1_history)}"
    print(f"[PASS] Test 14: Multiple assignments for same employee (EMP001 has {len(emp1_history)} assignments in history)")
    passed += 1

    # 15. Preserve data after restart
    emps_disk = read_records(EMP_FILE, EMP_HEADERS)
    depts_disk = read_records(DEPT_FILE, DEPT_HEADERS)
    asgs_disk = read_records(ASG_FILE, ASG_HEADERS)
    assert len(emps_disk) == 3 and len(depts_disk) == 3 and len(asgs_disk) >= 6
    print(f"[PASS] Test 15: Data persistence verified ({len(emps_disk)} emps, {len(depts_disk)} depts, {len(asgs_disk)} asgs)")
    passed += 1

    # 16. Prevent deletion of departments with history
    ok, msg = department.delete_department("DEP001")
    assert not ok and "existing assignment history" in msg.lower(), f"Test 16 Failed: {msg}"
    print(f"[PASS] Test 16: Prevent deletion of departments with history ('{msg}')")
    passed += 1

    print("\n=================================================================")
    print(f"ALL {passed}/{total} SPECIFICATION SCENARIOS PASSED WITH ZERO ERRORS!")
    print("=================================================================\n")


if __name__ == "__main__":
    test_custom_date_engine()
    test_full_system_scenarios()

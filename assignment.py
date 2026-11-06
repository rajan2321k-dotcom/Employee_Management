"""
assignment.py - Employee Department Assignment Module

Handles employee department assignments and transfers using CSV format
and custom manual date validation logic (zero built-in date libraries).
"""

import re
from typing import List, Dict, Optional, Tuple
from file_handler import (
    ASG_FILE,
    ASG_HEADERS,
    read_records,
    append_record,
    update_record,
)
from employee import get_employee_by_id
from department import get_department_by_id
from validation import (
    validate_date_format,
    validate_assignment_dates,
    compare_dates,
    check_current_department_duplicate,
    check_active_assignment_exists,
    check_assignment_overlap,
    MIN_DATE_TUPLE,
    MAX_DATE_TUPLE,
)


def get_all_assignments() -> List[Dict[str, str]]:
    """Retrieve all assignment records from employee_department.txt (CSV format)."""
    return read_records(ASG_FILE, ASG_HEADERS)


def get_assignments_for_employee(emp_id: str) -> List[Dict[str, str]]:
    """
    Retrieve all assignments for a specific employee,
    sorted chronologically by Start Date.
    """
    norm_id = emp_id.strip().upper()
    user_asgs = [
        asg for asg in get_all_assignments()
        if asg.get("Employee ID", "").strip().upper() == norm_id
    ]

    def sort_key(asg):
        s_str = asg.get("Start Date", "").strip()
        ok, _, s_tuple = validate_date_format(s_str)
        return s_tuple if ok and s_tuple else MIN_DATE_TUPLE

    user_asgs.sort(key=sort_key)
    return user_asgs


def get_current_assignment(emp_id: str) -> Optional[Dict[str, str]]:
    """
    Find the currently active assignment ('Current') for the employee.
    Returns None if the employee has no active assignment.
    """
    norm_id = emp_id.strip().upper()
    for asg in get_all_assignments():
        if (
            asg.get("Employee ID", "").strip().upper() == norm_id
            and asg.get("End Date", "").strip().upper() == "CURRENT"
        ):
            return asg
    return None


def generate_next_assignment_id() -> str:
    """
    Generate next unique Assignment ID: ASG001, ASG002, etc.
    """
    assignments = get_all_assignments()
    max_id = 0
    for asg in assignments:
        raw_id = asg.get("Assignment ID", "").strip()
        match = re.match(r"^ASG(\d+)$", raw_id, re.IGNORECASE)
        if match:
            num = int(match.group(1))
            if num > max_id:
                max_id = num
    next_num = max_id + 1
    return f"ASG{next_num:03d}"


def assign_employee_to_department(
    emp_id: str,
    dept_id: str,
    start_date_str: str,
    end_date_str: str = "Current",
    custom_asg_id: Optional[str] = None
) -> Tuple[bool, str, Optional[Dict[str, str]]]:
    """
    Assign an employee to a department with full validation:
    1. Employee must exist.
    2. Department must exist.
    3. Start Date and End Date format and logic (MM-DD-CCYY or Current, End >= Start).
    4. Duplicate Current Department Assignment check:
       'This employee is already working in this department.'
    5. An employee cannot have two active assignments at the same time.
    6. Overlapping assignments check via custom interval comparison.
    7. An employee can return to a department where they worked previously (provided dates do not overlap).
    """
    # 1. Verify Employee
    emp = get_employee_by_id(emp_id)
    if not emp:
        return False, f"Employee with ID '{emp_id}' does not exist.", None
    actual_emp_id = emp["Employee ID"]

    # 2. Verify Department
    dept = get_department_by_id(dept_id)
    if not dept:
        return False, f"Department with ID '{dept_id}' does not exist.", None
    actual_dept_id = dept["Department ID"]

    # 3. Validate Dates manually
    ok_dates, start_tuple, end_tuple, date_msg = validate_assignment_dates(start_date_str, end_date_str)
    if not ok_dates or not start_tuple or not end_tuple:
        return False, date_msg, None

    all_asgs = get_all_assignments()

    # 4. Check Duplicate Current Assignment
    is_dup, dup_msg = check_current_department_duplicate(actual_emp_id, actual_dept_id, all_asgs)
    if is_dup:
        return False, dup_msg, None

    # 5. Check if employee already has an active ongoing assignment ('Current')
    clean_end_str = "Current" if end_date_str.strip().upper() == "CURRENT" else end_date_str.strip()
    if clean_end_str == "Current":
        has_active, active_asg = check_active_assignment_exists(actual_emp_id, all_asgs)
        if has_active and active_asg:
            return (
                False,
                f"Employee already has an active assignment ({active_asg['Assignment ID']} in Department {active_asg['Department ID']}). "
                "An employee cannot have two active assignments at the same time. Please use 'Change Employee Department' to transfer them.",
                None,
            )

    # 6. Check Overlapping Assignments using manual overlap logic
    has_overlap, overlap_msg = check_assignment_overlap(
        actual_emp_id, start_tuple, end_tuple, all_asgs
    )
    if has_overlap:
        return False, overlap_msg, None

    # 7. Generate ID and Persist in CSV
    if custom_asg_id:
        asg_id = custom_asg_id.strip().upper()
    else:
        asg_id = generate_next_assignment_id()

    new_asg = {
        "Assignment ID": asg_id,
        "Employee ID": actual_emp_id,
        "Department ID": actual_dept_id,
        "Start Date": start_date_str.strip(),
        "End Date": clean_end_str,
    }

    success = append_record(ASG_FILE, ASG_HEADERS, new_asg)
    if success:
        return (
            True,
            f"Assignment {asg_id} created successfully for Employee {actual_emp_id} "
            f"in Department {actual_dept_id} ({start_date_str.strip()} to {clean_end_str}).",
            new_asg,
        )
    return False, "Failed to save assignment record.", None


def change_employee_department(
    emp_id: str,
    new_dept_id: str,
    close_end_date_str: str,
    new_start_date_str: str,
    new_end_date_str: str = "Current"
) -> Tuple[bool, str]:
    """
    Change an employee's department according to business rules:
    - Select existing employee.
    - Identify current department assignment.
    - Close current active assignment with an appropriate end date.
    - Create new assignment for the new department.
    - Validate new start date (must be strictly after closed assignment's end date).
    - Ensure no overlapping assignments across all past and new assignments.
    - Preserve complete previous assignment history.
    - If any validation fails, do not save an incomplete or incorrect assignment.
    """
    # 1. Verify Employee
    emp = get_employee_by_id(emp_id)
    if not emp:
        return False, f"Employee with ID '{emp_id}' does not exist."
    actual_emp_id = emp["Employee ID"]

    # 2. Find currently active assignment
    current_asg = get_current_assignment(actual_emp_id)
    if not current_asg:
        return (
            False,
            f"Employee {actual_emp_id} has no currently active assignment ('Current'). "
            "Please use 'Assign Employee to Department' to create a new assignment.",
        )

    current_dept_id = current_asg["Department ID"].strip()
    current_start_str = current_asg["Start Date"].strip()

    # 3. Verify new department exists
    dept = get_department_by_id(new_dept_id)
    if not dept:
        return False, f"Department with ID '{new_dept_id}' does not exist."
    actual_new_dept_id = dept["Department ID"]

    # Prevent moving to the same current department
    if actual_new_dept_id.upper() == current_dept_id.upper():
        return False, "This employee is already working in this department."

    # 4. Validate closing end date for current assignment manually
    ok_close, close_msg, close_tuple = validate_date_format(close_end_date_str)
    if not ok_close or not close_tuple:
        return False, f"Invalid current assignment closing date: {close_msg}"

    ok_cur_start, _, cur_start_tuple = validate_date_format(current_start_str)
    if not ok_cur_start or not cur_start_tuple:
        return False, f"Corrupted current assignment start date: {current_start_str}"

    if compare_dates(close_tuple, cur_start_tuple) < 0:
        return (
            False,
            f"Closing end date ({close_end_date_str.strip()}) cannot be earlier than "
            f"current assignment start date ({current_start_str}).",
        )

    # 5. Validate new assignment start date manually
    ok_new_start, new_start_msg, new_start_tuple = validate_date_format(new_start_date_str)
    if not ok_new_start or not new_start_tuple:
        return False, f"Invalid new assignment start date: {new_start_msg}"

    # An employee cannot work in two departments at the same time:
    # new start date must be strictly after the closing date (new_start_tuple > close_tuple)
    if compare_dates(new_start_tuple, close_tuple) <= 0:
        return (
            False,
            f"New assignment start date ({new_start_date_str.strip()}) must be after the "
            f"closing end date ({close_end_date_str.strip()}) of the previous department.",
        )

    # 6. Validate new assignment end date manually
    ok_new_dates, _, new_end_tuple, new_end_msg = validate_assignment_dates(
        new_start_date_str, new_end_date_str
    )
    if not ok_new_dates or not new_end_tuple:
        return False, new_end_msg

    # 7. Check for overlap against all other assignments (excluding current_asg)
    all_asgs = get_all_assignments()
    has_overlap, overlap_msg = check_assignment_overlap(
        actual_emp_id,
        new_start_tuple,
        new_end_tuple,
        all_asgs,
        exclude_asg_id=current_asg["Assignment ID"],
    )
    if has_overlap:
        return False, overlap_msg

    # 8. Perform update and insert atomically
    # A. Update existing assignment: set End Date
    updated = update_record(
        ASG_FILE,
        ASG_HEADERS,
        "Assignment ID",
        current_asg["Assignment ID"],
        {"End Date": close_end_date_str.strip()},
    )
    if not updated:
        return False, "Failed to update current assignment end date."

    # B. Add new assignment
    new_asg_id = generate_next_assignment_id()
    clean_new_end = "Current" if new_end_date_str.strip().upper() == "CURRENT" else new_end_date_str.strip()
    new_asg = {
        "Assignment ID": new_asg_id,
        "Employee ID": actual_emp_id,
        "Department ID": actual_new_dept_id,
        "Start Date": new_start_date_str.strip(),
        "End Date": clean_new_end,
    }

    added = append_record(ASG_FILE, ASG_HEADERS, new_asg)
    if not added:
        return False, "Failed to create new assignment record."

    return (
        True,
        f"Department changed successfully!\n"
        f"  - Closed Assignment {current_asg['Assignment ID']}: Department {current_dept_id} "
        f"ended on {close_end_date_str.strip()}.\n"
        f"  - Created Assignment {new_asg_id}: Department {actual_new_dept_id} "
        f"started on {new_start_date_str.strip()} ({clean_new_end}).",
    )

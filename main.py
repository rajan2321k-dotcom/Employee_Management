"""
main.py - Main Console Application & Menu Interface

Entry point for the Employee & Department Management System.
Implements the exact 7-option main menu with sequential immediate validation:
1. Add Employee
2. Add Department
3. Assign Employee to Department
4. Change Employee Department
5. View Employees Working on a Date
6. View Employees Working Within a Date Range
7. Exit
"""

import sys
import os

# Ensure local modules can be imported directly
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from file_handler import (
    initialize_storage_files,
    format_ascii_table,
    EMP_HEADERS,
    DEPT_HEADERS,
    ASG_HEADERS,
)
import employee
import department
import assignment
import reports
from validation import (
    validate_employee_name,
    validate_age,
    validate_location_field,
    validate_department_description,
    validate_date_format,
    compare_dates,
)


def print_banner(title: str):
    """Print a clean section banner."""
    line = "=" * max(60, len(title) + 8)
    print(f"\n{line}")
    print(f"   {title}")
    print(f"{line}")


def print_header(title: str):
    """Print an operation header."""
    print(f"\n--- {title} ---")


def safe_input(prompt: str) -> str:
    """Read console input safely handling EOF / KeyboardInterrupt."""
    try:
        return input(prompt).strip()
    except (KeyboardInterrupt, EOFError):
        print("\n\nOperation interrupted by user.")
        return ""


# ==============================================================================
# FEATURE 1: ADD EMPLOYEE (SEQUENTIAL VALIDATION)
# ==============================================================================

def menu_add_employee():
    """
    Collect employee details sequentially.
    Validate each input immediately after receiving it.
    If invalid, display an error and STOP collecting the remaining details.
    Do not ask for Age, City, State, or Country.
    """
    print_header("ADD EMPLOYEE")

    # 1. Collect & Validate Name immediately
    name = safe_input("Enter Employee Name: ")
    ok_name, msg_name = validate_employee_name(name)
    if not ok_name:
        print(f"[ERROR] {msg_name}")
        return  # STOP collecting remaining details

    # 2. Collect & Validate Age immediately
    age_input = safe_input("Enter Age (18 - 65): ")
    ok_age, msg_age, val_age = validate_age(age_input)
    if not ok_age:
        print(f"[ERROR] {msg_age}")
        return  # STOP collecting remaining details

    # 3. Collect & Validate City immediately
    city = safe_input("Enter City: ")
    ok_city, msg_city = validate_location_field(city, "City")
    if not ok_city:
        print(f"[ERROR] {msg_city}")
        return  # STOP collecting remaining details

    # 4. Collect & Validate State immediately
    state = safe_input("Enter State: ")
    ok_state, msg_state = validate_location_field(state, "State")
    if not ok_state:
        print(f"[ERROR] {msg_state}")
        return  # STOP collecting remaining details

    # 5. Collect & Validate Country immediately
    country = safe_input("Enter Country: ")
    ok_country, msg_country = validate_location_field(country, "Country")
    if not ok_country:
        print(f"[ERROR] {msg_country}")
        return  # STOP collecting remaining details

    # Save employee record after all details are validated
    success, message, new_record = employee.add_employee(
        name=name, age_input=val_age, city=city, state=state, country=country
    )
    if success and new_record:
        print(f"\n[SUCCESS] {message}")
        print("\nSaved Employee Record (CSV stored, ASCII display):")
        print(format_ascii_table(EMP_HEADERS, [new_record]))
    else:
        print(f"\n[ERROR] {message}")


# ==============================================================================
# FEATURE 2: ADD DEPARTMENT
# ==============================================================================

def menu_add_department():
    """
    Collect department description and validate immediately.
    Automatically generates Department ID and saves to department.txt.
    """
    print_header("ADD DEPARTMENT")

    description = safe_input("Enter Department Description: ")
    ok_desc, msg_desc = validate_department_description(description)
    if not ok_desc:
        print(f"[ERROR] {msg_desc}")
        return  # STOP immediately

    success, message, new_record = department.add_department(description)
    if success and new_record:
        print(f"\n[SUCCESS] {message}")
        print("\nSaved Department Record (CSV stored, ASCII display):")
        print(format_ascii_table(DEPT_HEADERS, [new_record]))
    else:
        print(f"\n[ERROR] {message}")


# ==============================================================================
# FEATURE 3: ASSIGN EMPLOYEE TO DEPARTMENT
# ==============================================================================

def menu_assign_employee():
    """
    Assign an employee to a department.
    Validates each input immediately before requesting the next input.
    """
    print_header("ASSIGN EMPLOYEE TO DEPARTMENT")

    # 1. Collect & Validate Employee ID immediately
    emp_id = safe_input("Enter Employee ID (e.g., EMP001): ")
    if not emp_id:
        print("[ERROR] Employee ID cannot be empty.")
        return
    existing_emp = employee.get_employee_by_id(emp_id)
    if not existing_emp:
        print(f"[ERROR] Employee with ID '{emp_id}' does not exist.")
        return

    # 2. Collect & Validate Department ID immediately
    dept_id = safe_input("Enter Department ID (e.g., DEP001): ")
    if not dept_id:
        print("[ERROR] Department ID cannot be empty.")
        return
    existing_dept = department.get_department_by_id(dept_id)
    if not existing_dept:
        print(f"[ERROR] Department with ID '{dept_id}' does not exist.")
        return

    # 3. Collect & Validate Start Date immediately
    start_date = safe_input("Enter Start Date (MM-DD-CCYY, e.g., 01-15-2024): ")
    ok_start, msg_start, start_tuple = validate_date_format(start_date)
    if not ok_start or not start_tuple:
        print(f"[ERROR] Start Date error: {msg_start}")
        return

    # 4. Collect & Validate End Date immediately
    end_date = safe_input("Enter End Date (MM-DD-CCYY or press Enter for 'Current'): ")
    if not end_date:
        end_date = "Current"

    if end_date.strip().upper() != "CURRENT":
        ok_end, msg_end, end_tuple = validate_date_format(end_date)
        if not ok_end or not end_tuple:
            print(f"[ERROR] End Date error: {msg_end}")
            return
        if compare_dates(end_tuple, start_tuple) < 0:
            print(f"[ERROR] End Date ({end_date.strip()}) must be greater than or equal to Start Date ({start_date.strip()}).")
            return

    # Execute assignment with business rules (active assignment check, overlap check)
    success, message, new_record = assignment.assign_employee_to_department(
        emp_id=emp_id,
        dept_id=dept_id,
        start_date_str=start_date,
        end_date_str=end_date,
    )

    if success and new_record:
        print(f"\n[SUCCESS] {message}")
        print("\nSaved Assignment Record (CSV stored, ASCII display):")
        print(format_ascii_table(ASG_HEADERS, [new_record]))
    else:
        print(f"\n[ERROR] {message}")


# ==============================================================================
# FEATURE 4: CHANGE EMPLOYEE DEPARTMENT
# ==============================================================================

def menu_change_employee_department():
    """
    Change an employee's department:
    - Select existing employee.
    - Identify current department assignment.
    - Collect closing date of current assignment.
    - Collect new Department ID.
    - Collect new assignment Start Date.
    - Collect new assignment End Date.
    - Validate each input immediately before requesting the next input.
    """
    print_header("CHANGE EMPLOYEE DEPARTMENT")

    # 1. Select & Validate Employee ID
    emp_id = safe_input("Enter Employee ID (e.g., EMP001): ")
    if not emp_id:
        print("[ERROR] Employee ID cannot be empty.")
        return
    emp = employee.get_employee_by_id(emp_id)
    if not emp:
        print(f"[ERROR] Employee with ID '{emp_id}' does not exist.")
        return

    # 2. Identify current active assignment
    current = assignment.get_current_assignment(emp_id)
    if not current:
        print(f"[ERROR] Employee '{emp_id}' has no currently active assignment ('Current').")
        print("Use 'Assign Employee to Department' to create an initial assignment.")
        return

    cur_dept = department.get_department_by_id(current['Department ID'])
    cur_desc = cur_dept['Description'] if cur_dept else "Unknown"

    print(f"\nCurrent Active Assignment for {emp['Name']} ({emp_id}):")
    print(f"  Assignment ID: {current['Assignment ID']}")
    print(f"  Department:    {current['Department ID']} - {cur_desc}")
    print(f"  Start Date:    {current['Start Date']}")
    print(f"  End Date:      Current\n")

    # 3. Collect Closing Date for current assignment
    close_end_date = safe_input("Enter Closing Date for Current Department (MM-DD-CCYY): ")
    ok_close, msg_close, close_tuple = validate_date_format(close_end_date)
    if not ok_close or not close_tuple:
        print(f"[ERROR] Closing Date error: {msg_close}")
        return

    ok_cur_start, _, cur_start_tuple = validate_date_format(current["Start Date"])
    if ok_cur_start and cur_start_tuple and compare_dates(close_tuple, cur_start_tuple) < 0:
        print(f"[ERROR] Closing date ({close_end_date.strip()}) cannot be earlier than current assignment start date ({current['Start Date']}).")
        return

    # 4. Collect New Department ID
    new_dept_id = safe_input("Enter New Department ID (e.g., DEP002): ")
    if not new_dept_id:
        print("[ERROR] New Department ID cannot be empty.")
        return
    new_dept = department.get_department_by_id(new_dept_id)
    if not new_dept:
        print(f"[ERROR] Department with ID '{new_dept_id}' does not exist.")
        return

    if new_dept["Department ID"].upper() == current["Department ID"].strip().upper():
        print("[ERROR] This employee is already working in this department.")
        return

    # 5. Collect New Assignment Start Date
    new_start_date = safe_input("Enter Start Date for New Department (MM-DD-CCYY): ")
    ok_new_start, msg_new_start, new_start_tuple = validate_date_format(new_start_date)
    if not ok_new_start or not new_start_tuple:
        print(f"[ERROR] New Start Date error: {msg_new_start}")
        return

    if compare_dates(new_start_tuple, close_tuple) <= 0:
        print(f"[ERROR] New assignment start date ({new_start_date.strip()}) must be after the closing date ({close_end_date.strip()}) of the previous department.")
        return

    # 6. Collect New Assignment End Date
    new_end_date = safe_input("Enter End Date for New Department (MM-DD-CCYY or press Enter for 'Current'): ")
    if not new_end_date:
        new_end_date = "Current"

    if new_end_date.strip().upper() != "CURRENT":
        ok_new_end, msg_new_end, new_end_tuple = validate_date_format(new_end_date)
        if not ok_new_end or not new_end_tuple:
            print(f"[ERROR] New End Date error: {msg_new_end}")
            return
        if compare_dates(new_end_tuple, new_start_tuple) < 0:
            print(f"[ERROR] New End Date ({new_end_date.strip()}) must be greater than or equal to New Start Date ({new_start_date.strip()}).")
            return

    # Execute department transfer atomically
    success, message = assignment.change_employee_department(
        emp_id=emp_id,
        new_dept_id=new_dept_id,
        close_end_date_str=close_end_date,
        new_start_date_str=new_start_date,
        new_end_date_str=new_end_date,
    )

    if success:
        print(f"\n[SUCCESS] {message}")
    else:
        print(f"\n[ERROR] {message}")


# ==============================================================================
# FEATURE 5: EMPLOYEES WORKING ON A PARTICULAR DATE
# ==============================================================================

def menu_view_employees_on_date():
    """
    Ask for date in MM-DD-CCYY format.
    Validate date immediately.
    Display all employees working in a department on that date in an ASCII table.
    """
    print_header("VIEW EMPLOYEES WORKING ON A DATE")
    date_str = safe_input("Enter Date (MM-DD-CCYY, e.g., 01-20-2024): ")
    if not date_str:
        print("[ERROR] Date cannot be empty.")
        return

    ok_d, msg_d, _ = validate_date_format(date_str)
    if not ok_d:
        print(f"[ERROR] {msg_d}")
        return

    success, message, results = reports.get_employees_working_on_date(date_str)
    if not success:
        print(f"\n[ERROR] {message}")
        return

    print("\n---------------------------------")
    print(f"Employees Working On: {date_str.strip()}")
    print("---------------------------------")
    if not results:
        print("No employees were working on this date.")
        print("---------------------------------")
        return

    headers = ["Employee Name", "Department"]
    print(format_ascii_table(headers, results))
    print(f"Total Employees: {len(results)}")


# ==============================================================================
# FEATURE 6: EMPLOYEES WORKING WITHIN A DATE RANGE
# ==============================================================================

def menu_view_employees_in_date_range():
    """
    Ask for Start Date and End Date.
    Validate both dates immediately (End Date >= Start Date).
    Display all overlapping assignments in an ASCII table.
    """
    print_header("VIEW EMPLOYEES WORKING WITHIN A DATE RANGE")

    start_date = safe_input("Enter Start Date (MM-DD-CCYY, e.g., 01-01-2024): ")
    ok_s, msg_s, start_tuple = validate_date_format(start_date)
    if not ok_s or not start_tuple:
        print(f"[ERROR] Start Date error: {msg_s}")
        return

    end_date = safe_input("Enter End Date (MM-DD-CCYY, e.g., 12-31-2024): ")
    ok_e, msg_e, end_tuple = validate_date_format(end_date)
    if not ok_e or not end_tuple:
        print(f"[ERROR] End Date error: {msg_e}")
        return

    if compare_dates(end_tuple, start_tuple) < 0:
        print(f"[ERROR] End Date ({end_date.strip()}) must be greater than or equal to Start Date ({start_date.strip()}).")
        return

    success, message, results = reports.get_employees_working_in_date_range(start_date, end_date)
    if not success:
        print(f"\n[ERROR] {message}")
        return

    print("\n-----------------------------------------------------------------------------------------")
    print(f"Employees Working Within Date Range: {start_date.strip()} to {end_date.strip()}")
    print("-----------------------------------------------------------------------------------------")
    if not results:
        print("No employee assignments found overlapping the requested date range.")
        print("-----------------------------------------------------------------------------------------")
        return

    headers = ["Employee Name", "Department", "Assignment Start Date", "Assignment End Date"]
    print(format_ascii_table(headers, results))
    print(f"Total Overlapping Assignments Found: {len(results)}")


# ==============================================================================
# MAIN APPLICATION LOOP
# ==============================================================================

def main():
    """
    Main menu loop with EXACTLY 7 requested options.
    """
    # Ensure all CSV text files exist
    initialize_storage_files()

    while True:
        print_banner("EMPLOYEE & DEPARTMENT MANAGEMENT SYSTEM")
        print("1. Add Employee")
        print("2. Add Department")
        print("3. Assign Employee to Department")
        print("4. Change Employee Department")
        print("5. View Employees Working on a Date")
        print("6. View Employees Working Within a Date Range")
        print("7. Exit")
        print("====================================================")

        choice = safe_input("Enter your choice (1-7): ")
        if choice == '1':
            menu_add_employee()
        elif choice == '2':
            menu_add_department()
        elif choice == '3':
            menu_assign_employee()
        elif choice == '4':
            menu_change_employee_department()
        elif choice == '5':
            menu_view_employees_on_date()
        elif choice == '6':
            menu_view_employees_in_date_range()
        elif choice == '7':
            print("\nThank you for using the Employee & Department Management System. Goodbye!\n")
            sys.exit(0)
        else:
            print("[ERROR] Invalid choice. Please enter a valid number (1-7).")


if __name__ == "__main__":
    main()

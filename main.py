

import sys
import os

# Ensure local modules can be imported directly
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from file_handler import (
    initialize_storage_files,
    format_ascii_table,
    EMP_FILE,
    EMP_HEADERS,
    DEPT_FILE,
    DEPT_HEADERS,
    ASG_FILE,
    ASG_HEADERS,
    write_records,
)
import employee
import department
import assignment
import reports
from validation import validate_date_format


def clear_console():
    """Clear terminal screen cross-platform (optional, kept simple for compatibility)."""
    pass


def print_banner(title: str):
    """Print a clean section banner."""
    line = "=" * max(60, len(title) + 8)
    print(f"\n{line}")
    print(f"   {title}")
    print(f"{line}")


def print_header(title: str):
    """Print a submenu header."""
    print(f"\n--- {title} ---")


def safe_input(prompt: str) -> str:
    """Read console input safely handling EOF / KeyboardInterrupt."""
    try:
        return input(prompt).strip()
    except (KeyboardInterrupt, EOFError):
        print("\n\nOperation interrupted by user.")
        return ""



def initialize_sample_data(prompt_user: bool = True) -> bool:
   
    if prompt_user:
        print_header("INITIALIZE SAMPLE TEST DATA")
        print("This will replace current data files with the standardized sample dataset.")
        confirm = safe_input("Are you sure you want to initialize sample test data? (y/n): ")
        if confirm.lower() != 'y':
            print("Operation cancelled. Existing records remain unchanged.")
            return False

    sample_employees = [
        {"Employee ID": "EMP001", "Name": "Rajan", "Age": "21", "City": "Coimbatore", "State": "Tamil Nadu", "Country": "India"},
        {"Employee ID": "EMP002", "Name": "Arun", "Age": "25", "City": "Chennai", "State": "Tamil Nadu", "Country": "India"},
        {"Employee ID": "EMP003", "Name": "Kumar", "Age": "30", "City": "Madurai", "State": "Tamil Nadu", "Country": "India"},
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

    print("\n[SUCCESS] Sample test data loaded successfully into emp.txt, department.txt, and employee_department.txt!")
    return True



def menu_add_employee():
    print_header("ADD NEW EMPLOYEE")
    name = safe_input("Enter Employee Name: ")
    if not name:
        print("[ERROR] Employee name cannot be empty.")
        return

    age_input = safe_input("Enter Age (18 - 65): ")
    city = safe_input("Enter City: ")
    state = safe_input("Enter State: ")
    country = safe_input("Enter Country: ")

    success, message, new_record = employee.add_employee(
        name=name, age_input=age_input, city=city, state=state, country=country
    )
    if success and new_record:
        print(f"\n[SUCCESS] {message}")
        print(format_ascii_table(EMP_HEADERS, [new_record]))
    else:
        print(f"\n[ERROR] {message}")


def menu_view_all_employees():
    print_header("ALL REGISTERED EMPLOYEES")
    records = employee.get_all_employees()
    if not records:
        print("No employee records found in emp.txt.")
        return
    print(format_ascii_table(EMP_HEADERS, records))
    print(f"Total Employees: {len(records)}")


def menu_search_employee():
    print_header("SEARCH EMPLOYEE")
    query = safe_input("Enter search keyword (Employee ID or Name): ")
    if not query:
        print("[ERROR] Search query cannot be empty.")
        return

    results = employee.search_employees(query)
    if not results:
        print(f"No employees found matching '{query}'.")
        return

    print(f"\nSearch results for '{query}':")
    print(format_ascii_table(EMP_HEADERS, results))
    print(f"Matches found: {len(results)}")


def menu_update_employee():
    print_header("UPDATE EMPLOYEE DETAILS")
    emp_id = safe_input("Enter Employee ID to update: ")
    if not emp_id:
        print("[ERROR] Employee ID cannot be empty.")
        return

    existing = employee.get_employee_by_id(emp_id)
    if not existing:
        print(f"[ERROR] Employee '{emp_id}' not found.")
        return

    print("\nCurrent Employee Details:")
    print(format_ascii_table(EMP_HEADERS, [existing]))
    print("Press Enter to keep current value.\n")

    name = safe_input(f"Name [{existing['Name']}]: ")
    age = safe_input(f"Age [{existing['Age']}]: ")
    city = safe_input(f"City [{existing['City']}]: ")
    state = safe_input(f"State [{existing['State']}]: ")
    country = safe_input(f"Country [{existing['Country']}]: ")

    success, message = employee.update_employee(
        emp_id=emp_id,
        name=name if name else None,
        age_input=age if age else None,
        city=city if city else None,
        state=state if state else None,
        country=country if country else None,
    )

    if success:
        print(f"\n[SUCCESS] {message}")
        updated = employee.get_employee_by_id(emp_id)
        if updated:
            print(format_ascii_table(EMP_HEADERS, [updated]))
    else:
        print(f"\n[ERROR] {message}")


def menu_delete_employee():
    print_header("DELETE EMPLOYEE")
    emp_id = safe_input("Enter Employee ID to delete: ")
    if not emp_id:
        print("[ERROR] Employee ID cannot be empty.")
        return

    existing = employee.get_employee_by_id(emp_id)
    if not existing:
        print(f"[ERROR] Employee '{emp_id}' not found.")
        return

    print("\nEmployee to delete:")
    print(format_ascii_table(EMP_HEADERS, [existing]))

    confirm = safe_input(f"Are you sure you want to delete {existing['Employee ID']} ({existing['Name']})? (y/n): ")
    if confirm.lower() != 'y':
        print("Deletion cancelled.")
        return

    success, message = employee.delete_employee(emp_id)
    if success:
        print(f"\n[SUCCESS] {message}")
    else:
        print(f"\n[ERROR] {message}")


def employee_management_menu():
    while True:
        print_banner("EMPLOYEE MANAGEMENT")
        print("1. Add Employee")
        print("2. View All Employees")
        print("3. Search Employee")
        print("4. Update Employee Details")
        print("5. Delete Employee")
        print("6. Back to Main Menu")

        choice = safe_input("Enter your choice (1-6): ")
        if choice == '1':
            menu_add_employee()
        elif choice == '2':
            menu_view_all_employees()
        elif choice == '3':
            menu_search_employee()
        elif choice == '4':
            menu_update_employee()
        elif choice == '5':
            menu_delete_employee()
        elif choice == '6':
            break
        else:
            print("[ERROR] Invalid choice. Please enter a number between 1 and 6.")



# SUBMENU 2: DEPARTMENT MANAGEMENT


def menu_add_department():
    print_header("ADD NEW DEPARTMENT")
    desc = safe_input("Enter Department Description: ")
    if not desc:
        print("[ERROR] Department description cannot be empty.")
        return

    success, message, new_record = department.add_department(desc)
    if success and new_record:
        print(f"\n[SUCCESS] {message}")
        print(format_ascii_table(DEPT_HEADERS, [new_record]))
    else:
        print(f"\n[ERROR] {message}")


def menu_view_all_departments():
    print_header("ALL DEPARTMENTS")
    records = department.get_all_departments()
    if not records:
        print("No departments found in department.txt.")
        return
    print(format_ascii_table(DEPT_HEADERS, records))
    print(f"Total Departments: {len(records)}")


def menu_search_department():
    print_header("SEARCH DEPARTMENT")
    query = safe_input("Enter search keyword (Department ID or Description): ")
    if not query:
        print("[ERROR] Search query cannot be empty.")
        return

    results = department.search_departments(query)
    if not results:
        print(f"No departments found matching '{query}'.")
        return

    print(f"\nSearch results for '{query}':")
    print(format_ascii_table(DEPT_HEADERS, results))
    print(f"Matches found: {len(results)}")


def menu_update_department():
    print_header("UPDATE DEPARTMENT")
    dept_id = safe_input("Enter Department ID to update: ")
    if not dept_id:
        print("[ERROR] Department ID cannot be empty.")
        return

    existing = department.get_department_by_id(dept_id)
    if not existing:
        print(f"[ERROR] Department '{dept_id}' not found.")
        return

    print("\nCurrent Department Details:")
    print(format_ascii_table(DEPT_HEADERS, [existing]))

    new_desc = safe_input(f"New Description [{existing['Description']}]: ")
    if not new_desc:
        print("No changes made.")
        return

    success, message = department.update_department(dept_id, new_desc)
    if success:
        print(f"\n[SUCCESS] {message}")
        updated = department.get_department_by_id(dept_id)
        if updated:
            print(format_ascii_table(DEPT_HEADERS, [updated]))
    else:
        print(f"\n[ERROR] {message}")


def menu_delete_department():
    print_header("DELETE DEPARTMENT")
    dept_id = safe_input("Enter Department ID to delete: ")
    if not dept_id:
        print("[ERROR] Department ID cannot be empty.")
        return

    existing = department.get_department_by_id(dept_id)
    if not existing:
        print(f"[ERROR] Department '{dept_id}' not found.")
        return

    print("\nDepartment to delete:")
    print(format_ascii_table(DEPT_HEADERS, [existing]))

    confirm = safe_input(f"Are you sure you want to delete {existing['Department ID']} ({existing['Description']})? (y/n): ")
    if confirm.lower() != 'y':
        print("Deletion cancelled.")
        return

    success, message = department.delete_department(dept_id)
    if success:
        print(f"\n[SUCCESS] {message}")
    else:
        print(f"\n[ERROR] {message}")


def department_management_menu():
    while True:
        print_banner("DEPARTMENT MANAGEMENT")
        print("1. Add Department")
        print("2. View All Departments")
        print("3. Search Department")
        print("4. Update Department")
        print("5. Delete Department")
        print("6. Back to Main Menu")

        choice = safe_input("Enter your choice (1-6): ")
        if choice == '1':
            menu_add_department()
        elif choice == '2':
            menu_view_all_departments()
        elif choice == '3':
            menu_search_department()
        elif choice == '4':
            menu_update_department()
        elif choice == '5':
            menu_delete_department()
        elif choice == '6':
            break
        else:
            print("[ERROR] Invalid choice. Please enter a number between 1 and 6.")



# SUBMENU 3: EMPLOYEE DEPARTMENT ASSIGNMENT


def menu_assign_employee():
    print_header("ASSIGN EMPLOYEE TO DEPARTMENT")
    emp_id = safe_input("Enter Employee ID (e.g., EMP001): ")
    if not emp_id:
        print("[ERROR] Employee ID cannot be empty.")
        return

    dept_id = safe_input("Enter Department ID (e.g., DEP001): ")
    if not dept_id:
        print("[ERROR] Department ID cannot be empty.")
        return

    start_date = safe_input("Enter Start Date (MM-DD-CCYY, e.g., 01-15-2024): ")
    end_date = safe_input("Enter End Date (MM-DD-CCYY or press Enter for 'Current'): ")
    if not end_date:
        end_date = "Current"

    success, message, new_record = assignment.assign_employee_to_department(
        emp_id=emp_id,
        dept_id=dept_id,
        start_date_str=start_date,
        end_date_str=end_date,
    )

    if success and new_record:
        print(f"\n[SUCCESS] {message}")
        print(format_ascii_table(ASG_HEADERS, [new_record]))
    else:
        print(f"\n[ERROR] {message}")


def menu_change_employee_department():
    print_header("CHANGE EMPLOYEE DEPARTMENT")
    emp_id = safe_input("Enter Employee ID: ")
    if not emp_id:
        print("[ERROR] Employee ID cannot be empty.")
        return

    current = assignment.get_current_assignment(emp_id)
    if not current:
        print(f"[ERROR] Employee '{emp_id}' has no currently active assignment ('Current').")
        print("Use 'Assign Employee to Department' to create an initial assignment.")
        return

    cur_dept = department.get_department_by_id(current['Department ID'])
    cur_desc = cur_dept['Description'] if cur_dept else "Unknown"

    print(f"\nCurrent Active Assignment for Employee {emp_id}:")
    print(f"  Assignment ID: {current['Assignment ID']}")
    print(f"  Department:    {current['Department ID']} - {cur_desc}")
    print(f"  Start Date:    {current['Start Date']}")
    print(f"  End Date:      Current\n")

    new_dept_id = safe_input("Enter New Department ID (e.g., DEP002): ")
    if not new_dept_id:
        print("[ERROR] New Department ID cannot be empty.")
        return

    close_end_date = safe_input("Enter Closing End Date for Current Department (MM-DD-CCYY): ")
    new_start_date = safe_input("Enter Start Date for New Department (MM-DD-CCYY): ")
    new_end_date = safe_input("Enter End Date for New Department (MM-DD-CCYY or press Enter for 'Current'): ")
    if not new_end_date:
        new_end_date = "Current"

    success, message = assignment.change_employee_department(
        emp_id=emp_id,
        new_dept_id=new_dept_id,
        close_end_date_str=close_end_date,
        new_start_date_str=new_start_date,
        new_end_date_str=new_end_date,
    )

    if success:
        print(f"\n[SUCCESS] {message}")
        print("\nUpdated Assignment History for Employee:")
        menu_view_employee_history(emp_id)
    else:
        print(f"\n[ERROR] {message}")


def menu_view_employee_history(emp_id_arg: str = ""):
    if not emp_id_arg:
        print_header("VIEW EMPLOYEE ASSIGNMENT HISTORY")
        emp_id = safe_input("Enter Employee ID: ")
    else:
        emp_id = emp_id_arg

    if not emp_id:
        print("[ERROR] Employee ID cannot be empty.")
        return

    emp = employee.get_employee_by_id(emp_id)
    emp_name = emp["Name"] if emp else "Unknown"

    history = assignment.get_assignments_for_employee(emp_id)
    if not history:
        print(f"No assignment history found for Employee '{emp_id}'.")
        return

    # Add Department Description for enhanced clarity
    all_depts = {d["Department ID"]: d["Description"] for d in department.get_all_departments()}
    display_records = []
    for h in history:
        dept_desc = all_depts.get(h.get("Department ID", ""), "")
        display_records.append({
            "Assignment ID": h.get("Assignment ID", ""),
            "Employee ID": h.get("Employee ID", ""),
            "Department ID": h.get("Department ID", ""),
            "Department": dept_desc,
            "Start Date": h.get("Start Date", ""),
            "End Date": h.get("End Date", ""),
        })

    headers = ["Assignment ID", "Employee ID", "Department ID", "Department", "Start Date", "End Date"]
    print(f"\nAssignment History for: {emp_id} ({emp_name})")
    print(format_ascii_table(headers, display_records))


def menu_view_current_department(emp_id_arg: str = ""):
    if not emp_id_arg:
        print_header("VIEW CURRENT DEPARTMENT OF EMPLOYEE")
        emp_id = safe_input("Enter Employee ID (or press Enter to view all active): ")
    else:
        emp_id = emp_id_arg

    all_depts = {d["Department ID"]: d["Description"] for d in department.get_all_departments()}
    all_emps = {e["Employee ID"]: e["Name"] for e in employee.get_all_employees()}

    if emp_id:
        current = assignment.get_current_assignment(emp_id)
        if not current:
            emp = employee.get_employee_by_id(emp_id)
            if not emp:
                print(f"[ERROR] Employee '{emp_id}' does not exist.")
            else:
                print(f"Employee {emp_id} ({emp['Name']}) currently has no active assignment ('Current').")
            return

        dept_id = current.get("Department ID", "")
        dept_desc = all_depts.get(dept_id, "Unknown")
        emp_name = all_emps.get(current["Employee ID"], "Unknown")

        rec = [{
            "Employee ID": current["Employee ID"],
            "Employee Name": emp_name,
            "Department ID": dept_id,
            "Department": dept_desc,
            "Start Date": current["Start Date"],
            "End Date": current["End Date"],
        }]
        headers = ["Employee ID", "Employee Name", "Department ID", "Department", "Start Date", "End Date"]
        print(f"\nCurrent Department for {emp_id}:")
        print(format_ascii_table(headers, rec))
    else:
        # Show all employees with active assignment
        assignments = assignment.get_all_assignments()
        active = [a for a in assignments if a.get("End Date", "").strip().upper() == "CURRENT"]
        if not active:
            print("No employees currently have active assignments.")
            return

        display_records = []
        for a in active:
            e_id = a.get("Employee ID", "")
            d_id = a.get("Department ID", "")
            display_records.append({
                "Employee ID": e_id,
                "Employee Name": all_emps.get(e_id, "Unknown"),
                "Department ID": d_id,
                "Department": all_depts.get(d_id, "Unknown"),
                "Start Date": a.get("Start Date", ""),
                "End Date": a.get("End Date", ""),
            })

        headers = ["Employee ID", "Employee Name", "Department ID", "Department", "Start Date", "End Date"]
        print("\nAll Currently Active Employee Assignments:")
        print(format_ascii_table(headers, display_records))
        print(f"Total Active Employees: {len(display_records)}")


def assignment_menu():
    while True:
        print_banner("EMPLOYEE DEPARTMENT ASSIGNMENT")
        print("1. Assign Employee to Department")
        print("2. Change Employee Department")
        print("3. View Employee Assignment History")
        print("4. View Current Department of Employee")
        print("5. Back to Main Menu")

        choice = safe_input("Enter your choice (1-5): ")
        if choice == '1':
            menu_assign_employee()
        elif choice == '2':
            menu_change_employee_department()
        elif choice == '3':
            menu_view_employee_history()
        elif choice == '4':
            menu_view_current_department()
        elif choice == '5':
            break
        else:
            print("[ERROR] Invalid choice. Please enter a number between 1 and 5.")


# ==============================================================================
# REPORTS (MAIN MENU OPTIONS 4 & 5)
# ==============================================================================

def menu_report_specific_date():
    print_header("VIEW EMPLOYEES WORKING ON A SPECIFIC DATE")
    date_str = safe_input("Enter date (MM-DD-CCYY, e.g., 01-20-2024): ")
    if not date_str:
        print("[ERROR] Date cannot be empty.")
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

    # Formatted display matching both simple and detailed view
    display_records = [
        {
            "Employee ID": r["Employee ID"],
            "Employee Name": r["Employee Name"],
            "Department ID": r["Department ID"],
            "Department": r["Department"],
        }
        for r in results
    ]
    headers = ["Employee ID", "Employee Name", "Department ID", "Department"]
    print(format_ascii_table(headers, display_records))
    print(f"Total Employees Working on {date_str.strip()}: {len(results)}")


def menu_report_date_range():
    print_header("VIEW EMPLOYEES WORKING DURING A DATE RANGE")
    start_date = safe_input("Enter Start Date (MM-DD-CCYY, e.g., 01-01-2024): ")
    end_date = safe_input("Enter End Date (MM-DD-CCYY, e.g., 12-31-2024): ")

    success, message, results = reports.get_employees_working_in_date_range(start_date, end_date)
    if not success:
        print(f"\n[ERROR] {message}")
        return

    print("\n-----------------------------------------------------------------------------------------")
    print(f"Employees Working During Date Range: {start_date.strip()} to {end_date.strip()}")
    print("-----------------------------------------------------------------------------------------")
    if not results:
        print("No employee assignments found overlapping the requested date range.")
        print("-----------------------------------------------------------------------------------------")
        return

    headers = ["Employee ID", "Employee Name", "Department ID", "Department", "Start Date", "End Date"]
    display_records = [
        {
            "Employee ID": r["Employee ID"],
            "Employee Name": r["Employee Name"],
            "Department ID": r["Department ID"],
            "Department": r["Department"],
            "Start Date": r["Start Date"],
            "End Date": r["End Date"],
        }
        for r in results
    ]
    print(format_ascii_table(headers, display_records))
    print(f"Total Overlapping Assignments Found: {len(results)}")


# ==============================================================================
# MAIN APPLICATION LOOP
# ==============================================================================

def main():
    """Main application loop."""
    # Ensure text files exist
    initialize_storage_files()

    while True:
        print_banner("EMPLOYEE & DEPARTMENT MANAGEMENT SYSTEM")
        print("1. Employee Management")
        print("2. Department Management")
        print("3. Employee Department Assignment")
        print("4. View Employees on a Specific Date")
        print("5. View Employees During a Date Range")
        print("6. View Employee Assignment History")
        print("7. View Current Employee Department")
        print("8. Initialize / Reset Sample Test Data")
        print("9. Exit")
        print("====================================================")

        choice = safe_input("Enter your choice (1-9): ")
        if choice == '1':
            employee_management_menu()
        elif choice == '2':
            department_management_menu()
        elif choice == '3':
            assignment_menu()
        elif choice == '4':
            menu_report_specific_date()
        elif choice == '5':
            menu_report_date_range()
        elif choice == '6':
            menu_view_employee_history()
        elif choice == '7':
            menu_view_current_department()
        elif choice == '8':
            initialize_sample_data(prompt_user=True)
        elif choice == '9':
            print("\nThank you for using the Employee & Department Management System. Goodbye!\n")
            sys.exit(0)
        else:
            print("[ERROR] Invalid choice. Please enter a valid number (1-9).")


if __name__ == "__main__":
    main()


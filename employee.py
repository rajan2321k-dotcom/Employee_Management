"""
employee.py - Employee Management Module

Provides CRUD operations and business logic for employees:
- Add Employee (Auto-ID generation: EMP001, EMP002, ...)
- View All Employees
- Search Employee (by ID or Name)
- Update Employee Details
- Delete Employee (safely protected if assignment history exists)
"""

import re
from typing import List, Dict, Optional, Tuple
from file_handler import (
    EMP_FILE,
    EMP_HEADERS,
    ASG_FILE,
    ASG_HEADERS,
    read_records,
    write_records,
    append_record,
    update_record,
    delete_record,
    format_ascii_table,
)
from validation import (
    validate_employee_name,
    validate_age,
    validate_location_field,
)


def get_all_employees() -> List[Dict[str, str]]:
    """Retrieve all employee records from emp.txt."""
    return read_records(EMP_FILE, EMP_HEADERS)


def get_employee_by_id(emp_id: str) -> Optional[Dict[str, str]]:
    """Look up an employee by their Employee ID (case-insensitive)."""
    norm_id = emp_id.strip().upper()
    for emp in get_all_employees():
        if emp.get("Employee ID", "").strip().upper() == norm_id:
            return emp
    return None


def generate_next_employee_id() -> str:
    """
    Generate the next unique Employee ID.
    Inspects all existing IDs (e.g., EMP001, EMP002) and returns EMP{:03d}.
    """
    employees = get_all_employees()
    max_id = 0
    for emp in employees:
        raw_id = emp.get("Employee ID", "").strip()
        match = re.match(r"^EMP(\d+)$", raw_id, re.IGNORECASE)
        if match:
            num = int(match.group(1))
            if num > max_id:
                max_id = num
    next_num = max_id + 1
    return f"EMP{next_num:03d}"


def add_employee(
    name: str,
    age_input,
    city: str,
    state: str,
    country: str,
    custom_id: Optional[str] = None
) -> Tuple[bool, str, Optional[Dict[str, str]]]:
    """
    Validate details, generate next ID, and persist new employee record in emp.txt.
    """
    # 1. Validate Name
    ok_name, msg_name = validate_employee_name(name)
    if not ok_name:
        return False, msg_name, None

    # 2. Validate Age
    ok_age, msg_age, validated_age = validate_age(age_input)
    if not ok_age:
        return False, msg_age, None

    # 3. Validate Locations
    ok_city, msg_city = validate_location_field(city, "City")
    if not ok_city:
        return False, msg_city, None

    ok_state, msg_state = validate_location_field(state, "State")
    if not ok_state:
        return False, msg_state, None

    ok_country, msg_country = validate_location_field(country, "Country")
    if not ok_country:
        return False, msg_country, None

    # 4. Generate or verify ID
    if custom_id:
        emp_id = custom_id.strip().upper()
        if get_employee_by_id(emp_id):
            return False, f"Employee ID '{emp_id}' already exists.", None
    else:
        emp_id = generate_next_employee_id()

    new_emp = {
        "Employee ID": emp_id,
        "Name": name.strip(),
        "Age": str(validated_age),
        "City": city.strip(),
        "State": state.strip(),
        "Country": country.strip(),
    }

    success = append_record(EMP_FILE, EMP_HEADERS, new_emp)
    if success:
        return True, f"Employee {emp_id} added successfully.", new_emp
    else:
        return False, "Failed to write employee record to file.", None


def search_employees(query: str) -> List[Dict[str, str]]:
    """
    Search employees by Employee ID or Name (case-insensitive partial match).
    """
    query_clean = query.strip().upper()
    if not query_clean:
        return []

    results = []
    for emp in get_all_employees():
        emp_id = emp.get("Employee ID", "").strip().upper()
        emp_name = emp.get("Name", "").strip().upper()
        if query_clean in emp_id or query_clean in emp_name:
            results.append(emp)
    return results


def update_employee(
    emp_id: str,
    name: Optional[str] = None,
    age_input = None,
    city: Optional[str] = None,
    state: Optional[str] = None,
    country: Optional[str] = None,
) -> Tuple[bool, str]:
    """
    Update employee fields if new values are provided.
    Preserves unchanged fields and validates new values.
    """
    existing = get_employee_by_id(emp_id)
    if not existing:
        return False, f"Employee with ID '{emp_id}' not found."

    updated_fields: Dict[str, str] = {}

    if name is not None and str(name).strip():
        ok, msg = validate_employee_name(name)
        if not ok:
            return False, msg
        updated_fields["Name"] = name.strip()

    if age_input is not None and str(age_input).strip():
        ok, msg, val_age = validate_age(age_input)
        if not ok:
            return False, msg
        updated_fields["Age"] = str(val_age)

    if city is not None and str(city).strip():
        ok, msg = validate_location_field(city, "City")
        if not ok:
            return False, msg
        updated_fields["City"] = city.strip()

    if state is not None and str(state).strip():
        ok, msg = validate_location_field(state, "State")
        if not ok:
            return False, msg
        updated_fields["State"] = state.strip()

    if country is not None and str(country).strip():
        ok, msg = validate_location_field(country, "Country")
        if not ok:
            return False, msg
        updated_fields["Country"] = country.strip()

    if not updated_fields:
        return False, "No fields were updated."

    success = update_record(EMP_FILE, EMP_HEADERS, "Employee ID", existing["Employee ID"], updated_fields)
    if success:
        return True, f"Employee '{existing['Employee ID']}' updated successfully."
    return False, "Failed to update employee in file."


def delete_employee(emp_id: str) -> Tuple[bool, str]:
 
    existing = get_employee_by_id(emp_id)
    if not existing:
        return False, f"Employee with ID '{emp_id}' not found."

    actual_id = existing["Employee ID"]

    # Check for assignment history
    assignments = read_records(ASG_FILE, ASG_HEADERS)
    has_history = any(
        asg.get("Employee ID", "").strip().upper() == actual_id.upper()
        for asg in assignments
    )

    if has_history:
        return (
            False,
            f"Cannot delete employee '{actual_id}': Active or historical assignment records exist. "
            "Company history must be preserved.",
        )

    success = delete_record(EMP_FILE, EMP_HEADERS, "Employee ID", actual_id)
    if success:
        return True, f"Employee '{actual_id}' deleted successfully."
    return False, "Failed to delete employee from file."


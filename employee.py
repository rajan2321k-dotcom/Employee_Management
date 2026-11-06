"""
employee.py - Employee Management Module

Provides Add Employee operations and data access for employees.
Stores employee details in emp.txt using CSV format.
Removes unused search, update, and delete functions.
"""

import re
from typing import List, Dict, Optional, Tuple
from file_handler import (
    EMP_FILE,
    EMP_HEADERS,
    read_records,
    append_record,
)
from validation import (
    validate_employee_name,
    validate_age,
    validate_location_field,
)


def get_all_employees() -> List[Dict[str, str]]:
    """Retrieve all employee records from emp.txt (CSV format)."""
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
    Generate the next unique Employee ID (EMP001, EMP002, EMP003...).
    Inspects all existing IDs and returns the next sequential ID.
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
    Validate details sequentially and persist new employee record into emp.txt (CSV format).
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

    # 4. Generate or verify unique Employee ID
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
    return False, "Failed to write employee record to file.", None

"""
department.py - Department Management Module

Provides Add Department operations and data access for departments.
Stores department details in department.txt using CSV format.
Removes unused search, update, and delete functions.
"""

import re
from typing import List, Dict, Optional, Tuple
from file_handler import (
    DEPT_FILE,
    DEPT_HEADERS,
    read_records,
    append_record,
)
from validation import validate_department_description


def get_all_departments() -> List[Dict[str, str]]:
    """Retrieve all department records from department.txt (CSV format)."""
    return read_records(DEPT_FILE, DEPT_HEADERS)


def get_department_by_id(dept_id: str) -> Optional[Dict[str, str]]:
    """Look up a department by its Department ID (case-insensitive)."""
    norm_id = dept_id.strip().upper()
    for dept in get_all_departments():
        if dept.get("Department ID", "").strip().upper() == norm_id:
            return dept
    return None


def generate_next_department_id() -> str:
    """
    Generate the next unique Department ID (DEP001, DEP002...).
    Inspects all existing IDs and returns the next sequential ID.
    """
    departments = get_all_departments()
    max_id = 0
    for dept in departments:
        raw_id = dept.get("Department ID", "").strip()
        match = re.match(r"^DEP(\d+)$", raw_id, re.IGNORECASE)
        if match:
            num = int(match.group(1))
            if num > max_id:
                max_id = num
    next_num = max_id + 1
    return f"DEP{next_num:03d}"


def add_department(
    description: str,
    custom_id: Optional[str] = None
) -> Tuple[bool, str, Optional[Dict[str, str]]]:
    """
    Validate description, generate next Department ID, and persist to department.txt.
    """
    ok_desc, msg_desc = validate_department_description(description)
    if not ok_desc:
        return False, msg_desc, None

    if custom_id:
        dept_id = custom_id.strip().upper()
        if get_department_by_id(dept_id):
            return False, f"Department ID '{dept_id}' already exists.", None
    else:
        dept_id = generate_next_department_id()

    new_dept = {
        "Department ID": dept_id,
        "Description": description.strip(),
    }

    success = append_record(DEPT_FILE, DEPT_HEADERS, new_dept)
    if success:
        return True, f"Department {dept_id} ('{description.strip()}') added successfully.", new_dept
    return False, "Failed to save department to file.", None

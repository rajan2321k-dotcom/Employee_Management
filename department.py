
import re
from typing import List, Dict, Optional, Tuple
from file_handler import (
    DEPT_FILE,
    DEPT_HEADERS,
    ASG_FILE,
    ASG_HEADERS,
    read_records,
    append_record,
    update_record,
    delete_record,
)
from validation import validate_department_description


def get_all_departments() -> List[Dict[str, str]]:
    return read_records(DEPT_FILE, DEPT_HEADERS)


def get_department_by_id(dept_id: str) -> Optional[Dict[str, str]]:
    norm_id = dept_id.strip().upper()
    for dept in get_all_departments():
        if dept.get("Department ID", "").strip().upper() == norm_id:
            return dept
    return None


def generate_next_department_id() -> str:
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


def search_departments(query: str) -> List[Dict[str, str]]:
    clean_q = query.strip().upper()
    if not clean_q:
        return []

    results = []
    for dept in get_all_departments():
        dept_id = dept.get("Department ID", "").strip().upper()
        dept_desc = dept.get("Description", "").strip().upper()
        if clean_q in dept_id or clean_q in dept_desc:
            results.append(dept)
    return results


def update_department(dept_id: str, new_description: str) -> Tuple[bool, str]:
    existing = get_department_by_id(dept_id)
    if not existing:
        return False, f"Department with ID '{dept_id}' not found."

    ok, msg = validate_department_description(new_description)
    if not ok:
        return False, msg

    actual_id = existing["Department ID"]
    success = update_record(
        DEPT_FILE,
        DEPT_HEADERS,
        "Department ID",
        actual_id,
        {"Description": new_description.strip()},
    )
    if success:
        return True, f"Department '{actual_id}' description updated successfully."
    return False, "Failed to update department."


def delete_department(dept_id: str) -> Tuple[bool, str]:
    
    existing = get_department_by_id(dept_id)
    if not existing:
        return False, f"Department with ID '{dept_id}' not found."

    actual_id = existing["Department ID"]

    # Verify assignment history
    assignments = read_records(ASG_FILE, ASG_HEADERS)
    has_history = any(
        asg.get("Department ID", "").strip().upper() == actual_id.upper()
        for asg in assignments
    )

    if has_history:
        return (
            False,
            f"Cannot delete department '{actual_id}': Existing assignment history found in records.",
        )

    success = delete_record(DEPT_FILE, DEPT_HEADERS, "Department ID", actual_id)
    if success:
        return True, f"Department '{actual_id}' deleted successfully."
    return False, "Failed to delete department."


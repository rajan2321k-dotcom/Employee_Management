
"""
reports.py - Date-Based Employee Department Reporting Module

Generates specialized date-based operational reports using 100% manual date
comparison algorithms without datetime, date, time, or calendar:
1. View Employees Working on a Date (Feature 5)
2. View Employees Working Within a Date Range (Feature 6)
"""

from typing import List, Dict, Tuple
from file_handler import (
    read_records,
    EMP_FILE,
    EMP_HEADERS,
    DEPT_FILE,
    DEPT_HEADERS,
    ASG_FILE,
    ASG_HEADERS,
)
from validation import (
    validate_date_format,
    compare_dates,
    is_employee_working_on_date,
    check_date_ranges_overlap,
    MAX_DATE_TUPLE,
)
def _load_lookups() -> Tuple[Dict[str, str], Dict[str, str], Dict[str, str], Dict[str, str]]:

    """
    Build lookup dictionaries from CSV files:
    emp_map: {Employee ID -> Employee Name}
    dept_map: {Department ID -> Department Description}
    city_map: {Employee ID -> City}
    """
    employees = read_records(EMP_FILE, EMP_HEADERS)
    departments = read_records(DEPT_FILE, DEPT_HEADERS)

    emp_map = {
        e.get("Employee ID", "").strip().upper(): e.get("Name", "").strip()
        for e in employees
    }

    dept_map = {
        d.get("Department ID", "").strip().upper(): d.get("Description", "").strip()
        for d in departments
    }

    city_map = {
    e.get("Employee ID", "").strip().upper(): e.get("City", "").strip()
    for e in employees
}
    department_map = {
    d.get("Department ID", "").strip().upper(): d.get("Description", "").strip()
    for d in departments
}
    return emp_map, dept_map,city_map,department_map
def _load_date_range_lookups() -> Tuple[Dict[str, str], Dict[str, str]]:
    emp_map = {}
    dept_map = {}



    return emp_map, dept_map


def get_employees_working_on_date(
    date_str: str
) -> Tuple[bool, str, List[Dict[str, str]]]:
    """
    Feature 5: Find all employees who were actively working in a department on a specific date.

    Manual date comparison:
        asg_start <= target_date <= asg_end

    For Current assignments, end date is treated as MAX_DATE_TUPLE.
    """

    ok, msg, target_tuple = validate_date_format(date_str)

    if not ok or not target_tuple:
        return False, msg, []

    emp_map, dept_map,city_map,department_map = _load_lookups()
    assignments = read_records(ASG_FILE, ASG_HEADERS)

    matching_rows: List[Dict[str, str]] = []

    for asg in assignments:

        s_str = asg.get("Start Date", "").strip()
        e_str = asg.get("End Date", "").strip()

        ok_s, _, s_tuple = validate_date_format(s_str)

        if not ok_s or not s_tuple:
            continue

        if e_str.upper() == "CURRENT":
            e_tuple = MAX_DATE_TUPLE
        else:
            ok_e, _, e_tuple = validate_date_format(e_str)

            if not ok_e or not e_tuple:
                continue

        # Check whether employee was working on the requested date
        if is_employee_working_on_date(s_tuple, e_tuple, target_tuple):

            emp_id = asg.get("Employee ID", "").strip().upper()
            dept_id = asg.get("Department ID", "").strip().upper()
            city = city_map.get(emp_id, "")
            emp_name = emp_map.get(emp_id, emp_id)
            dept_desc = department_map.get(dept_id, dept_id)
            

            matching_rows.append({
                "Employee ID": emp_id,
                "Employee Name": emp_name,
                "Department": dept_desc,
                "City": city,
                "Department ID": dept_id,
            })

    # Sort primarily by Employee Name
    matching_rows.sort(key=lambda r: r["Employee Name"])

    return True, "", matching_rows


def get_employees_working_in_date_range(
    start_date_str: str,
    end_date_str: str
) -> Tuple[bool, str, List[Dict[str, str]]]:
    """
    Feature 6: Find all assignments that overlap with the requested date range.

    Manual interval overlap logic:
        s1 <= e2 AND s2 <= e1

    If an employee worked in three departments during the requested range,
    they are listed as three separate rows with original start and end dates.

    Columns:
        Employee Name
        Department
        Assignment Start Date
        Assignment End Date
    """

    ok_q_start, msg_s, q_start_tuple = validate_date_format(start_date_str)

    if not ok_q_start or not q_start_tuple:
        return False, f"Start Date error: {msg_s}", []

    ok_q_end, msg_e, q_end_tuple = validate_date_format(end_date_str)

    if not ok_q_end or not q_end_tuple:
        return False, f"End Date error: {msg_e}", []

    # Manual comparison: End Date cannot be earlier than Start Date
    if compare_dates(q_end_tuple, q_start_tuple) < 0:
        return (
            False,
            f"End Date ({end_date_str.strip()}) must be greater than or equal to Start Date ({start_date_str.strip()}).",
            [],
        )

    emp_map, dept_map = _load_date_range_lookups()
    assignments = read_records(ASG_FILE, ASG_HEADERS)

    matching_rows: List[Dict[str, str]] = []

    for asg in assignments:

        s_str = asg.get("Start Date", "").strip()
        e_str = asg.get("End Date", "").strip()

        ok_s, _, a_start_tuple = validate_date_format(s_str)

        if not ok_s or not a_start_tuple:
            continue

        if e_str.upper() == "CURRENT":
            a_end_tuple = MAX_DATE_TUPLE
        else:
            ok_e, _, a_end_tuple = validate_date_format(e_str)

            if not ok_e or not a_end_tuple:
                continue

        # Manual interval overlap check
        if check_date_ranges_overlap(
            q_start_tuple,
            q_end_tuple,
            a_start_tuple,
            a_end_tuple
        ):

            emp_id = asg.get("Employee ID", "").strip().upper()
            dept_id = asg.get("Department ID", "").strip().upper()

            emp_name = emp_map.get(emp_id, emp_id)
            dept_desc = dept_map.get(dept_id, dept_id)

            matching_rows.append({
                "Employee Name": emp_name,
                "Department": dept_desc,
                "Assignment Start Date": s_str,
                "Assignment End Date": e_str,
                "_start_tuple": a_start_tuple,
            })

    # Sort by Employee Name, then chronological start date
    matching_rows.sort(
        key=lambda r: (r["Employee Name"], r["_start_tuple"])
    )

    for r in matching_rows:
        r.pop("_start_tuple", None)

    return True, "", matching_rows

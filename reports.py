
from typing import List, Dict, Tuple, Optional
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
    MIN_DATE_TUPLE,
)


def _load_lookups() -> Tuple[Dict[str, str], Dict[str, str]]:
  
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
    return emp_map, dept_map


def get_employees_working_on_date(
    date_str: str
) -> Tuple[bool, str, List[Dict[str, str]]]:
 
    ok, msg, target_tuple = validate_date_format(date_str)
    if not ok or not target_tuple:
        return False, msg, []

    emp_map, dept_map = _load_lookups()
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

        # Check whether employee is working on target date using custom date logic
        if is_employee_working_on_date(s_tuple, e_tuple, target_tuple):
            emp_id = asg.get("Employee ID", "").strip().upper()
            dept_id = asg.get("Department ID", "").strip().upper()

            emp_name = emp_map.get(emp_id, emp_id)
            dept_desc = dept_map.get(dept_id, dept_id)

            matching_rows.append({
                "Employee ID": emp_id,
                "Employee Name": emp_name,
                "Department ID": dept_id,
                "Department": dept_desc,
                "Start Date": s_str,
                "End Date": e_str,
            })

    # Sort primarily by Employee ID / Name
    matching_rows.sort(key=lambda r: (r["Employee Name"], r["Employee ID"]))
    return True, "", matching_rows


def get_employees_working_in_date_range(
    start_date_str: str,
    end_date_str: str
) -> Tuple[bool, str, List[Dict[str, str]]]:
   
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
            f"End date ({end_date_str.strip()}) cannot be earlier than start date ({start_date_str.strip()}).",
            [],
        )

    emp_map, dept_map = _load_lookups()
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
        if check_date_ranges_overlap(q_start_tuple, q_end_tuple, a_start_tuple, a_end_tuple):
            emp_id = asg.get("Employee ID", "").strip().upper()
            dept_id = asg.get("Department ID", "").strip().upper()

            emp_name = emp_map.get(emp_id, emp_id)
            dept_desc = dept_map.get(dept_id, dept_id)

            matching_rows.append({
                "Assignment ID": asg.get("Assignment ID", "").strip(),
                "Employee ID": emp_id,
                "Employee Name": emp_name,
                "Department ID": dept_id,
                "Department": dept_desc,
                "Start Date": s_str,
                "End Date": e_str,
                "_start_tuple": a_start_tuple,
            })

    # Sort by Employee Name, then chronological start date tuple
    matching_rows.sort(key=lambda r: (r["Employee Name"], r["_start_tuple"]))
    for r in matching_rows:
        r.pop("_start_tuple", None)

    return True, "", matching_rows

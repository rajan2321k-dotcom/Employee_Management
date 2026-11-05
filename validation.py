

import re
from typing import Tuple, Optional, List, Dict

# Logical maximum date tuple (year, month, day) to represent "Current" ongoing assignments
MAX_DATE_TUPLE: Tuple[int, int, int] = (9999, 12, 31)
MIN_DATE_TUPLE: Tuple[int, int, int] = (1000, 1, 1)


# ==============================================================================
# 1. MANUAL DATE UTILITIES (NO BUILT-IN DATE LIBRARIES)
# ==============================================================================

def is_leap_year(year: int) -> bool:
 
    return (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)


def get_days_in_month(month: int, year: int) -> int:
  
    if month < 1 or month > 12:
        return 0

    # Days in each calendar month: index 1 = January, ..., 12 = December
    days_per_month = [
        0,   # placeholder for 0-index
        31,  # 1: January
        29 if is_leap_year(year) else 28,  # 2: February (29 in leap year, else 28)
        31,  # 3: March
        30,  # 4: April
        31,  # 5: May
        30,  # 6: June
        31,  # 7: July
        31,  # 8: August
        30,  # 9: September
        31,  # 10: October
        30,  # 11: November
        31,  # 12: December
    ]
    return days_per_month[month]


def validate_date_format(date_str: str) -> Tuple[bool, str, Optional[Tuple[int, int, int]]]:
   
    if not date_str or not str(date_str).strip():
        return False, "Date cannot be empty.", None

    cleaned = str(date_str).strip()

    # Must be exactly 10 characters: MM-DD-CCYY
    if len(cleaned) != 10:
        return (
            False,
            f"Invalid date '{cleaned}'. Date must be exactly 10 characters in MM-DD-CCYY format (e.g., 01-15-2024).",
            None,
        )

    # Must contain exactly two hyphens
    parts = cleaned.split("-")
    if len(parts) != 3:
        return (
            False,
            f"Invalid date format '{cleaned}'. Date must use hyphen separators: MM-DD-CCYY.",
            None,
        )

    mm_str, dd_str, ccyy_str = parts

    # Check that parts contain only digits with expected lengths
    if len(mm_str) != 2 or not mm_str.isdigit():
        return False, f"Invalid month '{mm_str}'. Month must be exactly 2 digits (01-12).", None

    if len(dd_str) != 2 or not dd_str.isdigit():
        return False, f"Invalid day '{dd_str}'. Day must be exactly 2 digits (01-31).", None

    if len(ccyy_str) != 4 or not ccyy_str.isdigit():
        return False, f"Invalid century year '{ccyy_str}'. Year must be exactly 4 digits (e.g., 2024).", None

    month = int(mm_str)
    day = int(dd_str)
    year = int(ccyy_str)

    # Month bounds check
    if month < 1 or month > 12:
        return False, f"Invalid month '{month:02d}'. Month must be between 01 and 12.", None

    # Year reasonable century bounds
    if year < 1000 or year > 9999:
        return False, f"Invalid year '{year}'. Year must be between 1000 and 9999.", None

    # Day bounds check for the specific month and year
    max_days = get_days_in_month(month, year)
    if day < 1 or day > max_days:
        if month == 2 and day == 29 and not is_leap_year(year):
            return (
                False,
                f"Invalid date '{cleaned}': Year {year} is not a leap year (February has only 28 days).",
                None,
            )
        return (
            False,
            f"Invalid day '{day:02d}' for month {month:02d} in year {year}. Allowed days: 01 to {max_days:02d}.",
            None,
        )

    # Return validated chronological date tuple: (year, month, day)
    return True, "", (year, month, day)


def compare_dates(
    date1: Tuple[int, int, int],
    date2: Tuple[int, int, int]
) -> int:
   
    y1, m1, d1 = date1
    y2, m2, d2 = date2

    # Compare years first
    if y1 < y2:
        return -1
    if y1 > y2:
        return 1

    # Years are equal, compare months
    if m1 < m2:
        return -1
    if m1 > m2:
        return 1

    # Months are equal, compare days
    if d1 < d2:
        return -1
    if d1 > d2:
        return 1

    return 0


def is_date_before_or_equal(d1: Tuple[int, int, int], d2: Tuple[int, int, int]) -> bool:
    """Check if date d1 <= d2 manually."""
    return compare_dates(d1, d2) <= 0


def is_date_strictly_after(d1: Tuple[int, int, int], d2: Tuple[int, int, int]) -> bool:
    """Check if date d1 > d2 manually."""
    return compare_dates(d1, d2) > 0


def check_date_ranges_overlap(
    s1: Tuple[int, int, int],
    e1: Tuple[int, int, int],
    s2: Tuple[int, int, int],
    e2: Tuple[int, int, int]
) -> bool:
   
    condition1 = compare_dates(s1, e2) <= 0
    condition2 = compare_dates(s2, e1) <= 0
    return condition1 and condition2


def is_employee_working_on_date(
    asg_start: Tuple[int, int, int],
    asg_end: Tuple[int, int, int],
    target_date: Tuple[int, int, int]
) -> bool:
   
    after_or_on_start = compare_dates(asg_start, target_date) <= 0
    before_or_on_end = compare_dates(target_date, asg_end) <= 0
    return after_or_on_start and before_or_on_end


def find_assignments_overlapping_range(
    query_start: Tuple[int, int, int],
    query_end: Tuple[int, int, int],
    assignments: List[Dict[str, str]]
) -> List[Dict[str, str]]:
   
    overlapping = []
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

        if check_date_ranges_overlap(query_start, query_end, s_tuple, e_tuple):
            overlapping.append(asg)

    return overlapping


def validate_assignment_dates(
    start_date_str: str,
    end_date_str: str
) -> Tuple[bool, Optional[Tuple[int, int, int]], Optional[Tuple[int, int, int]], str]:
    
    ok_s, msg_s, s_tuple = validate_date_format(start_date_str)
    if not ok_s or not s_tuple:
        return False, None, None, f"Start Date error: {msg_s}"

    clean_end = end_date_str.strip()
    if clean_end.upper() == "CURRENT":
        return True, s_tuple, MAX_DATE_TUPLE, ""

    ok_e, msg_e, e_tuple = validate_date_format(clean_end)
    if not ok_e or not e_tuple:
        return False, None, None, f"End Date error: {msg_e}"

    # Verify End Date >= Start Date
    if compare_dates(e_tuple, s_tuple) < 0:
        return (
            False,
            None,
            None,
            f"End date ({clean_end}) cannot be earlier than start date ({start_date_str.strip()}).",
        )

    return True, s_tuple, e_tuple, ""


def check_current_department_duplicate(
    emp_id: str,
    dept_id: str,
    assignments: List[Dict[str, str]]
) -> Tuple[bool, str]:
   
    norm_emp = emp_id.strip().upper()
    norm_dept = dept_id.strip().upper()

    for asg in assignments:
        if (
            asg.get("Employee ID", "").strip().upper() == norm_emp
            and asg.get("Department ID", "").strip().upper() == norm_dept
            and asg.get("End Date", "").strip().upper() == "CURRENT"
        ):
            return True, "This employee is already working in this department."

    return False, ""


def check_assignment_overlap(
    emp_id: str,
    new_start_tuple: Tuple[int, int, int],
    new_end_tuple: Tuple[int, int, int],
    assignments: List[Dict[str, str]],
    exclude_asg_id: Optional[str] = None
) -> Tuple[bool, str]:
    
    norm_emp = emp_id.strip().upper()

    for asg in assignments:
        if asg.get("Employee ID", "").strip().upper() != norm_emp:
            continue

        asg_id = asg.get("Assignment ID", "").strip().upper()
        if exclude_asg_id and asg_id == exclude_asg_id.strip().upper():
            continue

        ex_start_str = asg.get("Start Date", "").strip()
        ex_end_str = asg.get("End Date", "").strip()

        ok_s, _, ex_start_tuple = validate_date_format(ex_start_str)
        if not ok_s or not ex_start_tuple:
            continue

        if ex_end_str.upper() == "CURRENT":
            ex_end_tuple = MAX_DATE_TUPLE
        else:
            ok_e, _, ex_end_tuple = validate_date_format(ex_end_str)
            if not ok_e or not ex_end_tuple:
                continue

        # Check manual overlap
        if check_date_ranges_overlap(new_start_tuple, new_end_tuple, ex_start_tuple, ex_end_tuple):
            dept_id = asg.get("Department ID", "").strip()
            return (
                True,
                f"Assignment dates overlap with existing assignment {asg_id} "
                f"(Department: {dept_id}, Period: {ex_start_str} to {ex_end_str}).",
            )

    return False, ""


# ==============================================================================
# 2. GENERAL FIELD VALIDATIONS (EMPLOYEE & DEPARTMENT)
# ==============================================================================

def validate_non_empty(value: str, field_name: str) -> Tuple[bool, str]:
    if not value or not str(value).strip():
        return False, f"{field_name} cannot be empty."
    return True, ""


def validate_employee_name(name: str) -> Tuple[bool, str]:
    valid, msg = validate_non_empty(name, "Employee name")
    if not valid:
        return False, msg

    cleaned = name.strip()
    if len(cleaned) < 2:
        return False, "Employee name must be at least 2 characters long."
    if len(cleaned) > 100:
        return False, "Employee name cannot exceed 100 characters."

    # Allow letters, spaces, dots, hyphens, apostrophes (e.g., O'Connor, Mary-Jane, Dr. Rajan)
    if not re.match(r"^[A-Za-z\s\.\-']+$", cleaned):
        return False, "Employee name contains invalid characters. Use letters, spaces, hyphens, or periods only."

    return True, ""


def validate_age(age_val) -> Tuple[bool, str, Optional[int]]:
   
    if isinstance(age_val, str):
        age_str = age_val.strip()
        if not age_str:
            return False, "Age cannot be empty.", None
        if not re.match(r"^-?\d+$", age_str):
            return False, f"Invalid age '{age_val}'. Age must be a valid whole number.", None
        try:
            age = int(age_str)
        except ValueError:
            return False, f"Invalid age '{age_val}'. Age must be a valid whole number.", None
    elif isinstance(age_val, int):
        age = age_val
    else:
        return False, "Age must be a valid whole number.", None

    if age < 18 or age > 65:
        return False, f"Age must be between 18 and 65 (inclusive). Entered age: {age}.", None

    return True, "", age


def validate_location_field(value: str, field_name: str) -> Tuple[bool, str]:
    valid, msg = validate_non_empty(value, field_name)
    if not valid:
        return False, msg
    cleaned = value.strip()
    if len(cleaned) < 2:
        return False, f"{field_name} must be at least 2 characters long."
    if len(cleaned) > 60:
        return False, f"{field_name} cannot exceed 60 characters."
    return True, ""


def validate_department_description(desc: str) -> Tuple[bool, str]:
    valid, msg = validate_non_empty(desc, "Department description")
    if not valid:
        return False, msg
    cleaned = desc.strip()
    if len(cleaned) < 2:
        return False, "Department description must be at least 2 characters long."
    if len(cleaned) > 100:
        return False, "Department description cannot exceed 100 characters."
    return True, ""

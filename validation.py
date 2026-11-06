"""
validation.py - Sequential Input & Manual Date Validation Engine

Features:
- Strict Name validation (A-Z, a-z, spaces only; no numbers or special characters)
- Strict Age validation (Numeric only, 18-65 inclusive)
- Location fields validation (City, State, Country: non-empty, letters/spaces only)
- Department description validation (Non-empty)
- Custom manual date validation and comparison (Zero built-in datetime/calendar modules)
- Date interval overlap logic
"""

import re
from typing import Tuple, Optional, List, Dict

# Logical maximum date tuple (year, month, day) to represent "Current" ongoing assignments
MAX_DATE_TUPLE: Tuple[int, int, int] = (9999, 12, 31)
MIN_DATE_TUPLE: Tuple[int, int, int] = (1000, 1, 1)


# ==============================================================================
# 1. FIELD VALIDATION (NAME, AGE, LOCATION, DEPARTMENT)
# ==============================================================================

def validate_employee_name(name: str) -> Tuple[bool, str]:
    """
    Validate employee name:
    - Accept only alphabetic characters (A-Z, a-z).
    - Allow spaces between words.
    - Reject numbers and special characters.
    - Do not accept empty input.
    """
    if not name or not str(name).strip():
        return False, "Employee name cannot be empty."

    cleaned = str(name).strip()

    # Reject numbers and special characters: allow only letters and spaces
    for ch in cleaned:
        if not (ch.isalpha() or ch.isspace()):
            return (
                False,
                "Employee name must contain only alphabetic characters (A-Z, a-z) and spaces. "
                "Numbers and special characters are not allowed.",
            )

    # Must contain at least one alphabetic character
    if not any(ch.isalpha() for ch in cleaned):
        return False, "Employee name cannot be only spaces."

    return True, ""


def validate_age(age_input) -> Tuple[bool, str, Optional[int]]:
    """
    Validate employee age:
    - Accept only numeric values.
    - Minimum age: 18.
    - Maximum age: 65.
    - Reject values outside this range.
    """
    if age_input is None:
        return False, "Age cannot be empty.", None

    age_str = str(age_input).strip()
    if not age_str:
        return False, "Age cannot be empty.", None

    # Check for strictly numeric digits
    if not age_str.isdigit():
        return False, f"Invalid age '{age_str}'. Age must be a numeric integer value.", None

    age = int(age_str)
    if age < 18 or age > 65:
        return (
            False,
            f"Age must be between 18 and 65 (inclusive). Entered age: {age}.",
            None,
        )

    return True, "", age


def validate_location_field(value: str, field_name: str) -> Tuple[bool, str]:
    """
    Validate location fields (City, State, Country):
    - Cannot be empty.
    - Must contain only letters and spaces.
    """
    if not value or not str(value).strip():
        return False, f"{field_name} cannot be empty."

    cleaned = str(value).strip()
    for ch in cleaned:
        if not (ch.isalpha() or ch.isspace()):
            return False, f"{field_name} must contain only alphabetic characters and spaces."

    if not any(ch.isalpha() for ch in cleaned):
        return False, f"{field_name} cannot be only spaces."

    return True, ""


def validate_department_description(desc: str) -> Tuple[bool, str]:
    """
    Validate department description:
    - Cannot be empty.
    """
    if not desc or not str(desc).strip():
        return False, "Department description cannot be empty."
    return True, ""


# ==============================================================================
# 2. MANUAL DATE ENGINE (NO DATETIME, DATE, TIME, OR CALENDAR MODULES)
# ==============================================================================

def is_leap_year(year: int) -> bool:
    """
    Manually determine whether a given year is a leap year.
    Rule:
    - Divisible by 4 AND NOT divisible by 100, OR
    - Divisible by 400.
    """
    return (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)


def get_days_in_month(month: int, year: int) -> int:
    """
    Return the maximum number of days in a given month and year.
    Accounts for leap years manually for February without external libraries.
    """
    if month < 1 or month > 12:
        return 0

    days_per_month = [
        0,   # placeholder for 1-based index
        31,  # 1: January
        29 if is_leap_year(year) else 28,  # 2: February
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
    """
    Validate a date string strictly following MM-DD-CCYY format manually.
    - Format must be exactly 10 characters: 2-digit month, '-', 2-digit day, '-', 4-digit year.
    - Rejects invalid months (e.g., 13-20-2024).
    - Rejects impossible calendar days (e.g., 02-30-2024, 04-31-2024, 02-29-2023).
    - Rejects improper formats (e.g., 2024-01-15, 01/15/2024, 1-5-2024).

    Returns:
        (is_valid, error_message, (year, month, day) or None)
    """
    if not date_str or not str(date_str).strip():
        return False, "Date cannot be empty.", None

    cleaned = str(date_str).strip()

    if len(cleaned) != 10:
        return (
            False,
            f"Invalid date format '{cleaned}'. Date must follow MM-DD-CCYY (e.g., 01-15-2024).",
            None,
        )

    parts = cleaned.split("-")
    if len(parts) != 3:
        return (
            False,
            f"Invalid date format '{cleaned}'. Date must use hyphen separators: MM-DD-CCYY.",
            None,
        )

    mm_str, dd_str, ccyy_str = parts

    if len(mm_str) != 2 or not mm_str.isdigit():
        return False, f"Invalid month '{mm_str}'. Month must be exactly 2 digits (01-12).", None

    if len(dd_str) != 2 or not dd_str.isdigit():
        return False, f"Invalid day '{dd_str}'. Day must be exactly 2 digits (01-31).", None

    if len(ccyy_str) != 4 or not ccyy_str.isdigit():
        return False, f"Invalid century year '{ccyy_str}'. Year must be exactly 4 digits (e.g., 2024).", None

    month = int(mm_str)
    day = int(dd_str)
    year = int(ccyy_str)

    if month < 1 or month > 12:
        return False, f"Invalid month '{month:02d}'. Month must be between 01 and 12.", None

    if year < 1000 or year > 9999:
        return False, f"Invalid year '{year}'. Year must be between 1000 and 9999.", None

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

    return True, "", (year, month, day)


def compare_dates(
    date1: Tuple[int, int, int],
    date2: Tuple[int, int, int]
) -> int:
    """
    Manually compare two chronological date tuples: (year, month, day).
    Returns:
        -1 if date1 is earlier than date2
         0 if date1 is the exact same date as date2
         1 if date1 is later than date2
    """
    y1, m1, d1 = date1
    y2, m2, d2 = date2

    if y1 < y2:
        return -1
    if y1 > y2:
        return 1

    if m1 < m2:
        return -1
    if m1 > m2:
        return 1

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
    """
    Check whether two closed date intervals [s1, e1] and [s2, e2] overlap.
    Condition: s1 <= e2 AND s2 <= e1
    """
    condition1 = compare_dates(s1, e2) <= 0
    condition2 = compare_dates(s2, e1) <= 0
    return condition1 and condition2


def is_employee_working_on_date(
    asg_start: Tuple[int, int, int],
    asg_end: Tuple[int, int, int],
    target_date: Tuple[int, int, int]
) -> bool:
    """
    Check whether an employee's assignment is active on a specific target date.
    Condition: asg_start <= target_date <= asg_end
    """
    after_or_on_start = compare_dates(asg_start, target_date) <= 0
    before_or_on_end = compare_dates(target_date, asg_end) <= 0
    return after_or_on_start and before_or_on_end


def find_assignments_overlapping_range(
    query_start: Tuple[int, int, int],
    query_end: Tuple[int, int, int],
    assignments: List[Dict[str, str]]
) -> List[Dict[str, str]]:
    """
    Filter assignments that overlap with the specified [query_start, query_end] window.
    """
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
    """
    Validate assignment start and end dates manually:
    - Start Date must follow MM-DD-CCYY.
    - End Date must follow MM-DD-CCYY OR be 'Current'.
    - End Date must be equal to or later than Start Date.
    """
    ok_s, msg_s, s_tuple = validate_date_format(start_date_str)
    if not ok_s or not s_tuple:
        return False, None, None, f"Start Date error: {msg_s}"

    clean_end = end_date_str.strip()
    if clean_end.upper() == "CURRENT":
        return True, s_tuple, MAX_DATE_TUPLE, ""

    ok_e, msg_e, e_tuple = validate_date_format(clean_end)
    if not ok_e or not e_tuple:
        return False, None, None, f"End Date error: {msg_e}"

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
    """
    Check if the employee is already working in this department currently.
    """
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


def check_active_assignment_exists(
    emp_id: str,
    assignments: List[Dict[str, str]]
) -> Tuple[bool, Optional[Dict[str, str]]]:
    """
    Check if the employee already has an active ongoing assignment ('Current').
    An employee cannot have two active assignments at the same time.
    """
    norm_emp = emp_id.strip().upper()
    for asg in assignments:
        if (
            asg.get("Employee ID", "").strip().upper() == norm_emp
            and asg.get("End Date", "").strip().upper() == "CURRENT"
        ):
            return True, asg
    return False, None


def check_assignment_overlap(
    emp_id: str,
    new_start_tuple: Tuple[int, int, int],
    new_end_tuple: Tuple[int, int, int],
    assignments: List[Dict[str, str]],
    exclude_asg_id: Optional[str] = None
) -> Tuple[bool, str]:
    """
    Check whether [new_start_tuple, new_end_tuple] overlaps with any existing assignments
    of the employee using manual interval overlap logic.
    """
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

        if check_date_ranges_overlap(new_start_tuple, new_end_tuple, ex_start_tuple, ex_end_tuple):
            dept_id = asg.get("Department ID", "").strip()
            return (
                True,
                f"Assignment dates overlap with existing assignment {asg_id} "
                f"(Department: {dept_id}, Period: {ex_start_str} to {ex_end_str}).",
            )

    return False, ""

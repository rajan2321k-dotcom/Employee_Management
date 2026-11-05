<<<<<<< HEAD
# Employee & Department Management System

A robust, enterprise-grade console application built in Python for managing employees, departments, historical and ongoing department assignments, and date-based operational reports.

This project strictly adheres to **zero-database**, **pure ASCII-table plain text storage** constraints—no SQLite, MySQL, MongoDB, JSON, CSV, or binary serialization is used. All permanent records are stored in human-readable `.txt` files formatted as ASCII tables.

> [!IMPORTANT]
> **Custom Date Engine**: This system contains **NO Python built-in date utilities** (`datetime`, `date`, `time`, or `calendar`). All date parsing, monthly limits, leap years, chronological comparisons, date range overlap checks, and employee schedule filtering are implemented completely from scratch using basic Python logic.

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Key Features](#key-features)
3. [Technology Stack](#technology-stack)
4. [Folder Structure](#folder-structure)
5. [Storage Architecture](#storage-architecture)
6. [Manual Date Engine Explanation](#manual-date-engine-explanation)
7. [Business Rules & Validation](#business-rules--validation)
8. [Installation & Windows Execution Guide](#installation--windows-execution-guide)
9. [Menu Guide & Walkthrough](#menu-guide--walkthrough)
10. [Sample Test Cases & Scenarios](#sample-test-cases--scenarios)
11. [Technical Interview Demonstration Guide](#technical-interview-demonstration-guide)

---

## 1. Project Overview

The **Employee & Department Management System** provides complete lifecycle management for an organization's workforce:
- Employee registration, personal details management, and strict age/field validations.
- Department cataloging and referential integrity protection (cannot delete departments with active or past assignments).
- Flexible assignment tracking supporting historical transitions, ongoing assignments (`Current`), duplicate prevention, and strict temporal overlap protection.
- Operational reporting for any specific date or date range.

---

## 2. Key Features

### Employee Management
- **Add Employee**: Auto-generates unique ID (`EMP001`, `EMP002`, ...), validates age (18–65 inclusive), and non-empty name/location.
- **View All Employees**: Renders all registered employees in a formatted ASCII table.
- **Search Employee**: Case-insensitive search by Employee ID or Name.
- **Update Employee**: Interactive prompt allowing selective updates while preserving existing values.
- **Delete Employee**: Referential integrity check prevents deleting an employee who has assignment records.

### Department Management
- **Add Department**: Auto-generates unique ID (`DEP001`, `DEP002`, ...), validates non-empty description.
- **View All Departments**: Renders department catalog in an ASCII table.
- **Search Department**: Search by Department ID or Description.
- **Update Department**: Modify department descriptions.
- **Delete Department**: **Strictly blocked** if assignment history exists for that department.

### Employee Department Assignment (Feature 3)
- **Assign Employee**: Assigns an employee to a department for a specified date range (`MM-DD-CCYY`) or ongoing (`Current`).
- **Change Employee Department**: Closes current active assignment with an end date and creates the new assignment atomically without losing history.
- **View Assignment History**: Displays chronological assignment history for an employee with department names.
- **View Current Department**: Displays active assignment (`Current`) for a given employee or all active employees.

### Advanced Date-Based Reports (Features 4 & 5)
- **Report by Specific Date (Feature 4)**: Displays all employees actively assigned to a department on a requested date using manual date comparison.
- **Report by Date Range (Feature 5)**: Displays every assignment that overlaps the query window using manual interval overlap logic. If an employee held multiple assignments during the range, each is reported individually with original dates.

---

## 3. Technology Stack

- **Language**: Python 3.8+ (Tested on Python 3.13)
- **Standard Library Modules Used**:
  - `re` (regex patterns for name and basic string format validation)
  - `os`, `sys` (cross-platform path resolution, process control)
  - `tempfile` (atomic file replacement to prevent data corruption)
  - `typing` (type hints for readability and static analysis)
- **Date Modules**: **None**. Built-in `datetime`, `date`, `time`, and `calendar` modules are strictly forbidden and not imported anywhere.
- **External Dependencies**: **None**. Zero third-party packages required.

---

## 4. Folder Structure

```
Employee_Department_System/
│
├── main.py                     # Main console menu application & entry point
├── employee.py                 # Employee CRUD and auto-ID generation
├── department.py               # Department CRUD and deletion safeguards
├── assignment.py               # Assignment logic, department changes, overlap checks
├── reports.py                  # Date-based reporting (specific date & date range)
├── validation.py               # Custom manual date engine & field validation
├── file_handler.py             # ASCII table parser, serializer, and atomic file I/O
├── init_sample_data.py         # Standalone sample data initializer
├── test_system.py              # Automated 16-scenario verification test suite
├── emp.txt                     # Plain text ASCII table storage for employees
├── department.txt              # Plain text ASCII table storage for departments
├── employee_department.txt     # Plain text ASCII table storage for assignments
├── README.md                   # Complete system documentation
└── requirements.txt            # Environment specifications
```

---

## 5. Storage Architecture

All data is stored in plain text `.txt` files in ASCII table format. The file handler computes column widths dynamically and parses rows back into structured dictionaries.

### Atomic File Write Protection
To prevent data corruption if the system crashes mid-write:
1. The new ASCII table content is written to a temporary file (`tmp_agy_*.txt`).
2. The file is flushed and closed.
3. `os.replace` replaces the destination file atomically.

### Storage Files Schema

#### `emp.txt`
```text
+-------------+-------+-----+------------+------------+---------+
| Employee ID | Name  | Age | City       | State      | Country |
+-------------+-------+-----+------------+------------+---------+
| EMP001      | Rajan | 21  | Coimbatore | Tamil Nadu | India   |
| EMP002      | Arun  | 25  | Chennai    | Tamil Nadu | India   |
| EMP003      | Kumar | 30  | Madurai    | Tamil Nadu | India   |
+-------------+-------+-----+------------+------------+---------+
```

#### `department.txt`
```text
+---------------+----------------------+
| Department ID | Description          |
+---------------+----------------------+
| DEP001        | Human Resources      |
| DEP002        | Software Development |
| DEP003        | Finance              |
+---------------+----------------------+
```

#### `employee_department.txt`
```text
+---------------+-------------+---------------+------------+------------+
| Assignment ID | Employee ID | Department ID | Start Date | End Date   |
+---------------+-------------+---------------+------------+------------+
| ASG001        | EMP001      | DEP001        | 01-01-2024 | 06-30-2024 |
| ASG002        | EMP001      | DEP002        | 07-01-2024 | Current    |
| ASG003        | EMP002      | DEP003        | 02-01-2024 | Current    |
| ASG004        | EMP003      | DEP001        | 03-01-2024 | 05-31-2024 |
| ASG005        | EMP003      | DEP002        | 06-01-2024 | Current    |
+---------------+-------------+---------------+------------+------------+
```

---

## 6. Manual Date Engine Explanation

The system replaces all built-in date modules with custom functions in `validation.py`:

### 1. Manual Leap Year Calculation (`is_leap_year`)
A year is a leap year if:
$$\text{year} \pmod 4 = 0 \quad \text{AND} \quad (\text{year} \pmod{100} \ne 0 \quad \text{OR} \quad \text{year} \pmod{400} = 0)$$

```python
def is_leap_year(year: int) -> bool:
    return (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)
```
- Examples: `2024` (True), `2000` (True), `1900` (False), `2023` (False).

### 2. Manual Monthly Day Limits (`get_days_in_month`)
Days per calendar month:
- Months with 31 days: 1 (Jan), 3 (Mar), 5 (May), 7 (Jul), 8 (Aug), 10 (Oct), 12 (Dec).
- Months with 30 days: 4 (Apr), 6 (Jun), 9 (Sep), 11 (Nov).
- February (Month 2): 29 days if `is_leap_year(year)` is True, else 28 days.

### 3. Custom Date Format & Validation (`validate_date_format`)
Input: `MM-DD-CCYY` string (e.g., `01-15-2024`).
- Ensures exactly 10 characters and 2 hyphen delimiters.
- Extracts `month`, `day`, `year` integers.
- Validates $1 \le \text{month} \le 12$.
- Validates $1000 \le \text{year} \le 9999$.
- Validates $1 \le \text{day} \le \text{get\_days\_in\_month}(\text{month}, \text{year})$.
- Returns a normalized chronological tuple: `(year, month, day)`.

### 4. Custom Date Comparison (`compare_dates`)
Compares two `(year, month, day)` tuples without external utilities:
```python
def compare_dates(date1: tuple, date2: tuple) -> int:
    y1, m1, d1 = date1
    y2, m2, d2 = date2
    if y1 != y2:
        return -1 if y1 < y2 else 1
    if m1 != m2:
        return -1 if m1 < m2 else 1
    if d1 != d2:
        return -1 if d1 < d2 else 1
    return 0
```
- Returns `-1` if `date1 < date2`, `0` if `date1 == date2`, `1` if `date1 > date2`.

### 5. Custom Date Range Overlap Logic (`check_date_ranges_overlap`)
For two intervals $[S_1, E_1]$ and $[S_2, E_2]$ (where `Current` is represented by `(9999, 12, 31)`):
- Overlap exists if and only if:
  $$S_1 \le E_2 \quad \text{AND} \quad S_2 \le E_1$$
- Implemented with:
  ```python
  compare_dates(s1, e2) <= 0 and compare_dates(s2, e1) <= 0
  ```

### 6. Employee Working on a Given Date (`is_employee_working_on_date`)
An assignment $[S, E]$ is active on `target_date` if:
$$S \le \text{target\_date} \le E$$
- Implemented with:
  ```python
  compare_dates(asg_start, target_date) <= 0 and compare_dates(target_date, asg_end) <= 0
  ```

### 7. Finding Assignments in a Range (`find_assignments_overlapping_range`)
Iterates all stored assignments, parses each interval, and applies `check_date_ranges_overlap(query_start, query_end, asg_start, asg_end)`.

---

## 7. Business Rules & Validation

### 1. Employee Details
- **Name**: Cannot be empty. Must contain letters, spaces, hyphens, or periods (length 2–100).
- **Age**: Must be a whole integer between **18 and 65 (inclusive)**. Rejected otherwise.
- **City, State, Country**: Non-empty strings (length 2–60).
- **Employee ID**: Unique, auto-generated sequence `EMP001`, `EMP002`, ...

### 2. Department Details
- **Description**: Cannot be empty (length 2–100).
- **Department ID**: Unique, auto-generated sequence `DEP001`, `DEP002`, ...
- **Integrity Rule**: A department **cannot be deleted** if it has any past or active assignment records.

### 3. Assignment Business Rules
- **End Date >= Start Date**: End date cannot be earlier than start date.
- **Ongoing Assignments**: Represented by `"Current"`, logically mapped to `(9999, 12, 31)`.
- **Duplicate Current Assignment Prevention**: If an employee is currently assigned to Department A, another assignment to Department A is rejected with:
  `"This employee is already working in this department."`
- **Department Transfer**: When moving an employee from Department A to Department B:
  1. Department A's assignment is closed with a user-specified end date ($Closing \ge Start$).
  2. Department B's new assignment starts strictly after Department A's closing date ($NewStart > Closing$).
  3. No past history is ever deleted.
  4. Employees may return to a previously worked department in the future.

---

## 8. Installation & Windows Execution Guide

### Prerequisites
- Python 3.8 or higher installed on Windows.
- Python added to Windows `PATH`.

Verify Python installation:
```cmd
python --version
```

### Execution Steps on Windows

1. Open PowerShell or Command Prompt.
2. Navigate to the project directory:
   ```cmd
   cd c:\Users\rajan\OneDrive\Desktop\Employee\Employee_Department_System
   ```
3. Run the interactive console application:
   ```cmd
   python main.py
   ```
4. (Optional) Run the automated verification test suite:
   ```cmd
   python test_system.py
   ```
5. (Optional) Re-initialize sample test data at any time:
   ```cmd
   python init_sample_data.py
   ```

---

## 9. Menu Guide & Walkthrough

```text
====================================================
   EMPLOYEE & DEPARTMENT MANAGEMENT SYSTEM
====================================================
1. Employee Management
2. Department Management
3. Employee Department Assignment
4. View Employees on a Specific Date
5. View Employees During a Date Range
6. View Employee Assignment History
7. View Current Employee Department
8. Initialize / Reset Sample Test Data
9. Exit
====================================================
```

- **Option 1: Employee Management**: Add, View, Search, Update, Delete employees.
- **Option 2: Department Management**: Add, View, Search, Update, Delete departments.
- **Option 3: Employee Department Assignment**: Assign, Transfer/Change department, View history, View active department.
- **Option 4: View Employees on a Specific Date**: Prompts for `MM-DD-CCYY` and reports all staff active on that date.
- **Option 5: View Employees During a Date Range**: Prompts for Start and End dates, reporting all overlapping assignments.
- **Option 6: View Employee Assignment History**: Quick shortcut from main menu.
- **Option 7: View Current Employee Department**: Quick shortcut from main menu.
- **Option 8: Initialize / Reset Sample Test Data**: Resets files to the official sample test dataset.
- **Option 9: Exit**: Clean shutdown.

---

## 10. Sample Test Cases & Scenarios

All custom date functions and 16 specification scenarios are verified via `test_system.py`:

| # | Test Scenario | Input / Action | Expected Result | Status |
|---|---------------|----------------|-----------------|:------:|
| A1| Leap year calculation | 2024, 2000, 1900, 2023 | T, T, F, F | **PASS** |
| A2| Month day boundaries | Feb 2024 (29), Feb 2023 (28), Apr (30) | Correct maximum day returned | **PASS** |
| A3| Custom date format | 01-15-2024 vs 13-20-2024, 02-30-2024 | Valid parsed; invalid rejected | **PASS** |
| A4| Manual date compare | (2024, 1, 1) vs (2024, 6, 30) | -1 (earlier) | **PASS** |
| A5| Manual overlap math | [01-01 to 06-30] & [06-15 to Current] | Overlap detected | **PASS** |
| 1 | Add valid employee | Rajan, 21, Coimbatore, Tamil Nadu, India | Created with ID `EMP001` | **PASS** |
| 2 | Reject age < 18 | Age = 17 | Rejected with age validation error | **PASS** |
| 3 | Reject age > 65 | Age = 66 | Rejected with age validation error | **PASS** |
| 4 | Add department | Description = "Human Resources" | Created with ID `DEP001` | **PASS** |
| 5 | Assign employee | EMP001 -> DEP001 (01-01-2024 to 06-30-2024) | Created with ID `ASG001` | **PASS** |
| 6 | Reject invalid date | 13-20-2024, 02-30-2024, 2024-01-15 | Rejected with format error | **PASS** |
| 7 | Reject overlapping dates | 06-15-2024 to Current when existing is 01-01-2024 to 06-30-2024 | Rejected due to date overlap | **PASS** |
| 8 | Reject duplicate current dept | Assign to DEP002 when already active in DEP002 | Rejected: "This employee is already working in this department." | **PASS** |
| 9 | Allow department change | Close DEP002 on 09-30-2024, start DEP003 on 10-01-2024 | Old closed, new active, history intact | **PASS** |
| 10 | Return to previous dept | Return to DEP001 starting 01-01-2025 | Allowed; history preserved | **PASS** |
| 11 | Reject end date < start date | Start: 05-10-2024, End: 05-01-2024 | Rejected: End date cannot be earlier than start date | **PASS** |
| 12 | Specific date report | Date: 05-15-2024 | Returns all 3 active employees | **PASS** |
| 13 | Date range report | 01-01-2024 to 12-31-2024 | Returns all overlapping assignments | **PASS** |
| 14 | Multiple assignments | View history for EMP001 | Shows all 4 sequential assignments | **PASS** |
| 15 | Data persistence | Restart app & read `.txt` files directly | All records preserved from disk | **PASS** |
| 16 | Prevent dept deletion with history | Attempt to delete DEP001 | Blocked with referral error | **PASS** |

---

## 11. Technical Interview Demonstration Guide

When explaining this application during an interview, highlight these key design patterns:

1. **Manual Date Handling Without Magic Libraries**:
   Explain how `is_leap_year` implements the Gregorian algorithm, how `get_days_in_month` handles month lengths, and how `compare_dates` compares year $\rightarrow$ month $\rightarrow$ day hierarchically.
2. **Interval Overlap Formula**:
   Demonstrate that checking whether two intervals $[S_1, E_1]$ and $[S_2, E_2]$ overlap requires only two inequalities: $S_1 \le E_2$ and $S_2 \le E_1$.
3. **Custom ASCII Parser & Serializer**:
   Explain how `format_ascii_table` calculates maximum column widths dynamically and how `parse_ascii_table` reads pipe-separated rows safely.
4. **Data Integrity & Fault Tolerance**:
   Explain how referential checks protect historical departments and how `tempfile` + `os.replace` guarantees atomic writes without corrupted files.
=======
# Employee_Management
>>>>>>> 9505a739b06412418a572da85e68185825453f39

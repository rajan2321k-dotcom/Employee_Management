# Employee & Department Management System

A focused, enterprise-grade Python console application for managing employee registrations, department creation, department assignments, and date-based workforce reporting.

---

## 1. Project Overview & Core Constraints

* **Storage Format**: Plain-text `.txt` files using **CSV format** (`emp.txt`, `department.txt`, `employee_department.txt`).
* **Python Built-in `csv` Module**: All file operations use `csv.DictReader` and `csv.DictWriter`.
* **Zero Databases**: No MySQL, SQLite, PostgreSQL, MongoDB, or Pandas.
* **Zero Built-in Date Libraries**: Completely free of `datetime`, `date`, `time`, and `calendar`. All date calculations (leap years, month days, format validation, comparisons, and interval overlaps) are written from scratch.
* **Terminal Display**: Formatted as clean **ASCII tables**.
* **Sequential Validation**: Every user input is validated immediately upon entry. If invalid, subsequent input collection is aborted immediately.

---

## 2. Project Folder Structure

```
Employee_Department_System/
│
├── main.py                     # Main application loop with EXACTLY 7 menu options
├── employee.py                 # Add Employee & sequential validation
├── department.py               # Add Department logic
├── assignment.py               # Department assignment & department change logic
├── reports.py                  # Specific date & date range employee reporting
├── validation.py               # Custom manual date engine & strict field validation
├── file_handler.py             # CSV reading/writing & ASCII table terminal formatting
├── init_sample_data.py         # Standalone CSV sample data initializer
├── test_system.py              # Automated 15-case verification test suite
├── emp.txt                     # Plain text CSV storage for employees
├── department.txt              # Plain text CSV storage for departments
├── employee_department.txt     # Plain text CSV storage for assignments
├── README.md                   # Complete system documentation
└── requirements.txt            # Environment specifications
```

---

## 3. Main Menu

The main menu contains ONLY the following 7 options:

```text
====================================================
   EMPLOYEE & DEPARTMENT MANAGEMENT SYSTEM
====================================================
1. Add Employee
2. Add Department
3. Assign Employee to Department
4. Change Employee Department
5. View Employees Working on a Date
6. View Employees Working Within a Date Range
7. Exit
====================================================
```

---

## 4. Text File Storage (CSV Format)

All records are stored as comma-separated values inside `.txt` files.

### `emp.txt`
```csv
Employee ID,Name,Age,City,State,Country
EMP001,Rajan S,21,Coimbatore,Tamil Nadu,India
EMP002,Arun,25,Chennai,Tamil Nadu,India
EMP003,Kumar,30,Madurai,Tamil Nadu,India
EMP004,Prem Kumar S,20,Coimbatore,Tamilnadu,India
```

### `department.txt`
```csv
Department ID,Description
DEP001,Human Resources
DEP002,Software Development
DEP003,Finance
```

### `employee_department.txt`
```csv
Assignment ID,Employee ID,Department ID,Start Date,End Date
ASG001,EMP001,DEP001,01-01-2024,06-30-2024
ASG002,EMP001,DEP002,07-01-2024,Current
ASG003,EMP002,DEP003,02-01-2024,Current
ASG004,EMP003,DEP001,03-01-2024,05-31-2024
ASG005,EMP003,DEP002,06-01-2024,Current
```

---

## 5. How to View the Contents of the Text Files

### In Command Prompt / PowerShell:
```cmd
type Employee_Department_System\emp.txt
type Employee_Department_System\department.txt
type Employee_Department_System\employee_department.txt
```

### In VS Code:
Simply click and open `emp.txt`, `department.txt`, or `employee_department.txt` from the file explorer.

---

## 6. How to Run the Project

### Running in VS Code or Command Prompt:

1. Open your terminal in the project directory:
   ```cmd
   cd c:\Users\rajan\OneDrive\Desktop\Employee
   ```
2. Run the application:
   ```cmd
   python run.py
   ```
   *(Or navigate into `Employee_Department_System` and run `python main.py`)*

3. Run the automated 15-case test suite:
   ```cmd
   python Employee_Department_System/test_system.py
   ```

4. Reset / re-initialize sample test data:
   ```cmd
   python Employee_Department_System/init_sample_data.py
   ```

---

## 7. Sample Input and Output for All Six Operations

### Operation 1: Add Employee
```text
Enter your choice (1-7): 1

--- ADD EMPLOYEE ---
Enter Employee Name: Rajan S
Enter Age (18 - 65): 21
Enter City: Coimbatore
Enter State: Tamil Nadu
Enter Country: India

[SUCCESS] Employee EMP005 added successfully.

Saved Employee Record (CSV stored, ASCII display):
+-------------+---------+-----+------------+------------+---------+
| Employee ID | Name    | Age | City       | State      | Country |
+-------------+---------+-----+------------+------------+---------+
| EMP005      | Rajan S | 21  | Coimbatore | Tamil Nadu | India   |
+-------------+---------+-----+------------+------------+---------+
```

### Operation 2: Add Department
```text
Enter your choice (1-7): 2

--- ADD DEPARTMENT ---
Enter Department Description: Quality Assurance

[SUCCESS] Department DEP004 ('Quality Assurance') added successfully.

Saved Department Record (CSV stored, ASCII display):
+---------------+-------------------+
| Department ID | Description       |
+---------------+-------------------+
| DEP004        | Quality Assurance |
+---------------+-------------------+
```

### Operation 3: Assign Employee to Department
```text
Enter your choice (1-7): 3

--- ASSIGN EMPLOYEE TO DEPARTMENT ---
Enter Employee ID (e.g., EMP001): EMP004
Enter Department ID (e.g., DEP001): DEP001
Enter Start Date (MM-DD-CCYY, e.g., 01-15-2024): 01-10-2024
Enter End Date (MM-DD-CCYY or press Enter for 'Current'): 05-20-2024

[SUCCESS] Assignment ASG006 created successfully for Employee EMP004 in Department DEP001 (01-10-2024 to 05-20-2024).

Saved Assignment Record (CSV stored, ASCII display):
+---------------+-------------+---------------+------------+------------+
| Assignment ID | Employee ID | Department ID | Start Date | End Date   |
+---------------+-------------+---------------+------------+------------+
| ASG006        | EMP004      | DEP001        | 01-10-2024 | 05-20-2024 |
+---------------+-------------+---------------+------------+------------+
```

### Operation 4: Change Employee Department
```text
Enter your choice (1-7): 4

--- CHANGE EMPLOYEE DEPARTMENT ---
Enter Employee ID (e.g., EMP001): EMP001

Current Active Assignment for Rajan S (EMP001):
  Assignment ID: ASG002
  Department:    DEP002 - Software Development
  Start Date:    07-01-2024
  End Date:      Current

Enter Closing Date for Current Department (MM-DD-CCYY): 09-30-2024
Enter New Department ID (e.g., DEP002): DEP003
Enter Start Date for New Department (MM-DD-CCYY): 10-01-2024
Enter End Date for New Department (MM-DD-CCYY or press Enter for 'Current'): 

[SUCCESS] Department changed successfully!
  - Closed Assignment ASG002: Department DEP002 ended on 09-30-2024.
  - Created Assignment ASG007: Department DEP003 started on 10-01-2024 (Current).
```

### Operation 5: View Employees Working on a Date
```text
Enter your choice (1-7): 5

--- VIEW EMPLOYEES WORKING ON A DATE ---
Enter Date (MM-DD-CCYY, e.g., 01-20-2024): 01-20-2024

---------------------------------
Employees Working On: 01-20-2024
---------------------------------
+---------------+-----------------+
| Employee Name | Department      |
+---------------+-----------------+
| Rajan S       | Human Resources |
+---------------+-----------------+

Total Employees: 1
```

### Operation 6: View Employees Working Within a Date Range
```text
Enter your choice (1-7): 6

--- VIEW EMPLOYEES WORKING WITHIN A DATE RANGE ---
Enter Start Date (MM-DD-CCYY, e.g., 01-01-2024): 01-01-2024
Enter End Date (MM-DD-CCYY, e.g., 12-31-2024): 12-31-2024

-----------------------------------------------------------------------------------------
Employees Working Within Date Range: 01-01-2024 to 12-31-2024
-----------------------------------------------------------------------------------------
+---------------+----------------------+-----------------------+---------------------+
| Employee Name | Department           | Assignment Start Date | Assignment End Date |
+---------------+----------------------+-----------------------+---------------------+
| Arun          | Finance              | 02-01-2024            | Current             |
| Kumar         | Human Resources      | 03-01-2024            | 05-31-2024          |
| Kumar         | Software Development | 06-01-2024            | Current             |
| Rajan S       | Human Resources      | 01-01-2024            | 06-30-2024          |
| Rajan S       | Software Development | 07-01-2024            | Current             |
+---------------+----------------------+-----------------------+---------------------+

Total Overlapping Assignments Found: 5
```

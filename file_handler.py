"""
file_handler.py - CSV Text File Storage Engine

Handles all persistence operations for the Employee & Department Management System.
All data is stored exclusively in plain-text .txt files using CSV format.
Uses Python's built-in csv module.
No database, Pandas, or binary formats are used.
Includes ASCII table formatting for terminal output.
"""

import os
import csv
import tempfile
from typing import List, Dict, Optional

# Base directory for data files (same directory as this module)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

EMP_FILE = os.path.join(BASE_DIR, "emp.txt")
DEPT_FILE = os.path.join(BASE_DIR, "department.txt")
ASG_FILE = os.path.join(BASE_DIR, "employee_department.txt")

EMP_HEADERS = ["Employee ID", "Name", "Age", "City", "State", "Country"]
DEPT_HEADERS = ["Department ID", "Description"]
ASG_HEADERS = ["Assignment ID", "Employee ID", "Department ID", "Start Date", "End Date"]


def format_ascii_table(headers: List[str], records: List[Dict[str, str]]) -> str:
    """
    Format a list of record dictionaries into a clean ASCII table string for terminal display.
    Calculates dynamic column widths based on headers and data contents.
    """
    if not headers:
        return ""

    # Compute maximum width needed for each column
    col_widths = []
    for h in headers:
        max_len = len(h)
        for r in records:
            val_len = len(str(r.get(h, "")))
            if val_len > max_len:
                max_len = val_len
        col_widths.append(max_len)

    # Build ASCII table borders and rows
    sep = "+" + "+".join("-" * (w + 2) for w in col_widths) + "+"
    header_row = "|" + "|".join(f" {headers[i].ljust(col_widths[i])} " for i in range(len(headers))) + "|"

    lines = [sep, header_row, sep]
    if records:
        for r in records:
            row_str = "|" + "|".join(f" {str(r.get(headers[i], '')).ljust(col_widths[i])} " for i in range(len(headers))) + "|"
            lines.append(row_str)
        lines.append(sep)
    return "\n".join(lines) + "\n"


def _migrate_ascii_to_csv_if_needed(filepath: str, headers: List[str]) -> Optional[List[Dict[str, str]]]:
    """
    Detects if an existing .txt file is in the older ASCII table format (| col |)
    and extracts the records so they can be smoothly converted to CSV without data loss.
    """
    if not os.path.exists(filepath):
        return None

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            first_line = f.readline()
            if not first_line.startswith("+"):
                return None  # Already CSV or empty

            f.seek(0)
            content = f.read()

        lines = [line.strip() for line in content.splitlines() if line.strip()]
        table_headers = None
        records = []
        for line in lines:
            if line.startswith("+"):
                continue
            if line.startswith("|") and line.endswith("|"):
                raw_cells = [c.strip() for c in line.split("|")[1:-1]]
                if table_headers is None:
                    table_headers = raw_cells
                else:
                    if len(raw_cells) == len(table_headers):
                        rec = {table_headers[i]: raw_cells[i] for i in range(len(table_headers))}
                        records.append(rec)
        return records
    except Exception:
        return None


def ensure_file_exists(filepath: str, headers: List[str]) -> None:
    """
    Ensure the data file exists in CSV format.
    If missing or empty (0 bytes), creates it initialized with the CSV header row.
    If it contains legacy ASCII formatting, automatically migrates to CSV.
    """
    # Check for legacy ASCII format to preserve existing data
    migrated_records = _migrate_ascii_to_csv_if_needed(filepath, headers)
    if migrated_records is not None:
        write_records(filepath, headers, migrated_records)
        return

    need_init = False
    if not os.path.exists(filepath):
        need_init = True
    else:
        try:
            if os.path.getsize(filepath) == 0:
                need_init = True
        except OSError:
            need_init = True

    if need_init:
        dir_name = os.path.dirname(filepath)
        if dir_name and not os.path.exists(dir_name):
            os.makedirs(dir_name, exist_ok=True)
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(headers)


def read_records(filepath: str, headers: List[str]) -> List[Dict[str, str]]:
    """
    Read all records from a CSV-formatted .txt file using Python's built-in csv module.
    Automatically creates the file if it does not exist.
    Returns a list of dictionaries mapping header names to string values.
    """
    ensure_file_exists(filepath, headers)
    records: List[Dict[str, str]] = []
    try:
        with open(filepath, "r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Strip whitespace from keys and values
                cleaned_row = {
                    (k.strip() if k else ""): (v.strip() if v else "")
                    for k, v in row.items()
                    if k is not None
                }
                # Ensure all expected headers are present
                if all(h in cleaned_row for h in headers):
                    records.append(cleaned_row)
        return records
    except Exception as e:
        print(f"[Error reading {os.path.basename(filepath)}: {e}]")
        return []


def write_records(filepath: str, headers: List[str], records: List[Dict[str, str]]) -> bool:
    """
    Write records to a CSV-formatted .txt file atomically using a temporary file.
    Prevents file corruption in case of unexpected termination.
    """
    try:
        dir_name = os.path.dirname(filepath)
        if dir_name and not os.path.exists(dir_name):
            os.makedirs(dir_name, exist_ok=True)

        # Atomic write pattern: write to temp file then replace
        temp_fd, temp_path = tempfile.mkstemp(dir=dir_name, prefix="tmp_csv_", suffix=".txt")
        with os.fdopen(temp_fd, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=headers, extrasaction="ignore")
            writer.writeheader()
            for r in records:
                writer.writerow(r)

        # os.replace is atomic on both Windows and POSIX
        os.replace(temp_path, filepath)
        return True
    except Exception as e:
        print(f"[Error writing to {os.path.basename(filepath)}: {e}]")
        if "temp_path" in locals() and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except OSError:
                pass
        return False


def append_record(filepath: str, headers: List[str], new_record: Dict[str, str]) -> bool:
    """
    Append a new record to the CSV-formatted .txt file.
    """
    ensure_file_exists(filepath, headers)
    try:
        with open(filepath, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=headers, extrasaction="ignore")
            writer.writerow(new_record)
        return True
    except Exception as e:
        print(f"[Error appending to {os.path.basename(filepath)}: {e}]")
        return False


def update_record(
    filepath: str,
    headers: List[str],
    id_field: str,
    id_value: str,
    updated_fields: Dict[str, str]
) -> bool:
    """
    Update a record identified by id_field == id_value.
    Preserves all other fields not included in updated_fields.
    """
    records = read_records(filepath, headers)
    updated = False
    for r in records:
        if r.get(id_field, "").strip().upper() == id_value.strip().upper():
            for k, v in updated_fields.items():
                if k in headers:
                    r[k] = str(v)
            updated = True
            break

    if updated:
        return write_records(filepath, headers, records)
    return False


def initialize_storage_files() -> None:
    """
    Ensure all three system .txt files exist in CSV format.
    """
    ensure_file_exists(EMP_FILE, EMP_HEADERS)
    ensure_file_exists(DEPT_FILE, DEPT_HEADERS)
    ensure_file_exists(ASG_FILE, ASG_HEADERS)

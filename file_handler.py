"""
file_handler.py - ASCII Table File Storage Engine

Handles all persistence operations for the Employee & Department Management System.
All data is stored exclusively in readable plain-text files using ASCII table formatting.
No database or binary formats are used.
"""

import os
import tempfile
from typing import List, Dict, Optional, Tuple

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
    Format a list of record dictionaries into a neat ASCII table string.
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

    # Build ASCII components
    sep = "+" + "+".join("-" * (w + 2) for w in col_widths) + "+"
    header_row = "|" + "|".join(f" {headers[i].ljust(col_widths[i])} " for i in range(len(headers))) + "|"

    lines = [sep, header_row, sep]
    if records:
        for r in records:
            row_str = "|" + "|".join(f" {str(r.get(headers[i], '')).ljust(col_widths[i])} " for i in range(len(headers))) + "|"
            lines.append(row_str)
        lines.append(sep)
    return "\n".join(lines) + "\n"


def parse_ascii_table(content: str, expected_headers: List[str]) -> List[Dict[str, str]]:
    """
    Parse an ASCII table string into a list of record dictionaries.
    Handles empty content, whitespace, and malformed lines gracefully.
    """
    records: List[Dict[str, str]] = []
    if not content or not content.strip():
        return records

    lines = [line.strip() for line in content.splitlines() if line.strip()]
    table_headers: Optional[List[str]] = None

    for line in lines:
        # Skip border/separator lines
        if line.startswith("+"):
            continue

        # Process row lines
        if line.startswith("|") and line.endswith("|"):
            raw_cells = line.split("|")[1:-1]
            cells = [c.strip() for c in raw_cells]

            # The first pipe line is treated as the header
            if table_headers is None:
                table_headers = cells
            else:
                # Malformed row safeguard: must match header length
                if len(cells) == len(table_headers):
                    record = {table_headers[i]: cells[i] for i in range(len(table_headers))}
                    records.append(record)

    return records


def ensure_file_exists(filepath: str, headers: List[str]) -> None:
    """
    Ensure the data file exists. If missing or empty (0 bytes),
    creates it initialized with the standard ASCII table header.
    """
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
        initial_content = format_ascii_table(headers, [])
        # Write safely
        dir_name = os.path.dirname(filepath)
        if dir_name and not os.path.exists(dir_name):
            os.makedirs(dir_name, exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(initial_content)


def read_records(filepath: str, headers: List[str]) -> List[Dict[str, str]]:
  
    ensure_file_exists(filepath, headers)
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        return parse_ascii_table(content, headers)
    except Exception as e:
        # In case of I/O error, avoid crash, return empty list
        print(f"[Error reading {os.path.basename(filepath)}: {e}]")
        return []


def write_records(filepath: str, headers: List[str], records: List[Dict[str, str]]) -> bool:
   
    try:
        content = format_ascii_table(headers, records)
        dir_name = os.path.dirname(filepath)
        if dir_name and not os.path.exists(dir_name):
            os.makedirs(dir_name, exist_ok=True)

        # Atomic write pattern: write to temp file then replace
        temp_fd, temp_path = tempfile.mkstemp(dir=dir_name, prefix="tmp_agy_", suffix=".txt")
        with os.fdopen(temp_fd, "w", encoding="utf-8") as f:
            f.write(content)

        # os.replace is atomic on both Windows and POSIX
        os.replace(temp_path, filepath)
        return True
    except Exception as e:
        print(f"[Error writing to {os.path.basename(filepath)}: {e}]")
        if 'temp_path' in locals() and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except OSError:
                pass
        return False


def append_record(filepath: str, headers: List[str], new_record: Dict[str, str]) -> bool:

    records = read_records(filepath, headers)
    records.append(new_record)
    return write_records(filepath, headers, records)


def update_record(
    filepath: str,
    headers: List[str],
    id_field: str,
    id_value: str,
    updated_fields: Dict[str, str]
) -> bool:
   
    records = read_records(filepath, headers)
    updated = False
    for r in records:
        if r.get(id_field, "").strip() == id_value.strip():
            for k, v in updated_fields.items():
                if k in headers:
                    r[k] = str(v)
            updated = True
            break

    if updated:
        return write_records(filepath, headers, records)
    return False


def delete_record(filepath: str, headers: List[str], id_field: str, id_value: str) -> bool:
   
    records = read_records(filepath, headers)
    initial_count = len(records)
    records = [r for r in records if r.get(id_field, "").strip() != id_value.strip()]

    if len(records) < initial_count:
        return write_records(filepath, headers, records)
    return False


def initialize_storage_files() -> None:
  
    ensure_file_exists(EMP_FILE, EMP_HEADERS)
    ensure_file_exists(DEPT_FILE, DEPT_HEADERS)
    ensure_file_exists(ASG_FILE, ASG_HEADERS)

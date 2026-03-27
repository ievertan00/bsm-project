import os
import re
import requests
from pathlib import Path

# Configuration
BASE_DIR = r"D:\工作\Work\1.汇通智融\4.报表统计\3.业务数据\1.业务报表"
API_URL = "http://127.0.0.1:8000/bulk_import/"
SCHEMA_TYPE = "business_data"

# Regex to match '智融担保项目明细_YYYY年MM月.xlsx' or .xls
# It extracts YYYY as group 1 and MM as group 2
FILE_PATTERN = re.compile(r"智融担保项目明细_(\d{4})年(\d{1,2})月\.(xlsx|xls)")

def bulk_upload():
    files_to_upload = []
    snapshot_years = []
    snapshot_months = []
    opened_files = []

    print(f"Scanning directory: {BASE_DIR}")
    
    # Search recursively for files
    for path in Path(BASE_DIR).rglob("智融担保项目明细_*.xls*"):
        match = FILE_PATTERN.match(path.name)
        if match:
            year = match.group(1)
            month = match.group(2)
            
            print(f"Found: {path.name} (Year: {year}, Month: {month})")
            
            # Prepare the file for requests
            f = open(path, 'rb')
            opened_files.append(f)
            files_to_upload.append(('files', (path.name, f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')))
            snapshot_years.append(year)
            snapshot_months.append(month)

    if not files_to_upload:
        print("No matching files found.")
        return

    print(f"Uploading {len(files_to_upload)} files to {API_URL}...")

    # Prepare form data
    # Note: snapshot_years and snapshot_months are passed as multiple values for the same key
    data = {
        'schema_type': SCHEMA_TYPE
    }
    
    # Since years/months are marked as File(...) in your main.py, 
    # they are treated as form fields.
    payload = []
    for y in snapshot_years: payload.append(('snapshot_years', (None, y)))
    for m in snapshot_months: payload.append(('snapshot_months', (None, m)))
    
    # Combine files and the "File" fields for years/months
    all_files = files_to_upload + payload

    try:
        # schema_type is a Query parameter
        response = requests.post(
            API_URL, 
            params={'schema_type': SCHEMA_TYPE}, 
            files=all_files
        )
        
        if response.status_code == 200:
            print("Success!")
            print(response.json())
        else:
            print(f"Failed with status code: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Close all file handles
        for f in opened_files:
            f.close()

if __name__ == "__main__":
    bulk_upload()

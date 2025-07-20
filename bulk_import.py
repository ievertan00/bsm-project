import os
import requests
import glob

# --- Configuration ---
data_dir = "/Users/evertan/gemini_project/bsm/sample_data"
api_url = "http://localhost:5000/api/import"

# --- Get all Excel files ---
files_to_upload = sorted(glob.glob(os.path.join(data_dir, "sample_data_*.xlsx")))

if not files_to_upload:
    print("No sample data files found to upload.")
else:
    print(f"Found {len(files_to_upload)} files to import...")

# --- Loop and Upload ---
for file_path in files_to_upload:
    try:
        filename = os.path.basename(file_path)
        # Extract YYYY-MM from filename like 'sample_data_2025-01.xlsx'
        temp = filename.replace("sample_data_", "").replace(".xlsx", "")
        year_month = temp

        print(f"Importing {filename} for year-month {year_month}...", end='')
        
        with open(file_path, 'rb') as f:
            files = {'file': (filename, f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
            data = {'year_month': year_month}
            
            response = requests.post(api_url, files=files, data=data)
            
            if response.status_code == 200:
                print(" Success")
            else:
                print(f" Failed (Status: {response.status_code}, Response: {response.text})")

    except Exception as e:
        print(f" An error occurred while processing {file_path}: {e}")

print("\nBulk import process complete.")

# Reproduction Guide: Normalized Business Data Import & Analysis System

This guide outlines the architecture and steps required to reproduce the demo application, a system designed for managing periodic business data snapshots for technology and industrial enterprises, specifically for the "Guaranty/Surety" (智融担保) sector.

## 1. Tech Stack
To rebuild this system, you will need the following environment:

*   **Language**: Python 3.9+
*   **Web Framework**: [FastAPI](https://fastapi.tiangolo.com/) (Backend)
*   **Application Server**: [Uvicorn](https://www.uvicorn.org/)
*   **Database & ORM**: PostgreSQL with [SQLAlchemy](https://www.sqlalchemy.org/) for low-latency data handling
*   **Data Processing**: [Pandas](https://pandas.pydata.org/) (Core ETL engine), `openpyxl`, `xlrd` (Excel engines)
*   **Frontend**: Modern UI framework (e.g., React, Vue)
*   **Security**: Robust Authentication (JWT / OAuth2)

## 2. Environment Setup
Follow these steps to initialize the project from scratch:

### Step 1: Initialize Virtual Environment
```powershell
python -m venv venv
.\venv\Scripts\activate
pip install fastapi uvicorn sqlalchemy pandas openpyxl xlrd python-multipart passlib[bcrypt] python-jose[cryptography]
```

### Step 2: Database Initialization
The project uses a PostgreSQL database. Ensure you have updated the connection string in `database.py`. You can initialize the tables by running a script that leverages SQLAlchemy's `create_all` method:
```python
# init_db.py
from database import engine
import models
models.Base.metadata.create_all(bind=engine)
```

### Step 3: Run the Application
Start the server with Uvicorn:
```powershell
python main.py
# Or directly via uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## 3. Core Implementation & Key Features

### Feature A: Multi-Source Excel ETL (The Logic Core)
The system's most complex part is the `services.py` layer, which acts as a specialized parser for different bank and offline report formats (e.g., WeBank, ICBC, CCB).

**High-Level Pseudocode:**
```python
def process_excel_import(db, contents, schema_type, year, month):
    # 1. Read byte contents into Pandas DataFrame based on schema_type rules
    df = pd.read_excel(io.BytesIO(contents))
    
    # 2. Normalize columns (e.g., map '客户名称' or '企业名称' to 'company_name')
    normalized_data = map_columns(df, schema_type)
    
    # 3. Snapshot logic: For each row:
    #    - If Company doesn't exist, create it.
    #    - Create/Update a 'BusinessData' entry linked to (company_id, year, month).
```

### Feature B: Automated Statistics Generation
The system calculates cross-year trends by aggregating data points like "Guarantee Balance" and "Unique Company Counts."
*   **Logic**: It queries the `BusinessData` table, filters by (Year, Month), and uses Pandas to perform group-bys and sums to generate a JSON report for the frontend.

### Feature C: Data Enrichment (QCC Synchronization)
*   **Logic**: The system loads master data from `qcc_industry.xlsx` and `qcc_tech.xlsx` into the database. A "Sync" endpoint then performs a left-join between active business snapshots and these master tables to tag enterprises with their industry and technology level.

## 4. Potential Pitfalls
When rebuilding, watch out for these common issues:

1.  **Excel Schema Sensitivity**: The ETL logic in `services.py` depends heavily on exact column names (e.g., "借款金额（万元）"). If the source Excel file format changes slightly, the import will fail with a `KeyError`.
2.  **Hardcoded Credentials**: In the demo, `VALID_USERS` is a hardcoded dictionary in `main.py`. For production, this should be moved to a hashed database table or environment variables.
3.  **Local Path Dependencies**: Scripts like `bulk_upload_client.py` often contain hardcoded Windows paths (e.g., `D:\工作\...`). Ensure these are parameterized or relative to the project root.
4.  **Database Connection Pooling**: While PostgreSQL handles concurrency better than SQLite, bulk imports can still exhaust connection limits. Ensure proper transaction management (`db.commit()`, `db.rollback()`) and consider using a connection pooler like PgBouncer for production.

## 5. Primary Components
*   `models.py`: Defines the Relational Schema (Company 1:N BusinessData).
*   `main.py`: The API Router and Basic Auth handler.
*   `services.py`: The "Heavy Lifter" containing the Pandas-based processing logic.
*   `index.html`: The dashboard interface.

# BSM Project Reproduction Guide

This guide provides step-by-step instructions for setting up and understanding the BSM Project, a modernized Business Statistics Management system.

## Tech Stack

### Backend
- **Framework:** FastAPI (Python 3.12+)
- **Dependency Management:** [UV](https://astral.sh/uv/) (Fast Python package installer and resolver)
- **Database:** PostgreSQL
- **ORM:** SQLAlchemy with Alembic for migrations
- **Authentication:** JWT (JSON Web Tokens) with `python-jose` and `passlib`
- **Data Processing:** Pandas, Openpyxl (for Excel import)

### Frontend
- **Framework:** React (TypeScript)
- **UI Library:** Ant Design (v6+)
- **Charts/Visualization:** ECharts (via `echarts-for-react`)
- **State/Routing:** React Router DOM (v6)
- **HTTP Client:** Axios

---

## Environment Setup

### Prerequisites
- Python 3.12 or higher
- Node.js (LTS recommended)
- PostgreSQL running locally or accessible via network

### 1. Backend Setup (UV)

1.  **Install UV:**
    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```

2.  **Initialize Virtual Environment:**
    Navigate to the `backend` directory:
    ```bash
    cd backend
    uv venv
    # Activate:
    # Windows: .venv\Scripts\activate
    # Unix: source .venv/bin/activate
    ```

3.  **Install Dependencies:**
    ```bash
    uv pip install -r requirements.txt
    ```

4.  **Configure Environment Variables:**
    Create a `.env` file in the `backend` directory:
    ```env
    DATABASE_URL=postgresql://postgres:password@localhost:5432/bsm_db
    SECRET_KEY=your_super_secret_key_for_jwt
    ALGORITHM=HS256
    ACCESS_TOKEN_EXPIRE_MINUTES=60
    ```

5.  **Database Migrations:**
    ```bash
    alembic upgrade head
    ```

6.  **Run Development Server:**
    ```bash
    uv run uvicorn app.main:app --reload
    ```

### 2. Frontend Setup (NPM)

1.  **Navigate to Frontend:**
    ```bash
    cd frontend
    ```

2.  **Install Dependencies:**
    ```bash
    npm install
    ```

3.  **Run Development Server:**
    ```bash
    npm start
    ```

---

## Core Implementation Details

### 1. Authentication (JWT)
The system uses FastAPI's `OAuth2PasswordBearer` for token handling.
- **Login:** `POST /api/auth/login` issues a JWT token.
- **Protection:** Use `Depends(get_current_user)` in route parameters to protect endpoints.

### 2. Excel Data Import
The `backend/app/importer.py` handles parsing Excel files using Pandas.
- **Logic:** It checks for existing companies by name to avoid duplicates and creates new `BusinessData` entries linked to the company.
- **Key Columns:** `enterprise_name`, `loan_amount`, `guarantee_amount`, `snapshot_year`, `snapshot_month`.

### 3. Dashboard Aggregations
Data is aggregated directly via SQLAlchemy `func` calls in `backend/app/api/dashboard.py`.
- **Growth Data:** Grouped by `snapshot_year` and `snapshot_month` to provide time-series data for ECharts.
- **Summary:** Provides high-level totals for loans and guarantees.

---

## Potential Pitfalls & Troubleshooting

### CORS (Cross-Origin Resource Sharing)
If the frontend cannot reach the backend, ensure the `CORSMiddleware` in `backend/app/main.py` is configured with the correct `allow_origins`.

### Database Migrations
If you modify `models.py`, generate a new migration:
```bash
alembic revision --autogenerate -m "description of changes"
alembic upgrade head
```

### JWT Token Expiration
If you receive 401 Unauthorized unexpectedly, check if your token has expired. The default is set in the `.env` file.

### Excel Format
Ensure the Excel file contains the expected column names defined in `importer.py`. Missing columns will result in `KeyError` during import.

---

## Sample Data
A `sample_data.xlsx` template should be used for testing the import functionality. Ensure it contains at least one row with valid enterprise and financial data.

# BSM Reproduction Guide Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create a comprehensive "Reproduction Guide" for a Business Success Metrics (BSM) platform using FastAPI, PostgreSQL, and React.

**Architecture:** A full-stack application with a FastAPI backend (JWT Auth, Async BackgroundTasks, PostgreSQL) and a React frontend (Context API, ECharts).

**Tech Stack:** FastAPI, PostgreSQL, SQLAlchemy, Pydantic, Alembic, Jose, Passlib, React, Axios, ECharts, Ant Design.

**Out of Scope:**
- Production deployment (Docker/Nginx).
- Multi-tenancy or Enterprise RBAC.
- Real-time notifications (WebSockets).

---

### Task 1: Project Initialization

**Files:**
- Create: `backend/requirements.txt`
- Create: `backend/.env`
- Create: `frontend/package.json`

- [ ] **Step 1: Define Backend Dependencies**
  Add the following to `backend/requirements.txt`:
  ```text
  fastapi
  uvicorn[standard]
  sqlalchemy
  psycopg[binary]
  pydantic
  pydantic-settings
  alembic
  python-jose[cryptography]
  passlib[bcrypt]
  pandas
  openpyxl
  python-multipart
  fastapi-cors
  ```

- [ ] **Step 2: Initialize Backend Environment**
  Run: `cd backend && uv venv && .\venv\Scripts\activate && uv pip install -r requirements.txt`

- [ ] **Step 3: Define Frontend Dependencies**
  Add the following to `frontend/package.json`:
  ```json
  {
    "dependencies": {
      "react": "^18.2.0",
      "react-dom": "^18.2.0",
      "react-router-dom": "^6.10.0",
      "axios": "^1.3.5",
      "echarts": "^5.4.2",
      "echarts-for-react": "^3.0.2",
      "antd": "^5.4.2"
    }
  }
  ```

- [ ] **Step 4: Configure CORS Middleware**
  Create `backend/app/main.py` and add `CORSMiddleware`:
  ```python
  from fastapi import FastAPI
  from fastapi.middleware.cors import CORSMiddleware

  app = FastAPI()
  app.add_middleware(
      CORSMiddleware,
      allow_origins=["http://localhost:3000"],
      allow_credentials=True,
      allow_methods=["*"],
      allow_headers=["*"],
  )
  ```

- [ ] **Step 5: Commit**
  ```bash
  git add backend/requirements.txt backend/app/main.py frontend/package.json
  git commit -m "chore: initialize project dependencies and CORS"
  ```

---

### Task 2: Database Schema & Migration

**Files:**
- Create: `backend/app/database.py`
- Create: `backend/app/models.py`
- Modify: `backend/alembic/env.py`

- [ ] **Step 1: Configure Database Connection**
  Implement `backend/app/database.py` with SQLAlchemy `create_engine` and `sessionmaker`.

- [ ] **Step 2: Define SQLAlchemy Models**
  Implement `backend/app/models.py` with `User`, `Company`, and `BusinessData` tables. Ensure `Base` is imported.

- [ ] **Step 3: Initialize Alembic & Configure Metadata**
  Run: `cd backend && alembic init alembic`
  Modify `backend/alembic/env.py` to include:
  ```python
  from app.models import Base
  target_metadata = Base.metadata
  ```

- [ ] **Step 4: Create & Run Initial Migration**
  Run: `cd backend && alembic revision --autogenerate -m "initial_schema" && alembic upgrade head`

- [ ] **Step 5: Commit**
  ```bash
  git add backend/app/database.py backend/app/models.py backend/alembic/
  git commit -m "feat: define database schema and initial migration"
  ```

---

### Task 3: Authentication & Security

**Files:**
- Create: `backend/app/auth.py`
- Create: `backend/app/schemas.py`
- Create: `backend/app/api/auth.py`
- Create: `backend/tests/test_auth.py`

- [ ] **Step 1: Implement JWT & Hashing Utilities**
  Implement `backend/app/auth.py` using `jose` and `passlib`. Include `SECRET_KEY` and `ALGORITHM` from `.env`.

- [ ] **Step 2: Define Pydantic Schemas**
  Implement `backend/app/schemas.py` for `UserCreate`, `UserOut`, and `Token`.

- [ ] **Step 3: Implement Login API**
  Create `backend/app/api/auth.py` with a `/token` route and a `get_current_user` dependency.

- [ ] **Step 4: Write & Run Auth Tests**
  Create `backend/tests/test_auth.py` and test the `/token` endpoint with a test user.
  Run: `pytest backend/tests/test_auth.py`

- [ ] **Step 5: Commit**
  ```bash
  git add backend/app/auth.py backend/app/schemas.py backend/app/api/auth.py backend/tests/test_auth.py
  git commit -m "feat: implement JWT authentication and tests"
  ```

---

### Task 4: Data Import Engine

**Files:**
- Create: `backend/app/importer.py`
- Create: `backend/app/api/data.py`
- Create: `sample_data.xlsx`

- [ ] **Step 1: Implement Excel Processing Logic**
  Implement `backend/app/importer.py`. Logic:
  - Read with Pandas.
  - Normalize column names (strip whitespace, map to internal names).
  - Handle missing columns with default values.
  - Match `Company` by name; update static fields.

- [ ] **Step 2: Implement Async Upload Route**
  Add `POST /api/import` in `backend/app/api/data.py` that uses `BackgroundTasks` to process the file in the background.

- [ ] **Step 3: Create Sample Excel File**
  Generate a `sample_data.xlsx` with dummy business data for testing.

- [ ] **Step 4: Verify Import Workflow**
  Test the endpoint via Swagger UI (`/docs`) using the sample file.

- [ ] **Step 5: Commit**
  ```bash
  git add backend/app/importer.py backend/app/api/data.py sample_data.xlsx
  git commit -m "feat: implement async excel data import with sample data"
  ```

---

### Task 5: Analysis API

**Files:**
- Create: `backend/app/api/dashboard.py`
- Create: `backend/tests/test_analysis.py`

- [ ] **Step 1: Implement Aggregation Queries**
  Implement `/api/dashboard/summary` and `/api/dashboard/growth` routes.
  Use SQLAlchemy `func.sum()` and `func.count()` to aggregate `BusinessData` across snapshots.

- [ ] **Step 2: Write & Run Analysis Tests**
  Create `backend/tests/test_analysis.py` to verify the calculated metrics for the sample data.
  Run: `pytest backend/tests/test_analysis.py`

- [ ] **Step 3: Commit**
  ```bash
  git add backend/app/api/dashboard.py backend/tests/test_analysis.py
  git commit -m "feat: implement analysis api and verification tests"
  ```

---

### Task 6: Frontend Auth & State

**Files:**
- Create: `frontend/src/context/AuthContext.js`
- Create: `frontend/src/api/axiosConfig.js`
- Create: `frontend/src/pages/Login.js`

- [ ] **Step 1: Implement AuthContext**
  Create a React Context to manage `user` and `token` state. Persist the token to `localStorage`.

- [ ] **Step 2: Configure Axios Interceptors**
  Implement `axiosConfig.js` to attach the JWT token to the `Authorization` header on every request.

- [ ] **Step 3: Implement Login Page**
  Create a basic Login form using Ant Design. Test the login flow.

- [ ] **Step 4: Commit**
  ```bash
  git add frontend/src/context/AuthContext.js frontend/src/api/axiosConfig.js frontend/src/pages/Login.js
  git commit -m "feat: implement frontend auth and interceptors"
  ```

---

### Task 7: Dashboard & Visualization

**Files:**
- Create: `frontend/src/pages/Dashboard.js`
- Create: `frontend/src/components/Charts/BSMCharts.js`

- [ ] **Step 1: Implement Dashboard Page**
  Create the Dashboard layout with filters (Year, Month, Bank) and chart containers.

- [ ] **Step 2: Integrate ECharts**
  Implement reusable chart components using `echarts-for-react`.
  - Line chart for Balance Projection.
  - Bar chart for New Business.

- [ ] **Step 3: Verify Visual Feedback**
  Ensure charts render correctly with data fetched from the API after login.

- [ ] **Step 4: Commit**
  ```bash
  git add frontend/src/pages/Dashboard.js frontend/src/components/Charts/BSMCharts.js
  git commit -m "feat: implement interactive dashboard with charts"
  ```

---

### Task 8: Reproduction Guide Drafting

**Files:**
- Create: `ReproductionGuide.md`

- [ ] **Step 1: Draft the Final Guide**
  Consolidate all snippets, explanations, and instructions into a single Markdown file.
  Include sections: Tech Stack, Setup, Models, API, Frontend, and Security.

- [ ] **Step 2: Review Guide for Clarity**
  Ensure all steps are atomic and explain the "why." Add a "Troubleshooting" section for CORS and Auth.

- [ ] **Step 3: Final Commit**
  ```bash
  git add ReproductionGuide.md
  git commit -m "docs: finalize reproduction guide"
  ```

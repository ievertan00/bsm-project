# Business Success Metrics (BSM) Analysis Platform

The BSM Analysis Platform is a secure, high-performance web application designed to transform raw Excel data into actionable business insights. It features a modernized backend built with FastAPI and a responsive React frontend, providing comprehensive visualization of business success metrics.

## Key Features

*   **Secure Authentication**: JWT-based login system to protect sensitive business data.
*   **Asynchronous Data Import**: Efficiently process large Excel files in the background using FastAPI `BackgroundTasks` and Pandas.
*   **Normalized Database Schema**: Robust PostgreSQL storage separating static enterprise attributes from periodic financial snapshots.
*   **Interactive Dashboard**: Real-time visualization of key metrics (Cumulative Loans, YTD Growth, In-force counts) using ECharts and Ant Design.
*   **Dynamic Filtering**: Slice data by Year, Month, Bank, and Business Type across all charts and tables.
*   **Data Management**: Full CRUD operations for individual business records and automated company attribute synchronization.

## Tech Stack

### Backend
- **Framework**: [FastAPI](https://fastapi.tiangolo.com/) (Python 3.12+)
- **ORM**: SQLAlchemy 2.0 with [Alembic](https://alembic.sqlalchemy.org/) for migrations.
- **Database**: PostgreSQL.
- **Dependency Management**: [UV](https://astral.sh/uv/) for lightning-fast environment setup.
- **Security**: JWT Authentication with `python-jose` and `passlib`.

### Frontend
- **Framework**: React 18 (TypeScript).
- **UI Library**: [Ant Design](https://ant.design/).
- **Visualization**: [ECharts](https://echarts.apache.org/) via `echarts-for-react`.
- **API Client**: Axios with automatic JWT interceptors.

## Project Structure

```text
├── backend/
│   ├── app/                # FastAPI application logic
│   │   ├── api/            # REST API routes (Auth, Dashboard, Data)
│   │   ├── models.py       # SQLAlchemy database models
│   │   ├── schemas.py      # Pydantic validation models
│   │   └── importer.py     # Excel processing logic
│   ├── alembic/            # Database migration scripts
│   └── requirements.txt    # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/     # Reusable UI & Chart components
│   │   ├── context/        # Global Auth state management
│   │   └── pages/          # Application views (Login, Dashboard)
│   └── package.json        # Frontend dependencies
└── ReproductionGuide.md    # Detailed step-by-step rebuild instructions
```

## Quick Start

### Prerequisites
- Python 3.12+
- Node.js (LTS)
- PostgreSQL

### 1. Backend Setup
```bash
cd backend
uv venv
# Activate venv: .venv\Scripts\activate (Windows) or source .venv/bin/activate (Unix)
uv pip install -r requirements.txt
# Configure .env with DATABASE_URL and SECRET_KEY
alembic upgrade head
uv run uvicorn app.main:app --reload
```

### 2. Frontend Setup
```bash
cd frontend
npm install
npm start
```

For a comprehensive guide on how to reproduce this project from scratch, please refer to the [Reproduction Guide](ReproductionGuide.md).

## License
MIT

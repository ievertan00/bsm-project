# Tech Stack & Database Schema Update Plan

## Overview
This plan outlines the systematic migration from a SQLite/Vanilla JS demo setup to a production-ready architecture using PostgreSQL, a modern UI framework (React/Vue), and JWT-based authentication. It also incorporates the normalized database schema as defined in `NEW_DATABASE_SCHEMA_DETAIL.md`.

## Scope Definition (CRITICAL)

### In Scope
- Migration from SQLite to PostgreSQL.
- Implementation of JWT/OAuth2 Authentication.
- Transition from Vanilla JS to a modern frontend framework (React or Vue).
- Database schema normalization (Company 1:N BusinessData).
- Updating backend logic in `services.py` to support the new schema and high-performance queries.

### Out of Scope
- Direct banking API integrations (maintaining Excel ETL).
- Complex RBAC (Role-Based Access Control) beyond basic secure login.
- Migrating historical data from the current `business_data.db` (assuming a clean start).

## Implementation Phases

### Phase 1: Database & Backend Core
- **Goal**: Establish the new PostgreSQL foundation and secure API layer.
- **Steps**:
  1. [ ] Update `database.py` to use a PostgreSQL connection string and configure connection pooling.
  2. [ ] Modify `models.py` to match the normalized schema in `NEW_DATABASE_SCHEMA_DETAIL.md`.
  3. [ ] Implement JWT token generation and verification logic in `auth.py`.
  4. [ ] Update `main.py` dependencies to use `JWTBearer` instead of `HTTPBasic`.
  5. [ ] Refactor `services.py` to use SQLAlchemy JOINs for statistics, leveraging the new `Company` and `BusinessData` split.
- **Verification**:
  - Run `pytest` on core ETL and statistics functions.
  - Verify PostgreSQL connectivity and table creation via `init_db.py`.
  - Manual verification of JWT login and protected endpoint access.

### Phase 2: Modern Frontend Migration
- **Goal**: Rebuild the UI for better performance and a modern look.
- **Steps**:
  1. [ ] Initialize a new React or Vue project in a `frontend/` directory.
  2. [ ] Implement a secure Login page utilizing the new JWT backend.
  3. [ ] Create a Dashboard component with data visualization (using Recharts or similar) for the statistics returned by `/statistics/`.
  4. [ ] Build a robust Excel Upload component with real-time progress and error handling.
  5. [ ] Implement a Company Management view to see and edit normalized company tags (Industry, Tech level).
- **Verification**:
  - Frontend unit tests for key components.
  - End-to-end (E2E) testing of the "Upload -> Sync -> View Stats" flow.
  - Audit UI responsiveness and latency.

### Phase 3: Deployment & Optimization
- **Goal**: Ensure the system is robust and ready for production-like use.
- **Steps**:
  1. [ ] Update `nginx.conf` to serve the new modern frontend build.
  2. [ ] Optimize PostgreSQL indices on `company_name`, `snapshot_year`, and `snapshot_month`.
  3. [ ] Final security audit of the JWT implementation.
- **Verification**:
  - Load testing of the statistics endpoint with 10k+ records.
  - Successful deployment in the target environment.

## Potential Risks & Mitigations
- **Risk**: Increased frontend complexity (Build tools, state management). -> **Mitigation**: Use a well-documented framework like Vite/React and keep state management simple (React Context or simple Props).
- **Risk**: PostgreSQL connection overhead. -> **Mitigation**: Implement a connection pooler (SQLAlchemy `QueuePool`) from the start.

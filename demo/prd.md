# Normalized Business Data Import & Analysis System PRD

## HR Eng

| Normalized Business Data System PRD |  | A system designed for managing periodic business data snapshots for technology and industrial enterprises, specifically for the "Guaranty/Surety" (智融担保) sector, enabling multi-source Excel ETL and automated statistics generation. |
| :---- | :---- | :---- |
| **Author**: Pickle Rick **Contributors**: Engineering Team **Intended audience**: Engineering, PM, Design | **Status**: Draft **Created**: 2026-03-23 | **Self Link**: [Link] **Context**: [Link] 

## Introduction

The Normalized Business Data Import & Analysis System is a FastAPI-based backend application with a web frontend dashboard. It serves as a centralized hub for importing, normalizing, and analyzing business performance data provided via various bank and offline Excel report formats. 

## Problem Statement

**Current Process:** Business data is provided periodically (monthly/yearly) in disparate Excel formats from various sources (WeBank, ICBC, CCB, Offline). This requires manual consolidation and analysis to track "Guarantee Balance" and "Unique Company Counts."
**Primary Users:** Data Analysts, Business Managers, and Operations teams in the Guaranty/Surety sector.
**Pain Points:** The manual process of mapping columns, merging data across different schemas, and generating cross-year statistics is laborious, prone to human error, and lacks a centralized source of truth.
**Importance:** Automating this process reduces operational costs, ensures data integrity, and provides timely insights for business decision-making.

## Objective & Scope

**Objective:** Automate the ETL process for multi-format Excel business data and provide a centralized, normalized database for automated cross-year statistics generation.
**Ideal Outcome:** Users can seamlessly upload Excel reports, and the system automatically normalizes the data, enriches it with master industry information, and generates real-time statistical reports.

### In-scope or Goals
- Multi-Source Excel ETL (WeBank, ICBC, CCB, Offline schemas).
- Automated column normalization and mapping.
- Low-latency database storage using PostgreSQL/SQLAlchemy (Company 1:N BusinessData).
- Automated cross-year statistics generation (Guarantee Balance, Company Counts).
- Data enrichment via QCC master data synchronization.
- Robust Authentication using JWT (JSON Web Tokens) or OAuth2.
- Modern frontend UI/UX built with React or Vue.

### Not-in-scope or Non-Goals
- Real-time data streaming.
- Complex user role management (RBAC).
- Direct integration with banking APIs (relies on Excel exports).

## Technical Architecture & Normalized Data Schema

The system uses a relational database (PostgreSQL) managed via SQLAlchemy ORM for high performance and low-latency access. The schema separates static enterprise attributes from periodic financial performance data to eliminate redundancy and ensure data consistency.

### 1. `Company` Table (Entity Master)
This table is the single source of truth for an enterprise's identity and policy-related status.

| Column | Type | Constraint | Description |
| :--- | :--- | :--- | :--- |
| **`id`** | Integer | **Primary Key** | Unique internal identifier. |
| **`company_name`** | String | **Unique, Indexed** | Official enterprise name (used for matching). |
| `enterprise_size` | String | | e.g., Small, Medium, Large. |
| `establishment_date` | Date | | The date the company was founded. |
| `enterprise_institution_type` | String | | e.g., Limited Liability Company. |
| `national_standard_industry_main` | String | | Official industry classification (Main). |
| `national_standard_industry_major` | String | | Official industry classification (Major). |
| `qcc_industry_main` | String | | Industry categories from QiChaCha (Main). |
| `qcc_industry_major` | String | | Industry categories from QiChaCha (Major). |
| `is_high_tech_enterprise` | Boolean | | Flag for High-Tech status. |
| `is_little_giant_enterprise` | Boolean | | Flag for Little Giant status. |
| `is_innovative_sme` | Boolean | | Flag for Innovative SME status. |
| `is_tech_based_sme` | Boolean | | Flag for Tech-based SME status. |
| `is_technology_enterprise` | Boolean | | Flag for Technology Enterprise status. |
| `is_qyjh_enterprise` | Boolean | | Flag for "Thousand Billion Plan" status. |
| `created_at` | DateTime | | Audit timestamp for record creation. |

### 2. `BusinessData` Table (Periodic Transactional Data)
This table stores the financial "snapshot" of a company's relationship with the bank at a specific point in time.

| Column | Type | Constraint | Description |
| :--- | :--- | :--- | :--- |
| **`id`** | Integer | **Primary Key** | Unique internal identifier. |
| **`company_id`** | Integer | **Foreign Key** | References `Company(id)`. |
| **`snapshot_year`** | Integer | | Year of the snapshot (e.g., 2026). |
| **`snapshot_month`** | Integer | | Month of the snapshot (1-12). |
| `loan_amount` | Numeric | | Total principal borrowed (10k CNY). |
| `guarantee_amount` | Numeric | | Total amount guaranteed (10k CNY). |
| `outstanding_loan_balance` | Numeric | | Current remaining loan amount. |
| `outstanding_guarantee_balance`| Numeric | | Current remaining guarantee risk. |
| `loan_interest_rate` | Numeric | | Annual interest rate (%). |
| `guarantee_fee_rate` | Numeric | | Annual guarantee fee rate (%). |
| `loan_status` | String | | e.g., "Normal", "Settled", "Overdue". |
| `cooperative_bank` | String | | The bank partner (e.g., CCB, WeBank). |
| `business_type` | String | | e.g., "Batch Loan", "Offline Project". |
| `loan_start_date` | Date | | Start date of the loan. |
| `loan_due_date` | Date | | Contractual due date. |
| `settlement_date` | Date | | Actual settlement date. |
| `business_year` | Integer | | The year of the business entry. |
| `enterprise_classification` | String | | Classification in bank reporting. |
| `created_at` | DateTime | | Audit timestamp for record creation. |

### 3. Key Relationships & Architectural Benefits
- **Relational Mapping:** One `Company` record can have many `BusinessData` records (historical monthly snapshots).
- **Referential Integrity:** `BusinessData.company_id` ensures financial records always link back to a valid enterprise entity.
- **Analytical Power:** Complex reports are generated via SQL **JOINs**. This allows filtering by any company attribute (like `is_high_tech_enterprise`) while calculating financial totals from the snapshot data.
- **Normalization Advantages:** Reduced redundancy, simplified maintenance, and guaranteed data consistency across monthly imports.

## Business Data Statistics Logic (`get_statistics`)

The system calculates core financial and operational reports using specialized aggregation logic within the `services.py` layer.

### 1. Data Filtering & Pre-processing
- **Exclusion of Non-disbursed Loans:** Records with `loan_status == "未放款"` are excluded.
- **Precision Handling:** All financial columns use `Decimal` for high-precision arithmetic.
- **Snapshot Selection:** Uses specific month/year for current reports and year-end (December) snapshots for historical tracking.

### 2. Calculation Metrics (Summary Table Columns)

| Metric | Business Definition | Logic |
| :--- | :--- | :--- |
| **新增借款金额** | New loans issued in the target year. | `sum(loan_amount)` where `business_year == target_year`. |
| **新增担保金额** | New guarantees issued in the target year. | `sum(guarantee_amount)` where `business_year == target_year`. |
| **新增担保企业数** | Unique companies receiving new guarantees this year. | `nunique(company_name)` where `business_year == target_year` AND `guarantee_amount > 0`. |
| **累计担保企业数** | Total unique companies served since inception. | `nunique(company_name)` where `guarantee_amount > 0` in current snapshot. |
| **在保企业** | Companies with active risk exposure. | `nunique(company_name)` where `outstanding_guarantee_balance > 0`. |
| **借款余额** | Current total loan principal outstanding. | `sum(outstanding_loan_balance)` in current snapshot. |
| **担保余额** | Current total guarantee risk exposure. | `sum(outstanding_guarantee_balance)` in current snapshot. |

### 3. Aggregation Logic
- **"合计" (Total Row):** Simple sum of values and unique counts from individual business types.
- **"合并去重数" (Merged Unique Count Row):** Global unique count of companies across all business types to identify the true number of unique clients.

## Product Requirements

The system must handle the end-to-end flow of uploading Excel reports, normalizing the data, and providing aggregated statistics.

### Critical User Journeys (CUJs)
1. **Data Import & Normalization**: A Data Analyst logs into the system, uploads a monthly Excel report (e.g., WeBank format), selects the schema type and snapshot date. The system parses the file, normalizes columns (e.g., mapping '客户名称' to 'company_name'), creates new company records if necessary, and saves the business data snapshot.
2. **Statistics Review**: A Business Manager logs into the dashboard, selects a snapshot year and month. The system queries the database, aggregates data (e.g., total guarantee balance), and displays the cross-year trends and summary statistics.

### Functional Requirements

| Priority | Requirement | User Story |
| :---- | :---- | :---- |
| P0 | Multi-Schema Excel Import | As a Data Analyst, I want to upload Excel files with different schemas so the system can normalize them automatically. |
| P0 | Data Normalization | As a system, I need to map varying column names to a standard schema to ensure data consistency. |
| P0 | Snapshot Management | As a Data Analyst, I want to associate uploaded data with a specific year and month to track historical performance. |
| P1 | Automated Statistics | As a Business Manager, I want to view aggregated statistics (e.g., total loan amount, guarantee balance) for specific periods. |
| P1 | QCC Data Synchronization | As a Data Analyst, I want to enrich business data with master industry tags to categorize companies correctly. |
| P2 | Data Status Export | As a Data Analyst, I want to export the processed and normalized data back to Excel for offline use or auditing. |

## Assumptions

- Excel report formats from banks remain relatively stable. Minor changes can be handled via schema mapping updates.
- The database infrastructure supports PostgreSQL for low-latency queries and higher concurrency.
- A secure authentication service (JWT/OAuth2) is necessary for the current operational environment.

## Risks & Mitigations

- **Risk**: Excel file structures change significantly, causing import failures. -> **Mitigation**: Implement robust error handling and descriptive error messages to guide users. Design the schema mapping logic to be easily configurable.
- **Risk**: Database locking issues during bulk imports. -> **Mitigation**: Ensure proper transaction management (`db.commit()`, `db.rollback()`) and consider using an external database (e.g., PostgreSQL) if concurrency becomes an issue.

## Tradeoff

- **PostgreSQL vs. SQLite**: Migrating to PostgreSQL to prioritize low-latency query performance, robust concurrency, and enterprise-grade scalability, moving away from the initial SQLite demo setup.
- **Modern UI vs. Vanilla JS**: Choosing a modern framework (React/Vue) increases the initial build complexity but delivers a vastly superior, responsive UI/UX.

## Business Benefits/Impact/Metrics

**Success Metrics:**

| Metric | Current State (Benchmark) | Future State (Target) | Savings/Impacts |
| :---- | :---- | :---- | :---- |
| *Time to Consolidate Monthly Data* | Several days (Manual) | Minutes (Automated) | Significant reduction in manual labor |
| *Data Accuracy* | Prone to human error | High consistency | Improved trust in reports |
| *Time to Generate Cross-Year Stats* | Hours (Manual) | Seconds (Automated) | Faster business insights |

## Stakeholders / Owners

| Name | Team/Org | Role | Note |
| :---- | :---- | :---- | :---- |
| Engineering Team | Engineering | Implementers | Responsible for system development and maintenance |
| Data Analysts | Operations | Primary Users | Responsible for uploading and verifying data |
| Business Managers | Management | Stakeholders | Rely on the generated statistics for decision-making |

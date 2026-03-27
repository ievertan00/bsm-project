# Normalized Database Schema Design

This document details the redesigned, normalized database schema for the Business Data Management System. The schema separates static enterprise attributes from periodic financial performance data to eliminate redundancy.

## 1. `Company` Table (Entity Master)
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

---

## 2. `BusinessData` Table (Periodic Transactional Data)
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

---

## 3. Key Relationships & Architectural Benefits

### Relational Mapping
- **One-to-Many:** One `Company` record can have many `BusinessData` records (historical monthly snapshots).
- **Referential Integrity:** `BusinessData.company_id` ensures financial records always link back to a valid enterprise entity.

### Analytical Power
Complex reports are generated via SQL **JOINs**. This allows filtering by any company attribute (like `is_high_tech_enterprise`) while calculating financial totals from the snapshot data.

### Advantages of Normalization
1. **Reduced Redundancy:** Static strings (like industry names) are stored once per company, rather than being repeated for every month of history.
2. **Simplified Maintenance:** Updates to a company’s status (e.g., gaining "High-Tech" certification) are made in **one row** in the `Company` table.
3. **Data Consistency:** Eliminates the risk of a company having conflicting industry tags across different monthly Excel imports.

# Business Data Statistics Logic Analysis (`get_statistics`)

This document provides a technical breakdown of the `get_statistics` function located in `services.py`. This logic is responsible for generating the core financial and operational reports for the system.

## 1. Data Filtering & Pre-processing
Before any calculations occur, the data undergoes strict filtering:
- **Exclusion of Non-disbursed Loans:** Any record where `loan_status` is "未放款" is excluded.
- **Precision Handling:** All financial columns (`loan_amount`, `guarantee_amount`, `outstanding_loan_balance`, `outstanding_guarantee_balance`) are converted to `Decimal` objects to prevent floating-point rounding errors in large-sum aggregations.
- **Snapshot Selection:** 
    - For the **Current Period**, the logic uses the user-specified `snapshot_year` and `snapshot_month`.
    - For **Historical Years**, the logic attempts to use the **December (12)** snapshot of that year. If December is unavailable, it falls back to the latest available month for that specific year.

## 2. Calculation Metrics (Summary Table Columns)
The logic calculates seven key metrics for each business type (`常规业务`, `建行批量业务`, `微众批量业务`, `工行批量业务`):

| Metric | Business Definition | Logic |
| :--- | :--- | :--- |
| **新增借款金额** | New loans issued in the target year. | `sum(loan_amount)` where `business_year == target_year`. |
| **新增担保金额** | New guarantees issued in the target year. | `sum(guarantee_amount)` where `business_year == target_year`. |
| **新增担保企业数** | Unique companies receiving new guarantees this year. | `nunique(company_name)` where `business_year == target_year` AND `guarantee_amount > 0`. |
| **累计担保企业数** | Total unique companies served since inception. | `nunique(company_name)` where `guarantee_amount > 0` in the current snapshot. |
| **在保企业** | Companies with active (non-zero) risk exposure. | `nunique(company_name)` where `outstanding_guarantee_balance > 0`. |
| **借款余额** | Current total loan principal outstanding. | `sum(outstanding_loan_balance)` in the current snapshot. |
| **担保余额** | Current total guarantee risk exposure. | `sum(outstanding_guarantee_balance)` in the current snapshot. |

## 3. Row Aggregation Logic
The statistics table provides two different types of totals, serving distinct reporting needs:

### A. "合计" (Total Row)
- **Financial Metrics:** A simple sum of the values from the four business types.
- **Company Counts:** A sum of the unique counts from each type. 
- *Note: If Company A has both a "Regular" loan and a "CCB" loan, it is counted **twice** in this row. This represents the total "contracts" or "bank-specific relationships."*

### B. "合并去重数" (Merged Unique Count Row)
- **Company Counts Only:** Performs a global `nunique(company_name)` across all business types combined.
- *Note: This represents the **true number of unique clients** served by the institution, regardless of how many banks or products they use.*

## 4. Resulting JSON Structure
The API returns a structured object with two main components:

### `overall_summary`
Represents the state of the entire portfolio **as of the current snapshot date**. This provides the "Current Portfolio" view.

### `yearly_summaries`
A dictionary keyed by year (e.g., `"2024"`, `"2025"`) providing a historical "Snapshot in Time" for each year. 
- Each entry represents the performance metrics for that specific calendar year.
- It uses the year-end (December) data to represent the final state of that year's business.

## 5. Architectural Implementation
The logic is encapsulated in the `calculate_summary(year_df, full_df)` helper function within `services.py`. This design allows the system to reuse the same aggregation logic for both current monthly reporting and historical yearly performance tracking.

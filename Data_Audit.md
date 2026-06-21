# Phase 1: Data Quality Triage & Issue Log

**Project:** Aegis GBS - Workforce Capacity & Overtime Optimizer  
**Dataset:** Fiscal Year 2023 Corporate Payroll Extract (~550,000 records)  
**Objective:** To perform an initial data audit on the raw HRIS payroll extract prior to pipeline engineering, isolating solvable structural issues from unsolvable anomalies.

### Executive Summary
Initial exploratory data analysis (EDA) using Python (Pandas) revealed legacy system data fragmentation. Notable issues include naming variations for core departments, string-formatted financial columns, and impossible overtime hours. These findings directed the architecture of the Phase 2 Python Cleaning Pipeline.

---

### Issue Log

| Table | Column | Issue | Row Count | Magnitude | Solvable? | Resolution Plan |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `raw_payroll` | `Agency Name` | **Entity Fragmentation:** Naming inconsistencies and misspellings (e.g., "DEPT OF ED PEDAGOGICAL"). | ~300,000+ | High | Yes | Implement Python regex mapping dictionary to roll fragmented names up into unified Parent Departments. |
| `raw_payroll` | `Title Description` | **Missing Core Dimension:** Null values detected in job role field. | 3 | Low | Yes | Dropped 3 rows. Representing 0.0005% of a 550,000-row dataset, dropping preserves aggregate accuracy without introducing artificial 'Unknown' categories. |
| `raw_payroll` | `Work Location` | **Missing Core Dimension:** Null value detected. | 1 | Low | Yes | Dropped 1 row to prevent artificial categorization. |
| `raw_payroll` | `Names/Payroll Num` | **Missing Identity Data:** Expected system placeholders/contractors. | ~370 | Low | No | **Dropped from final pipeline.** Specific employee identities (PII) are not required for high-level capacity metrics, reducing model size and mitigating privacy risk. |
| `raw_payroll` | `Mid Init` | **Expected Nulls:** Missing data is a standard data entry convention. | ~230,993 | Low | Yes | Impute with empty string `""` to prevent text-concatenation errors. |
| `raw_payroll` | `Mid Init` | **Invalid Type:** Contains numbers (e.g., `41`) or special characters. | 41 | Low | Yes | Verified numeric values were not mis-mapped Employee IDs via cross-referencing, then cleared them as invalid text entries using Regex (`^[a-zA-Z]$`). |
| `raw_payroll` | `Agency Start Date` | **Formatting Inconsistency:** Mixed string and numeric data types. | 550,000 | High | Yes | Force standardization via Pandas `to_datetime(errors='coerce')` to establish a uniform ISO format. |
| `raw_payroll` | `Financial Cols` | **Invalid Type:** Loaded as string due to hidden commas and dollar signs causing `NaN` coercion. | 550,000 | High | Yes | Add pipeline step to strip `$` and `,` via Regex before casting to float. |
| `raw_payroll` | `Hours/OT Hours` | **Business Logic Anomaly:** Negative values present indicating retroactive adjustments. | [Various] | Medium | Yes | Quarantine or filter out `< 0` values when calculating baseline utilization averages. |
| `raw_payroll` | `OT Hours` | **Critical Outliers:** Impossible values equating to sustained 100+ hour workweeks. | Top 10+ | Critical | No | Applied a logical hard cap of 3,120 OT hours per year (representing a sustained 60-hour work week). Outliers above this threshold were quarantined as system errors to prevent skewing averages. |

<br>

# Phase 2: Strategic SQL EDA & Business Insights

**Project:** Aegis GBS - Workforce Capacity & Overtime Optimizer  
**Dataset:** Cleaned `payroll_fact` table (SQL Data Warehouse)  
**Objective:** To execute business-focused EDA using SQL, testing competing stakeholder hypotheses (seasonal volume spikes vs. structural understaffing).

### Requirements Gathering
* **Stakeholder Goals:** Evaluate the HR Director's seasonal spike theory against the COO's structural understaffing theory to guide headcount strategy.
* **Columns & Coverage:** Isolate `Department_Clean` and `Title Description` against the core financial metrics (`OT Hours` and `Total OT Paid`).

---

### Insights Log

| SQL Query Focus | Metric & Dimension | The Finding | Relevant Stakeholder | Domain Context (Why it matters) |
| :--- | :--- | :--- | :--- | :--- |
| **Aggregates** (Dept Overtime) | Sum of `Total OT Paid` by `Department_Clean` | The **Department of Correction** is an anomaly. With the 6th lowest headcount among top spenders, they rank 3rd in total OT spend ($294M+). | COO / CFO | This points toward localized structural understaffing, though we would need to validate this against shift scheduling data (which we currently lack) to rule out other operational bottlenecks. |
| **Notable Segments** (Role Overtime) | `Avg_OT_Per_Employee` by `Title Description` | **Severe understaffing in skilled facilities roles.** Senior Stationary Engineers average 1,180+ OT hours/year (approx 65-hr workweeks). | HR Director / COO | Identifies the exact roles needing headcount increases. A 1,180+ annual OT hour volume cannot mathematically fit into a short 'busy season', confirming chronic understaffing. *Note: Initial SQL aggregation returned 1,300+ hours for this cohort. After applying the 3,120-hour hard cap consistently across the Power BI semantic layer, the figure normalized to 1,180+ hours. The Power BI figure is used as the canonical metric throughout this project.* |
| **Financial Modeling** (Cost Neutrality) | `Wasted_OT_Spend` vs `True_Annual_Salary` | **The OT premium outpaces base salaries.** Normalizing daily union rates into annual salaries reveals $4.4M in pure OT premium penalties for Stationary Engineers alone. | CFO / COO | Proves that Aegis GBS can fund 15 new full-time Stationary Engineers entirely by reallocating the wasted OT penalty. This allows for team right-sizing with zero net-new budget requests. |
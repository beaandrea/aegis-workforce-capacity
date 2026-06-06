# Phase 1: Data Quality Triage & Issue Log

**Project:** Aegis GBS - Workforce Capacity & Overtime Optimizer  
**Dataset:** Fiscal Year 2023 Corporate Payroll Extract (~550,000 records)  
**Objective:** To perform an initial data audit on the raw HRIS payroll extract prior to pipeline engineering, isolating solvable structural issues from unsolvable business logic anomalies.

### Executive Summary
Initial exploratory data analysis (EDA) using Python (Pandas) revealed significant data integrity issues typical of legacy HRIS exports. Key findings include severe entity fragmentation across core departments (e.g., 7+ variations of the Department of Education), inconsistent data typing rendering financial columns as strings, and critical business logic violations, including impossible overtime hours (100+ hour workweeks). 

These issues have been logged below and will dictate the architecture of the Phase 2 Python Cleaning Pipeline.

---

### Issue Log

| Table | Column | Issue | Row Count | Magnitude | Solvable? | Resolution Plan |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `raw_payroll` | `Agency Name` | **Entity Fragmentation:** Severe naming inconsistencies and misspellings (e.g., "DEPT OF ED PEDAGOGICAL", "DOE CUSTODIAL PAYROL"). | ~300,000+ | High | Yes | Implement Python regex mapping dictionary to roll fragmented names up into unified "Parent Departments". |
| `raw_payroll` | `Title Description` | **Missing Core Dimension:** Null values detected in critical job role field. | 3 | Low | Yes | Impute as `"Unknown"`. Dropping is unnecessary. |
| `raw_payroll` | `Work Location` | **Missing Core Dimension:** Null value detected. | 1 | Low | Yes | Impute as `"Unknown"`. |
| `raw_payroll` | `Names/Payroll Num` | **Missing Identity Data:** Expected system placeholders/contractors. | ~370 | Low | No | Flag for potential PII drop in Phase 2; specific employee identities are not required for high-level capacity metrics. |
| `raw_payroll` | `Mid Init` | **Expected Nulls:** Missing data is biologically standard. | ~230,993 | Low | Yes | Impute with empty string `""` to prevent text-concatenation errors. |
| `raw_payroll` | `Mid Init` | **Invalid Type:** Contains numbers (e.g., `41`) or special characters instead of A-Z letters. | 41 | Low | Yes | Apply Regex filter (`^[a-zA-Z]$`) to isolate and clear invalid entries. |
| `raw_payroll` | `Agency Start Date` | **Severe Formatting Inconsistency:** Mixed string and numeric data types (e.g., `04/11/2016` vs. `222263`). | 550,000 | High | Yes | Force standardization via Pandas `to_datetime(errors='coerce')` to establish a uniform ISO format. |
| `raw_payroll` | `Financial Cols` *(All)* | **Invalid Type:** Loaded as `object` (string) due to hidden commas (`,`) and dollar signs (`$`) causing `NaN` coercion. | 550,000 | High | Yes | Add pipeline step to strip `$` and `,` via Regex before casting to float using `pd.to_numeric()`. |
| `raw_payroll` | `Hours/OT Hours` | **Business Logic Anomaly:** Negative values present indicating retroactive HR payroll adjustments. | [Various] | Medium | Yes | Quarantine or filter out `< 0` values when calculating baseline utilization averages. |
| `raw_payroll` | `OT Hours` | **Critical Outliers:** Impossible values (Max > 3,172 hrs), equating to sustained 100+ hour workweeks. | Top 10+ | Critical | No | Flag as extreme outliers for operations review; implement logical cap in Python pipeline to prevent skewed departmental averages. |

<br>

# Phase 3: Strategic SQL EDA & Business Insights

**Project:** Aegis GBS - Workforce Capacity & Overtime Optimizer  
**Dataset:** Cleaned `payroll_fact` table (SQL Data Warehouse)  
**Objective:** To execute business-focused exploratory data analysis (EDA) using SQL, testing the competing stakeholder hypotheses (seasonal volume spikes vs. structural understaffing).

### Requirements Gathering
Before writing SQL aggregations, the domain context and North Star metrics were established to guide the analysis:
* **Stakeholder Goals:** Resolve the executive gridlock. The HR Director suspects company-wide seasonal spikes; the COO suspects localized structural understaffing. The goal is to determine which theory the data supports to guide future hiring strategies.
* **Columns & Coverage:** Analysis leverages the fully standardized Phase 2 output, specifically isolating `Department_Clean` and `Title Description` against the core financial metrics (`OT Hours` and `Total OT Paid`).

---

### Insights Log

| SQL Query Focus | Metric & Dimension | The Finding | Relevant Stakeholder | Domain Context (Why it matters) |
| :--- | :--- | :--- | :--- | :--- |
| **Aggregates** (Dept Overtime) | Sum of `Total OT Paid` by `Department_Clean` | The **Department of Correction** is the primary anomaly. Despite having the 6th lowest headcount of the top spenders, they rank 3rd in total OT spend ($294M+). | COO / CFO | Proves that Aegis GBS's overtime bleed is not strictly proportional to department size, indicating localized structural understaffing rather than company-wide seasonal spikes. |
| **Notable Segments** (Role Overtime) | `Avg_OT_Per_Employee` by `Title Description` | **Severe understaffing in skilled facilities roles.** While Correction Officers drive total spend, roles like Senior Stationary Engineer average 1,300+ OT hours/year (65-hr workweeks), identifying the exact roles needing urgent headcount increases. | HR Director / COO | Shifts the hiring strategy from generic headcount to highly targeted skilled-labor acquisition. Furthermore, the mathematical impossibility of cramming 1,300+ OT hours into a short 'busy season' definitively disproves the HR Director's seasonality theory, confirming chronic year-round understaffing. |

### Strategic Recommendations (Insight Categorization)

To ensure these data findings translate into tangible business value, the insights have been categorized based on the levers the executive team can actually pull. 

| Category | The Finding | The Business Lever | Recommendation |
| :--- | :--- | :--- | :--- |
| **Contextual** | **Police & Fire dominate total OT spend.** Their massive size naturally drives high overall costs. | *Low Control.* Emergency response volume is dictated by city needs, not internal HR policy. | **No immediate action.** Exclude from emergency headcount restructuring; maintain current baseline budget. |
| **Directional** | **Correction Dept. OT ratio is anomalous.** They spend $100M+ more on overtime than departments with significantly higher headcounts. | *Medium Control.* Highlights a broken operational model, prompting a shift from "seasonal" to "structural" thinking. | **Investigate localized workflows.** Shift executive focus away from generic company-wide cuts and zero in on Correction Dept. resource allocation. |
| **Actionable** *(Short-Term)* | **Skilled facilities roles are severely burning out.** Senior Stationary Engineers are averaging 1,300+ OT hours annually (65-hour workweeks). | *High Control.* The HR Director controls job requisitions and targeted hiring campaigns. | **Open job requisitions immediately.** Draft and post hiring targets for 5-10 Senior Stationary Engineers and Plumbers to alleviate extreme individual burnout. |
| **Actionable** *(Strategic)* | **Overtime premium > Base Salary for trades.** Aegis GBS is paying massive time-and-a-half premiums for year-round work. | *High Control.* The CFO and COO control budget allocation between OT pools and Base Headcount. | **Restructure the budget.** Redirect funds from the bleeding Overtime pool to fund competitive Base Salaries for full-time facilities staff. |

> 💡 **Financial Modeling & Cost Neutrality:** Engineered a SQL cost-benefit simulation normalizing legacy union daily rates into true annual salaries. The model proved that Aegis GBS could fund **15 net-new full-time Stationary Engineers** and **20 net-new Electricians** strictly by reallocating the $4.4M currently burned on their overtime premiums, achieving right-sizing with zero net-new budget requests.
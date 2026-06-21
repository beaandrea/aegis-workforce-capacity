# Aegis GBS: Workforce Capacity & Overtime Optimizer

![Dashboard Screenshot](dashboard.png)
*Annual overtime volume for stationary engineers exceeds mathematically possible seasonal limits, indicating chronic understaffing.*

👉 📄 **[View Data Quality & SQL Insights Audit](Data_Audit.md)**

## 1. Executive Summary
Aegis GBS was losing $2.53 billion annually to overtime costs, sparking an executive debate between HR and the COO regarding workforce capacity. I analyzed 550,000 legacy HRIS records using Python and SQL to identify the root cause of this structural waste. I delivered an executive Power BI dashboard that pinpointed the exact cohorts causing the bleed and provided a mathematically backed, cost-neutral restructuring plan.

## 2. The Business Questions
* Are we overspending because of brief, unexpected seasonal volume spikes, or do we have chronic, structural understaffing in specific operational teams that we are masking with premium overtime pay?
* And if it is structural understaffing — which specific roles, departments, or shifts are carrying disproportionate load, and what would right-sizing actually cost versus what the current overtime premium is costing?
* **Can we achieve this right-sizing without requesting additional net-new budget from Finance?**

**Stakeholder Context:** The HR Director believes the issue is seasonal volume spikes and is resistant to headcount discussions. The COO suspects structural understaffing but lacks the data to make the case. Finance refuses to approve new budget without proof of ROI.

## 3. Data Architecture
I extracted over 550,000 raw payroll records and engineered a cleaning pipeline using Python (Pandas) to resolve heavy entity fragmentation. The data flow was modeled as follows: `raw_payroll` → `cleaning pipeline` → `payroll_fact` (grain: one row per employee-year). This fact table was housed in a SQL (SQLite) relational database before being connected to Power BI to form the semantic layer for executive reporting. 

## 4. Insights Deep-Dive
The data entirely invalidated the HR Director's "seasonal spike" hypothesis. The Department of Correction emerged as a massive anomaly, spending $294M+ on overtime despite having a lower headcount than other top-spending departments. A role-specific deep dive revealed that Senior Stationary Engineers were averaging 1,180+ annual overtime hours—a mathematically impossible volume for a short busy season, equating to sustained 65+ hour workweeks. Furthermore, the financial model proved that the OT premium paid to these engineers ($4.4M) far outpaced their base salaries, presenting a clear bottleneck and a massive opportunity for cost-neutral restructuring.

## 5. Operational Recommendations

| Category | The Finding | Recommendation |
| :--- | :--- | :--- |
| **Directional** | **The Correction Dept. OT ratio is anomalous.** They spend $100M+ more on overtime than departments with significantly higher headcounts. | **Investigate localized workflows.** Stop looking for company-wide cuts. The COO needs to audit resource allocation specifically within the Correction Dept. |
| **Actionable (Short-Term)** | **Skilled facilities roles are severely burning out.** Senior Stationary Engineers are averaging 1,180+ OT hours annually. | **Open job requisitions immediately.** Draft and post hiring targets for 5-10 Senior Stationary Engineers to alleviate individual burnout. |
| **Actionable (Strategic)** | **The Cost-Benefit Math.** Aegis GBS can fund 15 new Stationary Engineers entirely by reallocating the $4.4M wasted on their OT premiums. | **Restructure the budget.** Shift funds from the overtime budget to base salaries. This right-sizes the facilities team without requiring an additional budget request from Finance. |

---
**Tech Stack:** Python (Pandas), SQL (SQLite), Power BI, DAX
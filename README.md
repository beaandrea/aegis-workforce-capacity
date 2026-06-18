# Aegis GBS: Workforce Capacity & Overtime Optimizer

![Dashboard Screenshot](dashboard.png)
*Annual overtime volume for stationary engineers exceeds mathematically possible seasonal limits, indicating chronic understaffing.*

## Executive Summary
Aegis GBS was losing $2.53 billion annually to overtime costs, sparking an executive debate between HR and the COO regarding workforce capacity. I analyzed 550,000 legacy HRIS records using Python and SQL to identify the root cause of this structural waste. I delivered an executive Power BI dashboard that pinpointed the exact cohorts causing the bleed and provided a mathematically backed, cost-neutral restructuring plan.

## The Business Scenario
**Company:** Aegis Global Business Services (Aegis GBS)  
**Role:** Operational Data Analyst  
**Target Audience:** Chief Operating Officer (COO) & HR Director  

Aegis GBS is a multinational shared services center burning **$2.53 billion** in annual overtime costs with no corresponding increase in operational throughput. The executive team is gridlocked: The HR Director believes the issue is caused by brief seasonal volume spikes, while the COO suspects chronic understaffing masked by premium overtime pay. 

This project analyzes a 550,000-row HRIS extract to test these hypotheses, identify exactly which departments are burning out, and build a financial model to prove the ROI of hiring full-time staff rather than paying overtime penalties.es.

---

## Data Source & Methodology
*Note: To replicate real-world enterprise scale, data fragmentation, and administrative messiness, this project utilizes a public city-wide payroll dataset, modified to simulate Aegis GBS's legacy HRIS conditions.*

**Tech Stack:** 
* **Python (Pandas):** Data quality triage, regex string cleaning, and automated pipeline engineering.
* **SQL (SQLite):** Relational data warehousing and financial cost-benefit modeling.
* **Power BI:** Executive dashboarding and DAX measure creation.

📄 **[View the complete Data Quality & SQL Insights Audit Here](Data_Audit.md)**

---

## Technical Highlights

### 1. Python: Handling Legacy System Fragmentation
The raw data contained massive entity fragmentation (e.g., 7+ variations of the Department of Education). A regex mapping dictionary was deployed to roll these up into unified dimensions.

```python
# Standardizing fragmented agency names using Regex mapping
agency_mapping = {
    r'.*POLICE.*': 'Police Department',
    r'.*FIRE.*': 'Fire Department',
    r'.*CORRECTION.*': 'Department Of Correction',
    r'.*EDUCATION.*|.*ED PEDAGOGICAL.*': 'Department Of Education'
}

for pattern, clean_name in agency_mapping.items():
    raw_df.loc[raw_df['Agency Name'].str.contains(pattern, case=False, na=False), 'Agency Name_Clean'] = clean_name
```

### 2. SQL: The Cost-Neutral Hiring Model
To prove the structural understaffing hypothesis, a cost-benefit simulation was engineered. Legacy union daily pay rates (<$1,000) were dynamically normalized into true annual salaries to calculate exactly how many Full-Time Equivalents (FTEs) could be hired using wasted overtime cash.

```sql
SELECT 
    "Title Description" AS Job_Role,
    COUNT(*) AS Current_Headcount,
    SUM("Total OT Paid") AS Wasted_OT_Spend,
    
    -- Normalize the salary: If it's a daily rate (<$1000), multiply by 260 working days
    AVG(CASE WHEN "Base Salary" < 1000 THEN "Base Salary" * 260 ELSE "Base Salary" END) AS True_Annual_Salary,
    
    -- Calculate FTEs using the normalized annual salary
    (SUM("Total OT Paid") / AVG(CASE WHEN "Base Salary" < 1000 THEN "Base Salary" * 260 ELSE "Base Salary" END)) AS FTEs_We_Could_Hire
    
FROM payroll_fact
WHERE Department_Clean = 'Department Of Correction' AND "OT Hours" > 0 AND "Base Salary" > 0
GROUP BY "Title Description"
ORDER BY Wasted_OT_Spend DESC
LIMIT 5;
```

---

## Strategic Recommendations

| Category | The Finding | Recommendation |
| :--- | :--- | :--- |
| **Directional** | **The Correction Dept. OT ratio is anomalous.** They spend $100M+ more on overtime than departments with significantly higher headcounts. | **Investigate localized workflows.** Stop looking for company-wide cuts. The COO needs to audit resource allocation specifically within the Correction Dept. |
| **Actionable (Short-Term)** | **Skilled facilities roles are severely burning out.** Senior Stationary Engineers are averaging 1,300+ OT hours annually (approx. 65-hour workweeks). | **Open job requisitions immediately.** Draft and post hiring targets for 5-10 Senior Stationary Engineers to alleviate individual burnout. |
| **Actionable (Strategic)** | **The Cost-Benefit Math.** Aegis GBS can fund 15 new Stationary Engineers entirely by reallocating the $4.4M wasted on their OT premiums. | **Restructure the budget.** Shift funds from the bleeding overtime pool to base salaries. This right-sizes the facilities team without requiring an additional budget request from Finance. |
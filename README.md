# Aegis GBS: Workforce Capacity & Overtime Optimizer

![Dashboard Screenshot](dashboard.png)
*Annual overtime volume for stationary engineers exceeds mathematically possible seasonal limits, indicating chronic understaffing.*

## 📖 The Business Scenario
**Company:** Aegis Global Business Services (Aegis GBS)  
**Role:** Operational Data Analyst  

Aegis GBS is a multinational shared services center experiencing unpredictable, massive overtime costs. The company is burning $2.53 billion globally, but operational throughput hasn’t increased. The executive team is gridlocked: The HR Director believes the issue is caused by brief, expected seasonal volume spikes, while the COO suspects chronic, structural understaffing masked by premium overtime pay. 

This project analyzes a 550,000+ row HRIS extract to resolve this debate, identifying exactly which departments are burning out and building a cost-benefit financial model to prove the ROI of right-sizing the workforce.

---

## ⚙️ Data Source & Methodology
*Note: To replicate real-world enterprise scale, data fragmentation, and administrative messiness, this project utilizes a public city-wide payroll dataset, modified to simulate Aegis GBS's legacy HRIS conditions.*

**Tech Stack:** * **Python (Pandas):** Data quality triage, regex string cleaning, and automated pipeline engineering.
* **SQL (SQLite):** Relational data warehousing, time-series analysis, and financial cost-benefit modeling.
* **Power BI:** Executive dashboarding and DAX measure creation.

📄 **[View the complete Data Quality & SQL Insights Audit Here](Data_Audit.md)**

---

## 💻 Technical Highlights

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

## 🎯 Strategic Recommendations

| Category | The Finding | Recommendation |
| :--- | :--- | :--- |
| **Directional** | **Correction Dept. OT ratio is anomalous.** They spend $100M+ more on overtime than departments with significantly higher headcounts. | **Investigate localized workflows.** Shift executive focus away from generic company-wide cuts and zero in on Correction Dept. resource allocation. |
| **Actionable (Short-Term)** | **Skilled facilities roles are severely burning out.** Senior Stationary Engineers are averaging 1,300+ OT hours annually (65-hour workweeks). | **Open job requisitions immediately.** Draft and post hiring targets for 5-10 Senior Stationary Engineers to alleviate extreme individual burnout. |
| **Actionable (Strategic)** | **The Cost-Benefit Math.** Aegis GBS could fund 15 net-new Stationary Engineers strictly by reallocating their $4.4M in wasted OT premium. | **Restructure the budget.** Redirect funds from the bleeding Overtime pool to fund competitive Base Salaries, achieving right-sizing with zero net-new budget requests. |
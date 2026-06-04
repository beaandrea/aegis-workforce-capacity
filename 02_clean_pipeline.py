import pandas as pd
import numpy as np
import warnings

# Suppress standard pandas warnings for clean terminal output
warnings.filterwarnings("ignore")

def run_pipeline():
    # Step 1: Ingestion
    print("Loading raw dataset...")
    df = pd.read_csv('raw_aegis_payroll_2023.csv')
    initial_rows = len(df)

    # Step 2: Core Dimension Standardization
    print("Standardizing core dimensions...")

    # Impute missing job titles and locations
    df['Title Description'] = df['Title Description'].fillna('Unknown')
    df['Work Location Borough'] = df['Work Location Borough'].fillna('Unknown')

    # Fix the Middle Initial (Fill nulls, remove non-letters)
    df['Mid Init'] = df['Mid Init'].fillna('')
    df['Mid Init'] = df['Mid Init'].astype(str).str.replace(r'[^a-zA-Z]', '', regex=True)

    # Force Start Date into a strict datetime format
    df['Agency Start Date'] = pd.to_datetime(df['Agency Start Date'], errors='coerce')

    # Step 3: Entity Resolution (Fixing the fragmented departments)
    print("Resolving entity fragmentation...")

    # Define the mapping logic for messy department names
    conditions = [
        df['Agency Name'].str.contains('DEPT OF ED|DEPARTMENT OF EDUCATION|DOE|TEACHER|PEDAGOGICAL', case=False, na=False),
        df['Agency Name'].str.contains('COMMUNITY COLLEGE', case=False, na=False),
        df['Agency Name'].str.contains('DISTRICT ATTORNEY', case=False, na=False),
        df['Agency Name'].str.contains('POLICE', case=False, na=False),
        df['Agency Name'].str.contains('FIRE', case=False, na=False),
        df['Agency Name'].str.contains('HRA/DEPT OF SOCIAL SERVICES|HOMELESS SERVICES', case=False, na=False),
    ]

    choices = [
        'Department of Education',
        'Community College',
        'District Attorney Office',
        'Police Department',
        'Fire Department',
        'Department of Social Services'
    ]

    # Apply the mapping to a new column, default to original name if no match
    df['Agency Name_Clean'] = np.select(conditions, choices, default=df['Agency Name'])

    # Convert ALL CAPS to Title Case for dashboard readability
    df['Agency Name_Clean'] = df['Agency Name_Clean'].str.title()

    # Step 4: Financial Casting and Anomaly Handling
    print("Formatting financials and handling outliers...")

    financial_cols = ['Base Salary','Regular Hours', 'Regular Gross Paid', 'OT Hours', 'Total OT Paid', 'Total Other Pay']

    for col in financial_cols:
        # Strip dollar signs and commas then force to numeric float
        df[col] = df[col].astype(str).str.replace(r'[\$,]', '', regex=True)
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0)

   # Handle negative retroactive adjustments for ALL financial columns
    for col in financial_cols:
        df.loc[df[col] < 0, col] = 0

    # Handle the extreme burnout outliers (Cap max OT at 2080 hours - one full extra work year)
    # This prevets extreme data entry errors from destroying department-wide averages
    df.loc[df['OT Hours'] > 2080, 'OT Hours'] = 2080

    # Step 5: Export
    print("Exporting clean dataset...")
    df = df.drop(columns=['Agency Name'])

    # Save polished data to new file
    output_filename = 'clean_aegis_payroll_2023.csv'
    df.to_csv(output_filename, index=False)

    print("-" * 40)
    print("PIPELINE COMPLETE.")

if __name__ == "__main__":
    run_pipeline()



                    
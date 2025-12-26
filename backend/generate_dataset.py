import pandas as pd
import numpy as np
import random
import os

def generate_dataset(num_records=5000):
    """
    Generates a synthetic dataset for business credit evaluation.
    
    Columns:
    - applicant_id: Unique ID
    - business_type: Manufacturing / Trading / Services
    - years_in_operation: Number of years
    - annual_revenue: Annual revenue (₹)
    - monthly_cashflow: Avg monthly cash flow (₹)
    - loan_amount_requested: Requested loan amount (₹)
    - credit_score: Numeric score (300–900)
    - existing_loans: Number of active loans
    - debt_to_income_ratio: Financial ratio
    - collateral_value: Asset value (₹)
    - repayment_history: Good / Average / Poor
    - default_flag: Target variable (0 = No, 1 = Yes)
    """
    
    # Set seed for reproducibility
    np.random.seed(42)
    random.seed(42)
    
    ids = [f'AUTO_{i:04d}' for i in range(1, num_records + 1)]
    
    # Business Types
    business_types = np.random.choice(['Manufacturing', 'Trading', 'Services'], size=num_records, p=[0.3, 0.4, 0.3])
    
    # Years in Operation (skewed towards younger businesses)
    # Using a gamma distribution to simulate realistic business age
    years_in_opp = np.random.gamma(shape=2, scale=2.5, size=num_records).astype(int)
    years_in_opp = np.clip(years_in_opp, 0, 50)
    
    # Credit Score (Normal distribution centered around 650)
    credit_scores = np.random.normal(loc=650, scale=100, size=num_records).astype(int)
    credit_scores = np.clip(credit_scores, 300, 900)
    
    # Existing Loans (Poisson distribution)
    existing_loans = np.random.poisson(lam=2, size=num_records)
    existing_loans = np.clip(existing_loans, 0, 10)
    
    # Repayment History (Correlated with Credit Score)
    repayment_history = []
    for score in credit_scores:
        if score > 750:
            repayment_history.append(np.random.choice(['Good', 'Average'], p=[0.9, 0.1]))
        elif score > 600:
            repayment_history.append(np.random.choice(['Good', 'Average', 'Poor'], p=[0.5, 0.4, 0.1]))
        else:
            repayment_history.append(np.random.choice(['Average', 'Poor'], p=[0.2, 0.8]))
            
    # Financials (Log-normal distributions for realistic wealth gaps)
    # Annual Revenue: 1 Lakh to 10 Crores
    annual_revenue = np.random.lognormal(mean=14.5, sigma=1.2, size=num_records)
    annual_revenue = np.clip(annual_revenue, 100000, 100000000).astype(int)
    
    # Monthly Cashflow: roughly 5-15% of annual revenue / 12, with variance
    monthly_cashflow = (annual_revenue * np.random.uniform(0.05, 0.15, size=num_records) / 12).astype(int)
    
    # Loan Amount Requested: Correlated with revenue
    loan_amount = (annual_revenue * np.random.uniform(0.1, 0.5, size=num_records)).astype(int)
    loan_amount = np.clip(loan_amount, 50000, 50000000)
    
    # Collateral Value: Based on loan amount and business type
    collateral = []
    for i in range(num_records):
        base_val = loan_amount[i] * np.random.uniform(0.5, 1.5)
        if business_types[i] == 'Services':
            base_val *= 0.5 # Services typically have less tangible collateral
        collateral.append(int(base_val))
    
    # Debt to Income Ratio (DTI)
    # Calculated based on existing loans + new loan impact relative to cashflow
    dti = np.random.normal(loc=0.4, scale=0.15, size=num_records)
    dti = np.clip(dti, 0.1, 5.0)
    
    # Default Flag (The Target Variable)
    # Logic: Lower credit score, higher DTI, poor history, low years in opp -> Higher default probability
    default_flag = []
    
    for i in range(num_records):
        risk_score = 0
        
        # Credit Score Risk
        if credit_scores[i] < 600: risk_score += 40
        elif credit_scores[i] < 700: risk_score += 20
        
        # Repayment History Risk
        if repayment_history[i] == 'Poor': risk_score += 30
        elif repayment_history[i] == 'Average': risk_score += 10
        
        # DTI Risk
        if dti[i] > 0.6: risk_score += 25
        elif dti[i] > 0.4: risk_score += 10
        
        # Business Age Risk
        if years_in_opp[i] < 2: risk_score += 15
        
        # Probability of default
        prob_default = min(0.9, risk_score / 100.0)
        
        # Random roll
        if random.random() < prob_default:
            default_flag.append(1)
        else:
            default_flag.append(0)

    # Creating DataFrame
    df = pd.DataFrame({
        'applicant_id': ids,
        'business_type': business_types,
        'years_in_operation': years_in_opp,
        'annual_revenue': annual_revenue,
        'monthly_cashflow': monthly_cashflow,
        'loan_amount_requested': loan_amount,
        'credit_score': credit_scores,
        'existing_loans': existing_loans,
        'debt_to_income_ratio': np.round(dti, 2),
        'collateral_value': collateral,
        'repayment_history': repayment_history,
        'default_flag': default_flag
    })
    
    # Save to CSV
    output_dir = os.path.join('backend', 'data')
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'business_credit_data.csv')
    df.to_csv(output_path, index=False)
    
    print(f"Successfully generated {num_records} records at {output_path}")
    print("\nDataset Summary:")
    print(df['default_flag'].value_counts(normalize=True))
    print("\nSample Data:")
    print(df.head())

if __name__ == "__main__":
    generate_dataset()

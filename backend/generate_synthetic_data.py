import pandas as pd
import numpy as np
import random

def generate_data(num_records=1000):
    np.random.seed(42)
    random.seed(42)

    data = []

    for _ in range(num_records):
        # --- 1. Borrower Demographics (Shared LC/HC) ---
        # AMT_INCOME_TOTAL (Annual Revenue proxy)
        base_income = np.random.lognormal(mean=11, sigma=1.5) 
        amt_income_total = round(base_income * (1 + (np.random.randint(0, 25) * 0.05)), 2)
        amt_income_total = max(25000, amt_income_total) # Min 25k

        # DAYS_EMPLOYED / emp_length (Years in Business proxy)
        years_in_business = np.random.randint(0, 30)
        
        # HOME_OWNERSHIP
        home_ownership = np.random.choice(['OWN', 'MORTGAGE', 'RENT'], p=[0.5, 0.3, 0.2])

        # --- 2. Loan Details (Shared LC/HC) ---
        # AMT_CREDIT (Loan Amount)
        amt_credit = round(amt_income_total * np.random.uniform(0.1, 2.0), 2)
        
        # TERM (Lending Club standard)
        term = np.random.choice([' 36 months', ' 60 months'], p=[0.7, 0.3])
        
        # AMT_ANNUITY (Monthly Installment)
        # Simplified PMT calculation approx
        rate_approx = 0.10 # 10% avg
        months = 36 if '36' in term else 60
        amt_annuity = round((amt_credit * (1 + rate_approx)) / months, 2)
        
        # AMT_GOODS_PRICE (Collateral Value proxy from Home Credit)
        # Usually closely correlated with Credit amount for asset loans
        amt_goods_price = round(amt_credit * np.random.uniform(0.0, 1.5), 2)

        # NAME_CONTRACT_TYPE (Home Credit)
        name_contract_type = np.random.choice(['Cash loans', 'Revolving loans'], p=[0.9, 0.1])
        
        # --- 3. Risk Metrics (Lending Club) ---
        # FICO / Credit Score
        fico_score = int(np.random.normal(700, 100))
        fico_score = max(300, min(850, fico_score))
        
        # dti (Debt to Income)
        dti = round(np.random.uniform(0, 40), 2) # Typical range 0-40%

        # Grade (A-G) based on FICO + noise
        if fico_score > 750: grade = 'A'
        elif fico_score > 700: grade = 'B'
        elif fico_score > 660: grade = 'C'
        elif fico_score > 620: grade = 'D'
        elif fico_score > 580: grade = 'E'
        else: grade = 'F'
        
        # int_rate based on Grade
        base_rates = {'A': 7.0, 'B': 10.0, 'C': 13.0, 'D': 17.0, 'E': 20.0, 'F': 25.0}
        int_rate = round(base_rates.get(grade, 25.0) + np.random.uniform(-1, 1), 2)

        # --- 4. Custom Business Features (Project Specific) ---
        # These are kept for B2B context but derived from standard fields where possible
        operating_expenses = round((amt_income_total / 12) * 0.7, 2)
        monthly_cashflow = round((amt_income_total / 12) - operating_expenses, 2)
        business_type = np.random.choice(['Manufacturing', 'Trading', 'Services'])
        repayment_history = np.random.choice(['Good', 'Average', 'Poor'], p=[0.7, 0.2, 0.1])

        # --- 5. Target Logic ---
        risk_score = 0
        
        # Factors
        if Grade_Weight := {'A':0, 'B':1, 'C':3, 'D':5, 'E':7, 'F':10}[grade]: risk_score += Grade_Weight
        if dti > 30: risk_score += 3
        if amt_goods_price < amt_credit: risk_score += 2 # Under-collateralized
        if repayment_history == 'Poor': risk_score += 5
        if name_contract_type == 'Cash loans' and years_in_business < 2: risk_score += 2
        
        # Random Noise
        risk_score += np.random.normal(0, 2)
        
        # Target: 0 (Repaid) / 1 (Default)
        # Lending Club uses 'loan_status', Home Credit uses 'TARGET'
        # We will use 'target' (1 = Default)
        target = 1 if risk_score > 10 else 0

        data.append({
            # Identifiers
            'sk_id_curr': int(100000 + _),
            
            # Application / LC Features
            'amt_income_total': amt_income_total,
            'amt_credit': amt_credit,
            'amt_annuity': amt_annuity,
            'amt_goods_price': amt_goods_price,
            'name_contract_type': name_contract_type,
            'term': term,
            'int_rate': int_rate,
            'grade': grade,
            'fico_score': fico_score,
            'dti': dti,
            'emp_length': years_in_business,
            'home_ownership': home_ownership,
            
            # Custom / Enrichment
            'business_type': business_type,
            'monthly_cashflow': monthly_cashflow,
            'operating_expenses': operating_expenses,
            'repayment_history': repayment_history,
            
            # Target
            'target': target
        })

    df = pd.DataFrame(data)
    
    # Save to CSV
    output_path = 'backend/synthetic_training_data.csv'
    df.to_csv(output_path, index=False)
    print(f"Generated {num_records} records with Unified Schema to {output_path}")
    print(df[['amt_income_total', 'amt_credit', 'grade', 'target']].head())
    print("\nDefault Rate:", df['target'].mean())

if __name__ == "__main__":
    generate_data()

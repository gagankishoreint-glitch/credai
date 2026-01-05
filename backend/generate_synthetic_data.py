import pandas as pd
import numpy as np
import random

def generate_data(num_records=1000):
    np.random.seed(42)
    random.seed(42)

    data = []

    for _ in range(num_records):
        # 1. Business Demographics
        curr_score = int(np.random.normal(650, 100)) # Mean 650, SD 100
        curr_score = max(300, min(850, curr_score))
        
        years_in_business = np.random.randint(0, 25)
        
        # 2. Financials
        # Correlation: Higher years -> Higher revenue generally
        base_revenue = np.random.lognormal(mean=11, sigma=1.5) # Log-normal distribution for revenue
        annual_revenue = round(base_revenue * (1 + (years_in_business * 0.05)), 2)
        annual_revenue = max(10000, annual_revenue) # Min 10k revenue

        # Profit margin varies (-20% to +40%)
        margin = np.random.uniform(-0.2, 0.4)
        net_income = annual_revenue * margin
        operating_expenses = (annual_revenue - net_income) / 12 # Monthly

        # 3. Loan Request
        # Request usually proportional to revenue, but sometimes excessive
        loan_amount = round(annual_revenue * np.random.uniform(0.1, 1.5), 2)

        # 4. Outcome Logic (Target Variable)
        # We define "Default" (1) based on risky heuristics to let the model learn them
        risk_score = 0
        
        # Risk Factors
        if loan_amount > (annual_revenue * 0.8): risk_score += 3
        if margin < 0: risk_score += 4
        if curr_score < 600: risk_score += 3
        if years_in_business < 2: risk_score += 2
        
        # Random noise
        risk_score += np.random.normal(0, 1)

        # Threshold for default
        loan_default = 1 if risk_score > 4 else 0

        data.append({
            'annualRevenue': annual_revenue,
            'operatingExpenses': operating_expenses,
            'yearsInBusiness': years_in_business,
            'creditScore': curr_score,
            'loanAmount': loan_amount,
            'loan_default': loan_default # 1 = Default, 0 = Good
        })

    df = pd.DataFrame(data)
    
    # Save to CSV
    output_path = 'backend/synthetic_training_data.csv'
    df.to_csv(output_path, index=False)
    print(f"Generated {num_records} records to {output_path}")
    print(df.head())
    print("\nClass Balance:")
    print(df['loan_default'].value_counts(normalize=True))

if __name__ == "__main__":
    generate_data()

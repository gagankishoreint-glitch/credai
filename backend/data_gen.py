import pandas as pd
import numpy as np
from faker import Faker
import random

fake = Faker()
Faker.seed(42)
np.random.seed(42)

def generate_data(num_samples=5000):
    data = []
    
    for _ in range(num_samples):
        # Business Profile
        business_type = random.choice(['Retail', 'Services', 'Manufacturing', 'Tech', 'Logistics'])
        years_in_op = np.random.randint(1, 15)
        
        # Financials
        annual_revenue = np.random.uniform(500000, 50000000)
        expense_ratio = np.random.uniform(0.6, 1.2) # >1 means loss making
        expenses = annual_revenue * expense_ratio
        ebitda = annual_revenue - expenses
        
        # Loan Request
        loan_amount = np.random.uniform(100000, 5000000)
        loan_term = random.choice([12, 24, 36, 48, 60])
        
        # Credit History
        promoter_credit_score = np.random.randint(300, 850)
        existing_debt = np.random.uniform(0, 2000000)
        
        # Logic for Default Target (Simplified)
        # Higher risk if: Loss making, Low Credit Score, High Debt-to-Revenue
        debt_to_revenue = existing_debt / annual_revenue
        
        probability_default = 0.1 # Base risk
        
        if ebitda < 0: probability_default += 0.3
        if promoter_credit_score < 600: probability_default += 0.25
        if debt_to_revenue > 0.5: probability_default += 0.2
        if years_in_op < 2: probability_default += 0.1
        
        # Cap probability
        probability_default = min(0.95, probability_default)
        
        default_flag = np.random.choice([0, 1], p=[1-probability_default, probability_default])
        
        data.append({
            'business_type': business_type,
            'years_in_operation': years_in_op,
            'annual_revenue': round(annual_revenue, 2),
            'ebitda': round(ebitda, 2),
            'loan_amount': round(loan_amount, 2),
            'loan_term_months': loan_term,
            'promoter_credit_score': promoter_credit_score,
            'existing_debt': round(existing_debt, 2),
            'default_flag': default_flag
        })
        
    df = pd.DataFrame(data)
    df.to_csv('credit_data_synthetic.csv', index=False)
    print(f"Generated {num_samples} samples to credit_data_synthetic.csv")
    return df

if __name__ == "__main__":
    generate_data()

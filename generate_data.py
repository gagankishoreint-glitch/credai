import pandas as pd
import numpy as np
import random

# Set seed for reproducibility
np.random.seed(42)

# Parameters
num_records = 3500

# Generate Data
data = {
    'applicant_id': [f'APP-{i:04d}' for i in range(1, num_records + 1)],
    'business_type': np.random.choice(['Manufacturing', 'Trading', 'Services'], num_records),
    'years_in_operation': np.random.randint(1, 20, num_records),
    'annual_revenue': np.random.randint(50000, 5000000, num_records),
    'monthly_cashflow': lambda: np.random.randint(5000, 100000, num_records), # Initial Placeholder
    'loan_amount_requested': np.random.randint(10000, 1000000, num_records),
    'credit_score': np.random.randint(300, 850, num_records),
    'existing_loans': np.random.choice([0, 1, 2, 3], p=[0.4, 0.3, 0.2, 0.1], size=num_records),
    'collateral_value': np.random.randint(0, 500000, num_records),
    'repayment_history': np.random.choice(['Good', 'Average', 'Poor'], p=[0.7, 0.2, 0.1], size=num_records)
}

df = pd.DataFrame(data)

# Logic-based corrections
df['monthly_cashflow'] = (df['annual_revenue'] / 12 * np.random.uniform(0.1, 0.4, num_records)).astype(int)
df['debt_to_income_ratio'] = np.round(np.random.uniform(0.1, 0.8, num_records), 2)

# Generate Logic for Target Variable (Default Flag)
# High risk if: credit score < 600 OR debt_to_income > 0.6 OR repayment_history is Poor
conditions = [
    (df['credit_score'] < 580) | (df['debt_to_income_ratio'] > 0.6) | (df['repayment_history'] == 'Poor'),
    (df['credit_score'] >= 580) & (df['credit_score'] < 700),
    (df['credit_score'] >= 700)
]
choices = [1, np.random.choice([0, 1], p=[0.8, 0.2], size=num_records), 0]

# Note: The above numpy choice logic is slightly flawed for vectorization. 
# Implementing simpler logic:
def get_default_flag(row):
    score = 0
    if row['credit_score'] < 600: score += 3
    if row['debt_to_income_ratio'] > 0.5: score += 2
    if row['repayment_history'] == 'Poor': score += 4
    if row['years_in_operation'] < 2: score += 1
    
    # Probability of default based on "risk score"
    if score >= 5: return 1
    if score >= 3: return np.random.choice([0, 1], p=[0.7, 0.3])
    return 0

df['default_flag'] = df.apply(get_default_flag, axis=1)

# Save to CSV
df.to_csv('dataset/business_credit_data.csv', index=False)
print("CSV Generated successfully: dataset/business_credit_data.csv")

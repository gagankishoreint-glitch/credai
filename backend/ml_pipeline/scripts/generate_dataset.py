"""
Synthetic Business Credit Dataset Generator
Generates realistic business loan application data for ML model training
Follows exact specifications from project requirements
"""

import pandas as pd
import numpy as np
from datetime import datetime

# Set random seed for reproducibility
np.random.seed(42)

# Number of records to generate (within 2000-7000 range as specified)
NUM_RECORDS = 5000

print(f"Generating {NUM_RECORDS} synthetic business credit records...")

# Generate applicant IDs
applicant_ids = [f"APP{str(i).zfill(6)}" for i in range(1, NUM_RECORDS + 1)]

# Business types with realistic distribution
business_types = np.random.choice(
    ['Manufacturing', 'Trading', 'Services'],
    size=NUM_RECORDS,
    p=[0.35, 0.30, 0.35]  # Balanced distribution
)

# Years in operation (0-50 years, skewed towards established businesses)
years_in_operation = np.random.gamma(shape=3, scale=3, size=NUM_RECORDS).astype(int)
years_in_operation = np.clip(years_in_operation, 0, 50)

# Annual revenue (₹ 1L to ₹ 50Cr) - varies by business type and age
base_revenue = np.random.lognormal(mean=15, sigma=1.5, size=NUM_RECORDS)
# Established businesses tend to have higher revenue
revenue_multiplier = 1 + (years_in_operation / 100)
annual_revenue = (base_revenue * revenue_multiplier).astype(int)
annual_revenue = np.clip(annual_revenue, 100000, 500000000)  # 1L to 50Cr

# Monthly cash flow (5-15% of annual revenue with some variability)
cashflow_percentage = np.random.uniform(0.05, 0.15, size=NUM_RECORDS)
monthly_cashflow = (annual_revenue * cashflow_percentage / 12).astype(int)

# Loan amount requested (10-50% of annual revenue)
loan_percentage = np.random.uniform(0.10, 0.50, size=NUM_RECORDS)
loan_amount_requested = (annual_revenue * loan_percentage).astype(int)
loan_amount_requested = np.clip(loan_amount_requested, 50000, 100000000)

# Credit score (300-900) - influenced by years in operation and business health
base_credit_score = np.random.normal(loc=650, scale=100, size=NUM_RECORDS)
# Better credit for established businesses
credit_adjustment = years_in_operation * 2
credit_score = (base_credit_score + credit_adjustment).astype(int)
credit_score = np.clip(credit_score, 300, 900)

# Existing loans (0-10 loans) - influenced by business age
existing_loans = np.random.poisson(lam=years_in_operation / 10, size=NUM_RECORDS)
existing_loans = np.clip(existing_loans, 0, 10)

# Debt to income ratio (0.1 to 2.0) - lower is better
debt_to_income_ratio = np.random.uniform(0.1, 2.0, size=NUM_RECORDS)
# Higher existing loans = higher debt ratio
debt_to_income_ratio += existing_loans * 0.05
debt_to_income_ratio = np.clip(debt_to_income_ratio, 0.1, 3.0)

# Collateral value (50% to 200% of loan amount)
collateral_percentage = np.random.uniform(0.5, 2.0, size=NUM_RECORDS)
collateral_value = (loan_amount_requested * collateral_percentage).astype(int)

# Repayment history
repayment_history = np.random.choice(
    ['Good', 'Average', 'Poor'],
    size=NUM_RECORDS,
    p=[0.60, 0.25, 0.15]  # Most have good history
)

# Default flag (target variable) - realistic 15-20% default rate
# Influenced by multiple factors:
# - Low credit score increases default risk
# - High debt-to-income ratio increases risk
# - Poor repayment history increases risk
# - Insufficient collateral increases risk

default_probability = np.zeros(NUM_RECORDS)

# Credit score factor (higher score = lower risk)
credit_factor = (900 - credit_score) / 600  # 0 to 1

# Debt ratio factor (higher ratio = higher risk)
debt_factor = np.clip(debt_to_income_ratio / 2.0, 0, 1)

# Repayment history factor
repayment_factor = np.where(repayment_history == 'Poor', 0.4,
                             np.where(repayment_history == 'Average', 0.2, 0.0))

# Collateral factor (lower collateral = higher risk)
collateral_ratio = collateral_value / loan_amount_requested
collateral_factor = np.where(collateral_ratio < 1.0, 0.3, 0.0)

# Combine factors
default_probability = (
    0.30 * credit_factor +
    0.25 * debt_factor +
    0.25 * repayment_factor +
    0.20 * collateral_factor
)

# Add some randomness
default_probability += np.random.uniform(-0.1, 0.1, size=NUM_RECORDS)
default_probability = np.clip(default_probability, 0, 1)

# Generate binary default flag based on probability
default_flag = (np.random.random(NUM_RECORDS) < default_probability).astype(int)

# Create DataFrame with EXACT column names from specification
df = pd.DataFrame({
    'applicant_id': applicant_ids,
    'business_type': business_types,
    'years_in_operation': years_in_operation,
    'annual_revenue': annual_revenue,
    'monthly_cashflow': monthly_cashflow,
    'loan_amount_requested': loan_amount_requested,
    'credit_score': credit_score,
    'existing_loans': existing_loans,
    'debt_to_income_ratio': np.round(debt_to_income_ratio, 3),
    'collateral_value': collateral_value,
    'repayment_history': repayment_history,
    'default_flag': default_flag
})

# Save to CSV
output_path = 'backend/ml_pipeline/data/business_credit_data.csv'
df.to_csv(output_path, index=False)

print(f"\n✅ Dataset generated successfully!")
print(f"📁 Saved to: {output_path}")
print(f"\n📊 Dataset Statistics:")
print(f"   Total Records: {len(df)}")
print(f"   Default Rate: {(default_flag.sum() / len(df)) * 100:.2f}%")
print(f"\n   Business Type Distribution:")
print(df['business_type'].value_counts())
print(f"\n   Repayment History Distribution:")
print(df['repayment_history'].value_counts())
print(f"\n   Credit Score Range: {df['credit_score'].min()} - {df['credit_score'].max()}")
print(f"   Mean Credit Score: {df['credit_score'].mean():.2f}")
print(f"\n   Annual Revenue Range: ₹{df['annual_revenue'].min():,} - ₹{df['annual_revenue'].max():,}")
print(f"   Median Annual Revenue: ₹{df['annual_revenue'].median():,}")
print(f"\n   Loan Amount Range: ₹{df['loan_amount_requested'].min():,} - ₹{df['loan_amount_requested'].max():,}")

print("\n✨ First 5 records:")
print(df.head())

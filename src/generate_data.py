import numpy as np
import pandas as pd

np.random.seed(42)

N = 5000  # number of records

data = {
    "applicant_id": [f"APP_{i+1:05d}" for i in range(N)],

    "business_type": np.random.choice(
        ["Manufacturing", "Trading", "Services"],
        size=N,
        p=[0.3, 0.4, 0.3]
    ),

    "years_in_operation": np.random.randint(1, 25, size=N),

    "annual_revenue": np.random.normal(
        loc=5_000_000, scale=2_000_000, size=N
    ).clip(500_000),

    "monthly_cashflow": np.random.normal(
        loc=400_000, scale=150_000, size=N
    ).clip(50_000),

    "loan_amount_requested": np.random.normal(
        loc=1_500_000, scale=700_000, size=N
    ).clip(100_000),

    "credit_score": np.random.randint(300, 901, size=N),

    "existing_loans": np.random.randint(0, 6, size=N),

    "debt_to_income_ratio": np.random.uniform(0.05, 0.9, size=N),

    "collateral_value": np.random.normal(
        loc=2_000_000, scale=1_000_000, size=N
    ).clip(0),

    "repayment_history": np.random.choice(
        ["Good", "Average", "Poor"],
        size=N,
        p=[0.6, 0.25, 0.15]
    ),
}

df = pd.DataFrame(data)

# Target variable logic (semi-realistic)
risk_score = (
    0.4 * (df["credit_score"] < 620).astype(int) +
    0.3 * (df["debt_to_income_ratio"] > 0.55).astype(int) +
    0.2 * (df["repayment_history"] == "Poor").astype(int) +
    0.1 * (df["existing_loans"] > 3).astype(int)
)

df["default_flag"] = (risk_score >= 0.6).astype(int)

# Save dataset
df.to_csv("data/business_credit_data.csv", index=False)

print("Dataset generated successfully!")
print(df.head())

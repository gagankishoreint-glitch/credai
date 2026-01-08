import numpy as np
import pandas as pd
import random

def generate_refined_data():
    np.random.seed(42)
    random.seed(42)
    
    N = 5000  # number of records
    
    # Identifiers
    applicant_ids = [f"APP_{i+1:05d}" for i in range(N)]
    
    # Demographics
    education_levels = ["Secondary", "Higher Education", "Incomplete Higher", "Lower Secondary"]
    marital_statuses = ["Married", "Single", "Divorced", "Widowed"]
    housing_types = ["House / apartment", "Rented apartment", "With parents", "Municipal apartment"]
    
    age = np.random.randint(21, 70, size=N)
    education = np.random.choice(education_levels, size=N, p=[0.6, 0.25, 0.1, 0.05])
    marital_status = np.random.choice(marital_statuses, size=N, p=[0.5, 0.3, 0.15, 0.05])
    housing_type = np.random.choice(housing_types, size=N, p=[0.7, 0.15, 0.1, 0.05])
    cnt_children = np.random.choice([0, 1, 2, 3, 4], size=N, p=[0.5, 0.25, 0.15, 0.08, 0.02])
    
    # Employment & Financials
    employment_years = np.clip(age - 20 - np.random.exponential(5, size=N), 0, 40)
    annual_income = np.random.lognormal(mean=11, sigma=0.8, size=N) 
    annual_income = np.clip(annual_income, 5000, 1000000) # clip to reasonable range
    
    business_type = np.random.choice(["Manufacturing", "Trading", "Services", "IT", "Construction"], size=N)
    
    # NEW: Market Trends Analysis (Simulated)
    # Define current market risk for each sector (0-100, where 100 is high risk crisis)
    # E.g., Construction is risky, IT is safe.
    market_conditions = {
        "Manufacturing": 60,
        "Trading": 50,
        "Services": 40,
        "IT": 20,
        "Construction": 80
    }
    
    # Map sector to base risk
    market_risk_index = np.array([market_conditions[b] for b in business_type])
    # Add some temporal noise/variation per applicant (as if they applied at slightly different times in the trend)
    market_risk_index = market_risk_index + np.random.normal(0, 5, size=N)
    market_risk_index = np.clip(market_risk_index, 0, 100)
    
    # Financial Stability Metrics
    # Assets usually coincide with age and income
    assets_total = annual_income * np.random.uniform(0.5, 10.0, size=N) + (age * 1000)
    
    # Total Debt (should generally be less than assets, but not always)
    # Distressed people might have debt > assets
    debt_ratio = np.random.beta(2, 5, size=N) * 1.5 # skew towards < 1.0 but tail > 1.0
    total_debt = assets_total * debt_ratio
    
    # Monthly Obligations
    # A portion of debt is serviced monthly + other expenses
    monthly_debt_obligations = (total_debt * np.random.uniform(0.005, 0.02, size=N)) 
    
    # Credit History Indicators
    credit_score = np.random.normal(650, 100, size=N).clip(300, 850)
    total_credit_lines = np.random.randint(1, 15, size=N)
    utilization_rate = total_debt / (assets_total * 0.5 + 1000) # Proxy utilization
    utilization_rate = np.clip(utilization_rate, 0, 1.2) # Cap at 1.2
    
    days_since_last_delinquency = np.random.choice(
        [0, 30, 60, 90, 180, 365, 730, -1], 
        size=N, 
        p=[0.6, 0.1, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05]
    ) 
    
    # Transaction Summaries
    avg_trans_amount_3m = np.random.exponential(1000, size=N)
    trans_fail_count = np.random.poisson(0.5, size=N)
    
    df = pd.DataFrame({
        "applicant_id": applicant_ids,
        "age": age,
        "education_level": education,
        "marital_status": marital_status,
        "housing_type": housing_type,
        "cnt_children": cnt_children,
        "employment_years": employment_years,
        "annual_income": annual_income,
        "assets_total": assets_total,
        "total_debt": total_debt,
        "monthly_debt_obligations": monthly_debt_obligations,
        "business_type": business_type,
        "market_risk_index": market_risk_index, # NEW
        "credit_score": credit_score,
        "total_credit_lines": total_credit_lines,
        "utilization_rate": utilization_rate,
        "days_since_last_delinquency": days_since_last_delinquency,
        "avg_trans_amount_3m": avg_trans_amount_3m,
        "trans_fail_count": trans_fail_count
    })
    
    # Target Variable Logic (Ground Truth Generation)
    # Debt to Income Ratio
    dti = df["monthly_debt_obligations"] * 12 / df["annual_income"]
    
    risk_factor_1 = (dti > 0.6)
    risk_factor_2 = (df["days_since_last_delinquency"] > 0) & (df["days_since_last_delinquency"] < 90)
    risk_factor_3 = df["credit_score"] < 600
    risk_factor_4 = df["trans_fail_count"] > 2
    risk_factor_5 = df["total_debt"] > df["assets_total"] # Insolvent
    # New: Market Risk Impact
    risk_factor_6 = df["market_risk_index"] > 70
    
    base_score = -2.5 
    
    base_score += 2.0 * risk_factor_1.astype(int)
    base_score += 2.0 * risk_factor_2.astype(int)
    base_score += 1.5 * risk_factor_3.astype(int)
    base_score += 1.0 * risk_factor_4.astype(int)
    base_score += 1.5 * risk_factor_5.astype(int)
    base_score += 1.2 * risk_factor_6.astype(int) # Market trend impact
    
    base_score += np.random.normal(0, 0.5, size=N)
    
    prob_default = 1 / (1 + np.exp(-base_score))
    df["default_flag"] = np.random.binomial(1, prob_default)
    
    print(f"Generated {N} records.")
    print(f"Default Rate: {df['default_flag'].mean():.2%}")
    
    output_path = "data/refined_credit_data.csv"
    df.to_csv(output_path, index=False)
    print(f"Saved to {output_path}")

if __name__ == "__main__":
    generate_refined_data()

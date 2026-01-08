import pandas as pd
import joblib
import numpy as np
import json
from decision_engine import apply_decision_logic, generate_explanation, check_safety_rules

def test_scenarios():
    print("Loading model and preprocessor...")
    try:
        model = joblib.load("model/credit_risk_model.joblib")
        preprocessor = joblib.load("model/preprocessor.joblib")
    except FileNotFoundError:
        print("Model files not found.")
        return

    # Define Scenarios
    scenarios = [
        {
            "name": "Scenario A: Strong Business (Low Risk)",
            "data": {
                "age": 45, "education_level": "Higher Education", "marital_status": "Married", "housing_type": "House / apartment",
                "cnt_children": 2, "employment_years": 15, "annual_income": 150000, 
                "assets_total": 400000, "total_debt": 50000, "monthly_debt_obligations": 2000,
                "business_type": "IT", "credit_score": 780, "total_credit_lines": 10,
                "utilization_rate": 0.12, "days_since_last_delinquency": -1, # Never
                "avg_trans_amount_3m": 5000, "trans_fail_count": 0,
                "doc_verified_income": 150000, "doc_assets_reported": 400000, 
                "doc_derived_cashflow": 12000, "has_financial_stmts": 1,
                "market_risk_index": 20
            }
        },
        {
            "name": "Scenario B: Risky Business (High Risk)",
            "data": {
                "age": 25, "education_level": "Secondary", "marital_status": "Single", "housing_type": "Rented apartment",
                "cnt_children": 0, "employment_years": 2, "annual_income": 40000, 
                "assets_total": 10000, "total_debt": 35000, "monthly_debt_obligations": 1800,
                "business_type": "Services", "credit_score": 550, "total_credit_lines": 3,
                "utilization_rate": 3.5, # Very high (Debt > Asset proxy in generator logic was lower, but here we force high)
                "days_since_last_delinquency": 30, # Recent
                "avg_trans_amount_3m": 200, "trans_fail_count": 5,
                "doc_verified_income": 38000, "doc_assets_reported": 10000, 
                "doc_derived_cashflow": 500, "has_financial_stmts": 1,
                "market_risk_index": 80
            }
        },
        {
            "name": "Scenario C: Borderline (Medium Risk)",
            "data": {
                "age": 35, "education_level": "Higher Education", "marital_status": "Married", "housing_type": "Rented apartment",
                "cnt_children": 1, "employment_years": 5, "annual_income": 75000, 
                "assets_total": 50000, "total_debt": 40000, "monthly_debt_obligations": 2500,
                "business_type": "Trading", "credit_score": 640, "total_credit_lines": 8,
                "utilization_rate": 0.8,
                "days_since_last_delinquency": 365, # Old delinquency
                "avg_trans_amount_3m": 1200, "trans_fail_count": 1,
                "doc_verified_income": 75000, "doc_assets_reported": 50000, 
                "doc_derived_cashflow": 1000, "has_financial_stmts": 0,
                "market_risk_index": 50
            }
        },
        {
            "name": "Scenario D: Data Failure (Income Discrepancy)",
            "data": {
                "age": 30, "education_level": "Higher Education", "marital_status": "Single", "housing_type": "Rented apartment",
                "cnt_children": 0, "employment_years": 3, "annual_income": 100000, 
                "assets_total": 20000, "total_debt": 10000, "monthly_debt_obligations": 1000,
                "business_type": "Retail", "credit_score": 700, "total_credit_lines": 5,
                "utilization_rate": 0.5, "days_since_last_delinquency": -1,
                "avg_trans_amount_3m": 2000, "trans_fail_count": 0,
                "doc_verified_income": 50000, # Verified is 50k vs Reported 100k -> 50% gap -> Fail
                "doc_assets_reported": 20000, 
                "doc_derived_cashflow": 4000, "has_financial_stmts": 1,
                "market_risk_index": 40
            }
        }
    ]

    print("\n--- Running Scenario Tests ---\n")

    for sc in scenarios:
        row = sc["data"]
        
        # 0. SAFETY CHECK (Pre-Calculation)
        # Check integrity on raw inputs
        status, reason = check_safety_rules(row)
        if status != "PASS":
            print(f"[{sc['name']}]")
            print(f"  Inputs: Income=${row.get('annual_income',0)}, Verified=${row.get('doc_verified_income', 'N/A')}")
            print(f"  ⚠️ SAFETY BLOCK: {status} - {reason}")
            print("-" * 30)
            continue
        # Derived features normally handled in app/preprocess, must calculate here manually for the raw dict
        # or construct DF and let preprocess handle scaling, BUT preprocess expects columns to exist.
        # Our preprocess.py takes Raw + Derived.
        
        # Calculate derived metrics as per preprocess.py logic
        row["income_discrepancy"] = 0.0
        if "doc_verified_income" in row and row["doc_verified_income"]:
             row["income_discrepancy"] = abs(row["annual_income"] - row["doc_verified_income"]) / (row["annual_income"] + 1)
        
        row["debt_to_assets"] = row["total_debt"] / (row["assets_total"] + 1)
        row["payment_to_income"] = row["monthly_debt_obligations"] * 12 / (row["annual_income"] + 1)
        # utilization_rate is already in input for simplicity, but let's consistency check? 
        # The model uses the one provided in input (which comes from generator logic).
        
        # transaction_success_rate
        row["transaction_success_rate"] = 1.0 - (row["trans_fail_count"] / (row["total_credit_lines"] * 5 + 1))
        
        # NEW: Cashflow Coverage
        # doc_derived_cashflow is in row but checking for 0 div
        row["cashflow_coverage"] = 0.0
        if "doc_derived_cashflow" in row and row["doc_derived_cashflow"]:
             row["cashflow_coverage"] = row["doc_derived_cashflow"] / (row["monthly_debt_obligations"] + 1)

        # Create DataFrame
        df = pd.DataFrame([row])
        df["applicant_id"] = "TEST" # Dummy
        df["default_flag"] = 0 # Dummy

        # Log Transformations
        log_cols = ["doc_verified_income", "assets_total", "doc_derived_cashflow"]
        for c in log_cols:
            if c in df.columns:
                df[c] = np.log1p(df[c].clip(lower=0))

        # Transform
        # Drop strictly
        cols_to_drop = ["applicant_id", "default_flag", "marital_status", "cnt_children", "annual_income", "total_debt"]
        X = df.drop(columns=[c for c in cols_to_drop if c in df.columns], errors='ignore')

        try:
            X_processed = preprocessor.transform(X)
        except Exception as e:
            print(f"Preprocessing error for {sc['name']}: {e}")
            continue

        # Predict
        prob = model.predict_proba(X_processed)[0, 1]
        
        # Fairness Pass
        biz = row.get("business_type", "Other")
        tier, confidence, flag = apply_decision_logic(prob, business_type=biz)

        print(f"[{sc['name']}]")
        print(f"  Inputs: Income=${row['annual_income']}, Debt=${row['total_debt']}, Score={row['credit_score']}")
        print(f"  Model Probability of Default: {prob:.2%}")
        print(f"  Decision: {tier.upper()} (Confidence: {confidence:.2%})")
        if flag != "None":
            print(f"  Flag: {flag}")
            
        # Counterfactuals
        if tier != "Approve":
            from decision_engine import generate_counterfactuals
            advice = generate_counterfactuals(model, preprocessor, X)
            print("  Advice:", advice)
        print("-" * 30)

if __name__ == "__main__":
    test_scenarios()

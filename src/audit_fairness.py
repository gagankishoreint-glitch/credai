import pandas as pd
import numpy as np
import joblib
import json

def audit_fairness():
    print("--- Fairness Audit Started ---")
    
    # Load Data with Robust Merge (Replicating train.py logic)
    try:
        df = pd.read_csv("data/refined_credit_data.csv")
        try:
            doc_df = pd.read_csv("data/document_features.csv")
            # Merge on applicant_id 
            df = df.merge(doc_df, on="applicant_id", how="left", suffixes=("", "_doc"))
            for col in doc_df.columns:
                if col == "applicant_id": continue
                doc_col = f"{col}_doc"
                if doc_col in df.columns:
                    if col in df.columns: df[col] = df[col].fillna(df[doc_col])
                    else: df[col] = df[doc_col]
                    df.drop(columns=[doc_col], inplace=True)
            if "has_financial_stmts" in df.columns:
                df["has_financial_stmts"] = df["has_financial_stmts"].fillna(0)
        except FileNotFoundError:
            print("Warning: document_features.csv not found, using core data only.")
            
    except FileNotFoundError:
        print("Data not found. Skipping audit.")
        return

    # Load Model pipeline
    try:
        model = joblib.load("model/credit_risk_model.joblib")
        preprocessor = joblib.load("model/preprocessor.joblib")
    except Exception as e:
        print(f"Model/Preprocessor not found: {e}")
        return

    # Feature Engineering
    df["income_discrepancy"] = 0.0
    if "doc_verified_income" in df.columns:
        mask_docs = df["doc_verified_income"].notna()
        df.loc[mask_docs, "income_discrepancy"] = (
            (df.loc[mask_docs, "annual_income"] - df.loc[mask_docs, "doc_verified_income"]).abs() 
            / (df.loc[mask_docs, "annual_income"] + 1)
        )

    df["debt_to_assets"] = df["total_debt"] / (df["assets_total"] + 1)
    df["payment_to_income"] = df["monthly_debt_obligations"] * 12 / (df["annual_income"] + 1)
    df["transaction_success_rate"] = 1.0 - (df["trans_fail_count"] / (df["total_credit_lines"] * 5 + 1))
    df["cashflow_coverage"] = 0.0
    if "doc_derived_cashflow" in df.columns:
        mask_cf = df["doc_derived_cashflow"].notna()
        df.loc[mask_cf, "cashflow_coverage"] = df.loc[mask_cf, "doc_derived_cashflow"] / (df.loc[mask_cf, "monthly_debt_obligations"] + 1)
    
    log_cols = ["doc_verified_income", "assets_total", "doc_derived_cashflow"]
    for c in log_cols:
         if c in df.columns: df[c] = np.log1p(df[c].clip(lower=0))

    X = df.drop(columns=["applicant_id", "default_flag", "marital_status", "cnt_children", "annual_income", "total_debt"], errors='ignore')
    
    # Predict
    X_proc = preprocessor.transform(X)
    # CalibratedClassifierCV 'predict' uses the threshold 0.5 usually
    preds = model.predict(X_proc)
    df["prediction"] = preds # 1 = Default, 0 = Approve (Confusion: target is default_flag)
    # If prediction is 1 (Default), user is REJECTED. 
    # If prediction is 0 (Pay), user is APPROVED.
    df["approved"] = (df["prediction"] == 0).astype(int)

    # --- Audit: Age Groups ---
    df["age_group"] = pd.cut(df["age"], bins=[0, 25, 35, 50, 100], labels=["Gen Z (<25)", "Young Adult (25-35)", "Adult (35-50)", "Senior (>50)"])
    
    print("\n[ Fairness by Age Group ]")
    age_audit = df.groupby("age_group")["approved"].mean()
    print(age_audit)
    
    # Disparate Impact Ratio (DIR)
    # Reference group: Adult (35-50) often highest earning/stable
    ref_rate = age_audit.get("Adult (35-50)", 0.5)
    print("\nDisparate Impact Ratio (vs Adult group):")
    for group, rate in age_audit.items():
        dir_val = rate / ref_rate if ref_rate > 0 else 0
        status = "FAIL" if dir_val < 0.80 else "PASS" # "Four-Fifths Rule"
        print(f"  {group}: {dir_val:.2f} [{status}]")

    # --- Audit: Income Groups ---
    df["income_quartile"] = pd.qcut(df["annual_income"], 4, labels=["Low", "Mid-Low", "Mid-High", "High"])
    print("\n[ Fairness by Income ]")
    inc_audit = df.groupby("income_quartile")["approved"].mean()
    print(inc_audit)
    
    # Save Report
    report = {
        "age_fairness": age_audit.to_dict(),
        "income_fairness": inc_audit.to_dict()
    }
    with open("docs/fairness_audit_report.json", "w") as f:
        json.dump(report, f, indent=4)
    print("\nAudit Report saved to docs/fairness_audit_report.json")

if __name__ == "__main__":
    audit_fairness()

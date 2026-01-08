import pandas as pd
import numpy as np
import joblib
import json

def calculate_psi(expected, actual, buckets=10):
    """
    Calculate Population Stability Index (PSI)
    """
    def scale_range(input, min, max):
        input += (1e-6)
        interp = np.interp(input, (min, max), (0, 1))
        return interp
    
    breakpoints = np.arange(0, buckets + 1) / (buckets) * 100
    breakpoints = np.percentile(expected, breakpoints)
    breakpoints[0] = -np.inf
    breakpoints[-1] = np.inf
    
    expected_percents = np.histogram(expected, breakpoints)[0] / len(expected)
    actual_percents = np.histogram(actual, breakpoints)[0] / len(actual)
    
    def sub_psi(e_perc, a_perc):
        if a_perc == 0: a_perc = 0.0001
        if e_perc == 0: e_perc = 0.0001
        value = (e_perc - a_perc) * np.log(e_perc / a_perc)
        return value

    psi_value = np.sum([sub_psi(e, a) for e, a in zip(expected_percents, actual_percents)])
    return psi_value

def monitor_drift():
    print("--- Drift Monitoring Started ---")
    
    # 1. Load Baseline (Training Data Probabilities)
    # In a real system, this would be stored in a metrics store.
    # We will simulate baseline by reloading train/test split if possible or just assuming a distribution.
    # For this demo, let's load a saved artifact from training if it exists, or generate fresh from refined data.
    
    try:
        # Load and Merge Data (Refined + Docs)
        df = pd.read_csv("data/refined_credit_data.csv")
        try:
            doc_df = pd.read_csv("data/document_features.csv")
            df = df.merge(doc_df, on="applicant_id", how="left", suffixes=("", "_doc"))
            for col in doc_df.columns:
                if col == "applicant_id": continue
                doc_col = f"{col}_doc"
                if doc_col in df.columns:
                    if col in df.columns: df[col] = df[col].fillna(df[doc_col])
                    else: df[col] = df[doc_col]
                    df.drop(columns=[doc_col], inplace=True)
        except FileNotFoundError:
            pass
            
        model = joblib.load("model/credit_risk_model.joblib")
        preprocessor = joblib.load("model/preprocessor.joblib")
    except Exception as e:
        print(f"Resources missing: {e}")
        return

    # Helper: Preprocess
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

    for c in ["doc_verified_income", "assets_total", "doc_derived_cashflow"]:
         if c in df.columns: df[c] = np.log1p(df[c].clip(lower=0))
    X = df.drop(columns=["applicant_id", "default_flag", "marital_status", "cnt_children", "annual_income", "total_debt"], errors='ignore')
    X_proc = preprocessor.transform(X)
    
    # Baseline Probabilities (Hypothetically from last month)
    # We'll take the first 50% as baseline
    mid = len(X_proc) // 2
    baseline_probs = model.predict_proba(X_proc[:mid])[:, 1]
    
    # Current Probabilities (simulate drift by shifting input)
    # Let's artificially drift the second half to demonstrate detection
    X_current = X_proc[mid:].copy()
    
    # Simulate Economic Shock: Reduce income/assets features (which are likely scaled)
    # Finding index of 'assets_total' is hard on array, so we just run predict on normal data first
    current_probs = model.predict_proba(X_current)[:, 1]
    
    # Calculate PSI
    psi = calculate_psi(baseline_probs, current_probs)
    print(f"Population Stability Index (PSI): {psi:.4f}")
    
    status = "STABLE"
    if psi > 0.1: status = "WARNING"
    if psi > 0.2: status = "CRITICAL DRIFT"
    
    print(f"Drift Status: {status}")
    
    alert = {
        "metric": "PSI",
        "value": psi,
        "status": status,
        "thresholds": {"warning": 0.1, "critical": 0.2}
    }
    
    with open("docs/drift_alert.json", "w") as f:
        json.dump(alert, f, indent=4)
    print("Drift Alert saved to docs/drift_alert.json")

if __name__ == "__main__":
    monitor_drift()

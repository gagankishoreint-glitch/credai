import pandas as pd
import numpy as np
import joblib
import json
import os
from sklearn.metrics import confusion_matrix

def calculate_metrics(df_segment, y_true_col, y_pred_col):
    """
    Calculates Approval Rate, FPR (False Rejection Rate), FNR (Missed Risk Rate).
    Assuming:
    - Model Prediction 1 = Default (Reject/High Risk)
    - Model Prediction 0 = Good (Approve/Low Risk)
    - Model Target 1 = Default (Bad)
    
    Therefore:
    - TN: Predicted 0 (Approve), Actual 0 (Good) -> Correct Approval
    - FP: Predicted 1 (Reject), Actual 0 (Good) -> Unfair Rejection
    - FN: Predicted 0 (Approve), Actual 1 (Bad) -> Missed Risk
    - TP: Predicted 1 (Reject), Actual 1 (Bad) -> Correct Rejection
    
    - FPR = FP / (FP + TN)  -> Of all Good people, rate of rejection.
    - FNR = FN / (FN + TP)  -> Of all Bad people, rate of approval.
    """
    if len(df_segment) == 0:
        return {"approval_rate": 0, "fpr": 0, "fnr": 0, "count": 0}

    y_pred = df_segment[y_pred_col]
    y_true = df_segment[y_true_col]
    
    # Approval Rate (Predicted 0)
    approval_rate = (y_pred == 0).mean()
    
    try:
        tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
    except ValueError:
        tn, fp, fn, tp = 0, 0, 0, 0
        
    fpr = fp / (tn + fp + 1e-6) # False Rejection Rate
    fnr = fn / (fn + tp + 1e-6) # Missed Risk Rate
    
    return {
        "approval_rate": round(approval_rate, 4),
        "fpr": round(fpr, 4),
        "fnr": round(fnr, 4),
        "count": int(len(df_segment))
    }

def run_audit():
    print("Running Advanced Fairness Audit...")
    
    # 1. Load Data
    try:
        df = pd.read_csv("data/refined_credit_data.csv")
    except FileNotFoundError:
        print("Error: refined_credit_data.csv not found.")
        return

    # Attempt merge with docs for completeness (if used in feature eng)
    try:
        doc_df = pd.read_csv("data/document_features.csv")
        df = df.merge(doc_df, on="applicant_id", how="left", suffixes=("", "_doc"))
        if "doc_verified_income_doc" in df.columns:
            df["doc_verified_income"] = df["doc_verified_income_doc"].fillna(df.get("doc_verified_income", np.nan))
        if "doc_derived_cashflow_doc" in df.columns:
            df["doc_derived_cashflow"] = df["doc_derived_cashflow_doc"].fillna(df.get("doc_derived_cashflow", np.nan))
    except (FileNotFoundError, KeyError):
        pass

    # Basic Fills
    if "doc_verified_income" not in df.columns: df["doc_verified_income"] = df["annual_income"]
    
    # 2. Replicate Feature Engineering (MUST MATCH TRAIN.PY)
    # --------------------------------------------------------
    # Verify income consistency: (Reported Annual - Document Annual) / Reported
    df["income_discrepancy"] = 0.0
    mask_docs = df["doc_verified_income"].notna()
    if "annual_income" in df.columns:
         df.loc[mask_docs, "income_discrepancy"] = (
            (df.loc[mask_docs, "annual_income"] - df.loc[mask_docs, "doc_verified_income"]).abs() 
            / (df.loc[mask_docs, "annual_income"] + 1)
        )

    df["monthly_debt_obligations"] = df.get("monthly_debt_obligations", df["total_debt"] * 0.02)
    df["debt_to_assets"] = df["total_debt"] / (df["assets_total"] + 1)
    df["payment_to_income"] = df["monthly_debt_obligations"] * 12 / (df["annual_income"] + 1)
    df["transaction_success_rate"] = 1.0 - (df["trans_fail_count"] / (df["total_credit_lines"] * 5 + 1))
    
    df["cashflow_coverage"] = 0.0
    if "doc_derived_cashflow" in df.columns:
        mask_cf = df["doc_derived_cashflow"].notna()
        df.loc[mask_cf, "cashflow_coverage"] = df.loc[mask_cf, "doc_derived_cashflow"] / (df.loc[mask_cf, "monthly_debt_obligations"] + 1)
    
    log_cols = ["doc_verified_income", "assets_total", "doc_derived_cashflow"]
    for c in log_cols:
        if c in df.columns:
            df[c] = np.log1p(df[c].clip(lower=0))

    # X Construction
    cols_to_drop = ["applicant_id", "default_flag", "marital_status", "cnt_children", "annual_income", "total_debt"]
    X = df.drop(columns=[c for c in cols_to_drop if c in df.columns], errors='ignore')
    # --------------------------------------------------------

    # 3. Predict Outcomes
    try:
        preprocessor = joblib.load("model/preprocessor.joblib")
        model = joblib.load("model/credit_risk_model.joblib")
        
        X_proc = preprocessor.transform(X)
        probs = model.predict_proba(X_proc)[:, 1]
        
        # DECISION THRESHOLD for "Rejection"
        # Strategy: Strict > 0.45 is Reject.
        # But we now have Mitigation for Construction (Reject > 0.55).
        # We must apply this dynamically.
        
        # 1. Base Threshold array
        thresholds = np.full(len(df), 0.45)
        
        # 2. Apply Mitigation
        if "business_type" in df.columns:
            # Construction gets 0.60 (Relaxed)
            mask_const = (df["business_type"] == "Construction")
            thresholds[mask_const] = 0.60
            
        # 3. Preds
        df["predicted_default"] = (probs > thresholds).astype(int) 
        
    except Exception as e:
        print(f"Model prediction failed: {e}")
        return

    # 4. Segmentation
    # Age
    df["age_group"] = pd.cut(df["age"], bins=[0, 30, 45, 60, 100], labels=["Under 30", "30-45", "45-60", "Over 60"])
    
    # Income (Use Raw annual_income to bin)
    # If annual_income was dropped from X, it's still in 'df' (unless we dropped inplace, which input drop does not)
    # Check if annual_income exists
    if "annual_income" in df.columns:
         df["income_band"] = pd.qcut(df["annual_income"], q=4, labels=["Low", "Medium", "High", "Very High"])
    else:
         df["income_band"] = "Unknown"

    # Employment -> business_type

    # 5. Calculate Metrics
    report = {}
    dimensions = {
        "age": "age_group",
        "income": "income_band",
        "employment": "business_type"
    }

    for dim_name, col in dimensions.items():
        if col not in df.columns: continue
        
        stats_list = []
        groups = df[col].dropna().unique()
        
        for g in groups:
            sub = df[df[col] == g]
            stats = calculate_metrics(sub, "default_flag", "predicted_default")
            stats["group"] = str(g)
            stats_list.append(stats)
            
        # Identify Reference Group (Max Approval Rate)
        if stats_list:
            best_group = max(stats_list, key=lambda x: x["approval_rate"])
            ref_rate = best_group["approval_rate"]
            
            for s in stats_list:
                # DIR
                s["disparate_impact"] = round(s["approval_rate"] / (ref_rate + 1e-6), 2)
                s["flagged_dir"] = bool(s["disparate_impact"] < 0.80)
                
                # FPR Disparity (Parity Check)
                # Compare FPR to Best Group's FPR. 
                # Diff > 0.10? Or Ratio?
                # Let's store the raw values. Mitigation plan will interpret.
                pass
        
        report[dim_name] = stats_list

    # 6. Save Report
    def np_encoder(object):
        if isinstance(object, np.generic):
            return object.item()
        raise TypeError
        
    with open("data/advanced_bias_report.json", "w") as f:
        json.dump(report, f, indent=2, default=np_encoder)

    # 7. Print Console Summary
    print("\n=== ADVANCED FAIRNESS AUDIT REPORT ===")
    for dim, stats in report.items():
        print(f"\n--- Dimension: {dim.upper()} ---")
        # Sort by group name
        stats.sort(key=lambda x: x["group"])
        for s in stats:
            flag = "⚠️ FAIL" if s["flagged_dir"] else "✅ PASS"
            print(f"{flag} {s['group']:<15} | AR: {s['approval_rate']:.2f} | DIR: {s['disparate_impact']:.2f} | FPR: {s['fpr']:.2f} | FNR: {s['fnr']:.2f}")

    print("\nAudit saved to: data/advanced_bias_report.json")

if __name__ == "__main__":
    run_audit()

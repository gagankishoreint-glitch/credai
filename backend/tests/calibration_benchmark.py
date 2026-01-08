
import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss, roc_auc_score, recall_score, precision_score, log_loss
from sklearn.calibration import calibration_curve
from xgboost import XGBClassifier
import os
import sys

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_PATH = os.path.join(BASE_DIR, "data", "refined_credit_data.csv")
MODEL_PATH = os.path.join(BASE_DIR, "model", "credit_risk_model.joblib")
PREPROCESSOR_PATH = os.path.join(BASE_DIR, "model", "preprocessor.joblib")

def run_benchmark():
    print("🚀 STARTING PROMPT T3 & T4: CALIBRATION & BENCHMARKING")
    print("======================================================")
    
    # 1. Load Data
    print(f"📂 Loading data from {DATA_PATH}...")
    try:
        df = pd.read_csv(DATA_PATH)
        df.columns = df.columns.str.strip()
        
        # Merge Document Features if available (Simplified vs src/preprocess.py)
        doc_path = os.path.join(os.path.dirname(DATA_PATH), "document_features.csv")
        if os.path.exists(doc_path):
             doc_df = pd.read_csv(doc_path)
             df = df.merge(doc_df, on="applicant_id", how="left", suffixes=("", "_doc"))
             for col in doc_df.columns:
                if col == "applicant_id": continue
                doc_col = f"{col}_doc"
                if doc_col in df.columns:
                    if col in df.columns:
                        df[col] = df[col].fillna(df[doc_col])
                    else:
                        df[col] = df[doc_col]
                    df.drop(columns=[doc_col], inplace=True)
        
        # FEATURE ENGINEERING (Must match src/preprocess.py)
        # --------------------------------------------------
        if "doc_verified_income" not in df.columns: df["doc_verified_income"] = np.nan
        if "doc_derived_cashflow" not in df.columns: df["doc_derived_cashflow"] = np.nan
        if "assets_total" not in df.columns: df["assets_total"] = 0
        
        # Income Discrepancy
        df["income_discrepancy"] = 0.0
        mask_docs = df["doc_verified_income"].notna()
        df.loc[mask_docs, "income_discrepancy"] = (
            (df.loc[mask_docs, "annual_income"] - df.loc[mask_docs, "doc_verified_income"]).abs() 
            / (df.loc[mask_docs, "annual_income"] + 1)
        )

        # Derived Metrics
        df["debt_to_assets"] = df["total_debt"] / (df["assets_total"] + 1)
        df["payment_to_income"] = df["monthly_debt_obligations"] * 12 / (df["annual_income"] + 1)
        df["transaction_success_rate"] = 1.0 - (df["trans_fail_count"] / (df["total_credit_lines"] * 5 + 1))

        # Cashflow Coverage
        df["cashflow_coverage"] = 0.0
        mask_cf = df["doc_derived_cashflow"].notna()
        df.loc[mask_cf, "cashflow_coverage"] = df.loc[mask_cf, "doc_derived_cashflow"] / (df.loc[mask_cf, "monthly_debt_obligations"] + 1)

        # Log Transforms
        log_cols = ["doc_verified_income", "assets_total", "doc_derived_cashflow"]
        for c in log_cols:
            if c in df.columns:
                df[c] = np.log1p(df[c].clip(lower=0))

        # --------------------------------------------------

        target_col = 'default_flag' # Found in preprocess.py line 110: y = df["default_flag"]
        if target_col not in df.columns:
             # Try fallback
             if 'loan_status' in df.columns:
                 df['default_flag'] = df['loan_status'].map({'Default': 1, 'Paid': 0})
                 
        print(f"DATA: {df.shape}, Target: {target_col}")
        
    except Exception as e:
        print(f"❌ Failed to load/process data: {e}")
        return

    # Preprocessing (Load existing preprocessor to be fair to Prod model)
    try:
        preprocessor = joblib.load(PREPROCESSOR_PATH)
        print("✅ Preprocessor loaded.")
    except:
        print("❌ Preprocessor missing. Cannot evaluate Prod Model fairly.")
        return

    # Prepare X, y
    # Must drop columns that preprocessor doesn't expect if we pass the whole DF?
    # No, ColumnTransformer ignores extra columns usually, unless 'remainder' is fail.
    # But preprocess.py drops specific cols line 99.
    cols_to_drop = ["applicant_id", "default_flag", "marital_status", "cnt_children", "annual_income", "total_debt"]
    X = df.drop(columns=[c for c in cols_to_drop if c in df.columns])
    y = df[target_col]
        
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # 2. Train Baselines
    print("\n🏋️ Training Baselines...")
    
    # Transform Data for Baselines (using same preprocessor to be fair)
    # The preprocessor likely expects a DataFrame and returns a dense array.
    try:
        X_train_proc = preprocessor.transform(X_train)
        X_test_proc = preprocessor.transform(X_test)
    except Exception as e:
        print(f"Transformation Error: {e}")
        # Maybe preprocessor includes OneHotEncoder which needs strings?
        # Proceeding assuming it works as intended in prod.
        return

    # Baseline A: Logistic Regression
    lr = LogisticRegression(class_weight='balanced', max_iter=1000)
    lr.fit(X_train_proc, y_train)
    
    # Baseline B: Raw XGBoost (Uncalibrated)
    xgb = XGBClassifier(use_label_encoder=False, eval_metric='logloss')
    xgb.fit(X_train_proc, y_train)
    
    # 3. Load Production Model
    print("🤖 Loading Production Model...")
    try:
        prod_model = joblib.load(MODEL_PATH)
    except:
        print("❌ Prod model not found.")
        return
        
    # 4. Evaluate All
    models = {
        "Logistic Regression": lr,
        "Uncalibrated XGB": xgb,
        "Production Model": prod_model
    }
    
    results = []
    
    print("\n📊 PERFORMANCE METRICS (Target: Default=1)")
    print(f"{'Model':<25} | {'AUC':<6} | {'Recall':<6} | {'Prec':<6} | {'Brier':<6}")
    print("-" * 65)
    
    for name, model in models.items():
        # Prod model includes pipeline? Or is it just the classifier?
        # Typically joblib saves the Pipeline if standard, or just the Clf.
        # If it's a Pipeline, we pass X_test (raw). If Clf, X_test_proc.
        # Let's try raw first for Prod Model (Pipeline assumption), else Proc.
        
        try:
            if name == "Production Model":
                try:
                    probs = model.predict_proba(X_test)[:, 1]
                    preds = model.predict(X_test)
                except:
                     # Maybe it expects processed data?
                     probs = model.predict_proba(X_test_proc)[:, 1]
                     preds = model.predict(X_test_proc)
            else:
                probs = model.predict_proba(X_test_proc)[:, 1]
                preds = model.predict(X_test_proc)
                
            auc = roc_auc_score(y_test, probs)
            rec = recall_score(y_test, preds)
            prec = precision_score(y_test, preds, zero_division=0)
            brier = brier_score_loss(y_test, probs)
            
            print(f"{name:<25} | {auc:.4f} | {rec:.4f} | {prec:.4f} | {brier:.4f}")
            
            results.append({"name": name, "probs": probs, "y": y_test, "brier": brier})
            
        except Exception as e:
            print(f"{name:<25} | ERROR: {e}")

    # 5. Calibration Curve (Prompt T3)
    print("\n📉 CALIBRATION DIAGNOSTICS")
    for res in results:
        y_true = res['y']
        prob_pred = res['probs']
        name = res['name']
        
        prob_true, prob_pred_binned = calibration_curve(y_true, prob_pred, n_bins=5)
        
        print(f"\n{name} (Brier: {res['brier']:.4f})")
        print("  Mean Predicted Prob | Fraction of Positives (Actual Risk)")
        for p, t in zip(prob_pred_binned, prob_true):
            # ASCII Bar
            bar_len = int(t * 20)
            bar = "█" * bar_len + "░" * (20 - bar_len)
            print(f"  {p:.2f}                | {t:.2f} {bar}")
            
    # Recommendations
    best_model = min(results, key=lambda x: x['brier'])
    print("\n🏆 RESULTS INTERPRETATION")
    print(f"Best Calibrated Model: {best_model['name']}")
    if best_model['name'] == "Production Model":
        print("✅ Production Model is well-calibrated and ready.")
    else:
        print(f"⚠️ Production Model underperforms {best_model['name']} in calibration.")
        print("   Recommendation: Apply Isotonic Regression or Platt Scaling.")

if __name__ == "__main__":
    run_benchmark()

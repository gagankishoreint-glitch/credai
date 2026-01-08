import pandas as pd
import numpy as np
import joblib
from xgboost import XGBClassifier
from sklearn.metrics import classification_report, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import VotingClassifier
from sklearn.calibration import calibration_curve
import json
import matplotlib.pyplot as plt
import numpy as np

def load_and_merge_data():
    # Load core refined data
    df = pd.read_csv("data/refined_credit_data.csv")
    
    # Load document features (if available)
    try:
        doc_df = pd.read_csv("data/document_features.csv")
        # Merge on applicant_id with valid suffixes to avoid collision
        df = df.merge(doc_df, on="applicant_id", how="left", suffixes=("", "_doc"))
        
        # Coalesce columns that might exist in both
        for col in doc_df.columns:
            if col == "applicant_id": continue
            doc_col = f"{col}_doc"
            if doc_col in df.columns:
                if col in df.columns:
                    df[col] = df[col].fillna(df[doc_col])
                else:
                    df[col] = df[doc_col]
                df.drop(columns=[doc_col], inplace=True)

        if "has_financial_stmts" in df.columns:
            df["has_financial_stmts"] = df["has_financial_stmts"].fillna(0)
    except FileNotFoundError:
        print("Warning: data/document_features.csv not found.")
        df["doc_verified_income"] = np.nan
        df["doc_assets_reported"] = np.nan
        df["doc_derived_cashflow"] = np.nan
        df["has_financial_stmts"] = 0
    return df

# Load dataset
df = load_and_merge_data()

# Feature engineering (Must match preprocess.py)
df["income_discrepancy"] = 0.0
mask_docs = df["doc_verified_income"].notna()
df.loc[mask_docs, "income_discrepancy"] = (
    (df.loc[mask_docs, "annual_income"] - df.loc[mask_docs, "doc_verified_income"]).abs() 
    / (df.loc[mask_docs, "annual_income"] + 1)
)

# NEW: Derived Metrics (Sync with preprocess.py)
df["debt_to_assets"] = df["total_debt"] / (df["assets_total"] + 1)
df["payment_to_income"] = df["monthly_debt_obligations"] * 12 / (df["annual_income"] + 1)
df["transaction_success_rate"] = 1.0 - (df["trans_fail_count"] / (df["total_credit_lines"] * 5 + 1))

# NEW: Cashflow Coverage
df["cashflow_coverage"] = 0.0
mask_cf = df["doc_derived_cashflow"].notna()
df.loc[mask_cf, "cashflow_coverage"] = df.loc[mask_cf, "doc_derived_cashflow"] / (df.loc[mask_cf, "monthly_debt_obligations"] + 1)

# Log Transformations (Sync with preprocess.py)
log_cols = ["doc_verified_income", "assets_total", "doc_derived_cashflow"]
for c in log_cols:
    if c in df.columns:
        df[c] = np.log1p(df[c].clip(lower=0))

# Drop unused/ethical/target cols
# Note: we don't strictly need to drop unrelated cols if `preprocessor.transform` selects by name,
# but it's safer to be explicit.
# However, preprocessor was fitted on specific cols. 
# We should just ensure X has the columns the preprocessor expects.
# The preprocessor handles selection.
X = df.drop(columns=["applicant_id", "default_flag", "marital_status", "cnt_children", "annual_income", "total_debt"], errors='ignore')
y = df["default_flag"]

# Load preprocessor
preprocessor = joblib.load("model/preprocessor.joblib")

# Transform data
X_processed = preprocessor.transform(X)

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X_processed, y, test_size=0.2, random_state=42, stratify=y
)

from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import brier_score_loss, precision_score, recall_score, f1_score
import shap
import matplotlib.pyplot as plt

# Handle class imbalance
pos_weight = (y_train == 0).sum() / (y_train == 1).sum()

xgb_model = XGBClassifier(
    n_estimators=200,
    max_depth=4, # Reduced depth for better generalization
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    scale_pos_weight=pos_weight,
    reg_alpha=0.5, # L1 Regularization
    reg_lambda=1.0, # L2 Regularization
    eval_metric="logloss",
    random_state=42
)

# Stronger regularization for LR (C=0.1 instead of 1.0)
lr_model = LogisticRegression(C=0.1, class_weight='balanced', max_iter=1000, random_state=42)

# Voting Ensemble
voting_model = VotingClassifier(
    estimators=[('lr', lr_model), ('xgb', xgb_model)],
    voting='soft',
    weights=[1, 2] # Higher weight to XGBoost as per request
)

# Calibrate probabilities (Isotonic Regression) using robust Cross-Validation
calibrated_model = CalibratedClassifierCV(voting_model, method="isotonic", cv=5)

# Train model
print("Training and Calibrating Ensemble Model (CV=5)...")
calibrated_model.fit(X_train, y_train)

# Predictions
y_pred = calibrated_model.predict(X_test)
y_prob = calibrated_model.predict_proba(X_test)[:, 1]

# --- Trust Metrics ---

# 1. Calibration Curve
prob_true, prob_pred = calibration_curve(y_test, y_prob, n_bins=10)
plt.figure(figsize=(8, 6))
plt.plot(prob_pred, prob_true, marker='o', label='Calibrated Ensemble')
plt.plot([0, 1], [0, 1], linestyle='--', label='Perfectly Calibrated')
plt.xlabel("Mean Predicted Probability")
plt.ylabel("Fraction of Positives")
plt.title("Calibration Curve (Reliability Diagram)")
plt.legend()
plt.savefig("model/calibration_curve.png")
print("Calibration curve saved to model/calibration_curve.png")

# 2. PSI (Drift Detection Example)
def calculate_psi(expected, actual, buckets=10):
    def scale_range(input, min, max):
        input += (1e-6) # Avoid zero
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

# Check drift on 'credit_score' (Raw column 8 in X_processed, checking column index might be risky without names)
# Ideally we check on raw dataframe columns, but splitting was done on processed. 
# We'll just verify drift on the predicted probabilities (Distribution Shift)
psi_score = calculate_psi(calibrated_model.predict_proba(X_train)[:,1], y_prob)
print(f"Prediction PSI (Train vs Test): {psi_score:.4f}")

# Explainability (SHAP)
# Refit XGB standalone for SHAP
explainer_model = xgb_model
explainer_model.fit(X_train, y_train) 

print("Generating SHAP values...")
explainer = shap.TreeExplainer(explainer_model)
shap_values = explainer.shap_values(X_test)

# Save SHAP Artifacts
joblib.dump(explainer, "model/shap_explainer.joblib")
np.save("model/shap_values_test.npy", shap_values)
np.save("model/X_test_processed.npy", X_test) # Save for reporting

# Evaluation
print("\n--- Model Evaluation ---")
print("Classification Report:")
print(classification_report(y_test, y_pred))

roc = roc_auc_score(y_test, y_prob)
brier = brier_score_loss(y_test, y_prob)
print(f"ROC-AUC Score: {roc:.4f}")
print(f"Brier Score:   {brier:.4f}")

# Save metrics
metrics = {
    "roc_auc": roc,
    "brier_score": brier,
    "precision_approve": precision_score(y_test, y_pred, pos_label=0),
    "recall_default": recall_score(y_test, y_pred, pos_label=1),
    "prediction_psi": psi_score
}

with open("model/training_metrics.json", "w") as f:
    json.dump(metrics, f, indent=2)

# Save calibrated model
joblib.dump(calibrated_model, "model/credit_risk_model.joblib") 

print("Model trained, calibrated, and saved successfully!")

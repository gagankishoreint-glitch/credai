import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import joblib

def load_and_merge_data():
    # Load core refined data
    df = pd.read_csv("data/refined_credit_data.csv")
    
    # Load document features (if available)
    try:
        doc_df = pd.read_csv("data/document_features.csv")
        # Merge on applicant_id with valid suffixes to avoid collision
        df = df.merge(doc_df, on="applicant_id", how="left", suffixes=("", "_doc"))
        
        # Coalesce columns that might exist in both (e.g. from feedback loop vs original docs)
        for col in doc_df.columns:
            if col == "applicant_id": continue
            doc_col = f"{col}_doc"
            if doc_col in df.columns:
                # Fill main column NaNs with values from the doc column
                if col in df.columns:
                    df[col] = df[col].fillna(df[doc_col])
                else:
                    # If it wasn't in main df, rename it back
                    df[col] = df[doc_col]
                df.drop(columns=[doc_col], inplace=True)
        
        # Fill missing document features (for applicants who didn't have docs)
        if "has_financial_stmts" in df.columns:
            df["has_financial_stmts"] = df["has_financial_stmts"].fillna(0)
    except FileNotFoundError:
        print("Warning: data/document_features.csv not found. Skipping merge.")
        df["doc_verified_income"] = np.nan
        df["doc_assets_reported"] = np.nan
        df["doc_derived_cashflow"] = np.nan
        df["has_financial_stmts"] = 0
        
    return df

# Load data
df = load_and_merge_data()

# Feature engineering
# Verify income consistency: (Reported Annual - Document Annual) / Reported
df["income_discrepancy"] = 0.0
mask_docs = df["doc_verified_income"].notna()
df.loc[mask_docs, "income_discrepancy"] = (
    (df.loc[mask_docs, "annual_income"] - df.loc[mask_docs, "doc_verified_income"]).abs() 
    / (df.loc[mask_docs, "annual_income"] + 1)
)

# NEW: Derived Metrics for methodology alignment
df["debt_to_assets"] = df["total_debt"] / (df["assets_total"] + 1)
df["payment_to_income"] = df["monthly_debt_obligations"] * 12 / (df["annual_income"] + 1)
df["transaction_success_rate"] = 1.0 - (df["trans_fail_count"] / (df["total_credit_lines"] * 5 + 1)) # Proxy

# APPROVED RATIO: Cashflow Coverage Ratio (CCR)
# doc_derived_cashflow / monthly_debt_obligations
# Handle 0 division and NaNs
df["cashflow_coverage"] = 0.0
mask_cf = df["doc_derived_cashflow"].notna()
df.loc[mask_cf, "cashflow_coverage"] = df.loc[mask_cf, "doc_derived_cashflow"] / (df.loc[mask_cf, "monthly_debt_obligations"] + 1)

# Log Transformations for Power-Law Features
# We do this BEFORE splitting/scaling as it's a monotonic transformation useful for linear stability
log_cols = ["doc_verified_income", "assets_total", "doc_derived_cashflow"]
for c in log_cols:
    if c in df.columns:
        # handle negatives or zeros by using log1p of absolute or clipping? 
        # usually income/assets >= 0.
        df[c] = np.log1p(df[c].clip(lower=0))

# New columns list
categorical_cols = [
    "education_level", "housing_type", "business_type" 
    # REMOVED: marital_status (Ethical)
]

numerical_cols = [
    "age", "employment_years", 
    # REMOVED: cnt_children (Ethical), annual_income (Redundant), total_debt (Redundant)
     "monthly_debt_obligations", 
    "market_risk_index", 
    "credit_score", "total_credit_lines", "utilization_rate", 
    "days_since_last_delinquency", "avg_trans_amount_3m", "trans_fail_count",
    "doc_assets_reported", "doc_verified_income", "doc_derived_cashflow", "income_discrepancy",
    "has_financial_stmts",
    "debt_to_assets", "payment_to_income", "transaction_success_rate",
    "cashflow_coverage" # NEW
]

# Ensure X contains all these columns
# Drop Target and ID. Also drop the Redundant/Ethical cols from X if they exist in df
cols_to_drop = ["applicant_id", "default_flag", "marital_status", "cnt_children", "annual_income", "total_debt"]
X = df.drop(columns=[c for c in cols_to_drop if c in df.columns])

# Double check if any col is missing
missing_cols = [c for c in numerical_cols if c not in X.columns]
if missing_cols:
    print(f"Warning: Missing columns in X: {missing_cols}")
    # Create them with 0s to avoid crash
    for c in missing_cols:
        X[c] = 0.0

y = df["default_flag"]

# Logging statistics for transparency
stats = X[numerical_cols].describe().T.to_dict()
import json
import os
if not os.path.exists("model"): os.makedirs("model")
with open("model/preprocessing_stats.json", "w") as f:
    json.dump(stats, f, indent=2)

# Preprocessing pipelines
# Add imputation because some doc features are NaN
categorical_pipeline = OneHotEncoder(handle_unknown="ignore")

numerical_pipeline = Pipeline([
    ("imputer", SimpleImputer(strategy="median")), 
    ("scaler", StandardScaler())
])

preprocessor = ColumnTransformer(
    transformers=[
        ("cat", categorical_pipeline, categorical_cols),
        ("num", numerical_pipeline, numerical_cols)
    ]
)

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# Fit preprocessor on training data
X_train_processed = preprocessor.fit_transform(X_train)
X_test_processed = preprocessor.transform(X_test)

# Save preprocessor
joblib.dump(preprocessor, "model/preprocessor.joblib")

print("Preprocessing completed successfully!")
print("Train shape:", X_train_processed.shape)
print("Test shape:", X_test_processed.shape)


import pandas as pd
import numpy as np
import joblib
import json
import os
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import accuracy_score, roc_auc_score, classification_report, confusion_matrix
import xgboost as xgb

# Use Agg backend for matplotlib to avoid GUI issues
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def train_and_save_models():
    """
    Trains Logistic Regression and XGBoost models for credit risk scoring.
    Performs calibration and saves artifacts.
    """
    print("Loading dataset...")
    data_path = os.path.join('backend', 'data', 'synthetic_credit_data.csv')
    df = pd.read_csv(data_path)
    
    # Feature Selection
    feature_cols = [
        'years_in_operation', 'promoter_credit_score', 'promoter_exp_years', 'prior_default',
        'annual_revenue', 'gst_turnover', 'ebitda_margin', 'net_margin',
        'total_debt', 'existing_emi', 'loan_amount_requested', 'loan_tenure_months',
        'proposed_emi', 'dscr', 'collateral_value',
        'business_type', 'loan_purpose', 'collateral_type'
    ]
    
    target_col = 'default_flag'
    
    X = df[feature_cols]
    y = df[target_col]
    
    # Split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    # Preprocessing
    numeric_features = [
        'years_in_operation', 'promoter_credit_score', 'promoter_exp_years', 
        'annual_revenue', 'gst_turnover', 'ebitda_margin', 'net_margin',
        'total_debt', 'existing_emi', 'loan_amount_requested', 'loan_tenure_months',
        'proposed_emi', 'dscr', 'collateral_value'
    ]
    categorical_features = ['business_type', 'loan_purpose', 'collateral_type', 'prior_default']
    
    numeric_transformer = StandardScaler()
    categorical_transformer = OneHotEncoder(handle_unknown='ignore', sparse_output=False)
    
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, numeric_features),
            ('cat', categorical_transformer, categorical_features)
        ])
    
    # --- Model 1: Logistic Regression (Baseline, Interpretable) ---
    print("\nTraining Logistic Regression...")
    lr_pipeline = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('classifier', LogisticRegression(random_state=42, max_iter=1000))
    ])
    
    # Calibration for probability accuracy
    lr_calibrated = CalibratedClassifierCV(lr_pipeline, method='sigmoid', cv=5)
    lr_calibrated.fit(X_train, y_train)
    
    # Evaluate
    y_pred_lr = lr_calibrated.predict(X_test)
    y_prob_lr = lr_calibrated.predict_proba(X_test)[:, 1]
    
    auc_lr = roc_auc_score(y_test, y_prob_lr)
    print(f"Logistic Regression AUC: {auc_lr:.4f}")
    
    # --- Model 2: XGBoost (High Performance) ---
    print("\nTraining XGBoost...")
    # XGBoost handles categorical natively somewhat, but pipeline is safer for one-hot consistency
    xgb_model = xgb.XGBClassifier(
        objective='binary:logistic',
        eval_metric='logloss',
        use_label_encoder=False,
        random_state=42,
        max_depth=4,
        n_estimators=100,
        learning_rate=0.1
    )
    
    xgb_pipeline = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('classifier', xgb_model)
    ])
    
    # Calibrating Tree models is crucial
    xgb_calibrated = CalibratedClassifierCV(xgb_pipeline, method='isotonic', cv=5)
    xgb_calibrated.fit(X_train, y_train)
    
    y_pred_xgb = xgb_calibrated.predict(X_test)
    y_prob_xgb = xgb_calibrated.predict_proba(X_test)[:, 1]
    
    auc_xgb = roc_auc_score(y_test, y_prob_xgb)
    print(f"XGBoost AUC: {auc_xgb:.4f}")
    
    # --- Explainability (SHAP preparation) ---
    # We train a standalone XGBoost on transformed data to save for SHAP
    # (CalibratedClassifierCV wraps the model, making SHAP hard to access directly)
    print("\nPreparing Explainability Model...")
    X_train_transformed = preprocessor.fit_transform(X_train)
    feature_names = (
        numeric_features + 
        list(preprocessor.named_transformers_['cat'].get_feature_names_out(categorical_features))
    )
    
    explainer_model = xgb.XGBClassifier(max_depth=4, n_estimators=100, learning_rate=0.1, random_state=42)
    explainer_model.fit(X_train_transformed, y_train)
    
    # --- Fairness Analysis ---
    print("\nSample Fairness Check (Approval Rate by Business Type)...")
    # Let's say we approve if Prob(Default) < 0.10
    threshold = 0.10
    
    test_df = X_test.copy()
    test_df['y_true'] = y_test
    test_df['y_pred_prob'] = y_prob_xgb
    test_df['approved'] = (test_df['y_pred_prob'] < threshold).astype(int)
    
    fairness_metrics = {}
    for b_type in df['business_type'].unique():
        group = test_df[test_df['business_type'] == b_type]
        if len(group) > 0:
            approval_rate = group['approved'].mean()
            fairness_metrics[b_type] = round(approval_rate, 4)
            print(f"Approval Rate for {b_type}: {approval_rate:.2%}")

    # --- Saving Artifacts ---
    output_dir = os.path.join('backend', 'ml_pipeline')
    models_dir = os.path.join(output_dir, 'models')
    os.makedirs(models_dir, exist_ok=True)
    
    artifacts = {
        'model_xgb': xgb_calibrated,
        'model_lr': lr_calibrated,
        'explainer_model': explainer_model, # Uncalibrated, for SHAP
        'preprocessor': preprocessor,
        'feature_names': feature_names
    }
    
    # Save models
    for name, obj in artifacts.items():
        path = os.path.join(models_dir, f'{name}.joblib')
        joblib.dump(obj, path)
        print(f"Saved {name} to {path}")
        
    # Save Metrics
    metrics = {
        'logistic_regression': {
            'auc': auc_lr,
            'accuracy': accuracy_score(y_test, y_pred_lr)
        },
        'xgboost': {
            'auc': auc_xgb,
            'accuracy': accuracy_score(y_test, y_pred_xgb)
        },
        'fairness_approval_rates': fairness_metrics,
        'feature_names': list(feature_names)
    }
    
    with open(os.path.join(output_dir, 'metrics.json'), 'w') as f:
        json.dump(metrics, f, indent=4)
        
    print("\nTraining Pipeline Completed Successfully.")

if __name__ == "__main__":
    train_and_save_models()

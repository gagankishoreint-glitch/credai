"""
Machine Learning Model Training and Evaluation
Trains multiple classification models for credit risk prediction
"""

import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score, GridSearchCV
from sklearn.metrics import (
    classification_report, confusion_matrix, roc_auc_score,
    roc_curve, precision_recall_curve, accuracy_score
)
import xgboost as xgb
import joblib
import matplotlib.pyplot as plt
import seaborn as sns
import os

def load_processed_data():
    """Load preprocessed training and test data"""
    print("Loading preprocessed data...")
    X_train = pd.read_csv('backend/ml_pipeline/data/X_train.csv')
    X_test = pd.read_csv('backend/ml_pipeline/data/X_test.csv')
    y_train = pd.read_csv('backend/ml_pipeline/data/y_train.csv').values.ravel()
    y_test = pd.read_csv('backend/ml_pipeline/data/y_test.csv').values.ravel()
    print(f"✅ Loaded train: {len(X_train)}, test: {len(X_test)}")
    return X_train, X_test, y_train, y_test

def train_logistic_regression(X_train, y_train):
    """Train Logistic Regression model"""
    print("\n" + "="*60)
    print("Training Logistic Regression...")
    print("="*60)
    
    # Hyperparameter tuning
    param_grid = {
        'C': [0.01, 0.1, 1, 10],
        'penalty': ['l2'],
        'solver': ['lbfgs'],
        'max_iter': [1000]
    }
    
    lr = LogisticRegression(random_state=42)
    grid_search = GridSearchCV(lr, param_grid, cv=5, scoring='roc_auc', n_jobs=-1, verbose=1)
    grid_search.fit(X_train, y_train)
    
    print(f"✅ Best parameters: {grid_search.best_params_}")
    print(f"✅ Best cross-validation ROC-AUC: {grid_search.best_score_:.4f}")
    
    return grid_search.best_estimator_

def train_random_forest(X_train, y_train):
    """Train Random Forest model"""
    print("\n" + "="*60)
    print("Training Random Forest...")
    print("="*60)
    
    # Hyperparameter tuning
    param_grid = {
        'n_estimators': [100, 200],
        'max_depth': [10, 20, None],
        'min_samples_split': [2, 5],
        'min_samples_leaf': [1, 2],
        'class_weight': ['balanced']
    }
    
    rf = RandomForestClassifier(random_state=42)
    grid_search = GridSearchCV(rf, param_grid, cv=5, scoring='roc_auc', n_jobs=-1, verbose=1)
    grid_search.fit(X_train, y_train)
    
    print(f"✅ Best parameters: {grid_search.best_params_}")
    print(f"✅ Best cross-validation ROC-AUC: {grid_search.best_score_:.4f}")
    
    return grid_search.best_estimator_

def train_xgboost(X_train, y_train):
    """Train XGBoost model"""
    print("\n" + "="*60)
    print("Training XGBoost...")
    print("="*60)
    
    # Calculate scale_pos_weight for class imbalance
    scale_pos_weight = (y_train == 0).sum() / (y_train == 1).sum()
    
    # Hyperparameter tuning
    param_grid = {
        'max_depth': [3, 5, 7],
        'learning_rate': [0.01, 0.1],
        'n_estimators': [100, 200],
        'scale_pos_weight': [scale_pos_weight],
        'subsample': [0.8, 1.0],
        'colsample_bytree': [0.8, 1.0]
    }
    
    xgb_model = xgb.XGBClassifier(random_state=42, use_label_encoder=False, eval_metric='logloss')
    grid_search = GridSearchCV(xgb_model, param_grid, cv=5, scoring='roc_auc', n_jobs=-1, verbose=1)
    grid_search.fit(X_train, y_train)
    
    print(f"✅ Best parameters: {grid_search.best_params_}")
    print(f"✅ Best cross-validation ROC-AUC: {grid_search.best_score_:.4f}")
    
    return grid_search.best_estimator_

def evaluate_model(model, X_test, y_test, model_name):
    """Evaluate model performance"""
    print(f"\n{'='*60}")
    print(f"Evaluating {model_name}")
    print(f"{'='*60}")
    
    # Predictions
    y_pred = model.predict(X_test)
    y_pred_proba = model.predict_proba(X_test)[:, 1]
    
    # Metrics
    accuracy = accuracy_score(y_test, y_pred)
    roc_auc = roc_auc_score(y_test, y_pred_proba)
    
    print(f"\n📊 Performance Metrics:")
    print(f"   Accuracy: {accuracy:.4f}")
    print(f"   ROC-AUC: {roc_auc:.4f}")
    
    print(f"\n📋 Classification Report:")
    print(classification_report(y_test, y_pred, target_names=['No Default', 'Default']))
    
    print(f"\n📈 Confusion Matrix:")
    cm = confusion_matrix(y_test, y_pred)
    print(cm)
    
    # Calculate additional metrics
    tn, fp, fn, tp = cm.ravel()
    specificity = tn / (tn + fp)
    sensitivity = tp / (tp + fn)
    
    print(f"\n   Sensitivity (Recall): {sensitivity:.4f}")
    print(f"   Specificity: {specificity:.4f}")
    
    return {
        'model_name': model_name,
        'accuracy': accuracy,
        'roc_auc': roc_auc,
        'confusion_matrix': cm,
        'y_pred': y_pred,
        'y_pred_proba': y_pred_proba
    }

def compare_models(results):
    """Compare model performance"""
    print("\n" + "="*60)
    print("MODEL COMPARISON")
    print("="*60)
    
    comparison_df = pd.DataFrame({
        'Model': [r['model_name'] for r in results],
        'Accuracy': [r['accuracy'] for r in results],
        'ROC-AUC': [r['roc_auc'] for r in results]
    })
    
    comparison_df = comparison_df.sort_values('ROC-AUC', ascending=False)
    print(comparison_df.to_string(index=False))
    
    best_model_name = comparison_df.iloc[0]['Model']
    print(f"\n🏆 Best Model: {best_model_name}")
    
    return best_model_name

def plot_feature_importance(model, feature_cols, model_name, output_dir='backend/ml_pipeline/models'):
    """Plot feature importance"""
    os.makedirs(output_dir, exist_ok=True)
    
    if hasattr(model, 'feature_importances_'):
        importance_df = pd.DataFrame({
            'feature': feature_cols,
            'importance': model.feature_importances_
        }).sort_values('importance', ascending=False).head(15)
        
        plt.figure(figsize=(10, 6))
        sns.barplot(data=importance_df, x='importance', y='feature')
        plt.title(f'Top 15 Feature Importance - {model_name}')
        plt.xlabel('Importance')
        plt.tight_layout()
        plt.savefig(f'{output_dir}/feature_importance_{model_name.replace(" ", "_").lower()}.png', dpi=300)
        plt.close()
        print(f"✅ Saved feature importance plot")

def main_training_pipeline():
    """Main training pipeline"""
    print("\n" + "="*60)
    print("CREDIT RISK MODEL TRAINING PIPELINE")
    print("="*60)
    
    # Load data
    X_train, X_test, y_train, y_test = load_processed_data()
    
    # Load feature columns
    feature_cols = joblib.load('backend/ml_pipeline/models/feature_columns.pkl')
    
    # Train models
    lr_model = train_logistic_regression(X_train, y_train)
    rf_model = train_random_forest(X_train, y_train)
    xgb_model = train_xgboost(X_train, y_train)
    
    # Evaluate models
    lr_results = evaluate_model(lr_model, X_test, y_test, "Logistic Regression")
    rf_results = evaluate_model(rf_model, X_test, y_test, "Random Forest")
    xgb_results = evaluate_model(xgb_model, X_test, y_test, "XGBoost")
    
    results = [lr_results, rf_results, xgb_results]
    
    # Compare models
    best_model_name = compare_models(results)
    
    # Select best model
    models = {
        "Logistic Regression": lr_model,
        "Random Forest": rf_model,
        "XGBoost": xgb_model
    }
    best_model = models[best_model_name]
    
    # Save best model
    output_dir = 'backend/ml_pipeline/models'
    os.makedirs(output_dir, exist_ok=True)
    joblib.dump(best_model, f'{output_dir}/best_model.pkl')
    joblib.dump({'name': best_model_name}, f'{output_dir}/best_model_info.pkl')
    print(f"\n✅ Best model saved: {best_model_name}")
    
    # Plot feature importance for best model
    plot_feature_importance(best_model, feature_cols, best_model_name)
    
    # Save all models for comparison
    joblib.dump(lr_model, f'{output_dir}/logistic_regression.pkl')
    joblib.dump(rf_model, f'{output_dir}/random_forest.pkl')
    joblib.dump(xgb_model, f'{output_dir}/xgboost.pkl')
    
    print("\n" + "="*60)
    print("✨ TRAINING COMPLETE!")
    print("="*60)

if __name__ == "__main__":
    main_training_pipeline()

"""
Model Explainability using SHAP
Generates feature importance explanations for predictions
"""

import shap
import joblib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

def load_model_and_data():
    """Load trained model and test data"""
    print("Loading model and data...")
    model = joblib.load('backend/ml_pipeline/models/best_model.pkl')
    X_test = pd.read_csv('backend/ml_pipeline/data/X_test.csv')
    feature_cols = joblib.load('backend/ml_pipeline/models/feature_columns.pkl')
    print(f"✅ Loaded model and {len(X_test)} test samples")
    return model, X_test, feature_cols

def generate_shap_values(model, X_data, sample_size=100):
    """Generate SHAP values for model explanations"""
    print(f"\nGenerating SHAP values for {sample_size} samples...")
    
    # Take a sample for faster computation
    X_sample = X_data.sample(min(sample_size, len(X_data)), random_state=42)
    
    # Create explainer based on model type
    model_type = type(model).__name__
    
    if 'XGB' in model_type:
        explainer = shap.TreeExplainer(model)
    elif 'RandomForest' in model_type:
        explainer = shap.TreeExplainer(model)
    else:  # Logistic Regression
        explainer = shap.LinearExplainer(model, X_sample)
    
    shap_values = explainer.shap_values(X_sample)
    
    print("✅ SHAP values generated")
    return explainer, shap_values, X_sample

def plot_shap_summary(shap_values, X_sample, output_dir='backend/ml_pipeline/models'):
    """Create SHAP summary plot"""
    os.makedirs(output_dir, exist_ok=True)
    
    plt.figure(figsize=(10, 8))
    shap.summary_plot(shap_values, X_sample, show=False)
    plt.tight_layout()
    plt.savefig(f'{output_dir}/shap_summary_plot.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✅ SHAP summary plot saved")

def get_global_feature_importance(shap_values, feature_cols):
    """Calculate global feature importance from SHAP values"""
    # Handle both 2D and 3D SHAP values arrays
    if isinstance(shap_values, list):
        shap_values = shap_values[1]  # For binary classification, take positive class
    
    if len(shap_values.shape) == 3:
        shap_values = shap_values[:, :, 1]  # Take positive class
    
    # Calculate mean absolute SHAP values
    feature_importance = np.abs(shap_values).mean(axis=0)
    
    importance_df = pd.DataFrame({
        'feature': feature_cols,
        'importance': feature_importance
    }).sort_values('importance', ascending=False)
    
    return importance_df

def explain_single_prediction(model, explainer, X_sample, idx=0):
    """Explain a single prediction"""
    print(f"\nExplaining prediction for sample {idx}...")
    
    # Get single sample
    sample = X_sample.iloc[[idx]]
    
    # Get prediction
    prediction = model.predict(sample)[0]
    probability = model.predict_proba(sample)[0]
    
    # Get SHAP values for this sample
    shap_value = explainer.shap_values(sample)
    
    print(f"   Prediction: {'Default' if prediction == 1 else 'No Default'}")
    print(f"   Probability: {probability[1]:.4f}")
    
    return {
        'prediction': int(prediction),
        'probability': float(probability[1]),
        'shap_values': shap_value
    }

def save_global_importance(importance_df, output_dir='backend/ml_pipeline/models'):
    """Save global feature importance"""
    os.makedirs(output_dir, exist_ok=True)
    
    importance_df.to_csv(f'{output_dir}/global_feature_importance.csv', index=False)
    print(f"✅ Global feature importance saved")
    
    # Plot top features
    plt.figure(figsize=(10, 6))
    top_features = importance_df.head(15)
    plt.barh(range(len(top_features)), top_features['importance'])
    plt.yticks(range(len(top_features)), top_features['feature'])
    plt.xlabel('Mean |SHAP value|')
    plt.title('Top 15 Most Important Features (SHAP)')
    plt.gca().invert_yaxis()
    plt.tight_layout()
    plt.savefig(f'{output_dir}/top_features_shap.png', dpi=300)
    plt.close()
    print("✅ Feature importance plot saved")

def main_explainability_pipeline():
    """Main explainability pipeline"""
    print("="*60)
    print("MODEL EXPLAINABILITY PIPELINE (SHAP)")
    print("="*60)
    
    # Load model and data
    model, X_test, feature_cols = load_model_and_data()
    
    # Generate SHAP values
    explainer, shap_values, X_sample = generate_shap_values(model, X_test, sample_size=200)
    
    # Plot SHAP summary
    plot_shap_summary(shap_values, X_sample)
    
    # Get global feature importance
    importance_df = get_global_feature_importance(shap_values, feature_cols)
    print("\n📊 Top 10 Most Important Features:")
    print(importance_df.head(10).to_string(index=False))
    
    # Save importance
    save_global_importance(importance_df)
    
    # Save explainer for API use
    joblib.dump(explainer, 'backend/ml_pipeline/models/shap_explainer.pkl')
    print("\n✅ SHAP explainer saved for API use")
    
    # Example: Explain a few predictions
    print("\n" + "="*60)
    print("EXAMPLE PREDICTIONS")
    print("="*60)
    for i in range(min(3, len(X_sample))):
        explain_single_prediction(model, explainer, X_sample, idx=i)
    
    print("\n" + "="*60)
    print("✨ EXPLAINABILITY ANALYSIS COMPLETE!")
    print("="*60)

if __name__ == "__main__":
    main_explainability_pipeline()

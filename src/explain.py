import pandas as pd
import shap
import joblib

# Load data
df = pd.read_csv("data/business_credit_data.csv")

X = df.drop(columns=["applicant_id", "default_flag"])

# Load preprocessor and model
preprocessor = joblib.load("model/preprocessor.joblib")
model = joblib.load("model/credit_risk_model.joblib")

# Transform features
X_processed = preprocessor.transform(X)

# SHAP explainer
explainer = shap.TreeExplainer(model)
shap_values = explainer.shap_values(X_processed)

# Global explanation
shap.summary_plot(shap_values, X_processed, show=False)

print("SHAP explanation generated successfully!")

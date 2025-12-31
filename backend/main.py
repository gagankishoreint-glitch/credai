from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import pandas as pd
import numpy as np
from fastapi.middleware.cors import CORSMiddleware

# Initialize App
app = FastAPI(title="Credit Evaluation API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load Artifacts
try:
    model = joblib.load('model.pkl')
    model_features = joblib.load('model_features.pkl')
    print("Model loaded successfully.")
except:
    print("Model not found. Please run train_model.py")
    model = None

# Input Schema
class ApplicationData(BaseModel):
    years_in_operation: int
    annual_revenue: float
    operating_expenses: float
    loan_amount: float
    loan_term_months: int
    promoter_credit_score: int
    existing_debt: float = 0.0

@app.get("/")
def home():
    return {"message": "Credit Evaluation API is Running"}

@app.post("/predict")
def predict_credit_risk(data: ApplicationData):
    if not model:
        raise HTTPException(status_code=500, detail="Model not initialized")

    # Preprocess
    # Calculate derived features used in training (if any)
    # Note: Our simple training used raw inputs + EBITDA derived in data_gen but not passed explicitly? 
    # Wait, in data_gen we had 'ebitda' in the CSV. The input form sends 'operating_expenses', so we must calculate 'ebitda'.
    
    ebitda = data.annual_revenue - data.operating_expenses
    
    input_dict = {
        'years_in_operation': data.years_in_operation,
        'annual_revenue': data.annual_revenue,
        'ebitda': ebitda,
        'loan_amount': data.loan_amount,
        'loan_term_months': data.loan_term_months,
        'promoter_credit_score': data.promoter_credit_score,
        'existing_debt': data.existing_debt
    }
    
    # Create DataFrame with correct feature order
    input_df = pd.DataFrame([input_dict])
    
    # Ensure columns match training
    try:
        input_df = input_df[model_features]
    except KeyError as e:
        return {"error": f"Missing features: {e}"}

    # Predict
    prob = model.predict_proba(input_df)[0][1] # Probability of Default (1)
    
    # Convert to Credit Score (300-900)
    # Prob 0 (Low Risk) -> 900
    # Prob 1 (High Risk) -> 300
    score = 900 - (prob * 600)
    
    risk_level = "Low"
    if prob > 0.3: risk_level = "Medium"
    if prob > 0.7: risk_level = "High"

    return {
        "status": "success",
        "probability_of_default": float(prob),
        "credit_score": int(score),
        "risk_level": risk_level,
        "features_used": input_dict
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

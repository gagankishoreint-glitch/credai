import joblib
import pandas as pd
import numpy as np

# Load model and preprocessor
model = joblib.load("model/credit_risk_model.joblib")
preprocessor = joblib.load("model/preprocessor.joblib")

def credit_decision(applicant_data: dict):
    """
    applicant_data: dictionary of applicant features
    """

    df = pd.DataFrame([applicant_data])
    X = preprocessor.transform(df)

    # Predict probability of default
    pd_default = model.predict_proba(X)[0][1]

    # Risk band logic
    if pd_default < 0.30:
        decision = "APPROVE"
        risk_band = "LOW"
    elif pd_default < 0.60:
        decision = "MANUAL_REVIEW"
        risk_band = "MEDIUM"
    else:
        decision = "REJECT"
        risk_band = "HIGH"

    # Confidence score (distance from threshold)
    confidence = max(
        abs(pd_default - 0.30),
        abs(pd_default - 0.60)
    )

    confidence = round(confidence * 100, 2)

    return {
        "probability_of_default": round(pd_default, 3),
        "risk_band": risk_band,
        "decision": decision,
        "confidence_score": confidence
    }

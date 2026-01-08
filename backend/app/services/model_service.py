import joblib
import pandas as pd
import numpy as np
from app.core.config import settings
import os

class ModelService:
    def __init__(self):
        self.model = None
        self.preprocessor = None
        self.calibrator = None
        self._load_model()

    def _load_model(self):
        print(f"Loading model from {settings.MODEL_PATH}...")
        try:
            self.model = joblib.load(settings.MODEL_PATH)
            self.preprocessor = joblib.load(settings.PREPROCESSOR_PATH)
            
            # Load isotonic calibrator if available
            calibrator_path = os.path.join(os.path.dirname(settings.MODEL_PATH), 'isotonic_calibrator.joblib')
            if os.path.exists(calibrator_path):
                self.calibrator = joblib.load(calibrator_path)
                print("✓ Isotonic calibrator loaded successfully.")
            else:
                print("⚠ Isotonic calibrator not found - using uncalibrated predictions")
                self.calibrator = None
            
            print("Model loaded successfully.")
        except Exception as e:
            print(f"FATAL: Failed to load model. {e}")
            raise e

    def predict_probability(self, input_data: dict) -> float:
        """
        Predicts Probability of Default (PD) with stability enhancements.
        Input: Dict of raw features.
        Output: Dict with calibrated PD, confidence, and version
        """
        # 1. Input Validation and Clipping (Stability Fix #1)
        input_data = self._validate_and_clip_inputs(input_data.copy())
        
        # 2. Convert to DataFrame
        df = pd.DataFrame([input_data])
        
        # 3. Feature Engineering / Derivation
        defaults = {
            "education_level": "Secondary",
            "marital_status": "Single",
            "housing_type": "Rented apartment",
            "cnt_children": 0,
            "employment_years": 0.0,
            "has_financial_stmts": 0,
            "days_since_last_delinquency": -1,
            "total_credit_lines": 1,
            "avg_trans_amount_3m": 0.0,
            "trans_fail_count": 0,
            "business_type": "Other"
        }
        
        for col, val in defaults.items():
            if col not in df.columns:
                df[col] = val
                
        # Derived Ratios (if not provided)
        if "debt_to_assets" not in df.columns:
             df["debt_to_assets"] = df.get("total_debt", 0) / (df.get("assets_total", 1) + 1)
             
        if "transaction_success_rate" not in df.columns:
             fails = df.get("trans_fail_count", 0)
             total = df.get("total_credit_lines", 1) * 5
             df["transaction_success_rate"] = 1.0 - (fails / (total + 1))
             
        if "doc_assets_reported" not in df.columns:
            df["doc_assets_reported"] = df.get("assets_total", 0)
            
        if "trans_fail_count" not in df.columns:
            df["trans_fail_count"] = 0
            
        # Log Transforms
        for c in ["doc_verified_income", "doc_assets_reported", "doc_derived_cashflow"]:
            if c in df.columns:
                 df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)
                 df[c] = np.log1p(df[c])
        
        # 4. Transform via Pipeline
        model_cols = [
             "education_level", "housing_type", "business_type",
             "age", "employment_years", "monthly_debt_obligations", "market_risk_index", 
             "credit_score", "total_credit_lines", "utilization_rate", 
             "days_since_last_delinquency", "avg_trans_amount_3m", "trans_fail_count",
             "doc_assets_reported", "doc_verified_income", "doc_derived_cashflow", 
             "income_discrepancy", "has_financial_stmts",
             "debt_to_assets", "payment_to_income", "transaction_success_rate", 
             "cashflow_coverage"
        ]
        
        for col in model_cols:
            if col not in df.columns:
                df[col] = 0
                
        try:
            X_input = df[model_cols]
            X_processed = self.preprocessor.transform(X_input)
            
            # Predict
            prob_calibrated = float(self.model.predict_proba(X_processed)[0, 1])
            
            # Apply isotonic calibration if available (Calibration Fix #3)
            if self.calibrator is not None:
                prob_calibrated = float(self.calibrator.transform([prob_calibrated])[0])
            
            # Stability Fix #2: Calibration Adjustment for Excellent Applicants
            prob_calibrated = self._apply_calibration_adjustment(prob_calibrated, input_data)
            
            prob_raw = prob_calibrated
            
            # Statistical Confidence
            stat_conf = max(prob_calibrated, 1.0 - prob_calibrated)

            return {
                "model_version": "ensemble_v1.0_calibrated" if self.calibrator else "ensemble_v1.0_stable",
                "raw_pd": prob_raw,
                "calibrated_pd": prob_calibrated,
                "confidence_score": stat_conf
            }
        except Exception as e:
            print(f"Prediction Error: {e}")
            raise e
    
    def _validate_and_clip_inputs(self, data: dict) -> dict:
        """
        Stability Fix #1: Validate and clip inputs to reasonable ranges
        """
        # Credit score: 300-850
        if 'credit_score' in data:
            data['credit_score'] = np.clip(data['credit_score'], 300, 850)
        
        # Annual income: $10K-$500K
        if 'annual_income' in data:
            data['annual_income'] = np.clip(data['annual_income'], 10000, 500000)
        
        # Age: 18-80
        if 'age' in data:
            data['age'] = np.clip(data['age'], 18, 80)
        
        # Credit utilization: 0-1.0 (0-100%)
        if 'credit_utilization' in data:
            data['credit_utilization'] = np.clip(data['credit_utilization'], 0.0, 1.0)
        
        # Total debt: $0-$200K
        if 'total_debt' in data:
            data['total_debt'] = np.clip(data['total_debt'], 0, 200000)
        
        # Delinquency count: 0-10
        if 'delinquency_count' in data:
            data['delinquency_count'] = np.clip(data['delinquency_count'], 0, 10)
        
        return data
    
    def _apply_calibration_adjustment(self, pd: float, input_data: dict) -> float:
        """
        Stability Fix #2: Adjust calibration for excellent applicants
        Reduces over-conservatism for low-risk profiles
        """
        # Check if applicant is "excellent"
        is_excellent = (
            input_data.get('credit_score', 0) >= 780 and
            input_data.get('total_debt', float('inf')) <= 20000 and
            input_data.get('annual_income', 0) >= 100000 and
            input_data.get('delinquency_count', 10) == 0
        )
        
        if is_excellent and pd < 0.15:
            # Reduce PD by 40% for excellent applicants
            pd = pd * 0.60
        elif pd < 0.10:
            # Reduce PD by 30% for very low risk predictions
            pd = pd * 0.70
        
        # Ensure PD stays in valid range
        return np.clip(pd, 0.001, 0.999)


# Singleton Instance
model_service = ModelService()

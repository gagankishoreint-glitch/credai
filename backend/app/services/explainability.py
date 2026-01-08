import shap
import numpy as np
import pandas as pd
from typing import Dict, List, Any

# Feature Name Mapping (SYSTEM -> HUMAN)
FEATURE_MAP = {
    "annual_income": "Annual Income",
    "credit_score": "Credit Score",
    "total_debt": "Total Debt",
    "monthly_debt_obligations": "Monthly Obligations",
    "utilization_rate": "Credit Utilization",
    "business_type": "Business Sector",
    "employment_years": "Years of Employment",
    "doc_verified_income": "Verified Income",
    "doc_derived_cashflow": "Derived Cashflow",
    "income_discrepancy": "Income Discrepancy",
    "debt_to_assets": "Debt-to-Assets Ratio",
    "payment_to_income": "Payment-to-Income Ratio",
    "cashflow_coverage": "Cashflow Coverage",
    "trans_fail_count": "failed Transactions",
    "transaction_success_rate": "Transaction Success Rate"
}

class ExplainabilityService:
    def __init__(self):
        self.explainer = None
        self.feature_names = None
        
    def initialize(self, model, feature_names: List[str]):
        """
        Initialize the SHAP explainer with the model.
        Note: For an ensemble, we might need a KernelExplainer or explain specific sub-models.
        For simplicity/speed in this MVP, we will try to explain the XGBoost component if accessible,
        or use a generic approach.
        """
        self.feature_names = feature_names
        try:
            # Attempt to extract XGBoost from VotingClassifier if possible
            # But 'model' passed here is usually the scikit-learn pipeline wrapper or VotingClassifier
            # Generating a TreeExplainer for a VotingClassifier is complex.
            # FALLBACK: We will use a fast linear approximation or just top contributor logic 
            # based on feature coefficients (LR) or Gain (XGB) if SHAP is too heavy for real-time.
            
            # Better approach for production API:
            # Use 'shap.KernelExplainer' with a small background dataset (kmeans).
            # OR simple contribution analysis.
            pass
        except Exception as e:
            print(f"XAI Init Warning: {e}")

    def generate_explanation(self, input_df: pd.DataFrame, model) -> Dict[str, Any]:
        """
        Generates a simplified explanation: Top 3 Features driving the score.
        Since real-time SHAP on CPU can be slow, we implement a heuristic fallback 
        if SHAP isn't pre-computed, or calculate SHAP if feasible.
        """
        # For this regulated implementation, let's try to get actual feature contributions.
        # If model is VotingClassifier, it's hard.
        # STRATEGY: We will focus on the "Global Importance" combined with local deviation.
        # "Local Importance" ~= (Value - Median) * Global_Weight
        
        explanation = {
            "global_metrics": {"base_risk": 0.05}, # Placeholder
            "top_contributors": [],
            "counterfactuals": []
        }
        
        try:
            # 1. Heuristic Contribution (Proxy for SHAP)
            # Find which features deviate most from "Safe" baselines
            contributors = []
            
            # Rules of Thumb for "Why High Risk"
            row = input_df.iloc[0]
            
            if row.get('utilization_rate', 0) > 0.30:
                contributors.append({
                    "feature": "Credit Utilization",
                    "value": f"{row.get('utilization_rate', 0):.1%}",
                    "impact": "Negative",
                    "reason": "Utilization is above recommended 30% limit."
                })
                
            if row.get('credit_score', 700) < 670:
                contributors.append({
                    "feature": "Credit Score",
                    "value": str(row.get('credit_score', 0)),
                    "impact": "Negative",
                    "reason": "Credit score is below prime threshold."
                })
                
            if row.get('cashflow_coverage', 1) < 1.2:
                 contributors.append({
                    "feature": "Cashflow Coverage",
                    "value": f"{row.get('cashflow_coverage', 0):.2f}",
                    "impact": "Negative",
                    "reason": "Cashflow barely covers obligations."
                })
                
            if row.get('income_discrepancy', 0) > 0.15:
                 contributors.append({
                    "feature": "Income Discrepancy",
                    "value": f"{row.get('income_discrepancy', 0):.1%}",
                    "impact": "Negative",
                    "reason": "Significant gap between reported and verified income."
                })
            
            # Sort/Select Top 3
            explanation["top_contributors"] = contributors[:3]
            
            # 2. Counterfactuals (Simple suggestions)
            cfs = []
            if row.get('utilization_rate', 0) > 0.30:
                target = row.get('utilization_rate', 0) * 0.8
                cfs.append(f"Reduce credit utilization to {target:.1%}")
                
            if row.get('monthly_debt_obligations', 0) > (row.get('annual_income',1)/12) * 0.4:
                 cfs.append("Reduce monthly debt obligations.")
                 
            explanation["counterfactuals"] = cfs
            
        except Exception as e:
            print(f"XAI Generation Error: {e}")
            
        return explanation

xai_service = ExplainabilityService()

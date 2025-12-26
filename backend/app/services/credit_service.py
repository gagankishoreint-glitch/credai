"""
Credit evaluation service - Core business logic
"""

import joblib
import pandas as pd
import numpy as np
import json
from typing import Dict, List, Tuple
import os

class CreditEvaluationService:
    def __init__(self):
        self.model = None
        self.scaler = None
        self.encoders = None
        self.feature_cols = None
        self.model_info = None
        self.load_model_artifacts()
    
    def load_model_artifacts(self):
        """Load trained model and preprocessing artifacts"""
        models_dir = 'backend/ml_pipeline/models'
        
        try:
            self.model = joblib.load(f'{models_dir}/best_model.pkl')
            self.scaler = joblib.load(f'{models_dir}/scaler.pkl')
            self.encoders = joblib.load(f'{models_dir}/label_encoders.pkl')
            self.feature_cols = joblib.load(f'{models_dir}/feature_columns.pkl')
            self.model_info = joblib.load(f'{models_dir}/best_model_info.pkl')
            print(f"✅ Model loaded: {self.model_info['name']}")
        except Exception as e:
            print(f"⚠️ Warning: Could not load model artifacts: {e}")
            print("   Run ML training pipeline first")
    
    def preprocess_application(self, application_data: Dict) -> pd.DataFrame:
        """Preprocess application data for model prediction"""
        # Create DataFrame
        df = pd.DataFrame([application_data])
        
        # Engineer features (same as training)
        df['loan_to_revenue_ratio'] = df['loan_amount_requested'] / df['annual_revenue']
        df['cashflow_adequacy'] = (df['monthly_cashflow'] * 12) / df['loan_amount_requested']
        df['collateral_coverage'] = df['collateral_value'] / df['loan_amount_requested']
        
        # Create categorical features
        df['credit_score_category'] = pd.cut(df['credit_score'], 
                                              bins=[0, 580, 670, 740, 900],
                                              labels=['Poor', 'Fair', 'Good', 'Excellent'])
        
        df['business_maturity'] = pd.cut(df['years_in_operation'],
                                          bins=[-1, 2, 5, 10, 100],
                                          labels=['Startup', 'Young', 'Established', 'Mature'])
        
        # Encode categorical variables
        categorical_cols = ['business_type', 'repayment_history', 'credit_score_category', 'business_maturity']
        for col in categorical_cols:
            if col in self.encoders:
                df[f'{col}_encoded'] = self.encoders[col].transform(df[col])
        
        # Scale numerical features
        cols_to_scale = [col for col in df.columns if col in self.feature_cols]
        scaled_df = df[cols_to_scale].copy()
        
        # Only scale columns that were scaled during training
        for col in cols_to_scale:
            if col.endswith('_encoded'):
                continue  # Don't scale encoded columns
            if col in df.columns:
                scaled_df[col] = self.scaler.transform(df[[col]])
        
        # Return only feature columns in correct order
        return scaled_df[self.feature_cols]
    
    def calculate_risk_score(self, probability: float) -> float:
        """Convert default probability to risk score (0-100)"""
        # Higher probability = higher risk score
        return round(probability * 100, 2)
    
    def generate_recommendation(self, risk_score: float, confidence: float) -> str:
        """Generate recommendation based on risk score and confidence"""
        if risk_score < 20 and confidence > 0.7:
            return "approve"
        elif risk_score > 50 or confidence < 0.5:
            return "reject"
        else:
            return "review"
    
    def get_feature_importance(self, X: pd.DataFrame) -> List[Dict]:
        """Get top feature importances for the prediction"""
        if hasattr(self.model, 'feature_importances_'):
            # Tree-based models
            importance = self.model.feature_importances_
        elif hasattr(self.model, 'coef_'):
            # Linear models
            importance = np.abs(self.model.coef_[0])
        else:
            return []
        
        # Get feature values
        feature_values = X.iloc[0].values
        
        # Create importance list
        feature_importance = [
            {
                'feature': self.feature_cols[i],
                'importance': float(importance[i]),
                'value': float(feature_values[i])
            }
            for i in range(len(self.feature_cols))
        ]
        
        # Sort by importance and return top 10
        feature_importance.sort(key=lambda x: x['importance'], reverse=True)
        return feature_importance[:10]
    
    def evaluate_application(self, application_data: Dict) -> Dict:
        """Main evaluation function"""
        if self.model is None:
            raise ValueError("Model not loaded. Run training pipeline first.")
        
        # Preprocess data
        X = self.preprocess_application(application_data)
        
        # Get prediction
        prediction = self.model.predict(X)[0]
        probabilities = self.model.predict_proba(X)[0]
        default_probability = probabilities[1]
        
        # Calculate risk score
        risk_score = self.calculate_risk_score(default_probability)
        
        # Calculate confidence (difference between class probabilities)
        confidence = float(abs(probabilities[1] - probabilities[0]))
        
        # Generate recommendation
        recommendation = self.generate_recommendation(risk_score, confidence)
        
        # Get feature importance
        top_features = self.get_feature_importance(X)
        
        return {
            'risk_score': risk_score,
            'default_probability': float(default_probability),
            'recommendation': recommendation,
            'confidence_score': confidence,
            'model_version': self.model_info['name'],
            'feature_importance': json.dumps(top_features)
        }

# Global service instance
credit_service = CreditEvaluationService()

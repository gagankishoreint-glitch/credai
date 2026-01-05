import numpy as np
from sklearn.linear_model import LogisticRegression
import pandas as pd
import pickle
import os

class CreditScoringModel:
    def __init__(self):
        self.model = LogisticRegression()
        self.is_trained = False
        # Initialize with some dummy training data to ensure it works immediately
        self._train_dummy_model()

    def _train_dummy_model(self):
        try:
            # Load Synthetic Data if exists
            data_path = os.path.join(os.path.dirname(__file__), 'synthetic_training_data.csv')
            
            if os.path.exists(data_path):
                print(f"Loading training data from {data_path}...")
                df = pd.read_csv(data_path)
                
                # Preprocess Training Data
                X = []
                y = []
                
                for _, row in df.iterrows():
                    # Construct feature vector matching preprocess()
                    # We pass the row as a dict to reuse the exact logic
                    feats = self.preprocess(row.to_dict())
                    X.append(feats[0])
                    # Target: 0 = Good (Approve), 1 = Default (Reject). 
                    # Our model expects 1 = Approve. So we invert the label.
                    y.append(1 if row['loan_default'] == 0 else 0)
                
                self.model.fit(X, y)
                self.is_trained = True
                print(f"Model trained on {len(df)} records.")
                
            else:
                print("Warning: Training data not found. Using fallback dummy data.")
                # Fallback: Synthetic data: [NormRevenue, NormYears, NormCreditScore, NormProfitMargin, NormLoanToRev]
                X_train = np.array([
                    [0.8, 0.9, 0.9, 0.4, 0.2], # Good Application
                    [0.2, 0.1, 0.4, -0.1, 0.8], # Bad Application
                    [0.6, 0.5, 0.7, 0.2, 0.4], # Average
                    [0.9, 0.8, 0.8, 0.5, 0.1], # Good
                    [0.1, 0.2, 0.3, -0.2, 0.9]  # Bad
                ])
                y_train = np.array([1, 0, 1, 1, 0]) # 1 = Approve, 0 = Reject
                
                self.model.fit(X_train, y_train)
                self.is_trained = True
                
        except Exception as e:
            print(f"Error training model: {e}")
            self.is_trained = False

    def preprocess(self, data):
        """
        Clean and normalize input data
        """
        try:
            annual_revenue = float(data.get('annualRevenue', 0))
            operating_expenses = float(data.get('operatingExpenses', 0))
            loan_amount = float(data.get('loanAmount', 0))
            years_in_business = int(data.get('yearsInBusiness', 0))
            credit_score = int(data.get('creditScore', 650))

            # Feature Engineering
            annual_expenses = operating_expenses * 12
            net_income = annual_revenue - annual_expenses
            revenue = max(annual_revenue, 1) # Avoid div/0
            
            profit_margin = net_income / revenue
            loan_to_revenue = loan_amount / revenue

            # Normalization (Min-Max Scaling based on assumptions)
            def normalize(val, min_val, max_val):
                return max(0, min(1, (val - min_val) / (max_val - min_val)))

            features = [
                normalize(annual_revenue, 0, 5000000),      # NormRevenue
                normalize(years_in_business, 0, 20),        # NormYears
                normalize(credit_score, 300, 850),          # NormCreditScore
                normalize(profit_margin, -0.5, 0.5),        # NormProfitMargin
                1 - normalize(loan_to_revenue, 0, 2)        # NormLoanToRev (inverted)
            ]
            
            return np.array([features])
        except Exception as e:
            print(f"Preprocessing error: {e}")
            return np.zeros((1, 5))

    def predict(self, data):
        features = self.preprocess(data)
        
        # Get probability of class 1 (Approval)
        probability = self.model.predict_proba(features)[0][1]
        
        # Confidence: Distance from 0.5
        confidence = abs(probability - 0.5) * 2
        
        # Mapping to Credit Score (300-850)
        credit_score = int(300 + (probability * 550))
        
        return {
            "probability": float(probability),
            "confidence": float(confidence),
            "credit_score": credit_score
        }

# Singleton instance
ml_service = CreditScoringModel()

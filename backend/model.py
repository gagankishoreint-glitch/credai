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
                    feats = self.preprocess(row.to_dict())
                    X.append(feats[0])
                    # Target: 0 = Repaid (Good), 1 = Default (Bad).
                    # Model expects: 1 = Approve (Good), 0 = Reject (Bad).
                    # So we INVERT the target.
                    y.append(0 if row['target'] == 1 else 1)
                
                self.model.fit(X, y)
                self.is_trained = True
                print(f"Model trained on {len(df)} records with Unified Schema.")
                
            else:
                print("Warning: Training data not found. Using fallback.")
                # Basic fallback
                self.model.fit([[0]*18, [1]*18], [0, 1])
                self.is_trained = True
                
        except Exception as e:
            print(f"Error training model: {e}")
            self.is_trained = False

    def preprocess(self, data):
        """
        Features (Unified Schema - 18 features): 
        [
            NormIncome, NormCredit, NormAnnuity, NormGoodsPrice,
            NormDaysEmployed, NormFICO, NormDTI, Term_60,
            Grade_A, Grade_B, Grade_C, Grade_D, Grade_E, Grade_F,
            Type_Cash, Type_Revolving,
            Ownership_Own, Ownership_Rent
        ]
        """
        try:
            # 1. Parse Unified Inputs (Lending Club / Home Credit keys)
            # Map legacy keys if present (for backward compat during migration)
            income = float(data.get('amt_income_total') or data.get('annualRevenue', 0))
            credit = float(data.get('amt_credit') or data.get('loanAmount', 0))
            annuity = float(data.get('amt_annuity') or data.get('monthly_cashflow', 0)) # Rough proxy
            goods_price = float(data.get('amt_goods_price') or data.get('collateral_value', 0))
            
            days_employed = float(data.get('emp_length') or data.get('yearsInBusiness', 0))
            fico = float(data.get('fico_score') or data.get('creditScore', 600))
            dti = float(data.get('dti') or data.get('debt_to_income_ratio', 0))
            
            term = data.get('term', '36 months')
            grade = data.get('grade', 'C') # Default C
            contract_type = data.get('name_contract_type', 'Cash loans')
            ownership = data.get('home_ownership', 'RENT')

            # 2. Normalization
            norm_income = np.clip(income / 1000000, 0, 1)
            norm_credit = np.clip(credit / 2000000, 0, 1)
            norm_annuity = np.clip(annuity / 100000, 0, 1)
            norm_goods = np.clip(goods_price / 2000000, 0, 1)
            
            norm_days = np.clip(days_employed / 40, 0, 1) # 40 years max
            norm_fico = np.clip((fico - 300) / (850 - 300), 0, 1)
            norm_dti = np.clip(dti / 100, 0, 1) # DTI can be > 100% sometimes? Cap at 100

            # 3. Encoding
            term_60 = 1 if '60' in str(term) else 0
            
            # Grade One-Hot
            g_a = 1 if grade == 'A' else 0
            g_b = 1 if grade == 'B' else 0
            g_c = 1 if grade == 'C' else 0
            g_d = 1 if grade == 'D' else 0
            g_e = 1 if grade == 'E' else 0
            g_f = 1 if grade == 'F' or grade == 'G' else 0
            
            # Contract Type
            t_cash = 1 if contract_type == 'Cash loans' else 0
            t_rev = 1 if contract_type == 'Revolving loans' else 0
            
            # Ownership
            o_own = 1 if ownership == 'OWN' or ownership == 'MORTGAGE' else 0
            o_rent = 1 if ownership == 'RENT' else 0

            features = [
                norm_income, norm_credit, norm_annuity, norm_goods,
                norm_days, norm_fico, norm_dti, term_60,
                g_a, g_b, g_c, g_d, g_e, g_f,
                t_cash, t_rev,
                o_own, o_rent
            ]
            
            return np.array([features])
            
        except Exception as e:
            print(f"Preprocessing Error: {e}")
            return np.zeros((1, 18))

    def predict(self, data):
        features = self.preprocess(data)
        
        # Get probability of class 1 (Approval)
        if hasattr(self.model, "predict_proba"):
            probability = self.model.predict_proba(features)[0][1]
        else:
            probability = 0.5 # Fallback
        
        # Confidence logic
        confidence = abs(probability - 0.5) * 2
        
        # Credit Score Mapping
        credit_score = int(300 + (probability * 550))
        
        # Insights Generation (Simple Rules)
        insights = []
        if probability > 0.7:
            insights.append({"type": "positive", "text": "Creating Strong Credit Profile (Grade A/B equivalent)"})
        if float(data.get('dti', 0)) > 40:
             insights.append({"type": "negative", "text": "High Debt-to-Income Ratio detected"})
        
        return {
            "probability": float(probability),
            "confidence": float(confidence),
            "credit_score": credit_score,
            "insights": insights
        }

# Singleton instance
ml_service = CreditScoringModel()

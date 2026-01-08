"""
Model Baseline Comparison
Compare production model against simpler baselines
"""

import sys
sys.path.insert(0, 'k:/credit-ai-model/backend')

from app.services.model_service import model_service
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, precision_score, recall_score, brier_score_loss
from sklearn.preprocessing import StandardScaler
import pandas as pd

class BaselineComparator:
    def __init__(self):
        self.results = {}
        
    def generate_test_data(self, n=1000):
        """Generate test data with known outcomes"""
        np.random.seed(42)
        
        test_cases = []
        true_labels = []
        
        # Generate diverse cases
        for _ in range(n):
            # Random risk level
            risk_level = np.random.choice(['low', 'medium', 'high'], p=[0.3, 0.4, 0.3])
            
            if risk_level == 'low':
                case = {
                    'age': np.random.randint(30, 60),
                    'annual_income': np.random.randint(80000, 200000),
                    'credit_score': np.random.randint(720, 850),
                    'total_debt': np.random.randint(0, 20000),
                    'business_type': 'IT',
                    'credit_utilization': np.random.uniform(0.0, 0.30)
                }
                true_label = 1 if np.random.random() < 0.10 else 0
            elif risk_level == 'medium':
                case = {
                    'age': np.random.randint(25, 50),
                    'annual_income': np.random.randint(40000, 80000),
                    'credit_score': np.random.randint(640, 720),
                    'total_debt': np.random.randint(20000, 50000),
                    'business_type': np.random.choice(['IT', 'Construction', 'Retail']),
                    'credit_utilization': np.random.uniform(0.30, 0.60)
                }
                true_label = 1 if np.random.random() < 0.30 else 0
            else:  # high
                case = {
                    'age': np.random.randint(18, 40),
                    'annual_income': np.random.randint(20000, 50000),
                    'credit_score': np.random.randint(300, 640),
                    'total_debt': np.random.randint(40000, 100000),
                    'business_type': 'Retail',
                    'credit_utilization': np.random.uniform(0.60, 1.0)
                }
                true_label = 1 if np.random.random() < 0.70 else 0
            
            test_cases.append(case)
            true_labels.append(true_label)
        
        return test_cases, np.array(true_labels)
    
    def baseline_1_logistic_regression(self, test_cases, true_labels):
        """Baseline 1: Simple Logistic Regression"""
        print("\n" + "="*80)
        print("BASELINE 1: LOGISTIC REGRESSION")
        print("="*80)
        
        # Extract features
        X = []
        for case in test_cases:
            features = [
                case['age'],
                case['annual_income'],
                case['credit_score'],
                case['total_debt'],
                case.get('credit_utilization', 0.5)
            ]
            X.append(features)
        
        X = np.array(X)
        
        # Train simple logistic regression
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        lr = LogisticRegression(random_state=42, max_iter=1000)
        lr.fit(X_scaled, true_labels)
        
        # Predict
        predictions = lr.predict_proba(X_scaled)[:, 1]
        
        # Evaluate
        auc = roc_auc_score(true_labels, predictions)
        precision = precision_score(true_labels, (predictions > 0.5).astype(int))
        recall = recall_score(true_labels, (predictions > 0.5).astype(int))
        brier = brier_score_loss(true_labels, predictions)
        
        print(f"\nMetrics:")
        print(f"  ROC-AUC: {auc:.4f}")
        print(f"  Precision: {precision:.4f}")
        print(f"  Recall: {recall:.4f}")
        print(f"  Brier Score: {brier:.4f}")
        
        self.results['Logistic Regression'] = {
            'auc': auc,
            'precision': precision,
            'recall': recall,
            'brier': brier,
            'predictions': predictions
        }
        
        return predictions
    
    def baseline_2_rule_based(self, test_cases, true_labels):
        """Baseline 2: Simple Rule-Based Scoring"""
        print("\n" + "="*80)
        print("BASELINE 2: RULE-BASED SCORING")
        print("="*80)
        
        predictions = []
        
        for case in test_cases:
            score = 0
            
            # Credit score rules
            if case['credit_score'] >= 750:
                score += 30
            elif case['credit_score'] >= 700:
                score += 20
            elif case['credit_score'] >= 650:
                score += 10
            else:
                score -= 20
            
            # Income rules
            if case['annual_income'] >= 100000:
                score += 25
            elif case['annual_income'] >= 60000:
                score += 15
            elif case['annual_income'] >= 40000:
                score += 5
            else:
                score -= 15
            
            # Debt rules
            if case['total_debt'] < 20000:
                score += 20
            elif case['total_debt'] < 40000:
                score += 5
            else:
                score -= 25
            
            # Utilization rules
            util = case.get('credit_utilization', 0.5)
            if util < 0.30:
                score += 15
            elif util < 0.60:
                score += 0
            else:
                score -= 20
            
            # Convert score to probability (0-100 -> 0-1)
            # High score = low risk = low PD
            pd = max(0.01, min(0.99, 1.0 - (score + 50) / 150))
            predictions.append(pd)
        
        predictions = np.array(predictions)
        
        # Evaluate
        auc = roc_auc_score(true_labels, predictions)
        precision = precision_score(true_labels, (predictions > 0.5).astype(int))
        recall = recall_score(true_labels, (predictions > 0.5).astype(int))
        brier = brier_score_loss(true_labels, predictions)
        
        print(f"\nMetrics:")
        print(f"  ROC-AUC: {auc:.4f}")
        print(f"  Precision: {precision:.4f}")
        print(f"  Recall: {recall:.4f}")
        print(f"  Brier Score: {brier:.4f}")
        
        self.results['Rule-Based'] = {
            'auc': auc,
            'precision': precision,
            'recall': recall,
            'brier': brier,
            'predictions': predictions
        }
        
        return predictions
    
    def baseline_3_production_model(self, test_cases, true_labels):
        """Production Model: Calibrated Ensemble"""
        print("\n" + "="*80)
        print("PRODUCTION MODEL: CALIBRATED ENSEMBLE")
        print("="*80)
        
        predictions = []
        
        for case in test_cases:
            try:
                result = model_service.predict_probability(case)
                predictions.append(result['calibrated_pd'])
            except:
                predictions.append(0.5)
        
        predictions = np.array(predictions)
        
        # Evaluate
        auc = roc_auc_score(true_labels, predictions)
        precision = precision_score(true_labels, (predictions > 0.5).astype(int))
        recall = recall_score(true_labels, (predictions > 0.5).astype(int))
        brier = brier_score_loss(true_labels, predictions)
        
        print(f"\nMetrics:")
        print(f"  ROC-AUC: {auc:.4f}")
        print(f"  Precision: {precision:.4f}")
        print(f"  Recall: {recall:.4f}")
        print(f"  Brier Score: {brier:.4f}")
        
        self.results['Production Ensemble'] = {
            'auc': auc,
            'precision': precision,
            'recall': recall,
            'brier': brier,
            'predictions': predictions
        }
        
        return predictions
    
    def compute_decision_consistency(self):
        """Measure how often models agree on decisions"""
        print("\n" + "="*80)
        print("DECISION CONSISTENCY ANALYSIS")
        print("="*80)
        
        models = list(self.results.keys())
        
        print(f"\nPairwise Agreement (% of cases with same decision):")
        print(f"{'Model Pair':50s} | Agreement")
        print("-" * 70)
        
        for i, model1 in enumerate(models):
            for model2 in models[i+1:]:
                pred1 = (self.results[model1]['predictions'] > 0.5).astype(int)
                pred2 = (self.results[model2]['predictions'] > 0.5).astype(int)
                agreement = np.mean(pred1 == pred2)
                print(f"{model1:25s} vs {model2:25s} | {agreement:.1%}")
    
    def generate_report(self):
        """Generate comprehensive comparison report"""
        print("\n" + "="*80)
        print("BASELINE COMPARISON REPORT")
        print("="*80)
        
        print(f"\n{'Model':30s} | {'ROC-AUC':>8s} | {'Precision':>10s} | {'Recall':>8s} | {'Brier':>8s}")
        print("-" * 80)
        
        for model, metrics in self.results.items():
            print(f"{model:30s} | {metrics['auc']:>8.4f} | {metrics['precision']:>10.4f} | {metrics['recall']:>8.4f} | {metrics['brier']:>8.4f}")
        
        # Find best model for each metric
        print("\n" + "="*80)
        print("BEST PERFORMING MODEL BY METRIC")
        print("="*80)
        
        best_auc = max(self.results.items(), key=lambda x: x[1]['auc'])
        best_precision = max(self.results.items(), key=lambda x: x[1]['precision'])
        best_recall = max(self.results.items(), key=lambda x: x[1]['recall'])
        best_brier = min(self.results.items(), key=lambda x: x[1]['brier'])
        
        print(f"\nROC-AUC: {best_auc[0]} ({best_auc[1]['auc']:.4f})")
        print(f"Precision: {best_precision[0]} ({best_precision[1]['precision']:.4f})")
        print(f"Recall: {best_recall[0]} ({best_recall[1]['recall']:.4f})")
        print(f"Brier Score: {best_brier[0]} ({best_brier[1]['brier']:.4f})")
        
        return self.results

def run_comparison():
    """Run complete baseline comparison"""
    print("="*80)
    print("MODEL BASELINE COMPARISON")
    print("="*80)
    
    comparator = BaselineComparator()
    
    # Generate test data
    print("\nGenerating test data...")
    test_cases, true_labels = comparator.generate_test_data(n=1000)
    print(f"Generated {len(test_cases)} test cases")
    print(f"Default rate: {true_labels.mean():.1%}")
    
    # Run baselines
    comparator.baseline_1_logistic_regression(test_cases, true_labels)
    comparator.baseline_2_rule_based(test_cases, true_labels)
    comparator.baseline_3_production_model(test_cases, true_labels)
    
    # Decision consistency
    comparator.compute_decision_consistency()
    
    # Generate report
    results = comparator.generate_report()
    
    return results

if __name__ == "__main__":
    results = run_comparison()

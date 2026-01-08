"""
Probability Calibration Evaluation
Assesses the quality of model's probability estimates
"""

import sys
sys.path.insert(0, 'k:/credit-ai-model/backend')

from app.services.model_service import model_service
import numpy as np
import pandas as pd
from sklearn.metrics import brier_score_loss
from sklearn.calibration import calibration_curve
import matplotlib.pyplot as plt
from datetime import datetime

class CalibrationEvaluator:
    def __init__(self):
        self.results = {
            'brier_score': None,
            'calibration_curve': None,
            'risk_bands': {},
            'diagnostics': [],
            'recommendations': []
        }
        
    def generate_test_cases(self, n=1000):
        """
        Generate diverse test cases across risk spectrum
        """
        np.random.seed(42)
        
        test_cases = []
        true_labels = []
        
        # Low Risk Cases (30%)
        for _ in range(int(n * 0.3)):
            case = {
                'age': np.random.randint(30, 60),
                'annual_income': np.random.randint(80000, 200000),
                'credit_score': np.random.randint(720, 850),
                'total_debt': np.random.randint(0, 20000),
                'business_type': np.random.choice(['IT', 'Healthcare']),
                'monthly_debt_obligations': np.random.randint(0, 1667),
                'employment_years': np.random.randint(5, 20),
                'recent_inquiries': np.random.randint(0, 2),
                'delinquency_count': 0,
                'payment_history_months': np.random.randint(60, 120),
                'credit_utilization': np.random.uniform(0.0, 0.30)
            }
            test_cases.append(case)
            true_labels.append(0)  # Low risk -> No default
        
        # Medium Risk Cases (40%)
        for _ in range(int(n * 0.4)):
            case = {
                'age': np.random.randint(25, 50),
                'annual_income': np.random.randint(40000, 80000),
                'credit_score': np.random.randint(640, 720),
                'total_debt': np.random.randint(20000, 50000),
                'business_type': np.random.choice(['Construction', 'Retail', 'IT']),
                'monthly_debt_obligations': np.random.randint(1667, 4167),
                'employment_years': np.random.randint(2, 10),
                'recent_inquiries': np.random.randint(1, 4),
                'delinquency_count': np.random.randint(0, 2),
                'payment_history_months': np.random.randint(24, 60),
                'credit_utilization': np.random.uniform(0.30, 0.60)
            }
            test_cases.append(case)
            # Medium risk -> 30% default rate
            true_labels.append(1 if np.random.random() < 0.30 else 0)
        
        # High Risk Cases (30%)
        for _ in range(int(n * 0.3)):
            case = {
                'age': np.random.randint(18, 40),
                'annual_income': np.random.randint(20000, 50000),
                'credit_score': np.random.randint(300, 640),
                'total_debt': np.random.randint(40000, 100000),
                'business_type': np.random.choice(['Retail', 'Construction']),
                'monthly_debt_obligations': np.random.randint(3333, 8333),
                'employment_years': np.random.randint(0, 5),
                'recent_inquiries': np.random.randint(3, 10),
                'delinquency_count': np.random.randint(1, 5),
                'payment_history_months': np.random.randint(6, 36),
                'credit_utilization': np.random.uniform(0.60, 1.0)
            }
            test_cases.append(case)
            # High risk -> 70% default rate
            true_labels.append(1 if np.random.random() < 0.70 else 0)
        
        return test_cases, np.array(true_labels)
    
    def compute_brier_score(self, predictions, true_labels):
        """
        Compute Brier Score (lower is better, 0 = perfect)
        """
        print("\n" + "="*80)
        print("BRIER SCORE COMPUTATION")
        print("="*80)
        
        brier = brier_score_loss(true_labels, predictions)
        
        print(f"\nBrier Score: {brier:.4f}")
        print(f"\nInterpretation:")
        print(f"  0.00 - 0.10: Excellent calibration")
        print(f"  0.10 - 0.20: Good calibration")
        print(f"  0.20 - 0.30: Fair calibration")
        print(f"  > 0.30: Poor calibration")
        
        if brier < 0.10:
            status = "✓ EXCELLENT"
            self.results['diagnostics'].append("Brier score indicates excellent calibration")
        elif brier < 0.20:
            status = "✓ GOOD"
            self.results['diagnostics'].append("Brier score indicates good calibration")
        elif brier < 0.30:
            status = "⚠ FAIR"
            self.results['diagnostics'].append("Brier score indicates fair calibration - consider recalibration")
            self.results['recommendations'].append("Consider isotonic regression recalibration")
        else:
            status = "✗ POOR"
            self.results['diagnostics'].append("Brier score indicates poor calibration - recalibration required")
            self.results['recommendations'].append("URGENT: Recalibrate model using Platt scaling or isotonic regression")
        
        print(f"\nStatus: {status}")
        
        self.results['brier_score'] = brier
        return brier
    
    def compute_calibration_curve(self, predictions, true_labels):
        """
        Compute calibration curve (predicted vs actual probabilities)
        """
        print("\n" + "="*80)
        print("CALIBRATION CURVE ANALYSIS")
        print("="*80)
        
        # Compute calibration curve with 10 bins
        fraction_of_positives, mean_predicted_value = calibration_curve(
            true_labels, predictions, n_bins=10, strategy='uniform'
        )
        
        print(f"\nCalibration Curve (10 bins):")
        print(f"{'Predicted':>12} | {'Actual':>12} | {'Difference':>12} | Status")
        print("-" * 60)
        
        max_diff = 0
        for pred, actual in zip(mean_predicted_value, fraction_of_positives):
            diff = abs(pred - actual)
            max_diff = max(max_diff, diff)
            status = "✓" if diff < 0.10 else "⚠" if diff < 0.20 else "✗"
            print(f"{pred:>12.3f} | {actual:>12.3f} | {diff:>12.3f} | {status}")
        
        print(f"\nMaximum Calibration Error: {max_diff:.3f}")
        
        if max_diff < 0.10:
            print("Status: ✓ EXCELLENT - Well calibrated across all bins")
        elif max_diff < 0.20:
            print("Status: ✓ GOOD - Minor calibration issues")
            self.results['diagnostics'].append("Minor calibration drift detected in some bins")
        else:
            print("Status: ✗ POOR - Significant calibration issues")
            self.results['diagnostics'].append("Significant calibration drift detected")
            self.results['recommendations'].append("Recalibration required to fix calibration drift")
        
        self.results['calibration_curve'] = {
            'predicted': mean_predicted_value.tolist(),
            'actual': fraction_of_positives.tolist(),
            'max_error': max_diff
        }
        
        return fraction_of_positives, mean_predicted_value
    
    def analyze_risk_bands(self, predictions, true_labels):
        """
        Analyze calibration quality by risk band
        """
        print("\n" + "="*80)
        print("RISK BAND ANALYSIS")
        print("="*80)
        
        # Define risk bands
        bands = {
            'Low Risk (PD < 0.20)': (0.0, 0.20),
            'Medium Risk (PD 0.20-0.45)': (0.20, 0.45),
            'High Risk (PD > 0.45)': (0.45, 1.0)
        }
        
        for band_name, (low, high) in bands.items():
            mask = (predictions >= low) & (predictions < high)
            band_preds = predictions[mask]
            band_labels = true_labels[mask]
            
            if len(band_preds) == 0:
                print(f"\n{band_name}: No samples")
                continue
            
            avg_pred = np.mean(band_preds)
            actual_rate = np.mean(band_labels)
            diff = abs(avg_pred - actual_rate)
            count = len(band_preds)
            
            print(f"\n{band_name}:")
            print(f"  Samples: {count}")
            print(f"  Avg Predicted PD: {avg_pred:.3f}")
            print(f"  Actual Default Rate: {actual_rate:.3f}")
            print(f"  Calibration Error: {diff:.3f}")
            
            # Assess calibration quality
            if diff < 0.05:
                status = "✓ EXCELLENT"
                trust = "High"
            elif diff < 0.10:
                status = "✓ GOOD"
                trust = "Medium-High"
            elif diff < 0.15:
                status = "⚠ FAIR"
                trust = "Medium"
            else:
                status = "✗ POOR"
                trust = "Low"
            
            print(f"  Status: {status}")
            print(f"  Trust Level: {trust}")
            
            # Detect over/under confidence
            if avg_pred > actual_rate + 0.10:
                print(f"  ⚠ OVERCONFIDENT: Model overestimates risk by {(avg_pred - actual_rate):.3f}")
                self.results['diagnostics'].append(f"{band_name}: Overconfident")
            elif avg_pred < actual_rate - 0.10:
                print(f"  ⚠ UNDERCONFIDENT: Model underestimates risk by {(actual_rate - avg_pred):.3f}")
                self.results['diagnostics'].append(f"{band_name}: Underconfident")
            else:
                print(f"  ✓ Well calibrated")
            
            self.results['risk_bands'][band_name] = {
                'count': count,
                'avg_predicted': avg_pred,
                'actual_rate': actual_rate,
                'error': diff,
                'status': status,
                'trust': trust
            }
    
    def detect_calibration_issues(self):
        """
        Detect specific calibration issues
        """
        print("\n" + "="*80)
        print("CALIBRATION DIAGNOSTICS")
        print("="*80)
        
        issues_found = len(self.results['diagnostics'])
        
        if issues_found == 0:
            print("\n✓ No calibration issues detected")
            print("✓ Model is well-calibrated across all risk bands")
        else:
            print(f"\n⚠ {issues_found} calibration issue(s) detected:")
            for i, issue in enumerate(self.results['diagnostics'], 1):
                print(f"  {i}. {issue}")
    
    def generate_recommendations(self):
        """
        Generate recalibration recommendations
        """
        print("\n" + "="*80)
        print("RECALIBRATION RECOMMENDATIONS")
        print("="*80)
        
        if len(self.results['recommendations']) == 0:
            print("\n✓ No recalibration needed")
            print("✓ Model calibration is acceptable for production use")
        else:
            print(f"\n⚠ {len(self.results['recommendations'])} recommendation(s):")
            for i, rec in enumerate(self.results['recommendations'], 1):
                print(f"  {i}. {rec}")
            
            print("\n  Recommended Recalibration Methods:")
            print("    a) Platt Scaling (Logistic Regression)")
            print("    b) Isotonic Regression (Non-parametric)")
            print("    c) Beta Calibration (For well-calibrated models)")
    
    def generate_report(self):
        """
        Generate comprehensive calibration report
        """
        print("\n" + "="*80)
        print("CALIBRATION EVALUATION REPORT")
        print("="*80)
        
        print(f"\nEvaluation Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Model Version: ensemble_v1.0_stable")
        
        # Overall Assessment
        brier = self.results['brier_score']
        max_error = self.results['calibration_curve']['max_error']
        
        print(f"\n{'='*80}")
        print("OVERALL ASSESSMENT")
        print(f"{'='*80}")
        
        print(f"\nBrier Score: {brier:.4f}")
        print(f"Max Calibration Error: {max_error:.3f}")
        
        # Determine overall grade
        if brier < 0.10 and max_error < 0.10:
            grade = "A (Excellent)"
            status = "✓ PRODUCTION READY"
        elif brier < 0.20 and max_error < 0.15:
            grade = "B (Good)"
            status = "✓ ACCEPTABLE FOR PRODUCTION"
        elif brier < 0.30 and max_error < 0.20:
            grade = "C (Fair)"
            status = "⚠ RECALIBRATION RECOMMENDED"
        else:
            grade = "D (Poor)"
            status = "✗ RECALIBRATION REQUIRED"
        
        print(f"\nOverall Grade: {grade}")
        print(f"Production Status: {status}")
        
        # Risk Band Summary
        print(f"\n{'='*80}")
        print("RISK BAND TRUST ASSESSMENT")
        print(f"{'='*80}")
        
        for band_name, metrics in self.results['risk_bands'].items():
            print(f"\n{band_name}:")
            print(f"  Trust Level: {metrics['trust']}")
            print(f"  Calibration Error: {metrics['error']:.3f}")
            print(f"  Status: {metrics['status']}")
        
        return self.results

def run_calibration_evaluation():
    """
    Run complete calibration evaluation
    """
    print("="*80)
    print("PROBABILITY CALIBRATION EVALUATION")
    print("="*80)
    print("\nGenerating test cases...")
    
    evaluator = CalibrationEvaluator()
    
    # Generate test cases
    test_cases, true_labels = evaluator.generate_test_cases(n=1000)
    print(f"Generated {len(test_cases)} test cases")
    
    # Get predictions
    print("Computing predictions...")
    predictions = []
    for case in test_cases:
        try:
            result = model_service.predict_probability(case)
            predictions.append(result['calibrated_pd'])
        except Exception as e:
            print(f"Error: {e}")
            predictions.append(0.5)  # Default to 50% if error
    
    predictions = np.array(predictions)
    print(f"Predictions computed: {len(predictions)}")
    
    # Run evaluations
    evaluator.compute_brier_score(predictions, true_labels)
    evaluator.compute_calibration_curve(predictions, true_labels)
    evaluator.analyze_risk_bands(predictions, true_labels)
    evaluator.detect_calibration_issues()
    evaluator.generate_recommendations()
    
    # Generate report
    results = evaluator.generate_report()
    
    return results

if __name__ == "__main__":
    results = run_calibration_evaluation()

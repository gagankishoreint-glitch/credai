"""
Model Stability and Sanity Audit
Tests for monotonicity, sensitivity, feature importance, and extreme values
"""

import sys
sys.path.insert(0, 'k:/credit-ai-model/backend')

from app.services.model_service import model_service
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

class ModelAuditor:
    def __init__(self):
        self.results = {
            'monotonicity': [],
            'sensitivity': [],
            'ablation': [],
            'extreme_values': [],
            'issues': []
        }
        
    def create_baseline_application(self):
        """Create a baseline 'safe' application"""
        return {
            "age": 35,
            "annual_income": 75000,
            "credit_score": 720,
            "total_debt": 25000,
            "business_type": "IT",
            "monthly_debt_obligations": 2083,
            "employment_years": 5,
            "recent_inquiries": 1,
            "delinquency_count": 0,
            "payment_history_months": 36,
            "credit_utilization": 0.30
        }
    
    def test_monotonicity(self):
        """
        Test 1: Monotonicity Checks
        Verify that risk increases when negative factors increase
        """
        print("\n" + "="*80)
        print("TEST 1: MONOTONICITY CHECKS")
        print("="*80)
        
        baseline = self.create_baseline_application()
        baseline_result = model_service.predict_probability(baseline)
        baseline_pd = baseline_result['calibrated_pd']
        
        print(f"\nBaseline PD: {baseline_pd:.4f}")
        
        # Test 1a: Credit Utilization (should increase PD)
        print("\n1a. Credit Utilization Test (expect PD to increase)")
        print("-" * 60)
        utilization_values = [0.10, 0.30, 0.50, 0.70, 0.90]
        utilization_pds = []
        
        for util in utilization_values:
            app = baseline.copy()
            app['credit_utilization'] = util
            result = model_service.predict_probability(app)
            pd = result['calibrated_pd']
            utilization_pds.append(pd)
            print(f"  Utilization: {util:.0%} -> PD: {pd:.4f}")
        
        # Check monotonicity
        is_monotonic = all(utilization_pds[i] <= utilization_pds[i+1] for i in range(len(utilization_pds)-1))
        status = "✓ PASS" if is_monotonic else "✗ FAIL"
        print(f"\n  {status}: {'Monotonic increase' if is_monotonic else 'Non-monotonic behavior detected!'}")
        
        self.results['monotonicity'].append({
            'feature': 'credit_utilization',
            'monotonic': is_monotonic,
            'values': utilization_values,
            'pds': utilization_pds
        })
        
        if not is_monotonic:
            self.results['issues'].append("Credit utilization does not monotonically increase PD")
        
        # Test 1b: Credit Score (should decrease PD)
        print("\n1b. Credit Score Test (expect PD to decrease)")
        print("-" * 60)
        credit_scores = [580, 640, 700, 760, 820]
        credit_pds = []
        
        for score in credit_scores:
            app = baseline.copy()
            app['credit_score'] = score
            result = model_service.predict_probability(app)
            pd = result['calibrated_pd']
            credit_pds.append(pd)
            print(f"  Credit Score: {score} -> PD: {pd:.4f}")
        
        # Check monotonicity (should decrease)
        is_monotonic = all(credit_pds[i] >= credit_pds[i+1] for i in range(len(credit_pds)-1))
        status = "✓ PASS" if is_monotonic else "✗ FAIL"
        print(f"\n  {status}: {'Monotonic decrease' if is_monotonic else 'Non-monotonic behavior detected!'}")
        
        self.results['monotonicity'].append({
            'feature': 'credit_score',
            'monotonic': is_monotonic,
            'values': credit_scores,
            'pds': credit_pds
        })
        
        if not is_monotonic:
            self.results['issues'].append("Credit score does not monotonically decrease PD")
        
        # Test 1c: Total Debt (should increase PD)
        print("\n1c. Total Debt Test (expect PD to increase)")
        print("-" * 60)
        debt_values = [10000, 25000, 40000, 55000, 70000]
        debt_pds = []
        
        for debt in debt_values:
            app = baseline.copy()
            app['total_debt'] = debt
            app['monthly_debt_obligations'] = debt / 12
            result = model_service.predict_probability(app)
            pd = result['calibrated_pd']
            debt_pds.append(pd)
            print(f"  Total Debt: ${debt:,} -> PD: {pd:.4f}")
        
        is_monotonic = all(debt_pds[i] <= debt_pds[i+1] for i in range(len(debt_pds)-1))
        status = "✓ PASS" if is_monotonic else "✗ FAIL"
        print(f"\n  {status}: {'Monotonic increase' if is_monotonic else 'Non-monotonic behavior detected!'}")
        
        self.results['monotonicity'].append({
            'feature': 'total_debt',
            'monotonic': is_monotonic,
            'values': debt_values,
            'pds': debt_pds
        })
        
        if not is_monotonic:
            self.results['issues'].append("Total debt does not monotonically increase PD")
    
    def test_sensitivity(self):
        """
        Test 2: Sensitivity Tests
        Small changes should produce small PD changes
        """
        print("\n" + "="*80)
        print("TEST 2: SENSITIVITY TESTS")
        print("="*80)
        
        baseline = self.create_baseline_application()
        baseline_result = model_service.predict_probability(baseline)
        baseline_pd = baseline_result['calibrated_pd']
        
        print(f"\nBaseline PD: {baseline_pd:.4f}")
        
        # Test 2a: Income sensitivity
        print("\n2a. Income Sensitivity (±10% change)")
        print("-" * 60)
        
        income_changes = [-0.10, -0.05, 0, 0.05, 0.10]
        for change in income_changes:
            app = baseline.copy()
            app['annual_income'] = baseline['annual_income'] * (1 + change)
            result = model_service.predict_probability(app)
            pd = result['calibrated_pd']
            pd_change = pd - baseline_pd
            print(f"  Income change: {change:+.0%} -> PD: {pd:.4f} (Δ: {pd_change:+.4f})")
            
            # Check if change is proportional (not over-sensitive)
            if abs(change) > 0 and abs(pd_change) > abs(change) * 2:
                self.results['issues'].append(f"Income over-sensitive: {change:.0%} change -> {pd_change:.4f} PD change")
        
        # Test 2b: Age sensitivity
        print("\n2b. Age Sensitivity (±5 years)")
        print("-" * 60)
        
        age_changes = [-5, -2, 0, 2, 5]
        for change in age_changes:
            app = baseline.copy()
            app['age'] = baseline['age'] + change
            result = model_service.predict_probability(app)
            pd = result['calibrated_pd']
            pd_change = pd - baseline_pd
            print(f"  Age change: {change:+d} years -> PD: {pd:.4f} (Δ: {pd_change:+.4f})")
            
            # Age should have minimal impact
            if abs(pd_change) > 0.05:
                self.results['issues'].append(f"Age over-sensitive: {change} years -> {pd_change:.4f} PD change")
    
    def test_feature_ablation(self):
        """
        Test 3: Feature Ablation
        Remove features one at a time to see impact
        """
        print("\n" + "="*80)
        print("TEST 3: FEATURE ABLATION")
        print("="*80)
        
        baseline = self.create_baseline_application()
        baseline_result = model_service.predict_probability(baseline)
        baseline_pd = baseline_result['calibrated_pd']
        
        print(f"\nBaseline PD (all features): {baseline_pd:.4f}\n")
        
        # Features to test
        features_to_ablate = [
            'credit_score',
            'annual_income',
            'total_debt',
            'credit_utilization',
            'employment_years',
            'delinquency_count'
        ]
        
        ablation_results = []
        
        for feature in features_to_ablate:
            app = baseline.copy()
            # Set feature to neutral/median value
            if feature == 'credit_score':
                app[feature] = 700  # Median
            elif feature == 'annual_income':
                app[feature] = 60000  # Median
            elif feature == 'total_debt':
                app[feature] = 30000  # Median
                app['monthly_debt_obligations'] = 2500
            elif feature == 'credit_utilization':
                app[feature] = 0.30  # Median
            elif feature == 'employment_years':
                app[feature] = 3  # Median
            elif feature == 'delinquency_count':
                app[feature] = 0  # Best case
            
            result = model_service.predict_probability(app)
            pd = result['calibrated_pd']
            impact = abs(pd - baseline_pd)
            
            ablation_results.append({
                'feature': feature,
                'pd': pd,
                'impact': impact
            })
            
            print(f"  {feature:25s} -> PD: {pd:.4f} (Impact: {impact:.4f})")
        
        # Sort by impact
        ablation_results.sort(key=lambda x: x['impact'], reverse=True)
        
        print("\n  Feature Importance Ranking:")
        print("  " + "-" * 60)
        for i, result in enumerate(ablation_results, 1):
            print(f"  {i}. {result['feature']:25s} Impact: {result['impact']:.4f}")
        
        self.results['ablation'] = ablation_results
        
        # Flag over-dominant features
        max_impact = ablation_results[0]['impact']
        if max_impact > 0.20:
            self.results['issues'].append(f"Feature '{ablation_results[0]['feature']}' has excessive impact: {max_impact:.4f}")
    
    def test_extreme_values(self):
        """
        Test 4: Extreme Value Tests
        Test model behavior at boundaries
        """
        print("\n" + "="*80)
        print("TEST 4: EXTREME VALUE TESTS")
        print("="*80)
        
        # Test 4a: Perfect applicant
        print("\n4a. Perfect Applicant")
        print("-" * 60)
        perfect = {
            "age": 45,
            "annual_income": 200000,
            "credit_score": 850,
            "total_debt": 0,
            "business_type": "IT",
            "monthly_debt_obligations": 0,
            "employment_years": 15,
            "recent_inquiries": 0,
            "delinquency_count": 0,
            "payment_history_months": 120,
            "credit_utilization": 0.0
        }
        
        result = model_service.predict_probability(perfect)
        pd = result['calibrated_pd']
        print(f"  PD: {pd:.4f}")
        
        if pd > 0.10:
            self.results['issues'].append(f"Perfect applicant has high PD: {pd:.4f}")
            print(f"  ⚠️  WARNING: Perfect applicant should have PD < 0.10")
        else:
            print(f"  ✓ PASS: Low PD for perfect applicant")
        
        # Test 4b: Worst applicant
        print("\n4b. Worst Applicant")
        print("-" * 60)
        worst = {
            "age": 18,
            "annual_income": 20000,
            "credit_score": 300,
            "total_debt": 80000,
            "business_type": "Retail",
            "monthly_debt_obligations": 6667,
            "employment_years": 0,
            "recent_inquiries": 10,
            "delinquency_count": 5,
            "payment_history_months": 6,
            "credit_utilization": 1.0
        }
        
        result = model_service.predict_probability(worst)
        pd = result['calibrated_pd']
        print(f"  PD: {pd:.4f}")
        
        if pd < 0.70:
            self.results['issues'].append(f"Worst applicant has low PD: {pd:.4f}")
            print(f"  ⚠️  WARNING: Worst applicant should have PD > 0.70")
        else:
            print(f"  ✓ PASS: High PD for worst applicant")
        
        # Test 4c: Boundary values
        print("\n4c. Boundary Value Tests")
        print("-" * 60)
        
        baseline = self.create_baseline_application()
        
        # Test zero income
        app = baseline.copy()
        app['annual_income'] = 1  # Avoid division by zero
        try:
            result = model_service.predict_probability(app)
            print(f"  Zero income: PD = {result['calibrated_pd']:.4f} ✓")
        except Exception as e:
            print(f"  Zero income: ERROR - {e}")
            self.results['issues'].append(f"Model crashes on zero income: {e}")
        
        # Test maximum credit score
        app = baseline.copy()
        app['credit_score'] = 850
        try:
            result = model_service.predict_probability(app)
            print(f"  Max credit score (850): PD = {result['calibrated_pd']:.4f} ✓")
        except Exception as e:
            print(f"  Max credit score: ERROR - {e}")
            self.results['issues'].append(f"Model crashes on max credit score: {e}")
        
        # Test minimum credit score
        app = baseline.copy()
        app['credit_score'] = 300
        try:
            result = model_service.predict_probability(app)
            print(f"  Min credit score (300): PD = {result['calibrated_pd']:.4f} ✓")
        except Exception as e:
            print(f"  Min credit score: ERROR - {e}")
            self.results['issues'].append(f"Model crashes on min credit score: {e}")
    
    def generate_report(self):
        """Generate comprehensive stability report"""
        print("\n" + "="*80)
        print("STABILITY AUDIT REPORT")
        print("="*80)
        
        print(f"\nAudit Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Model Version: ensemble_v1.0")
        
        # Summary
        total_issues = len(self.results['issues'])
        print(f"\n{'='*80}")
        print(f"SUMMARY: {total_issues} issues found")
        print(f"{'='*80}")
        
        if total_issues == 0:
            print("\n✓ Model passed all stability tests!")
        else:
            print("\n⚠️  Issues Identified:")
            for i, issue in enumerate(self.results['issues'], 1):
                print(f"  {i}. {issue}")
        
        # Monotonicity results
        print(f"\n{'='*80}")
        print("MONOTONICITY TESTS")
        print(f"{'='*80}")
        for test in self.results['monotonicity']:
            status = "✓ PASS" if test['monotonic'] else "✗ FAIL"
            print(f"  {status}: {test['feature']}")
        
        # Feature importance
        if self.results['ablation']:
            print(f"\n{'='*80}")
            print("FEATURE IMPORTANCE (by ablation impact)")
            print(f"{'='*80}")
            for i, result in enumerate(self.results['ablation'][:5], 1):
                print(f"  {i}. {result['feature']:25s} Impact: {result['impact']:.4f}")
        
        # Recommendations
        print(f"\n{'='*80}")
        print("RECOMMENDATIONS")
        print(f"{'='*80}")
        
        if total_issues == 0:
            print("\n  ✓ Model is stable and behaves intuitively")
            print("  ✓ No constraints or transformations needed")
        else:
            print("\n  Recommended Actions:")
            
            # Check for non-monotonic features
            non_monotonic = [t for t in self.results['monotonicity'] if not t['monotonic']]
            if non_monotonic:
                print(f"\n  1. Fix Non-Monotonic Features:")
                for test in non_monotonic:
                    print(f"     - Add monotonicity constraint for '{test['feature']}'")
                    print(f"       OR apply monotonic transformation (e.g., isotonic regression)")
            
            # Check for over-sensitive features
            if any('over-sensitive' in issue for issue in self.results['issues']):
                print(f"\n  2. Reduce Feature Sensitivity:")
                print(f"     - Apply log transformation to sensitive features")
                print(f"     - Use feature scaling/normalization")
                print(f"     - Add regularization to reduce feature weights")
            
            # Check for extreme value issues
            if any('crashes' in issue or 'Perfect' in issue or 'Worst' in issue for issue in self.results['issues']):
                print(f"\n  3. Handle Extreme Values:")
                print(f"     - Add input validation and clipping")
                print(f"     - Use robust scaling (e.g., RobustScaler)")
                print(f"     - Add safety checks in preprocessing")
        
        return self.results

def run_audit():
    """Run complete model audit"""
    print("="*80)
    print("MODEL STABILITY AND SANITY AUDIT")
    print("="*80)
    print("\nLoading model...")
    
    auditor = ModelAuditor()
    
    # Run all tests
    auditor.test_monotonicity()
    auditor.test_sensitivity()
    auditor.test_feature_ablation()
    auditor.test_extreme_values()
    
    # Generate report
    results = auditor.generate_report()
    
    return results

if __name__ == "__main__":
    results = run_audit()

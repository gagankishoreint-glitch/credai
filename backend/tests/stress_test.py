"""
Economic Stress Testing for Credit Risk Model
Simulates various economic shocks and measures model resilience
"""

import sys
sys.path.insert(0, 'k:/credit-ai-model/backend')

from app.services.model_service import model_service
import numpy as np
import pandas as pd
from datetime import datetime

class StressTester:
    def __init__(self):
        self.results = {
            'baseline': {},
            'income_shock_10': {},
            'income_shock_30': {},
            'expense_inflation': {},
            'behavioral_shift': {},
            'combined_shock': {}
        }
        
    def generate_baseline_portfolio(self, n=500):
        """Generate baseline portfolio"""
        np.random.seed(42)
        
        portfolio = []
        for _ in range(n):
            applicant = {
                'age': np.random.randint(25, 65),
                'annual_income': np.random.randint(40000, 150000),
                'credit_score': np.random.randint(600, 800),
                'total_debt': np.random.randint(10000, 80000),
                'business_type': np.random.choice(['IT', 'Healthcare', 'Construction', 'Retail']),
                'credit_utilization': np.random.uniform(0.1, 0.7),
                'employment_years': np.random.randint(1, 20)
            }
            portfolio.append(applicant)
        
        return pd.DataFrame(portfolio)
    
    def get_baseline_predictions(self, portfolio):
        """Get baseline predictions"""
        print("\n" + "="*80)
        print("BASELINE PREDICTIONS")
        print("="*80)
        
        predictions = []
        decisions = []
        confidences = []
        
        for _, applicant in portfolio.iterrows():
            try:
                result = model_service.predict_probability(applicant.to_dict())
                pd_val = result['calibrated_pd']
                conf = result['confidence_score']
                
                predictions.append(pd_val)
                confidences.append(conf)
                
                # Decision logic
                if pd_val < 0.20:
                    decision = 'Approve'
                elif pd_val > 0.45:
                    decision = 'Reject'
                else:
                    decision = 'Review'
                decisions.append(decision)
            except:
                predictions.append(0.5)
                confidences.append(0.5)
                decisions.append('Review')
        
        self.results['baseline'] = {
            'predictions': np.array(predictions),
            'decisions': decisions,
            'confidences': np.array(confidences),
            'avg_pd': np.mean(predictions),
            'approval_rate': (np.array(decisions) == 'Approve').mean(),
            'rejection_rate': (np.array(decisions) == 'Reject').mean()
        }
        
        print(f"\nBaseline Metrics:")
        print(f"  Average PD: {self.results['baseline']['avg_pd']:.3f}")
        print(f"  Approval Rate: {self.results['baseline']['approval_rate']:.1%}")
        print(f"  Rejection Rate: {self.results['baseline']['rejection_rate']:.1%}")
        print(f"  Review Rate: {1 - self.results['baseline']['approval_rate'] - self.results['baseline']['rejection_rate']:.1%}")
        
        return predictions, decisions, confidences
    
    def stress_test_income_reduction(self, portfolio, reduction_pct):
        """Stress Test 1: Income Reduction"""
        print(f"\n" + "="*80)
        print(f"STRESS TEST: {reduction_pct}% INCOME REDUCTION")
        print("="*80)
        
        shocked_portfolio = portfolio.copy()
        shocked_portfolio['annual_income'] = shocked_portfolio['annual_income'] * (1 - reduction_pct/100)
        
        predictions = []
        decisions = []
        confidences = []
        
        for _, applicant in shocked_portfolio.iterrows():
            try:
                result = model_service.predict_probability(applicant.to_dict())
                pd_val = result['calibrated_pd']
                conf = result['confidence_score']
                
                predictions.append(pd_val)
                confidences.append(conf)
                
                if pd_val < 0.20:
                    decision = 'Approve'
                elif pd_val > 0.45:
                    decision = 'Reject'
                else:
                    decision = 'Review'
                decisions.append(decision)
            except:
                predictions.append(0.5)
                confidences.append(0.5)
                decisions.append('Review')
        
        key = f'income_shock_{reduction_pct}'
        self.results[key] = {
            'predictions': np.array(predictions),
            'decisions': decisions,
            'confidences': np.array(confidences),
            'avg_pd': np.mean(predictions),
            'approval_rate': (np.array(decisions) == 'Approve').mean(),
            'rejection_rate': (np.array(decisions) == 'Reject').mean()
        }
        
        # Calculate changes
        pd_change = self.results[key]['avg_pd'] - self.results['baseline']['avg_pd']
        approval_change = self.results[key]['approval_rate'] - self.results['baseline']['approval_rate']
        
        print(f"\nShock Impact:")
        print(f"  Average PD: {self.results[key]['avg_pd']:.3f} (Δ: {pd_change:+.3f})")
        print(f"  Approval Rate: {self.results[key]['approval_rate']:.1%} (Δ: {approval_change:+.1%})")
        print(f"  Rejection Rate: {self.results[key]['rejection_rate']:.1%}")
        
        # Decision flips
        baseline_decisions = np.array(self.results['baseline']['decisions'])
        shocked_decisions = np.array(decisions)
        flips = (baseline_decisions != shocked_decisions).sum()
        flip_rate = flips / len(baseline_decisions)
        
        print(f"\nDecision Flips: {flips} ({flip_rate:.1%})")
        
        return predictions, decisions
    
    def stress_test_expense_inflation(self, portfolio):
        """Stress Test 2: Expense Inflation (20% debt increase)"""
        print("\n" + "="*80)
        print("STRESS TEST: 20% EXPENSE INFLATION")
        print("="*80)
        
        shocked_portfolio = portfolio.copy()
        shocked_portfolio['total_debt'] = shocked_portfolio['total_debt'] * 1.20
        shocked_portfolio['credit_utilization'] = np.minimum(
            shocked_portfolio['credit_utilization'] * 1.20,
            1.0
        )
        
        predictions = []
        decisions = []
        confidences = []
        
        for _, applicant in shocked_portfolio.iterrows():
            try:
                result = model_service.predict_probability(applicant.to_dict())
                pd_val = result['calibrated_pd']
                conf = result['confidence_score']
                
                predictions.append(pd_val)
                confidences.append(conf)
                
                if pd_val < 0.20:
                    decision = 'Approve'
                elif pd_val > 0.45:
                    decision = 'Reject'
                else:
                    decision = 'Review'
                decisions.append(decision)
            except:
                predictions.append(0.5)
                confidences.append(0.5)
                decisions.append('Review')
        
        self.results['expense_inflation'] = {
            'predictions': np.array(predictions),
            'decisions': decisions,
            'confidences': np.array(confidences),
            'avg_pd': np.mean(predictions),
            'approval_rate': (np.array(decisions) == 'Approve').mean(),
            'rejection_rate': (np.array(decisions) == 'Reject').mean()
        }
        
        pd_change = self.results['expense_inflation']['avg_pd'] - self.results['baseline']['avg_pd']
        approval_change = self.results['expense_inflation']['approval_rate'] - self.results['baseline']['approval_rate']
        
        print(f"\nShock Impact:")
        print(f"  Average PD: {self.results['expense_inflation']['avg_pd']:.3f} (Δ: {pd_change:+.3f})")
        print(f"  Approval Rate: {self.results['expense_inflation']['approval_rate']:.1%} (Δ: {approval_change:+.1%})")
        
        baseline_decisions = np.array(self.results['baseline']['decisions'])
        shocked_decisions = np.array(decisions)
        flips = (baseline_decisions != shocked_decisions).sum()
        flip_rate = flips / len(baseline_decisions)
        
        print(f"\nDecision Flips: {flips} ({flip_rate:.1%})")
        
        return predictions, decisions
    
    def stress_test_behavioral_shift(self, portfolio):
        """Stress Test 3: Behavioral Instability (credit score degradation)"""
        print("\n" + "="*80)
        print("STRESS TEST: BEHAVIORAL INSTABILITY")
        print("="*80)
        
        shocked_portfolio = portfolio.copy()
        # Simulate credit score degradation
        shocked_portfolio['credit_score'] = shocked_portfolio['credit_score'] - 50
        shocked_portfolio['credit_score'] = np.maximum(shocked_portfolio['credit_score'], 300)
        
        predictions = []
        decisions = []
        confidences = []
        
        for _, applicant in shocked_portfolio.iterrows():
            try:
                result = model_service.predict_probability(applicant.to_dict())
                pd_val = result['calibrated_pd']
                conf = result['confidence_score']
                
                predictions.append(pd_val)
                confidences.append(conf)
                
                if pd_val < 0.20:
                    decision = 'Approve'
                elif pd_val > 0.45:
                    decision = 'Reject'
                else:
                    decision = 'Review'
                decisions.append(decision)
            except:
                predictions.append(0.5)
                confidences.append(0.5)
                decisions.append('Review')
        
        self.results['behavioral_shift'] = {
            'predictions': np.array(predictions),
            'decisions': decisions,
            'confidences': np.array(confidences),
            'avg_pd': np.mean(predictions),
            'approval_rate': (np.array(decisions) == 'Approve').mean(),
            'rejection_rate': (np.array(decisions) == 'Reject').mean()
        }
        
        pd_change = self.results['behavioral_shift']['avg_pd'] - self.results['baseline']['avg_pd']
        approval_change = self.results['behavioral_shift']['approval_rate'] - self.results['baseline']['approval_rate']
        
        print(f"\nShock Impact:")
        print(f"  Average PD: {self.results['behavioral_shift']['avg_pd']:.3f} (Δ: {pd_change:+.3f})")
        print(f"  Approval Rate: {self.results['behavioral_shift']['approval_rate']:.1%} (Δ: {approval_change:+.1%})")
        
        baseline_decisions = np.array(self.results['baseline']['decisions'])
        shocked_decisions = np.array(decisions)
        flips = (baseline_decisions != shocked_decisions).sum()
        flip_rate = flips / len(baseline_decisions)
        
        print(f"\nDecision Flips: {flips} ({flip_rate:.1%})")
        
        return predictions, decisions
    
    def stress_test_combined_shock(self, portfolio):
        """Stress Test 4: Combined Economic Crisis"""
        print("\n" + "="*80)
        print("STRESS TEST: COMBINED ECONOMIC CRISIS")
        print("="*80)
        
        shocked_portfolio = portfolio.copy()
        # 20% income reduction + 15% debt increase + 30 point credit score drop
        shocked_portfolio['annual_income'] = shocked_portfolio['annual_income'] * 0.80
        shocked_portfolio['total_debt'] = shocked_portfolio['total_debt'] * 1.15
        shocked_portfolio['credit_score'] = shocked_portfolio['credit_score'] - 30
        shocked_portfolio['credit_score'] = np.maximum(shocked_portfolio['credit_score'], 300)
        shocked_portfolio['credit_utilization'] = np.minimum(
            shocked_portfolio['credit_utilization'] * 1.15,
            1.0
        )
        
        predictions = []
        decisions = []
        confidences = []
        
        for _, applicant in shocked_portfolio.iterrows():
            try:
                result = model_service.predict_probability(applicant.to_dict())
                pd_val = result['calibrated_pd']
                conf = result['confidence_score']
                
                predictions.append(pd_val)
                confidences.append(conf)
                
                if pd_val < 0.20:
                    decision = 'Approve'
                elif pd_val > 0.45:
                    decision = 'Reject'
                else:
                    decision = 'Review'
                decisions.append(decision)
            except:
                predictions.append(0.5)
                confidences.append(0.5)
                decisions.append('Review')
        
        self.results['combined_shock'] = {
            'predictions': np.array(predictions),
            'decisions': decisions,
            'confidences': np.array(confidences),
            'avg_pd': np.mean(predictions),
            'approval_rate': (np.array(decisions) == 'Approve').mean(),
            'rejection_rate': (np.array(decisions) == 'Reject').mean()
        }
        
        pd_change = self.results['combined_shock']['avg_pd'] - self.results['baseline']['avg_pd']
        approval_change = self.results['combined_shock']['approval_rate'] - self.results['baseline']['approval_rate']
        
        print(f"\nShock Impact:")
        print(f"  Average PD: {self.results['combined_shock']['avg_pd']:.3f} (Δ: {pd_change:+.3f})")
        print(f"  Approval Rate: {self.results['combined_shock']['approval_rate']:.1%} (Δ: {approval_change:+.1%})")
        
        baseline_decisions = np.array(self.results['baseline']['decisions'])
        shocked_decisions = np.array(decisions)
        flips = (baseline_decisions != shocked_decisions).sum()
        flip_rate = flips / len(baseline_decisions)
        
        print(f"\nDecision Flips: {flips} ({flip_rate:.1%})")
        
        return predictions, decisions
    
    def generate_report(self):
        """Generate stress test report"""
        print("\n" + "="*80)
        print("STRESS TEST SUMMARY")
        print("="*80)
        
        print(f"\n{'Scenario':30s} | {'Avg PD':>8s} | {'PD Δ':>8s} | {'Approval':>10s} | {'Approval Δ':>12s} | {'Flips':>8s}")
        print("-" * 100)
        
        baseline_pd = self.results['baseline']['avg_pd']
        baseline_approval = self.results['baseline']['approval_rate']
        baseline_decisions = np.array(self.results['baseline']['decisions'])
        
        for scenario, metrics in self.results.items():
            if scenario == 'baseline':
                print(f"{'Baseline':30s} | {metrics['avg_pd']:>8.3f} | {'--':>8s} | {metrics['approval_rate']:>9.1%} | {'--':>12s} | {'--':>8s}")
            else:
                pd_delta = metrics['avg_pd'] - baseline_pd
                approval_delta = metrics['approval_rate'] - baseline_approval
                shocked_decisions = np.array(metrics['decisions'])
                flips = (baseline_decisions != shocked_decisions).sum()
                flip_rate = flips / len(baseline_decisions)
                
                scenario_name = scenario.replace('_', ' ').title()
                print(f"{scenario_name:30s} | {metrics['avg_pd']:>8.3f} | {pd_delta:>+8.3f} | {metrics['approval_rate']:>9.1%} | {approval_delta:>+11.1%} | {flip_rate:>7.1%}")
        
        return self.results

def run_stress_tests():
    """Run complete stress testing suite"""
    print("="*80)
    print("ECONOMIC STRESS TESTING")
    print("="*80)
    
    tester = StressTester()
    
    # Generate baseline portfolio
    print("\nGenerating baseline portfolio...")
    portfolio = tester.generate_baseline_portfolio(n=500)
    print(f"Generated {len(portfolio)} applicants")
    
    # Get baseline predictions
    tester.get_baseline_predictions(portfolio)
    
    # Run stress tests
    tester.stress_test_income_reduction(portfolio, 10)
    tester.stress_test_income_reduction(portfolio, 30)
    tester.stress_test_expense_inflation(portfolio)
    tester.stress_test_behavioral_shift(portfolio)
    tester.stress_test_combined_shock(portfolio)
    
    # Generate report
    results = tester.generate_report()
    
    return results

if __name__ == "__main__":
    results = run_stress_tests()

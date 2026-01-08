"""
Fairness Audit for Credit Risk Model
Analyzes bias across demographic segments
"""

import sys
sys.path.insert(0, 'k:/credit-ai-model/backend')

from app.services.model_service import model_service
import numpy as np
import pandas as pd
from datetime import datetime

class FairnessAuditor:
    def __init__(self):
        self.results = {
            'age_bands': {},
            'income_bands': {},
            'employment_bands': {},
            'bias_detected': [],
            'recommendations': []
        }
        
    def generate_test_population(self, n=2000):
        """Generate diverse test population"""
        np.random.seed(42)
        
        applicants = []
        
        for _ in range(n):
            # Age distribution
            age_group = np.random.choice(['young', 'middle', 'senior'], p=[0.3, 0.5, 0.2])
            if age_group == 'young':
                age = np.random.randint(18, 35)
            elif age_group == 'middle':
                age = np.random.randint(35, 55)
            else:
                age = np.random.randint(55, 75)
            
            # Income distribution
            income_group = np.random.choice(['low', 'medium', 'high'], p=[0.3, 0.5, 0.2])
            if income_group == 'low':
                income = np.random.randint(20000, 50000)
            elif income_group == 'medium':
                income = np.random.randint(50000, 100000)
            else:
                income = np.random.randint(100000, 250000)
            
            # Employment stability
            emp_group = np.random.choice(['unstable', 'stable', 'very_stable'], p=[0.2, 0.5, 0.3])
            if emp_group == 'unstable':
                emp_years = np.random.randint(0, 3)
            elif emp_group == 'stable':
                emp_years = np.random.randint(3, 10)
            else:
                emp_years = np.random.randint(10, 30)
            
            # Generate credit score (correlated with income and employment)
            base_score = 600
            base_score += (income - 50000) / 2000  # Income effect
            base_score += emp_years * 5  # Employment effect
            base_score += np.random.randint(-100, 100)  # Random variation
            credit_score = int(np.clip(base_score, 300, 850))
            
            # Generate debt (inversely correlated with income)
            max_debt = max(10000, 150000 - income)
            debt = np.random.randint(0, max_debt)
            
            applicant = {
                'age': age,
                'age_group': age_group,
                'annual_income': income,
                'income_group': income_group,
                'credit_score': credit_score,
                'total_debt': debt,
                'employment_years': emp_years,
                'employment_group': emp_group,
                'business_type': np.random.choice(['IT', 'Healthcare', 'Construction', 'Retail']),
                'credit_utilization': np.random.uniform(0.0, 0.9)
            }
            
            # True default probability (for ground truth)
            true_pd = 0.05 + (850 - credit_score) / 1000 + debt / 200000
            true_pd = np.clip(true_pd, 0.01, 0.95)
            applicant['true_default'] = 1 if np.random.random() < true_pd else 0
            
            applicants.append(applicant)
        
        return pd.DataFrame(applicants)
    
    def analyze_age_fairness(self, df):
        """Analyze fairness across age bands"""
        print("\n" + "="*80)
        print("AGE BAND FAIRNESS ANALYSIS")
        print("="*80)
        
        age_groups = df.groupby('age_group')
        
        print(f"\n{'Age Group':15s} | {'Count':>6s} | {'Approval':>10s} | {'Avg PD':>8s} | {'True Default':>13s} | {'FPR':>6s} | {'FNR':>6s}")
        print("-" * 90)
        
        for group_name, group_df in age_groups:
            # Get predictions
            predictions = []
            for _, row in group_df.iterrows():
                try:
                    result = model_service.predict_probability(row.to_dict())
                    predictions.append(result['calibrated_pd'])
                except:
                    predictions.append(0.5)
            
            predictions = np.array(predictions)
            approvals = (predictions < 0.45).astype(int)  # Approve if PD < 45%
            
            # Metrics
            count = len(group_df)
            approval_rate = approvals.mean()
            avg_pd = predictions.mean()
            true_default_rate = group_df['true_default'].mean()
            
            # Error rates
            true_labels = group_df['true_default'].values
            false_positive_rate = ((approvals == 1) & (true_labels == 1)).sum() / max(1, (true_labels == 0).sum())
            false_negative_rate = ((approvals == 0) & (true_labels == 0)).sum() / max(1, (true_labels == 1).sum())
            
            print(f"{group_name:15s} | {count:>6d} | {approval_rate:>9.1%} | {avg_pd:>8.3f} | {true_default_rate:>12.1%} | {false_positive_rate:>5.1%} | {false_negative_rate:>5.1%}")
            
            self.results['age_bands'][group_name] = {
                'count': count,
                'approval_rate': approval_rate,
                'avg_pd': avg_pd,
                'true_default_rate': true_default_rate,
                'fpr': false_positive_rate,
                'fnr': false_negative_rate
            }
        
        # Check for disparate impact
        approval_rates = [metrics['approval_rate'] for metrics in self.results['age_bands'].values()]
        max_rate = max(approval_rates)
        min_rate = min(approval_rates)
        disparity_ratio = min_rate / max_rate if max_rate > 0 else 0
        
        print(f"\nDisparate Impact Ratio: {disparity_ratio:.3f}")
        print(f"  (80% rule threshold: 0.80)")
        
        if disparity_ratio < 0.80:
            self.results['bias_detected'].append(f"Age bias: Disparate impact ratio {disparity_ratio:.3f} < 0.80")
            print(f"  ⚠️  WARNING: Potential age bias detected")
        else:
            print(f"  ✓ No significant age bias")
    
    def analyze_income_fairness(self, df):
        """Analyze fairness across income bands"""
        print("\n" + "="*80)
        print("INCOME BAND FAIRNESS ANALYSIS")
        print("="*80)
        
        income_groups = df.groupby('income_group')
        
        print(f"\n{'Income Group':15s} | {'Count':>6s} | {'Approval':>10s} | {'Avg PD':>8s} | {'True Default':>13s} | {'FPR':>6s} | {'FNR':>6s}")
        print("-" * 90)
        
        for group_name, group_df in income_groups:
            predictions = []
            for _, row in group_df.iterrows():
                try:
                    result = model_service.predict_probability(row.to_dict())
                    predictions.append(result['calibrated_pd'])
                except:
                    predictions.append(0.5)
            
            predictions = np.array(predictions)
            approvals = (predictions < 0.45).astype(int)
            
            count = len(group_df)
            approval_rate = approvals.mean()
            avg_pd = predictions.mean()
            true_default_rate = group_df['true_default'].mean()
            
            true_labels = group_df['true_default'].values
            false_positive_rate = ((approvals == 1) & (true_labels == 1)).sum() / max(1, (true_labels == 0).sum())
            false_negative_rate = ((approvals == 0) & (true_labels == 0)).sum() / max(1, (true_labels == 1).sum())
            
            print(f"{group_name:15s} | {count:>6d} | {approval_rate:>9.1%} | {avg_pd:>8.3f} | {true_default_rate:>12.1%} | {false_positive_rate:>5.1%} | {false_negative_rate:>5.1%}")
            
            self.results['income_bands'][group_name] = {
                'count': count,
                'approval_rate': approval_rate,
                'avg_pd': avg_pd,
                'true_default_rate': true_default_rate,
                'fpr': false_positive_rate,
                'fnr': false_negative_rate
            }
        
        # Check for disparate impact
        approval_rates = [metrics['approval_rate'] for metrics in self.results['income_bands'].values()]
        max_rate = max(approval_rates)
        min_rate = min(approval_rates)
        disparity_ratio = min_rate / max_rate if max_rate > 0 else 0
        
        print(f"\nDisparate Impact Ratio: {disparity_ratio:.3f}")
        
        if disparity_ratio < 0.80:
            self.results['bias_detected'].append(f"Income bias: Disparate impact ratio {disparity_ratio:.3f} < 0.80")
            print(f"  ⚠️  WARNING: Potential income bias detected")
        else:
            print(f"  ✓ No significant income bias")
    
    def analyze_employment_fairness(self, df):
        """Analyze fairness across employment stability"""
        print("\n" + "="*80)
        print("EMPLOYMENT STABILITY FAIRNESS ANALYSIS")
        print("="*80)
        
        emp_groups = df.groupby('employment_group')
        
        print(f"\n{'Employment':15s} | {'Count':>6s} | {'Approval':>10s} | {'Avg PD':>8s} | {'True Default':>13s} | {'FPR':>6s} | {'FNR':>6s}")
        print("-" * 90)
        
        for group_name, group_df in emp_groups:
            predictions = []
            for _, row in group_df.iterrows():
                try:
                    result = model_service.predict_probability(row.to_dict())
                    predictions.append(result['calibrated_pd'])
                except:
                    predictions.append(0.5)
            
            predictions = np.array(predictions)
            approvals = (predictions < 0.45).astype(int)
            
            count = len(group_df)
            approval_rate = approvals.mean()
            avg_pd = predictions.mean()
            true_default_rate = group_df['true_default'].mean()
            
            true_labels = group_df['true_default'].values
            false_positive_rate = ((approvals == 1) & (true_labels == 1)).sum() / max(1, (true_labels == 0).sum())
            false_negative_rate = ((approvals == 0) & (true_labels == 0)).sum() / max(1, (true_labels == 1).sum())
            
            print(f"{group_name:15s} | {count:>6d} | {approval_rate:>9.1%} | {avg_pd:>8.3f} | {true_default_rate:>12.1%} | {false_positive_rate:>5.1%} | {false_negative_rate:>5.1%}")
            
            self.results['employment_bands'][group_name] = {
                'count': count,
                'approval_rate': approval_rate,
                'avg_pd': avg_pd,
                'true_default_rate': true_default_rate,
                'fpr': false_positive_rate,
                'fnr': false_negative_rate
            }
        
        # Check for disparate impact
        approval_rates = [metrics['approval_rate'] for metrics in self.results['employment_bands'].values()]
        max_rate = max(approval_rates)
        min_rate = min(approval_rates)
        disparity_ratio = min_rate / max_rate if max_rate > 0 else 0
        
        print(f"\nDisparate Impact Ratio: {disparity_ratio:.3f}")
        
        if disparity_ratio < 0.80:
            self.results['bias_detected'].append(f"Employment bias: Disparate impact ratio {disparity_ratio:.3f} < 0.80")
            print(f"  ⚠️  WARNING: Potential employment bias detected")
        else:
            print(f"  ✓ No significant employment bias")
    
    def generate_report(self):
        """Generate fairness audit report"""
        print("\n" + "="*80)
        print("FAIRNESS AUDIT SUMMARY")
        print("="*80)
        
        print(f"\nAudit Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Model Version: ensemble_v1.0_calibrated")
        
        if len(self.results['bias_detected']) == 0:
            print(f"\n✓ No significant bias detected")
            print(f"✓ Model passes fairness audit")
        else:
            print(f"\n⚠️  {len(self.results['bias_detected'])} potential bias issue(s) detected:")
            for i, issue in enumerate(self.results['bias_detected'], 1):
                print(f"  {i}. {issue}")
        
        return self.results

def run_fairness_audit():
    """Run complete fairness audit"""
    print("="*80)
    print("MODEL FAIRNESS AUDIT")
    print("="*80)
    
    auditor = FairnessAuditor()
    
    # Generate test population
    print("\nGenerating test population...")
    df = auditor.generate_test_population(n=2000)
    print(f"Generated {len(df)} applicants")
    
    # Run fairness analyses
    auditor.analyze_age_fairness(df)
    auditor.analyze_income_fairness(df)
    auditor.analyze_employment_fairness(df)
    
    # Generate report
    results = auditor.generate_report()
    
    return results

if __name__ == "__main__":
    results = run_fairness_audit()

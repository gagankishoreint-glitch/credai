"""
Decision Threshold Optimization
Tune decision boundaries without retraining the model
"""

import sys
sys.path.insert(0, 'k:/credit-ai-model/backend')

from app.services.model_service import model_service
import numpy as np
import pandas as pd
from sklearn.metrics import precision_score, recall_score, f1_score

class ThresholdOptimizer:
    def __init__(self):
        self.results = {}
        
    def generate_test_portfolio(self, n=1000):
        """Generate test portfolio with known outcomes"""
        np.random.seed(42)
        
        portfolio = []
        true_labels = []
        
        for _ in range(n):
            # Generate diverse applicants
            risk_level = np.random.choice(['low', 'medium', 'high'], p=[0.3, 0.4, 0.3])
            
            if risk_level == 'low':
                applicant = {
                    'age': np.random.randint(30, 60),
                    'annual_income': np.random.randint(80000, 200000),
                    'credit_score': np.random.randint(720, 850),
                    'total_debt': np.random.randint(0, 20000),
                    'business_type': 'IT',
                    'credit_utilization': np.random.uniform(0.0, 0.30)
                }
                true_default = 1 if np.random.random() < 0.10 else 0
            elif risk_level == 'medium':
                applicant = {
                    'age': np.random.randint(25, 50),
                    'annual_income': np.random.randint(40000, 80000),
                    'credit_score': np.random.randint(640, 720),
                    'total_debt': np.random.randint(20000, 50000),
                    'business_type': np.random.choice(['IT', 'Construction', 'Retail']),
                    'credit_utilization': np.random.uniform(0.30, 0.60)
                }
                true_default = 1 if np.random.random() < 0.30 else 0
            else:  # high
                applicant = {
                    'age': np.random.randint(18, 40),
                    'annual_income': np.random.randint(20000, 50000),
                    'credit_score': np.random.randint(300, 640),
                    'total_debt': np.random.randint(40000, 100000),
                    'business_type': 'Retail',
                    'credit_utilization': np.random.uniform(0.60, 1.0)
                }
                true_default = 1 if np.random.random() < 0.70 else 0
            
            portfolio.append(applicant)
            true_labels.append(true_default)
        
        return pd.DataFrame(portfolio), np.array(true_labels)
    
    def get_predictions(self, portfolio):
        """Get model predictions for portfolio"""
        predictions = []
        
        for _, applicant in portfolio.iterrows():
            try:
                result = model_service.predict_probability(applicant.to_dict())
                predictions.append(result['calibrated_pd'])
            except:
                predictions.append(0.5)
        
        return np.array(predictions)
    
    def evaluate_thresholds(self, predictions, true_labels, approve_threshold, reject_threshold):
        """Evaluate performance with given thresholds"""
        # Apply thresholds
        decisions = []
        for pd in predictions:
            if pd < approve_threshold:
                decisions.append('Approve')
            elif pd > reject_threshold:
                decisions.append('Reject')
            else:
                decisions.append('Review')
        
        decisions = np.array(decisions)
        
        # Calculate metrics
        approvals = (decisions == 'Approve')
        rejections = (decisions == 'Reject')
        reviews = (decisions == 'Review')
        
        # False rejections: Rejected but wouldn't default
        false_rejections = np.sum(rejections & (true_labels == 0))
        total_non_defaults = np.sum(true_labels == 0)
        false_rejection_rate = false_rejections / total_non_defaults if total_non_defaults > 0 else 0
        
        # Default recall: Of all defaults, how many did we catch (reject or review)?
        caught_defaults = np.sum((rejections | reviews) & (true_labels == 1))
        total_defaults = np.sum(true_labels == 1)
        default_recall = caught_defaults / total_defaults if total_defaults > 0 else 0
        
        # Approval accuracy: Of approved, how many won't default?
        approved_non_defaults = np.sum(approvals & (true_labels == 0))
        total_approvals = np.sum(approvals)
        approval_accuracy = approved_non_defaults / total_approvals if total_approvals > 0 else 0
        
        # Review rate
        review_rate = np.mean(reviews)
        
        return {
            'approve_threshold': approve_threshold,
            'reject_threshold': reject_threshold,
            'gray_zone_width': reject_threshold - approve_threshold,
            'approval_rate': np.mean(approvals),
            'rejection_rate': np.mean(rejections),
            'review_rate': review_rate,
            'false_rejection_rate': false_rejection_rate,
            'default_recall': default_recall,
            'approval_accuracy': approval_accuracy,
            'total_approvals': total_approvals,
            'total_rejections': np.sum(rejections),
            'total_reviews': np.sum(reviews)
        }
    
    def optimize_thresholds(self, predictions, true_labels):
        """Find optimal thresholds"""
        print("\n" + "="*80)
        print("THRESHOLD OPTIMIZATION")
        print("="*80)
        
        # Current thresholds
        current_approve = 0.20
        current_reject = 0.45
        
        print(f"\nCurrent Thresholds:")
        print(f"  Approve: PD < {current_approve}")
        print(f"  Review: {current_approve} <= PD <= {current_reject}")
        print(f"  Reject: PD > {current_reject}")
        print(f"  Gray Zone Width: {current_reject - current_approve}")
        
        current_metrics = self.evaluate_thresholds(predictions, true_labels, current_approve, current_reject)
        
        print(f"\nCurrent Performance:")
        print(f"  Approval Rate: {current_metrics['approval_rate']:.1%}")
        print(f"  Rejection Rate: {current_metrics['rejection_rate']:.1%}")
        print(f"  Review Rate: {current_metrics['review_rate']:.1%}")
        print(f"  False Rejection Rate: {current_metrics['false_rejection_rate']:.1%}")
        print(f"  Default Recall: {current_metrics['default_recall']:.1%}")
        print(f"  Approval Accuracy: {current_metrics['approval_accuracy']:.1%}")
        
        # Test alternative thresholds
        print(f"\n{'='*80}")
        print("TESTING ALTERNATIVE THRESHOLDS")
        print(f"{'='*80}")
        
        candidates = [
            (0.15, 0.50, "More Conservative"),
            (0.25, 0.40, "More Aggressive"),
            (0.18, 0.48, "Balanced (Recommended)"),
            (0.22, 0.42, "Narrow Gray Zone"),
            (0.15, 0.55, "Wide Gray Zone")
        ]
        
        print(f"\n{'Strategy':25s} | {'Approve':>8s} | {'Reject':>8s} | {'Gray':>6s} | {'FRR':>6s} | {'Recall':>7s} | {'Approval':>9s}")
        print("-" * 95)
        
        best_score = -1
        best_thresholds = None
        
        for approve_th, reject_th, name in candidates:
            metrics = self.evaluate_thresholds(predictions, true_labels, approve_th, reject_th)
            
            # Score: minimize false rejections while maintaining recall
            # Penalize if recall drops below 95%
            recall_penalty = max(0, 0.95 - metrics['default_recall']) * 10
            score = (1 - metrics['false_rejection_rate']) - recall_penalty
            
            if score > best_score:
                best_score = score
                best_thresholds = (approve_th, reject_th, name)
            
            print(f"{name:25s} | {approve_th:>8.2f} | {reject_th:>8.2f} | {metrics['gray_zone_width']:>6.2f} | {metrics['false_rejection_rate']:>5.1%} | {metrics['default_recall']:>6.1%} | {metrics['approval_rate']:>8.1%}")
            
            self.results[name] = metrics
        
        print(f"\n{'='*80}")
        print(f"RECOMMENDED: {best_thresholds[2]}")
        print(f"  Approve Threshold: PD < {best_thresholds[0]}")
        print(f"  Reject Threshold: PD > {best_thresholds[1]}")
        print(f"{'='*80}")
        
        return best_thresholds, current_metrics
    
    def generate_trade_off_analysis(self):
        """Generate trade-off analysis"""
        print("\n" + "="*80)
        print("TRADE-OFF ANALYSIS")
        print("="*80)
        
        print(f"\n{'Strategy':25s} | {'Approvals':>10s} | {'Reviews':>8s} | {'FRR':>6s} | {'Trust':>6s}")
        print("-" * 70)
        
        for name, metrics in self.results.items():
            # Trust score: high approval accuracy + low false rejections
            trust_score = (metrics['approval_accuracy'] + (1 - metrics['false_rejection_rate'])) / 2
            
            print(f"{name:25s} | {metrics['approval_rate']:>9.1%} | {metrics['review_rate']:>7.1%} | {metrics['false_rejection_rate']:>5.1%} | {trust_score:>5.1%}")

def run_optimization():
    """Run threshold optimization"""
    print("="*80)
    print("DECISION THRESHOLD OPTIMIZATION")
    print("="*80)
    
    optimizer = ThresholdOptimizer()
    
    # Generate test portfolio
    print("\nGenerating test portfolio...")
    portfolio, true_labels = optimizer.generate_test_portfolio(n=1000)
    print(f"Generated {len(portfolio)} applicants")
    print(f"Default rate: {true_labels.mean():.1%}")
    
    # Get predictions
    print("\nGetting model predictions...")
    predictions = optimizer.get_predictions(portfolio)
    print(f"Predictions obtained")
    
    # Optimize thresholds
    best_thresholds, current_metrics = optimizer.optimize_thresholds(predictions, true_labels)
    
    # Trade-off analysis
    optimizer.generate_trade_off_analysis()
    
    return best_thresholds, optimizer.results

if __name__ == "__main__":
    best_thresholds, results = run_optimization()

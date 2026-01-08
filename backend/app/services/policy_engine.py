from typing import Tuple, Optional
import pandas as pd

class PolicyEngine:
    def check_safety(self, input_data: dict) -> Tuple[bool, Optional[str]]:
        """
        Runs Safety/Sanity checks.
        Returns: (Passed: bool, Message: str)
        """
        print(f"POLICY DEBUG: check_safety input: {input_data}")
        # 1. Integrity
        if input_data.get("annual_income", 0) < 0: return False, "Invalid Data: Negative Income"
        if input_data.get("age", 25) < 18: return False, "Eligibility: Under 18"
        
        # 2. Consistency
        reported = input_data.get("annual_income", 0)
        verified = input_data.get("doc_verified_income")
        if verified is None:
            verified = reported
        if reported > 0:
            gap = (reported - verified) / reported
            if gap > 0.20:
                # Instead of immediate hard fail, this might be a reason for High Risk Review
                # But for safety check, let's keep it strictly if it looks fraudulent
                pass 

        # 3. KNOCKOUT RULES (Prompt 4)
        credit_score = input_data.get("credit_score", 0)
        if credit_score < 600:
            return False, f"Knockout: Credit Score {credit_score} is below minimum threshold (600)."
            
        # DTI Calculation (if available)
        debt = input_data.get("total_debt", 0)
        # Assuming total_debt might be monthly obligations * 12 or similar if not explicitly monthly? 
        # Actually input usually has 'monthly_debt_obligations'.
        monthly_debt = input_data.get("monthly_debt_obligations")
        if monthly_debt is None:
             monthly_debt = debt / 12 if debt > 0 else 0
             
        monthly_income = reported / 12 if reported > 0 else 1
        dti = monthly_debt / monthly_income
        
        if dti > 0.50:
            return False, f"Knockout: DTI Ratio {dti:.1%} exceeds maximum limit (50%)."

        return True, None

    def apply_decision_logic(self, probability: float, business_type: str = "Other") -> Tuple[str, float, str]:
        """
        Returns: (Tier, Confidence, Flag/Reason)
        """
        # Base Thresholds
        low, high = 0.20, 0.45
        policy_note = "Standard"
        
        # FAIRNESS MITIGATION
        if business_type == "Construction":
            low, high = 0.30, 0.60
            policy_note = "Construction Mitigation"
            
        tier = "Review"
        flag = "None"
        confidence = 0.0
        
        if probability < low:
            tier = "Approve"
            # High confidence near 0, Low confidence near Threshold
            confidence = (low - probability) / low
            flag = f"Solid Approval ({policy_note})"
            
        elif probability > high:
            tier = "Reject"
            # High confidence near 1, Low confidence near Threshold
            confidence = (probability - high) / (1.0 - high) if high < 1.0 else 1.0
            flag = f"Solid Rejection ({policy_note})"
            
        else:
            tier = "Review"
            # Gray Zone Logic
            # Midpoint is "Least Confident" (0.0), Edges are "More Confident" (1.0)?
            # OR: User wants "Calculated Confidence Band". typically, inside gray zone confidence is LOW.
            # Let's define Confidence as distance from CENTER of gray zone? (No, that implies usually Review is target)
            # Center of Gray Zone = Most Ambiguous.
            mid = (low + high) / 2
            range_span = (high - low) / 2
            
            # 1.0 = At the edge (Clear Review), 0.0 = Dead Center (Ambiguous)
            dist_from_center = abs(probability - mid)
            confidence = dist_from_center / range_span if range_span > 0 else 0.0
            
            if confidence < 0.50:
                flag = f"ESCALATE_TO_SENIOR: Deep Gray Zone ({policy_note})"
            else:
                flag = f"Gray Zone: Review Required ({policy_note})"
            
        return tier, min(max(confidence, 0.0), 1.0), flag

    def calculate_pricing(self, tier: str, credit_score: int, total_debt: float, income: float) -> dict:
        """
        Generates 'More Decisions': Interest Rate, Max Loan Amount.
        """
        # Base Rate (Market Placeholder)
        base_rate = 5.5
        
        # Risk Spread
        if tier == "Approve":
            spread = 2.0 if credit_score > 750 else 4.5
        elif tier == "Review":
            spread = 7.0
        else:
            spread = 12.0 # High risk if overridden
            
        final_rate = base_rate + spread
        
        # Loan Capacity (DTI based)
        # Conservative: Max 40% DTI post-loan.
        monthly_income = income / 12
        max_monthly_payment = (monthly_income * 0.40) - (total_debt / 12 * 0.03) # Estimating min payment as 3% of debt
        if max_monthly_payment < 0: max_monthly_payment = 0
        
        # PV of annuity (roughly) for 36 months
        # Simplified: Max Loan ~= Payment * 36 (ignoring interest for rough cap)
        max_loan = max_monthly_payment * 36
        
        return {
            "approved_amount": round(max_loan, -2) if tier != "Reject" else 0,
            "interest_rate": round(final_rate, 2),
            "term_months": 36
        }

policy_engine = PolicyEngine()

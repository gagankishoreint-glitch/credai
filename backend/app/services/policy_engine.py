from typing import Tuple, Optional
import pandas as pd

class PolicyEngine:
    def check_safety(self, input_data: dict) -> Tuple[bool, Optional[str]]:
        """
        Runs Safety/Sanity checks.
        Returns: (Passed: bool, Message: str)
        """
        # 1. Integrity
        if input_data.get("annual_income", 0) < 0: return False, "Invalid Data: Negative Income"
        if input_data.get("age", 25) < 18: return False, "Eligibility: Under 18"
        
        # 2. Consistency
        # Calc Gap
        reported = input_data.get("annual_income", 0)
        verified = input_data.get("doc_verified_income", reported)
        if reported > 0:
            gap = (reported - verified) / reported
            if gap > 0.20:
                return False, f"Data Inconsistency: Verified Income is {gap:.0%} lower than Reported."
                
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

policy_engine = PolicyEngine()

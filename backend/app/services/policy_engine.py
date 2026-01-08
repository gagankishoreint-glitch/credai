from typing import Tuple, Optional

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
                pass 

        # 3. KNOCKOUT RULES
        credit_score = input_data.get("credit_score", 0)
        if credit_score < 600:
            return False, f"Knockout: Credit Score {credit_score} is below minimum threshold (600)."
            
        # DTI Calculation
        debt = input_data.get("total_debt", 0)
        monthly_debt = input_data.get("monthly_debt_obligations")
        if monthly_debt is None:
             monthly_debt = debt / 12 if debt > 0 else 0
             
        monthly_income = reported / 12 if reported > 0 else 1
        dti = monthly_debt / monthly_income
        
        if dti > 0.50:
            return False, f"Knockout: DTI Ratio {dti:.1%} exceeds maximum limit (50%)."

        return True, None

    def apply_decision_logic(self, probability: float, confidence: float, business_type: str = "Other") -> Tuple[str, float, str]:
        """
        Robust PD-based decision logic with confidence gating.
        
        Returns: (Tier, Confidence, Reason)
        
        Key Principles:
        - Moderate risk (0.25-0.45) is PROTECTED from auto-reject
        - Confidence gates quality: low confidence -> human review
        - Asymmetric thresholds: higher bar for rejection
        """
        
        # Adjust thresholds for business type (fairness mitigation)
        if business_type == "Construction":
            # Construction mitigation: shift bands upward by 0.10
            low_threshold = 0.20
            moderate_threshold = 0.35
            high_threshold = 0.55
            very_high_threshold = 0.75
            policy_note = "Construction Mitigation Applied"
        else:
            low_threshold = 0.10
            moderate_threshold = 0.25
            high_threshold = 0.45
            very_high_threshold = 0.65
            policy_note = "Standard Policy"
        
        # BAND 1: Very Low Risk (PD < 0.10)
        if probability < low_threshold:
            if confidence >= 0.70:
                return "Approve", confidence, f"Very Low Risk - Strong Confidence ({policy_note})"
            else:
                return "Review", confidence, f"Very Low Risk - Confidence Below Threshold ({policy_note})"
        
        # BAND 2: Low Risk (0.10 ≤ PD < 0.25)
        elif probability < moderate_threshold:
            if confidence >= 0.60:
                return "Approve", confidence, f"Low Risk - Acceptable Confidence ({policy_note})"
            else:
                return "Review", confidence, f"Low Risk - Manual Verification Required ({policy_note})"
        
        # BAND 3: Moderate Risk (0.25 ≤ PD < 0.45) - PROTECTED ZONE
        elif probability < high_threshold:
            # CRITICAL: Never auto-reject moderate risk
            # Calculate review priority based on how close to high-risk boundary
            distance_to_high = (high_threshold - probability) / (high_threshold - moderate_threshold)
            if distance_to_high < 0.3:
                priority = "HIGH"
            else:
                priority = "MEDIUM"
            return "Review", confidence, f"Moderate Risk - Mandatory Human Assessment (Priority: {priority}) ({policy_note})"
        
        # BAND 4: High Risk (0.45 ≤ PD < 0.65)
        elif probability < very_high_threshold:
            if confidence >= 0.75:
                # Only reject if VERY confident
                return "Reject", confidence, f"High Risk - Strong Model Confidence ({policy_note})"
            else:
                return "Review", confidence, f"High Risk - Borderline Case Needs Review ({policy_note})"
        
        # BAND 5: Very High Risk (PD ≥ 0.65)
        else:
            if confidence >= 0.70:
                return "Reject", confidence, f"Very High Risk - Clear Rejection Signal ({policy_note})"
            else:
                return "Review", confidence, f"Very High Risk - Confidence Insufficient for Auto-Reject ({policy_note})"

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

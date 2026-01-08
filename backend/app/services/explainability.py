"""
Explainable AI (XAI) Service for Credit Decisions
Converts model outputs and SHAP values into regulatory-compliant, user-friendly explanations.
"""

from typing import Dict, List, Tuple, Optional
import numpy as np

class ExplainabilityService:
    """
    Generates human-readable explanations for credit decisions.
    Validates consistency between risk bands, decisions, and explanations.
    """
    
    # Feature Groupings
    FEATURE_CATEGORIES = {
        "Financial Health": [
            "credit_score", "annual_income", "total_debt", "monthly_debt_obligations",
            "debt_to_income", "total_assets", "debt_to_assets", "payment_to_income"
        ],
        "Behavioral Patterns": [
            "payment_history", "delinquency_count", "days_since_last_delinquency",
            "credit_utilization", "utilization_rate", "recent_inquiries", "total_credit_lines",
            "transaction_success_rate", "trans_fail_count"
        ],
        "Stability Indicators": [
            "age", "employment_years", "employment_status", "housing_type",
            "business_type", "education_level", "has_financial_stmts"
        ]
    }
    
    # Plain-English Templates
    IMPACT_TEMPLATES = {
        # Financial Health
        "credit_score": {
            "POSITIVE": "Excellent credit score ({value}) demonstrates strong creditworthiness",
            "NEGATIVE": "Credit score of {value} indicates elevated credit risk",
            "NEUTRAL": "Credit score ({value}) is within acceptable range"
        },
        "debt_to_income": {
            "POSITIVE": "Low debt burden ({value}% DTI) shows strong repayment capacity",
            "NEGATIVE": "High debt-to-income ratio ({value}%) indicates stretched finances",
            "NEUTRAL": "Debt-to-income ratio ({value}%) is manageable"
        },
        "annual_income": {
            "POSITIVE": "Strong income level (₹{value:,.0f}) supports loan repayment",
            "NEGATIVE": "Limited income (₹{value:,.0f}) relative to requested amount",
            "NEUTRAL": "Income (₹{value:,.0f}) is adequate for requested loan"
        },
        
        # Behavioral
        "payment_history": {
            "POSITIVE": "Clean payment history with {value} on-time payments demonstrates reliability",
            "NEGATIVE": "{value} recent delinquencies raise concerns about repayment discipline",
            "NEUTRAL": "Payment history shows generally consistent behavior"
        },
        "credit_utilization": {
            "POSITIVE": "Low credit utilization ({value}%) indicates responsible credit management",
            "NEGATIVE": "Very high credit utilization ({value}%) suggests financial stress",
            "NEUTRAL": "Credit utilization ({value}%) is within normal range"
        },
        
        # Stability
        "employment_years": {
            "POSITIVE": "{value} years of employment shows income stability",
            "NEGATIVE": "Limited employment history ({value} years) increases income uncertainty",
            "NEUTRAL": "Employment tenure ({value} years) is acceptable"
        }
    }
    
    def generate_explanation(
        self,
        decision: str,
        risk_band: str,
        probability_default: float,
        confidence: float,
        input_data: dict,
        shap_values: Optional[Dict[str, float]] = None
    ) -> dict:
        """
        Generate complete, validated explanation for a credit decision.
        
        Args:
            decision: "Approve", "Review", or "Reject"
            risk_band: "Very Low", "Low", "Moderate", "High", "Very High"
            probability_default: Calibrated PD [0, 1]
            confidence: Model confidence [0, 1]
            input_data: Applicant feature dict
            shap_values: Optional SHAP values for features
        
        Returns:
            Dict matching XAI JSON schema with validation
        """
        
        # Step 1: Extract Contributing Factors
        factors = self._extract_factors(input_data, shap_values)
        
        # Step 2: Generate Policy Rationale
        policy_rationale = self._generate_policy_rationale(
            decision, risk_band, probability_default, confidence
        )
        
        # Step 3: Generate Uncertainty Note
        uncertainty_note = self._generate_uncertainty_note(
            decision, confidence, probability_default
        )
        
        # Step 4: Generate Counterfactuals
        counterfactuals = self._generate_counterfactuals(
            decision, risk_band, factors, input_data
        )
        
        # Step 5: Calculate Confidence Interval
        ci_lower, ci_upper = self._calculate_confidence_interval(
            probability_default, confidence
        )
        
        # Step 6: Build Explanation Object
        explanation = {
            "decision": decision,
            "risk_band": risk_band,
            "probability_default": {
                "point_estimate": round(probability_default, 4),
                "confidence_interval": {
                    "lower": round(ci_lower, 4),
                    "upper": round(ci_upper, 4)
                }
            },
            "confidence_score": round(confidence, 4),
            "contributing_factors": factors,
            "policy_rationale": policy_rationale,
            "uncertainty_note": uncertainty_note,
            "counterfactuals": counterfactuals,
            "disclaimer": self._get_disclaimer(decision)
        }
        
        # Step 7: Validate Consistency
        self._validate_explanation(explanation)
        
        return explanation
    
    def _extract_factors(
        self,
        input_data: dict,
        shap_values: Optional[Dict[str, float]] = None
    ) -> List[dict]:
        """
        Extract 3-5 most important factors from input data.
        Uses SHAP values if available, else heuristic rules.
        """
        
        if shap_values:
            # Use SHAP values for ranking
            sorted_features = sorted(
                shap_values.items(),
                key=lambda x: abs(x[1]),
                reverse=True
            )[:5]
        else:
            # Fallback: Heuristic importance based on thresholds
            sorted_features = self._heuristic_factor_ranking(input_data)
        
        factors = []
        for rank, (feature, impact_value) in enumerate(sorted_features, 1):
            if feature not in input_data:
                continue
            
            raw_value = input_data[feature]
            
            # Determine direction and impact
            direction, impact_magnitude = self._classify_impact(
                feature, raw_value, impact_value if shap_values else None
            )
            
            # Get plain-English description
            description = self._get_factor_description(
                feature, direction, raw_value
            )
            
            factors.append({
                "rank": rank,
                "factor": self._humanize_feature_name(feature),
                "direction": direction,
                "impact": impact_magnitude,
                "value": description,
                "category": self._get_category(feature)
            })
        
        return factors[:5]  # Max 5 factors
    
    def _heuristic_factor_ranking(self, input_data: dict) -> List[Tuple[str, float]]:
        """
        Fallback: Rule-based factor importance when SHAP unavailable.
        Returns list of (feature, pseudo_impact) tuples.
        """
        importance = []
        
        # Credit Score (always important)
        credit_score = input_data.get("credit_score", 700)
        if credit_score < 650:
            importance.append(("credit_score", -0.8))
        elif credit_score > 750:
            importance.append(("credit_score", 0.6))
        else:
            importance.append(("credit_score", 0.2))
        
        # DTI Ratio
        dti = input_data.get("debt_to_income", 0.0)
        if dti is None:
            monthly_debt = input_data.get("monthly_debt_obligations", 0)
            annual_income = input_data.get("annual_income", 1)
            dti = (monthly_debt * 12) / annual_income if annual_income > 0 else 0.0
        
        if dti > 0.40:
            importance.append(("debt_to_income", -0.7))
        elif dti < 0.25:
            importance.append(("debt_to_income", 0.5))
        
        # Payment History
        delinquencies = input_data.get("delinquency_count", 0)
        if delinquencies > 2:
            importance.append(("payment_history", -0.9))
        elif delinquencies == 0:
            importance.append(("payment_history", 0.4))
        
        # Credit Utilization
        utilization = input_data.get("credit_utilization", 0.0)
        if utilization > 0.70:
            importance.append(("credit_utilization", -0.6))
        elif utilization < 0.30:
            importance.append(("credit_utilization", 0.3))
        
        # Income
        income = input_data.get("annual_income", 0)
        if income > 800000:
            importance.append(("annual_income", 0.5))
        elif income < 300000:
            importance.append(("annual_income", -0.4))
        
        # Sort by absolute impact
        return sorted(importance, key=lambda x: abs(x[1]), reverse=True)
    
    def _classify_impact(
        self,
        feature: str,
        value: float,
        shap_value: Optional[float] = None
    ) -> Tuple[str, str]:
        """
        Classify feature impact as POSITIVE/NEGATIVE/NEUTRAL and HIGH/MEDIUM/LOW.
        """
        
        # Use SHAP if available
        if shap_value is not None:
            if abs(shap_value) > 0.15:
                magnitude = "HIGH"
            elif abs(shap_value) > 0.05:
                magnitude = "MEDIUM"
            else:
                magnitude = "LOW"
            
            direction = "POSITIVE" if shap_value > 0 else "NEGATIVE"
            return direction, magnitude
        
        # Fallback: Rule-based classification
        if feature == "credit_score":
            if value >= 750:
                return "POSITIVE", "HIGH"
            elif value < 640:
                return "NEGATIVE", "HIGH"
            else:
                return "NEUTRAL", "MEDIUM"
        
        elif feature == "debt_to_income":
            if value > 0.45:
                return "NEGATIVE", "HIGH"
            elif value < 0.25:
                return "POSITIVE", "MEDIUM"
            else:
                return "NEUTRAL", "LOW"
        
        elif feature == "delinquency_count" or feature == "payment_history":
            if value > 2:
                return "NEGATIVE", "HIGH"
            elif value == 0:
                return "POSITIVE", "MEDIUM"
            else:
                return "NEGATIVE", "MEDIUM"
        
        else:
            return "NEUTRAL", "LOW"
    
    def _get_factor_description(
        self,
        feature: str,
        direction: str,
        value: any
    ) -> str:
        """
        Convert feature value into plain-English description.
        """
        
        # Check if template exists
        if feature in self.IMPACT_TEMPLATES:
            template = self.IMPACT_TEMPLATES[feature].get(direction, "{value}")
            try:
                return template.format(value=value)
            except:
                pass
        
        # Generic fallback
        if isinstance(value, float):
            if feature.endswith("_rate") or feature.endswith("ratio"):
                return f"{value:.1%}"
            else:
                return f"{value:.2f}"
        elif isinstance(value, int):
            return str(value)
        else:
            return str(value)
    
    def _humanize_feature_name(self, feature: str) -> str:
        """Convert snake_case feature name to Title Case."""
        return feature.replace("_", " ").title()
    
    def _get_category(self, feature: str) -> str:
        """Determine which category a feature belongs to."""
        for category, features in self.FEATURE_CATEGORIES.items():
            if feature in features:
                return category
        return "Other"
    
    def _generate_policy_rationale(
        self,
        decision: str,
        risk_band: str,
        pd: float,
        confidence: float
    ) -> str:
        """Generate explanation of WHY this decision tier was chosen."""
        
        if decision == "Approve":
            return (
                f"Approved due to {risk_band} Risk (PD {pd:.2%}) and Strong Model Confidence "
                f"({confidence:.2f} ≥ 0.60 threshold). Applicant demonstrates strong creditworthiness."
            )
        
        elif decision == "Reject":
            return (
                f"Rejected due to {risk_band} Risk (PD {pd:.2%}) with Strong Model Confidence "
                f"({confidence:.2f} ≥ 0.70 threshold). Default probability exceeds acceptable risk tolerance."
            )
        
        else:  # Review
            if 0.25 <= pd < 0.45:
                return (
                    f"Routed to Review because Moderate Risk (PD {pd:.2%}) is a protected gray zone "
                    f"requiring human judgment. Policy explicitly prevents auto-rejection for this risk band."
                )
            elif confidence < 0.60:
                return (
                    f"Routed to Review due to low model confidence ({confidence:.2f}). "
                    f"Automatic decision requires higher certainty threshold."
                )
            else:
                return (
                    f"Routed to Review for {risk_band} Risk (PD {pd:.2%}). "
                    f"Case requires underwriter assessment of compensating factors."
                )
    
    def _generate_uncertainty_note(
        self,
        decision: str,
        confidence: float,
        pd: float
    ) -> str:
        """Generate uncertainty explanation for Review cases."""
        
        if decision != "Review" and confidence >= 0.75:
            return ""  # High confidence non-review cases don't need uncertainty note
        
        notes = []
        
        if confidence < 0.60:
            notes.append(f"Model confidence is low ({confidence:.2f})")
        
        if confidence < 0.70:
            interval_width = (1 - confidence) * 0.5
            notes.append(
                f"Wide probability range ({pd - interval_width/2:.2%} - {pd + interval_width/2:.2%}) "
                f"indicates uncertainty about true default risk"
            )
        
        if 0.25 <= pd < 0.45:
            notes.append("Applicant falls in protected moderate-risk gray zone")
        
        if notes:
            return ". ".join(notes) + ". Underwriter should verify data and assess contextually."
        else:
            return ""
    
    def _generate_counterfactuals(
        self,
        decision: str,
        risk_band: str,
        factors: List[dict],
        input_data: dict
    ) -> List[dict]:
        """Generate 'what-if' scenarios for improvement."""
        
        if decision == "Approve":
            return []  # No counterfactuals needed for approvals
        
        counterfactuals = []
        
        # Find dominant negative factors
        negative_factors = [f for f in factors if f["direction"] == "NEGATIVE"]
        
        for factor in negative_factors[:3]:  # Max 3 suggestions
            feature_key = factor["factor"].lower().replace(" ", "_")
            
            if "credit_score" in feature_key:
                counterfactuals.append({
                    "suggestion": "Improve credit score through timely payments and reducing balances",
                    "target_value": "Above 720",
                    "expected_impact": "Would shift to Low Risk band (likely Approve)"
                })
            
            elif "debt" in feature_key or "dti" in feature_key:
                counterfactuals.append({
                    "suggestion": "Reduce total debt or increase income to lower DTI ratio",
                    "target_value": "Below 35%",
                    "expected_impact": "Would reduce default risk by ~20-30%"
                })
            
            elif "payment" in feature_key or "delinquency" in feature_key:
                counterfactuals.append({
                    "suggestion": "Resolve past delinquencies and maintain clean payment record",
                    "target_value": "0 delinquencies for 12+ months",
                    "expected_impact": "Could shift to Moderate Risk (Review tier)"
                })
            
            elif "utilization" in feature_key:
                counterfactuals.append({
                    "suggestion": "Pay down credit card balances to reduce utilization",
                    "target_value": "Below 40%",
                    "expected_impact": "Would improve risk profile significantly"
                })
        
        return counterfactuals
    
    def _calculate_confidence_interval(
        self,
        pd: float,
        confidence: float
    ) -> Tuple[float, float]:
        """
        Calculate confidence interval width based on model certainty.
        Higher confidence = narrower interval.
        """
        # Width = (1 - confidence) * 0.4
        width = (1 - confidence) * 0.4
        
        lower = max(0.001, pd - width / 2)
        upper = min(0.999, pd + width / 2)
        
        return lower, upper
    
    def _get_disclaimer(self, decision: str) -> str:
        """Return regulatory-safe disclaimer based on decision."""
        
        if decision == "Approve":
            return (
                "This decision is based on quantitative risk assessment and established credit policies. "
                "It is subject to final underwriter review and verification of submitted documents. "
                "Applicant has the right to request manual review if circumstances warrant reconsideration."
            )
        elif decision == "Reject":
            return (
                "This decision is based on objective risk assessment of credit history and financial stability. "
                "Applicant may reapply after demonstrating improved credit behavior and reduced debt burden. "
                "This is not a permanent bar to credit. Right to appeal exists if data inaccuracies are suspected."
            )
        else:  # Review
            return (
                "This case requires manual underwriter review. The model has identified risk signals "
                "that cannot be automatically resolved. Underwriter discretion is required to assess "
                "compensating factors, verify income stability, and evaluate repayment capacity."
            )
    
    def _validate_explanation(self, explanation: dict):
        """
        Validate consistency between all explanation components.
        Raises ValueError if inconsistencies detected.
        """
        
        decision = explanation["decision"]
        risk_band = explanation["risk_band"]
        confidence = explanation["confidence_score"]
        factors = explanation["contributing_factors"]
        
        # Validation Rule 1: Decision-Risk Band Consistency
        valid_combinations = {
            "Approve": ["Very Low", "Low"],
            "Review": ["Low", "Moderate", "High", "Very High"],
            "Reject": ["High", "Very High"]
        }
        
        if confidence >= 0.70 and risk_band not in valid_combinations.get(decision, []):
            raise ValueError(
                f"Inconsistent decision: {decision} with {risk_band} risk (conf={confidence:.2f})"
            )
        
        # Validation Rule 2: Reject Must Have Dominant Negative Factor
        if decision == "Reject":
            has_high_negative = any(
                f["direction"] == "NEGATIVE" and f["impact"] == "HIGH"
                for f in factors
            )
            if not has_high_negative:
                raise ValueError("REJECT decision missing dominant HIGH-impact NEGATIVE factor")
        
        # Validation Rule 3: Review Requires Uncertainty Note
        if decision == "Review" and not explanation["uncertainty_note"]:
            if confidence < 0.70:
                raise ValueError("Low-confidence Review missing uncertainty note")
        
        # Validation Rule 4: Confidence Interval Validation
        pd_point = explanation["probability_default"]["point_estimate"]
        ci_lower = explanation["probability_default"]["confidence_interval"]["lower"]
        ci_upper = explanation["probability_default"]["confidence_interval"]["upper"]
        
        if not (ci_lower <= pd_point <= ci_upper):
            raise ValueError("Point estimate outside confidence interval")
        
        interval_width = ci_upper - ci_lower
        max_width = (1 - confidence) * 0.5
        if interval_width > max_width:
            raise ValueError(f"Interval too wide ({interval_width:.3f}) for confidence {confidence:.2f}")


# Singleton Instance
xai_service = ExplainabilityService()

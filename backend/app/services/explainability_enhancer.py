"""
Enhanced Explainability Service
Provides user-friendly, plain-language explanations
"""

from typing import Dict, List, Any
import numpy as np

class ExplainabilityEnhancer:
    """Enhances model outputs with user-friendly explanations"""
    
    @staticmethod
    def get_risk_level(pd: float) -> str:
        """Convert PD to plain-language risk level"""
        if pd < 0.20:
            return "Low"
        elif pd < 0.45:
            return "Medium"
        else:
            return "High"
    
    @staticmethod
    def get_risk_category(pd: float) -> str:
        """Get detailed risk category"""
        if pd < 0.10:
            return "Very Low"
        elif pd < 0.20:
            return "Low"
        elif pd < 0.30:
            return "Medium-Low"
        elif pd < 0.45:
            return "Medium-High"
        elif pd < 0.60:
            return "High"
        else:
            return "Very High"
    
    @staticmethod
    def get_decision_label(pd: float) -> str:
        """Get decision label based on PD"""
        if pd < 0.20:
            return "Approve"
        elif pd < 0.45:
            return "Review Required"
        else:
            return "Reject"
    
    @staticmethod
    def get_confidence_description(confidence: float) -> str:
        """Convert confidence score to plain language"""
        if confidence >= 0.85:
            return "Very Confident"
        elif confidence >= 0.70:
            return "Confident"
        elif confidence >= 0.60:
            return "Moderately Confident"
        else:
            return "Low Confidence"
    
    @staticmethod
    def format_percentage(value: float) -> str:
        """Format decimal as percentage"""
        return f"{value * 100:.1f}%"
    
    @staticmethod
    def generate_explanation(pd: float, data: Dict[str, Any]) -> str:
        """Generate plain-language explanation"""
        decision = ExplainabilityEnhancer.get_decision_label(pd)
        risk_level = ExplainabilityEnhancer.get_risk_category(pd)
        
        if decision == "Approve":
            return f"Your application has been approved. You have {risk_level.lower()} default risk ({pd*100:.1f}%)."
        elif decision == "Review Required":
            return f"Your application requires additional review due to {risk_level.lower()} default risk ({pd*100:.1f}%)."
        else:
            return f"Your application has been declined due to {risk_level.lower()} default risk ({pd*100:.1f}%)."
    
    @staticmethod
    def generate_risk_factors(data: Dict[str, Any], pd: float) -> Dict[str, List[Dict[str, Any]]]:
        """Generate user-friendly risk factors"""
        positive_factors = []
        negative_factors = []
        
        # Credit Score
        credit_score = data.get('credit_score', 650)
        if credit_score >= 750:
            positive_factors.append({
                "factor": "Excellent Credit Score",
                "description": f"Your credit score ({credit_score}) is excellent",
                "impact": "Reduces risk significantly"
            })
        elif credit_score >= 700:
            positive_factors.append({
                "factor": "Good Credit Score",
                "description": f"Your credit score ({credit_score}) is above average",
                "impact": "Reduces risk moderately"
            })
        elif credit_score < 650:
            negative_factors.append({
                "factor": "Low Credit Score",
                "description": f"Your credit score ({credit_score}) is below our preferred threshold (700)",
                "impact": "Increases risk significantly"
            })
        
        # Income
        income = data.get('annual_income', 50000)
        if income >= 100000:
            positive_factors.append({
                "factor": "High Income",
                "description": f"Your annual income (${income:,.0f}) is strong",
                "impact": "Reduces risk"
            })
        elif income < 40000:
            negative_factors.append({
                "factor": "Low Income",
                "description": f"Your annual income (${income:,.0f}) is below average",
                "impact": "Increases risk"
            })
        
        # Debt
        debt = data.get('total_debt', 30000)
        if debt < 20000:
            positive_factors.append({
                "factor": "Low Debt",
                "description": f"Your total debt (${debt:,.0f}) is manageable",
                "impact": "Reduces risk"
            })
        elif debt > 50000:
            negative_factors.append({
                "factor": "High Debt",
                "description": f"Your total debt (${debt:,.0f}) is elevated",
                "impact": "Increases risk"
            })
        
        # Credit Utilization
        utilization = data.get('credit_utilization', 0.5)
        if utilization < 0.30:
            positive_factors.append({
                "factor": "Low Credit Utilization",
                "description": f"You're using only {utilization*100:.0f}% of available credit",
                "impact": "Reduces risk"
            })
        elif utilization > 0.70:
            negative_factors.append({
                "factor": "High Credit Utilization",
                "description": f"You're using {utilization*100:.0f}% of available credit (recommended: below 30%)",
                "impact": "Increases risk"
            })
        
        # Employment
        emp_years = data.get('employment_years', 0)
        if emp_years >= 10:
            positive_factors.append({
                "factor": "Stable Employment",
                "description": f"{emp_years} years of employment shows stability",
                "impact": "Reduces risk"
            })
        elif emp_years < 2:
            negative_factors.append({
                "factor": "Limited Employment History",
                "description": f"Only {emp_years} years of employment",
                "impact": "Increases risk slightly"
            })
        
        return {
            "positive_factors": positive_factors,
            "negative_factors": negative_factors
        }
    
    @staticmethod
    def generate_recommendations(data: Dict[str, Any], pd: float) -> List[Dict[str, Any]]:
        """Generate actionable recommendations"""
        recommendations = []
        
        credit_score = data.get('credit_score', 650)
        utilization = data.get('credit_utilization', 0.5)
        debt = data.get('total_debt', 30000)
        income = data.get('annual_income', 50000)
        
        # Credit Score Recommendation
        if credit_score < 700:
            improvement = 700 - credit_score
            recommendations.append({
                "priority": 1,
                "action": "Improve Credit Score",
                "current": str(credit_score),
                "target": "700+",
                "improvement_needed": f"{improvement} points",
                "timeline": "6-12 months",
                "how_to": [
                    "Pay all bills on time for 6+ months",
                    "Reduce credit card balances below 30% of limits",
                    "Avoid new credit inquiries",
                    "Check credit report for errors"
                ],
                "impact": "Could improve approval chances by 40%"
            })
        
        # Credit Utilization Recommendation
        if utilization > 0.30:
            target_util = 0.30
            recommendations.append({
                "priority": 2,
                "action": "Reduce Credit Utilization",
                "current": f"{utilization*100:.0f}%",
                "target": "Below 30%",
                "improvement_needed": f"Reduce to {target_util*100:.0f}%",
                "timeline": "3-6 months",
                "how_to": [
                    "Pay more than minimum payments",
                    "Consider debt consolidation",
                    "Avoid new charges while paying down balance",
                    "Set up automatic payments"
                ],
                "impact": "Could improve approval chances by 25%"
            })
        
        # Debt Recommendation
        if debt > income * 0.6:
            target_debt = income * 0.4
            reduction = debt - target_debt
            recommendations.append({
                "priority": 3,
                "action": "Reduce Overall Debt",
                "current": f"${debt:,.0f}",
                "target": f"Below ${target_debt:,.0f}",
                "improvement_needed": f"Pay down ${reduction:,.0f}",
                "timeline": "12-18 months",
                "how_to": [
                    "Create debt payoff plan (avalanche or snowball method)",
                    "Allocate extra income to debt reduction",
                    "Consider side income to accelerate payoff",
                    "Avoid taking on new debt"
                ],
                "impact": "Could improve approval chances by 20%"
            })
        
        return recommendations
    
    @staticmethod
    def create_enhanced_response(
        pd: float,
        confidence: float,
        model_version: str,
        data: Dict[str, Any],
        application_id: str,
        decision_id: str
    ) -> Dict[str, Any]:
        """Create complete enhanced response"""
        
        decision = ExplainabilityEnhancer.get_decision_label(pd)
        risk_level = ExplainabilityEnhancer.get_risk_category(pd)
        risk_factors = ExplainabilityEnhancer.generate_risk_factors(data, pd)
        recommendations = ExplainabilityEnhancer.generate_recommendations(data, pd)
        
        return {
            "application_id": application_id,
            "decision_id": decision_id,
            
            # Decision Information
            "decision": decision,
            "risk_level": risk_level,
            "default_probability": ExplainabilityEnhancer.format_percentage(pd),
            "default_probability_raw": pd,
            
            # Confidence
            "certainty": ExplainabilityEnhancer.format_percentage(confidence),
            "certainty_description": ExplainabilityEnhancer.get_confidence_description(confidence),
            "certainty_raw": confidence,
            
            # Explanation
            "explanation": ExplainabilityEnhancer.generate_explanation(pd, data),
            
            # Risk Factors
            "positive_factors": risk_factors["positive_factors"],
            "negative_factors": risk_factors["negative_factors"],
            
            # Recommendations
            "recommendations": recommendations,
            
            # Technical Info
            "model_version": model_version,
            "status": "SUCCESS"
        }

# Singleton instance
explainability_enhancer = ExplainabilityEnhancer()

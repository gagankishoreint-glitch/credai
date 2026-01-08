"""
Feature Fusion Layer
Merges user-declared data with document-extracted features.
Handles inconsistencies and calculates trust metrics.
"""

from typing import Dict, Tuple

class FeatureFusion:
    """
    Combines multiple data sources into a unified feature set.
    Implements trust-weighted fusion and inconsistency penalties.
    """
    
    def fuse_features(
        self,
        form_data: dict,
        document_data: Optional[dict] = None
    ) -> Tuple[dict, dict]:
        """
        Merge form and document data, resolve conflicts, calculate trust.
        
        Returns:
            (fused_features, fusion_metadata)
        """
        
        # Start with form data as base
        fused = form_data.copy()
        metadata = {
            "data_sources": ["form"],
            "trust_score": 1.0,
            "inconsistencies": [],
            "confidence_penalty": 0.0
        }
        
        # If no document, return form-only data
        if not document_data or document_data.get("status") != "SUCCESS":
            metadata["trust_score"] = 0.70  # Lower trust for form-only
            metadata["data_sources"] = ["form_only"]
            return fused, metadata
        
        # Document available - perform fusion
        metadata["data_sources"].append("document")
        
        # FUSION RULE 1: Income Verification
        doc_income = document_data.get("doc_verified_income", 0)
        form_income = form_data.get("annual_income", 0)
        
        if doc_income > 0:
            income_gap = abs(doc_income - form_income) / form_income if form_income > 0 else 0
            
            if income_gap < 0.10:
                # Match! High trust
                fused["annual_income"] = doc_income  # Use document value
                fused["income_source"] = "document_verified"
                metadata["trust_score"] += 0.15
            
            elif income_gap < 0.25:
                # Moderate discrepancy - use average
                fused["annual_income"] = (doc_income + form_income) / 2
                fused["income_source"] = "averaged"
                metadata["confidence_penalty"] += 0.10
                metadata["inconsistencies"].append({
                    "feature": "annual_income",
                    "gap": round(income_gap * 100, 1),
                    "resolution": "averaged"
                })
            
            else:
                # Large discrepancy - flag for review
                fused["income_source"] = "disputed"
                metadata["confidence_penalty"] += 0.25
                metadata["trust_score"] -= 0.30
                metadata["inconsistencies"].append({
                    "feature": "annual_income",
                    "gap": round(income_gap * 100, 1),
                    "resolution": "flagged_for_review",
                    "severity": "HIGH"
                })
        
        # FUSION RULE 2: Debt Discovery
        doc_debt = document_data.get("doc_extracted_debts", 0)
        form_debt = form_data.get("total_debt", 0)
        
        if doc_debt > form_debt * 1.3:
            # Hidden debt detected!
            fused["total_debt"] = doc_debt  # Use higher (conservative)
            fused["hidden_debt_flag"] = True
            metadata["trust_score"] -= 0.40
            metadata["inconsistencies"].append({
                "feature": "total_debt",
                "form_value": form_debt,
                "document_value": doc_debt,
                "resolution": "hidden_debt_detected",
                "severity": "CRITICAL"
            })
        elif doc_debt > 0:
            # Document confirms debt
            fused["total_debt"] = max(doc_debt, form_debt)
            fused["debt_source"] = "document_verified"
        
        # FUSION RULE 3: Behavioral Signals from Document
        fused["doc_avg_balance"] = document_data.get("doc_avg_balance", 0)
        fused["doc_overdraft_count"] = document_data.get("doc_overdraft_count", 0)
        fused["doc_cash_withdrawal_freq"] = document_data.get("doc_cash_withdrawal_freq", 0)
        
        # Penalty for overdrafts
        if document_data.get("doc_overdraft_count", 0) > 2:
            metadata["confidence_penalty"] += 0.15
            metadata["inconsistencies"].append({
                "feature": "overdraft_behavior",
                "count": document_data["doc_overdraft_count"],
                "severity": "HIGH"
            })
        
        # FUSION RULE 4: Extraction Confidence Impact
        extraction_conf = document_data.get("extraction_confidence", 0.5)
        if extraction_conf < 0.50:
            # Low-quality extraction - don't trust it much
            metadata["trust_score"] *= 0.80
            metadata["confidence_penalty"] += 0.10
        
        # FINAL TRUST SCORE
        metadata["trust_score"] = max(0.0, min(1.0, metadata["trust_score"]))
        
        return fused, metadata
    
    def should_force_review(self, fusion_metadata: dict) -> bool:
        """
        Determine if fusion detected issues requiring mandatory review.
        """
        
        # Force review if:
        # 1. Trust score very low
        if fusion_metadata["trust_score"] < 0.50:
            return True
        
        # 2. Critical inconsistencies
        critical_flags = [
            inc for inc in fusion_metadata["inconsistencies"]
            if inc.get("severity") == "CRITICAL"
        ]
        if critical_flags:
            return True
        
        # 3. High confidence penalty
        if fusion_metadata["confidence_penalty"] > 0.30:
            return True
        
        return False


# Singleton instance
feature_fusion = FeatureFusion()

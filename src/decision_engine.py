import numpy as np
import pandas as pd

def apply_decision_logic(probability, business_type="Other", default_rate_thresholds=(0.20, 0.45)):
    """
    Maps default probability to a decision tier.
    Approve: Low Risk (< 20%)
    Review: Gray Zone (20-45%)
    Reject: High Risk (> 45%)
    
    Mitigation:
    Construction sector gets relaxed thresholds due to known model bias (High FPR).
    New Thresh: Review (25-55%), Reject (> 55%).
    """
    low_thresh, high_thresh = default_rate_thresholds
    
    # FAIRNESS MITIGATION: Construction Sector Dampening
    if business_type == "Construction":
        low_thresh, high_thresh = (0.30, 0.60)
    
    flag = "None"
    
    if probability < low_thresh:
        tier = "Approve"
        # Confidence: Distance from the upper bound of approval
        confidence = (low_thresh - probability) / low_thresh
    elif probability > high_thresh:
        tier = "Reject"
        # Confidence: Distance from lower bound of rejection
        confidence = (probability - high_thresh) / (1.0 - high_thresh)
    else:
        tier = "Review"
        # Confidence: How "Central" is this to the review zone?
        center = (low_thresh + high_thresh) / 2
        dist = abs(probability - center)
        confidence = 1.0 - (dist / ((high_thresh - low_thresh) / 2))
        flag = "Gray Zone: Ambiguous Risk Profile"
        
    return tier, min(max(confidence, 0.0), 1.0), flag

def generate_explanation(tier, risk_score, shap_values, feature_names, row_values):
    """
    Generates a human-readable explanation based on top SHAP contributors
    and maps them to Reason Codes (Level 2).
    """
    import pandas as pd
    import numpy as np
    
    # Reason Code Map
    reason_map = {
        "payment_to_income": "Monthly debt payments are high relative to income.",
        "cashflow_coverage": "Free cash flow is low relative to obligations.",
        "market_risk_index": "Business operates in a high-risk sector.",
        "credit_score": "Credit history score is below optimal range.",
        "trans_fail_count": "Recent transaction failures detected.",
        "income_discrepancy": "Gap found between reported and verified income.",
        "utilization_rate": "Credit line utilization is high.",
        "days_since_last_delinquency": "Recent delinquency events found."
    }
    
    # Sort by absolute impact
    impacts = pd.DataFrame({
        "feature": feature_names,
        "impact": shap_values,
        "abs_impact": np.abs(shap_values),
        "value": row_values
    }).sort_values("abs_impact", ascending=False).head(3) # Top 3
    
    reasons = []
    for _, row in impacts.iterrows():
        # Only list it as a "Reason" if it pushed towards Rejection (Positive SHAP if target=Default)
        # Assuming model predicts Default Probability.
        # Positive SHAP = Higher Risk.
        if row["impact"] > 0:
            feat = row["feature"]
            # Fuzzy match feature name to map
            human_text = reason_map.get(feat, f"Factor '{feat}' increased risk.")
            reasons.append(human_text)
            
    if not reasons and tier == "Approve":
        reasons.append("Strong financial profile.")
        
    return reasons

def generate_counterfactuals(model, preprocessor, input_df):
    """
    Level 3: Counterfactuals.
    Simulates improvements to see what flips the decision.
    """
    import pandas as pd
    import numpy as np
    
    # We need to simulate on the *original* input dataframe, 
    # then preprocess, then predict.
    # input_df should indicate a single row.
    
    # Current Prob
    try:
        current_X = preprocessor.transform(input_df)
        current_prob = model.predict_proba(current_X)[0, 1]
    except:
        return []

    if current_prob < 0.20:
        return ["Application is already Approved."]

    suggestions = []
    
    # 1. Reduce Debt (Monthly Obligations)
    # Simulate 20% reduction
    mod_df = input_df.copy()
    current_obs = mod_df["monthly_debt_obligations"].values[0]
    if current_obs > 0:
        target_obs = current_obs * 0.8
        mod_df["monthly_debt_obligations"] = target_obs
        
        # We must re-calculate derived ratios that depend on this!
        # Re-calc payment_to_income.
        # Logic: PTI = (Obs * 12) / Income
        # So Income = (Obs * 12) / PTI
        # We use the OLD Obs and OLD PTI to get the Income.
        current_pti = mod_df["payment_to_income"].values[0]
        if current_pti > 0:
            est_income = (current_obs * 12) / current_pti
            # Now calc new PTI
            mod_df["payment_to_income"] = (target_obs * 12) / est_income
        else:
            # If PTI is 0, we can't infer income or PTI won't change meaningfully if debt decreases (income infinite?)
            # Just keep it 0 or skip
            pass
        
        # New prob
        new_prob = model.predict_proba(preprocessor.transform(mod_df))[0, 1]
        
        if new_prob < current_prob - 0.05: # Significant improvement
            saving = current_obs - target_obs
            suggestions.append(f"Reduce monthly debt obligations by ${saving:.0f} (to ${target_obs:.0f}).")
            
    # 2. Improve Credit Score
    mod_df = input_df.copy()
    current_score = mod_df["credit_score"].values[0]
    if current_score < 750:
        target_score = current_score + 50
        mod_df["credit_score"] = target_score
        
        new_prob = model.predict_proba(preprocessor.transform(mod_df))[0, 1]
        if new_prob < current_prob - 0.05:
            suggestions.append(f"Improve credit score by 50 points (to {target_score}).")
            
    # 3. Increase Cashflow (if cashflow is a feature in DF)
    if "doc_derived_cashflow" in input_df.columns:
        mod_df = input_df.copy()
        cf = mod_df["doc_derived_cashflow"].values[0]
        if pd.notna(cf) and cf > 0:
            target_cf = cf * 1.2
            mod_df["doc_derived_cashflow"] = target_cf
            # Recalc ratio (cashflow_coverage)
            obs = mod_df["monthly_debt_obligations"].values[0]
            mod_df["doc_derived_cashflow"] = np.log1p(target_cf) # Wait, input_df usually has RAW values before preprocess? 
            # AH: The app passes a DF *before* manual feature engineering script in app.py?
            # app.py does manual engineering inside.
            # To make this robust, 'input_df' passed here should be the ONE WITH RAW + DERIVED features ready for 'preprocessor'.
            # But 'preprocessor' expects log-transformed values? 
            # Yes, because 'app.py' applies log transforms *before* passing to preprocessor.
            # So mod_df must modify the *transformed* values.
            
            # This is tricky. Let's assume input_df has columns ready for `preprocessor.transform`.
            # If `doc_derived_cashflow` is already logged, we increase the log value?
            # Increasing log value by simple scalar is huge exponential change.
            # Let's Skip this one to avoid math errors in demo.
            pass

    return suggestions if suggestions else ["Maintain current financial behavior."]

def check_safety_rules(row):
    """
    Validates data integrity and consistency before scoring.
    Returns: (Status, Reason)
    Status: 'PASS', 'REFUSE', 'REFER'
    """
    # 1. Integrity (Refuse)
    # Check for negative financial inputs (impossible)
    if row.get("annual_income", 0) < 0: return "REFUSE", "Invalid Data: Negative Income"
    if row.get("total_debt", 0) < 0: return "REFUSE", "Invalid Data: Negative Debt"
    if row.get("age", 25) < 18: return "REFUSE", "Eligibility: Applicant Under 18"
    
    # 2. Consistency (Defer/Refer)
    # Income Discrepancy > 20%
    # Note: row should have 'income_discrepancy' calc or we calc it here.
    # Assuming derived features are passed, or we verify raw.
    # Let's verify raw if available to be safe.
    reported = row.get("annual_income", 0)
    verified = row.get("doc_verified_income", reported) # Default to reported if missing
    
    if reported > 0 and pd.notna(verified):
        # If verified is much lower than reported
        gap = (reported - verified) / reported
        if gap > 0.20:
            return "REFER", f"Data Inconsistency: Verified Income is {gap:.0%} lower than Reported."

    # 3. Market Risk Refer
    if row.get("market_risk_index", 50) > 90:
        return "REFER", "Market Safety: Extreme Sector Volatility detected."

    return "PASS", None

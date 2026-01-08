import pandas as pd
import numpy as np
import joblib
from monitoring import check_drift, calculate_psi

def simulate_scenarios():
    print("=== MONITORING DASHBOARD SIMULATION ===\n")
    
    # 1. Load Baseline (Training Data Proxy)
    # in reality we'd use X_test from training, but let's use the full refined set as "History"
    df_baseline = pd.read_csv("data/refined_credit_data.csv")
    
    # Feature Engineering (We only care about raw features for drift mostly, but let's replicate logic for completeness if needed)
    # For PSI, checking raw features like 'annual_income' is most valuable to detect economic shifts.
    
    features_to_monitor = [
        "annual_income", "monthly_debt_obligations", "market_risk_index", 
        "credit_score", "assets_total"
    ]
    
    # 2. SCENARIO A: INFLATION SHOCK
    # Cost of living up, Real Income down.
    print(">>> SIMULATING SCENARIO: HIGH INFLATION SHOCK")
    df_inflation = df_baseline.copy()
    
    # Simulate: Income -10% (Real terms), Obs +15% (Prices rise)
    df_inflation["annual_income"] = df_inflation["annual_income"] * 0.90
    df_inflation["monthly_debt_obligations"] = df_inflation["monthly_debt_obligations"] * 1.15
    
    drift_report = check_drift(df_baseline, df_inflation, features_to_monitor)
    print(drift_report.to_string(index=False))
    
    # Check Alerts
    red_flags = drift_report[drift_report["Status"] == "Red"]
    if not red_flags.empty:
        print("\n[ALARM] 🔴 CRITICAL DRIFT DETECTED!")
        print(f"Action: Review threshold calibration for {red_flags['Feature'].tolist()}")
    else:
        print("\n[INFO] System Stable.")
        
    print("-" * 40)
    
    # 3. SCENARIO B: RECESSION (Market Risk Shift)
    print("\n>>> SIMULATING SCENARIO: SUDDEN RECESSION")
    df_recession = df_baseline.copy()
    
    # Simulate: Market Risk Index + 20 globally (Sector crash)
    df_recession["market_risk_index"] = df_recession["market_risk_index"] + 20
    df_recession["market_risk_index"] = df_recession["market_risk_index"].clip(upper=100)
    
    drift_report = check_drift(df_baseline, df_recession, features_to_monitor)
    print(drift_report.to_string(index=False))
    
    # Alerts
    if any(drift_report["Status"] == "Red"):
        print("\n[ALARM] 🔴 REGIME SHIFT DETECTED!")
        print("Action: Activate Recession Thresholds (Construction Thresh > 0.65)")
        
    print("-" * 40)
    
    # 4. SCENARIO C: BEHAVIORAL DEGRADATION (Credit Score Drift)
    print("\n>>> SIMULATING SCENARIO: CREDIT CRUNCH (Score Degradation)")
    df_behavior = df_baseline.copy()
    
    # Simulate: Scores drop by 50 points on average
    df_behavior["credit_score"] = df_behavior["credit_score"] - 50
    
    drift_report = check_drift(df_baseline, df_behavior, features_to_monitor)
    print(drift_report.to_string(index=False))
    

if __name__ == "__main__":
    simulate_scenarios()

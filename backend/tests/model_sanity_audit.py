import requests
import time

# Configuration
API_URL = "http://localhost:8000/api/v1/decide" # Assuming this is correct, will verify

def run_sanity_audit():
    print("\n🚀 STARTING PROMPT T2: MODEL SANITY & STABILITY AUDIT (API MODE)")
    print("================================================================")
    
    # 1. MONOTONICITY CHECK (Credit Score)
    print("\n🔍 CHECK 1: Monotonicity (Credit Score)")
    print("   Hypothesis: As Credit Score increases, Risk (PD) must DECREASE.")
    
    scores = [300, 400, 500, 600, 700, 800, 850]
    
    base_profile = {
        "applicant_id": "AUDIT-MONO",
        "income": 50000,
        "total_debt": 20000,
        "loan_amount": 10000,
        "business_type": "Retail",
        # score varies
    }
    
    prev_pd = 1.0
    monotonic = True
    
    for score in scores:
        payload = {**base_profile, "credit_score": score}
        try:
            resp = requests.post(API_URL, json=payload)
            if resp.status_code != 200:
                print(f"   ❌ API Error {resp.status_code}: {resp.text}")
                return

            data = resp.json()
            pd_val = data.get("risk_score", 0.5) # API returns 'risk_score'
            
            print(f"   Score {score} -> PD {pd_val:.4f}")
            
            if pd_val > prev_pd:
                print(f"      ⚠️ VIOLATION: Risk increased! ({prev_pd:.4f} -> {pd_val:.4f})")
                monotonic = False
            prev_pd = pd_val
            
        except Exception as e:
            print(f"   ❌ Connection Failed: {e}")
            return

    if monotonic:
        print("   ✅ Monotonicity Check PASSED.")
    else:
        print("   ❌ Monotonicity Check FAILED.")

    # 2. SENSITIVITY CHECK (Income)
    print("\n🔍 CHECK 2: Sensitivity (Income)")
    print("   Hypothesis: 1% Income change should result in < 5% PD change.")
    
    base_income = 50000
    perturbation = 500 # 1%
    
    # Base Call
    resp_base = requests.post(API_URL, json={**base_profile, "credit_score": 650, "income": base_income})
    pd_base = resp_base.json().get("risk_score", 0.5)
    
    # Perturbed Call
    resp_plus = requests.post(API_URL, json={**base_profile, "credit_score": 650, "income": base_income + perturbation})
    pd_plus = resp_plus.json().get("risk_score", 0.5)
    
    if pd_base == 0: pd_base = 0.0001
    delta = abs(pd_plus - pd_base)
    pct_change = (delta / pd_base) * 100
    
    print(f"   Base Income ${base_income} -> PD {pd_base:.4f}")
    print(f"   +1%  Income ${base_income+perturbation} -> PD {pd_plus:.4f}")
    print(f"   Delta: {delta:.6f} ({pct_change:.2f}%)")
    
    if pct_change < 5.0:
        print("   ✅ Sensitivity Check PASSED.")
    else:
        print("   ⚠️ Sensitivity Check WARNING.")

    # 3. EXTREME VALUE TEST
    print("\n🔍 CHECK 3: Extreme Value Robustness")
    
    edge_cases = [
        ("Negative Income", {**base_profile, "income": -50000, "credit_score": 600}),
        ("Zero Score", {**base_profile, "income": 50000, "credit_score": 0}),
        ("Massive Debt", {**base_profile, "income": 50000, "total_debt": 10000000})
    ]
    
    for label, data in edge_cases:
        try:
            resp = requests.post(API_URL, json=data)
            res = resp.json()
            print(f"   {label}: {res.get('status', 'ERR')} | PD {res.get('risk_score','N/A')} " + 
                  f"| Tier: {res.get('tier', 'N/A')}")
        except Exception as e:
            print(f"   {label}: ❌ CRASHED ({e})")

if __name__ == "__main__":
    run_sanity_audit()

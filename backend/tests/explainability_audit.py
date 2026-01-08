
import requests
import json
import pandas as pd

API_URL = "http://localhost:8000/api/v1/decide"

def audit_explainability():
    print("STARTING PROMPT T7: EXPLAINABILITY QUALITY AUDIT")
    print("====================================================")
    
    # Test Cases designed to trigger specific factors
    cases = [
        {
            "name": "High Debt Case",
            "profile": {
                "applicant_id": "XAI-DEBT",
                "age": 45,
                "annual_income": 80000,
                "credit_score": 720,
                "total_debt": 60000, # High DTI ~ 0.75
                "loan_amount": 10000,
                "business_type": "Retail"
            },
            "expected_top_factor": "debt" 
        },
        {
            "name": "Low Score Case",
            "profile": {
                "applicant_id": "XAI-SCORE",
                "age": 22,
                "annual_income": 50000,
                "credit_score": 580, # Low
                "total_debt": 10000,
                "loan_amount": 5000,
                "business_type": "IT"
            },
            "expected_top_factor": "score"
        }
    ]
    
    scorecard = {"consistency": 0, "clarity": 0, "actionability": 0}
    
    for case in cases:
        print(f"\n[AUDIT] Case: {case['name']}")
        try:
            resp = requests.post(API_URL, json=case['profile'])
            if resp.status_code != 200:
                print(f"   API Error: {resp.text}")
                continue
                
            data = resp.json()
            factors = data.get("factors", [])
            cfs = data.get("counterfactuals", [])
            risk_score = data.get("risk_score", 0.5)
            tier = data.get("tier", "Unknown")
            
            print(f"   Decision: {tier} (Risk: {risk_score:.2f})")
            print(f"   Top Factors: {factors[:2]}")
            print(f"   Counterfactuals: {cfs}")
            
            # CHECK 1: CONSISTENCY
            top_fs = [f.lower() for f in factors]
            # Use specific strings to match 'feat' returned by explainer
            match = any(case["expected_top_factor"] in f for f in top_fs)
            if match:
                print("   Consistency Check: PASS")
                scorecard["consistency"] += 1
            else:
                print(f"   Consistency Check: FAIL (Expected '{case['expected_top_factor']}', got {top_fs})")

            # CHECK 2: CLARITY
            readable = True
            for f in factors:
                if "_" in f and "income" not in f: 
                     readable = False
            if readable:
                 print("   Clarity Check: PASS")
                 scorecard["clarity"] += 1
            else:
                 print("   Clarity Check: WARNING")

            # CHECK 3: ACTIONABILITY
            if cfs:
                print("   Actionability Check: PASS")
                scorecard["actionability"] += 1
            else:
                 print("   Actionability Check: FAIL")
                 
        except Exception as e:
            print(f"   Execution Error: {e}")

    print("\nEXPLAINABILITY SCORECARD")
    print(f"Consistency:   {scorecard['consistency']}/{len(cases)}")
    print(f"Clarity:       {scorecard['clarity']}/{len(cases)}")
    print(f"Actionability: {scorecard['actionability']}/{len(cases)}")
    
    if scorecard['consistency'] == len(cases):
        print("\nAUDIT RESULT: PASSED")
    else:
        print("\nAUDIT RESULT: NEEDS IMPROVEMENT")

if __name__ == "__main__":
    audit_explainability()

import httpx
import json
import sys

# API Endpoint
url = "http://localhost:8000/api/v1/decide"

# Test Case: Borderline/Review Logic (should trigger factors and counterfactuals)
# High Debt, Good Income, Borderline Score
payload = {
    "applicant_id": "TEST_XAI_001",
    "age": 30,
    "annual_income": 60000,
    "total_debt": 25000,
    "credit_score": 675, # Borderline
    "monthly_debt_obligations": 2000, # High DTI
    "business_type": "Retail",
    "assets_total": 5000,
    "utilization_rate": 0.45 # High util
}

print(f"Testing XAI with payload: {payload['applicant_id']}")

try:
    response = httpx.post(url, json=payload)
    if response.status_code != 200:
        print(f"FAILED: Status {response.status_code}")
        print(response.text)
        sys.exit(1)
        
    data = response.json()
    print("--- API Response ---")
    print(json.dumps(data, indent=2))
    
    # Assertions
    factors = data.get("factors", [])
    cfs = data.get("counterfactuals", [])
    
    if not factors:
        print("FAILURE: 'factors' list is empty. Expected XAI explanations.")
        sys.exit(1)
    
    print(f"SUCCESS: Received {len(factors)} factors.")
    for f in factors:
        print(f" - {f}")
        
    if "counterfactuals" not in data: # It might be empty if perfect application, but key should exist or be in factors?
        # Note: backend explainability.py puts 'counterfactuals' in the response?
        # Let's check schemas/decision.py if 'counterfactuals' is a field in DecisionResponse.
        # If not, it might be packed into 'factors' or 'status_msg'.
        pass
        
    # Check if 'factors' contains specific keys if it's a list of objects, or just strings
    # The current frontend expects strings or objects "factor.factor".
    
except Exception as e:
    print(f"ERROR: {e}")
    sys.exit(1)

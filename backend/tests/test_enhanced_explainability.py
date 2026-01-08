"""
Test Enhanced Explainability
"""
import requests
import json

# Test endpoint
url = "http://localhost:8000/api/v1/decide"

# Test case: Borderline applicant
test_case = {
    "age": 35,
    "annual_income": 65000,
    "credit_score": 680,
    "total_debt": 35000,
    "business_type": "Construction",
    "credit_utilization": 0.50
}

print("="*80)
print("TESTING ENHANCED EXPLAINABILITY")
print("="*80)

print(f"\nTest Case:")
print(json.dumps(test_case, indent=2))

try:
    response = requests.post(url, json=test_case)
    
    if response.status_code == 200:
        result = response.json()
        
        print(f"\n{'='*80}")
        print("ENHANCED RESPONSE")
        print(f"{'='*80}")
        
        print(f"\nDecision: {result.get('tier', 'N/A')}")
        print(f"Risk Score: {result.get('risk_score', 'N/A')}")
        print(f"Confidence: {result.get('confidence_score', 'N/A')}")
        print(f"Reason: {result.get('reason_flag', 'N/A')}")
        
        print(f"\nFactors:")
        for factor in result.get('factors', []):
            print(f"  - {factor}")
        
        print(f"\nRecommendations:")
        for rec in result.get('counterfactuals', []):
            print(f"  - {rec}")
        
        print(f"\nFull Response:")
        print(json.dumps(result, indent=2))
        
        print(f"\n✓ Enhanced explainability working!")
    else:
        print(f"\n✗ Error: {response.status_code}")
        print(response.text)
        
except Exception as e:
    print(f"\n✗ Connection error: {e}")
    print("Make sure the backend server is running on port 8000")

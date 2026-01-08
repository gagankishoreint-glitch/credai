"""
Test the simple endpoint
"""
import requests
import json

application = {
    "age": 42,
    "annual_income": 95000,
    "credit_score": 750,
    "total_debt": 15000,
    "business_type": "IT"
}

print("Testing /test-simple endpoint...")
response = requests.post(
    "http://localhost:8000/api/v1/test-simple",
    json=application
)

print(f"Status: {response.status_code}")
if response.status_code == 200:
    print(f"✓ SUCCESS!\n{json.dumps(response.json(), indent=2)}")
else:
    print(f"✗ FAILED: {response.text}")

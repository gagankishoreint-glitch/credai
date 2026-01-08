"""
Test without authentication
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

application = {
    "age": 42,
    "annual_income": 95000,
    "credit_score": 750,
    "total_debt": 15000,
    "business_type": "IT"
}

print("Testing /decide endpoint (no auth)...")
print(f"Request: {json.dumps(application, indent=2)}\n")

response = requests.post(
    f"{BASE_URL}/decide",
    json=application
)

print(f"Status: {response.status_code}")
print(f"Headers: {dict(response.headers)}\n")

try:
    print(f"Response: {json.dumps(response.json(), indent=2)}")
except:
    print(f"Raw Response: {response.text[:500]}")
